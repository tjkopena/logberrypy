#!/usr/bin/env python3

import argparse
import pathlib
import tempfile
import os
import stat
import subprocess
import sys
import re
import shutil

parser = argparse.ArgumentParser(description='Command Line Spec Test')
parser.add_argument('file', type=str, help="name of test specification file")
parser.add_argument('--save_scr', action='store_true', default=False, help='save the temporary script file')
parser.add_argument('-q', '--quiet', action='store_true', default=False, help='only report success or error(s)')
parser.add_argument('-o', '--output', action='store_true', default=False, help='show script output even on success')
parser.add_argument('--noout', action='store_true', default=False, help='don\'t show script output even on error')
parser.add_argument('--nolines', action='store_true', default=False, help='do not include line numbers on script output')
parser.add_argument('-s', '--save_out', action='store_true', default=False, help='write script output to file')
parser.add_argument('--maxerr', type=int, default=8, help="maximum number of errors to display; -1 for all")
args = parser.parse_args()

_print = print
if args.quiet:
    def noprint(*args, **kwargs):
        pass
    print = noprint
print(f"Testing {args.file}")
suffix = ''.join(pathlib.Path(args.file).suffixes)

expressions = []
exp_retcode = 0

tmp = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)

with open(args.file, 'r') as fp:
    l = fp.readline()
    while l and l.strip().lower() != '## spec':
        tmp.write(l)
        l = fp.readline()
    tmp.close()
    perms = os.stat(args.file)
    os.chmod(tmp.name, perms.st_mode | stat.S_IEXEC)
    print(f"Wrote temp script to {tmp.name}")

    l = fp.readline().strip()
    while l:
        if l.startswith('##'):
            if l.lower().startswith('## retcode'):
                l = l[len('## retcode'):]
                exp_retcode = int(l.strip())
        else:
            if l.startswith('#'):
                l = l[1:]
            expressions.append(l)

        l = fp.readline().strip()


print(f"Executing {tmp.name}")
print(f"  Expecting retcode {exp_retcode}")
print(f"  Applying {len(expressions)} expression{'' if len(expressions) == 1 else 's'}")

proc = subprocess.Popen(tmp.name, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, env=os.environ.copy())
(output, _) = proc.communicate()

if not args.save_scr:
    os.remove(tmp.name)
    print(f"Deleted temp script {tmp.name}")

if args.save_out:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(output)
        print(f"Wrote output to {tmp.name}")


errors = []

if exp_retcode != proc.returncode:
    errors.append(f"Return code {proc.returncode} does not match expected {exp_retcode}")

output = output.decode('utf-8').splitlines()
if len(expressions) > len(output):
    errors.append(f"Missing output, {len(expressions)} expressions versus {len(output)} outputs")
elif len(expressions) < len(output):
    ex = False
    for l in output[len(expressions):]:
        if str(l):
            ex = True
    if ex:
        errors.append(f"Unexpected excess output, {len(expressions)} expressions versus {len(output)} outputs")

width = None
if sys.stdout.isatty():
    width = shutil.get_terminal_size().columns

for i in range(min(len(expressions), len(output))):
    m = re.match(expressions[i], output[i])
    if not m:
        errors.append(f"Mismatch on line {i+1}\n"
                      f"        Expected: {expressions[i]}\n"
                      f"        Received: {output[i]}")

outcome = 0
if not errors:
    print()
    _print("SUCCESS")
else:
    outcome = -1
    print()
    _print(f"ERRORS ({len(errors)})")
    n = min(len(errors), args.maxerr) if args.maxerr >= 0 else len(errors)
    for i,e in enumerate(errors[:n]):
        print(f"  {i:2}: " + e)

    if args.maxerr > 0 and n != len(errors):
        print("  Too many errors, stopping...")

if not args.quiet and (args.output or (len(errors) and not args.noout)):
    print("\nOUTPUT")
    for i,l in enumerate(output):
        if args.nolines:
            print(l)
        else:
            print(f"{i+1:3}:", l)

exit(outcome)

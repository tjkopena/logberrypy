#!/usr/bin/env python3

import logberry

logberry.start()
t = logberry.log().task('Run a simple task')
t.info("Say hello", time="morning", _banana='yellow')
t.end()
logberry.stop()

## SPEC
#\d{8}T\d\d:\d\d:\d\d.\d{6} BEGIN\s+main\s+1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} BEGIN\s+main::Run a simple task\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} INFO\s+main::Run a simple task - Say hello\s+2:1\s+time: "morning"\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main::Run a simple task\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main\s+1\s*

#!/usr/bin/env python3

import logberry

logberry.start()
t = logberry.log().task('Outer task')
t1 = t.task('Inner task')
t1.end()
t.end()
logberry.stop()

## SPEC
#\d{8}T\d\d:\d\d:\d\d.\d{6} BEGIN\s+main\s+1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} BEGIN\s+main::Outer task\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} DONE\s+main::Inner task\s+3:2\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main::Outer task\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main\s+1\s*

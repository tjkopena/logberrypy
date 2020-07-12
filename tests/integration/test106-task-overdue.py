#!/usr/bin/env python3

import logberry
import time

logberry.start()
t = logberry.log().task('Run a simple task')
time.sleep(3)
t.end()
logberry.stop()

## SPEC
#\d{8}T\d\d:\d\d:\d\d.\d{6} BEGIN\s+main\s+1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} LATE\s+main::Run a simple task\s+-\s+Overdue\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main::Run a simple task\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main\s+1\s*

#!/usr/bin/env python3

import logberry

@logberry.wrap(label="MYFUNCTION")
def foo():
    logberry.info("working normally")

logberry.start()
foo()
logberry.stop()

## SPEC
#\d{8}T\d\d:\d\d:\d\d.\d{6} BEGIN\s+main\s+1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} BEGIN\s+main::MYFUNCTION\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} INFO\s+main::MYFUNCTION - working normally\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main::MYFUNCTION\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main\s+1\s*

#!/usr/bin/env python3

import logberry

@logberry.wrap
def foo():
    logberry.info("working normally")

logberry.start()
foo()
logberry.stop()

## SPEC
#\d{8}T\d\d:\d\d:\d\d.\d{6} BEGIN\s+main\s+1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} BEGIN\s+main::foo\(\)\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} INFO\s+main::foo\(\) working normally\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main::foo\(\)\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main\s+1\s*

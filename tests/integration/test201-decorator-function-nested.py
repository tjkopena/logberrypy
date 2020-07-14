#!/usr/bin/env python3

import logberry

@logberry.wrap
def bar():
    logberry.info("inner functionality")

@logberry.wrap
def foo():
    logberry.info("working normally")
    bar()
    logberry.info("still working normally")

logberry.start()
foo()
logberry.stop()

## SPEC
#\d{8}T\d\d:\d\d:\d\d.\d{6} BEGIN\s+main\s+1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} BEGIN\s+main::foo\(\)\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} INFO\s+main::foo\(\) working normally\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} BEGIN\s+main::bar\(\)\s+3:2\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} INFO\s+main::bar\(\) inner functionality\s+3:2\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main::bar\(\)\s+3:2\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} INFO\s+main::foo\(\) still working normally\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main::foo\(\)\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main\s+1\s*

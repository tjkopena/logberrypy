#!/usr/bin/env python3

import logberry

@logberry.wrap
def foo(id=0, log=None):
    log.info("working normally")

logberry.start()
foo(7)
logberry.stop()

## SPEC
#\d{8}T\d\d:\d\d:\d\d.\d{6} BEGIN\s+main\s+1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} BEGIN\s+main::foo\(id: 7\)\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} INFO\s+main::foo\(id: 7\) working normally\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main::foo\(id: 7\)\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main\s+1\s*

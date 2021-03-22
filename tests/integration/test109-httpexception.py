#!/usr/bin/env python3

import logberry

@logberry.wrap
def myfunc():
    r = {
        'status_code': 400,
        }
    raise logberry.HTTPException("couldn't get bananagrams", r)


logberry.start()
try:
    myfunc()
except Exception as e:
    logberry.exception(e)
logberry.stop()

## SPEC
#\d{8}T\d\d:\d\d:\d\d.\d{6} BEGIN\s+main\s+1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} FAILED\s+main::myfunc\(\) HTTPException: couldn't get bananagrams\s+2:1\s+status_code: 400\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} ERROR\s+main HTTPException: couldn't get bananagrams\s+1\s+status_code: 400\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main\s+1\s*

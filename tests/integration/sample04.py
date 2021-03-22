#!/usr/bin/env python3

import logberry

logberry.start()
t = logberry.task("Login", user="joe")
t.info("Authenticated", server="dc")
t.info("Authorizing", permissions="r")
t.end()
logberry.stop()

## SPEC
#\d{8}T\d\d:\d\d:\d\d.\d{6} BEGIN\s+main\s+1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} BEGIN\s+main::Say hello\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} DONE\s+main::Wave\s+3:2\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main::Say hello\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main\s+1\s*

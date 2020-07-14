#!/usr/bin/env python3

import logberry

logberry.start()
t = logberry.log().task('Run a simple task', id=14, _ttl=7)
t.end()
logberry.stop()

## SPEC
#\d{8}T\d\d:\d\d:\d\d.\d{6} BEGIN\s+main\s+1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} DONE\s+main::Run a simple task \{id: 14\}\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main\s+1\s*

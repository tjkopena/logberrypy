#!/usr/bin/env python3

import logberry

@logberry.wrap
class Sushi:
    pass

logberry.start()
x = Sushi()
x = None
logberry.stop()

## SPEC
#\d{8}T\d\d:\d\d:\d\d.\d{6} BEGIN\s+main\s+1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} BEGIN\s+main::Sushi\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main::Sushi\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main\s+1\s*

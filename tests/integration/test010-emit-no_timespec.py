#!/usr/bin/env python3

import logberry

logberry.start(emitters=[logberry.Printer(timespec=None)])
logberry.stop()

## SPEC
#BEGIN\s+main\s+1\s*
#END\s+main\s+1\s*

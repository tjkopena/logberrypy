#!/usr/bin/env python3

import logberry
import requests

logberry.start()

t = logberry.task("Fetch data", user='joe')
try:
    r = requests.get("https://google.com", params={'user': 'joe'})
except Exception as e:
    t.end_exception(e)
else:
    t.end_success()

logberry.stop()

## SPEC
#\d{8}T\d\d:\d\d:\d\d.\d{6} BEGIN\s+main\s+1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} DONE\s+main::Say hello\s+2:1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main\s+1\s*

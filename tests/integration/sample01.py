#!/usr/bin/env python3

import logberry

logberry.start()
logberry.info('Hello world',
              port=7000,
              proto_version="1.0.7b",
              user={'dc': 'myorg', 'name': 'joe'})
logberry.stop()

## SPEC
#\d{8}T\d\d:\d\d:\d\d.\d{6} BEGIN\s+main\s+1\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} INFO\s+main Hello world\s+1\s+port: 7000, proto_version: "1.0.7b", user: {'dc': 'myorg', 'name': 'joe'}\s*
#\d{8}T\d\d:\d\d:\d\d.\d{6} END\s+main\s+1\s*

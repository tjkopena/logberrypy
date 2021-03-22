Logberry (py) <img src="docs/logberry.png" height=48 title="LogberryPy" alt="Picture of a strawberry" style="vertical-align: middle"/>
=======

Logberry (py) provides structured, contextualized logging for Python programs.

## Motivation

Historically most logging packages focus on "how." Many options for
output devices and formats and tiers and so on.  But the core action
is not that far advanced from the C classic:

```
#ifdef DEBUG
#define debug_print(fmt, ...) fprintf(stderr, fmt, __VA_ARGS__)
#else
#define debug_print(fmt, ...) do {} while (0)
#endif
```

Or the [much more sophisticated](https://stackoverflow.com/a/1644898):

```
#define debug_print(fmt, ...) \
            do { if (DEBUG) fprintf(stderr, fmt, __VA_ARGS__); } while (0)
```

Most logging packages don't provide much guidance on "what."
* What is the meaning of this debug statement?
* What is the context of this debug statement?
* What is the data relevant to this debug statement?

These are the questions to which Logberry tries to foster answers.

## Installation

```
% pip install git+https://github.com/tjkopena/logberrypy
```

## Usage

Most trivial example:

```
#!/usr/bin/env python3

import logberry

logberry.start()
logberry.info('Hello world')
logberry.stop()
```

```
20200806T00:59:27.059023 BEGIN   main                                                     1
20200806T00:59:27.059063 INFO    main Hello world                                         1
20200806T00:59:27.059081 END     main                                                     1
```

Some data:

```
logberry.start()
logberry.info('Hello world',
              port=7000,
              proto_version="1.0.7b",
              user={'dc': 'myorg', 'name': 'joe'})
logberry.stop()
```

```
20200806T01:04:29.778927 INFO    main Hello world                                         1     port: 7000, proto_version: "1.0.7b", user: {'dc': 'myorg', 'name': 'joe'}
20200806T01:04:29.778954 END     main                                                     1
```

A task:

```
logberry.start()
t = logberry.task("Say hello")
t.end()
logberry.stop()
```

```
20200806T01:08:33.753693 BEGIN   main                                                     1
20200806T01:08:33.753755 DONE    main::Say hello                                          2:1
20200806T01:08:33.753773 END     main                                                     1
```

Nested tasks:

```

logberry.start()
t = logberry.task("Say hello")
t1 = t.task("Wave")
t1.end()
t.end()
logberry.stop()
```

```
20200806T01:11:06.930737 BEGIN   main                                                     1
20200806T01:11:06.930778 BEGIN   main::Say hello                                          2:1
20200806T01:11:06.930817 DONE    main::Wave                                               3:2
20200806T01:11:06.930831 END     main::Say hello                                          2:1
20200806T01:11:06.930856 END     main                                                     1
```

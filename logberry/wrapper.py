import inspect
from functools import wraps

import asyncio
import contextvars
from contextlib import contextmanager

import logberry._globals as _globals

_hide = {}
hide = _hide

_show = {}
show = _show

context = contextvars.ContextVar('task context')

def _log():
    cxt = context.get([_globals.main])
    return cxt[-1]
log = _log

def _push(t):
    cxt = context.get([_globals.main])
    cxt.append(t)
    context.set(cxt)

def _pop():
    cxt = context.get()
    ret = cxt.pop()
    context.set(cxt)
    return ret

def _wrap_class(cls, label=None, **wrapargs):
    ini = getattr(cls, '__init__', None)
    dl = getattr(cls, '__del__', None)

    def newinit(self, *args, **kwargs):
        setattr(self, 'log', _globals.main.component(cls.__name__))
        if ini:
            ini(self, *args, **kwargs)

    def newdel(self, *args, **kwargs):
        if dl:
            dl(self, *args, **kwargs)
        self.log.end()

    setattr(cls, '__init__', newinit)
    setattr(cls, '__del__', newdel)
    return cls

def _wrap_func(func, label=None, hide=[], **wrapargs):

    desc = next((desc for desc in (staticmethod, classmethod) if isinstance(func, desc)), None)
    if desc:
        func = func.__func__

    def decorator(func):
        global _hide
        global _show

        sig = inspect.signature(func)

        is_func = False if label else True
        newlabel = label if label else func.__name__

        newhide = hide
        hideset = set()
        if newhide:
            if newhide == '*':
                hideset = { k for k in sig.parameters }
            else:
                if not isinstance(newhide, list):
                    newhide = [ newhide ]
                hideset = { k for k in newhide }

        for p in sig.parameters.values():
            if p.annotation is _hide:
                hideset.add(p.name)
            elif p.annotation is _show:
                hideset.discard(p.name)

        @wraps(func)
        def inner(*args, log=None, **kwargs):

            @contextmanager
            def wrapping_logic():
                nonlocal log
                cls, nonselfargs = _declassify(func, args)

                if not log:
                    if cls:
                        log = getattr(args[0], 'log', None)
                        if not log:
                            log = _log()
                    else:
                        log = _log()

                binding = sig.bind_partial(*nonselfargs, **kwargs)
                binding.apply_defaults()
                exargs = { k: v for k,v in binding.arguments.items() if k not in hideset }

                for k in ['log', 'self']:
                    if k in exargs:
                        del exargs[k]

                t = log.task(newlabel, is_func=is_func, **exargs)
                _push(t)

                if 'log' in sig.parameters:
                    kwargs['log'] = t

                try:
                    yield
                except Exception as e:
                    raise t.end_exception(e)
                finally:
                    _pop()

                t.end()

            if not asyncio.iscoroutinefunction(func):
                with wrapping_logic():
                    return func(*args, **kwargs)
            else:
                async def tmp():
                    with wrapping_logic():
                        return (await func(*args, **kwargs))
                return tmp()

        inner.original = func

        if desc:
            inner = desc(inner)

        return inner

    if func is not None:
        return decorator(func)
    return decorator

def _declassify(fun, args):
    if len(args):
        met = getattr(args[0], fun.__name__, None)
        if met:
            wrap = getattr(met, '__func__', None)
            if getattr(wrap, 'original', None) is fun:
                maybe_cls = args[0]
                cls = maybe_cls if inspect.isclass(maybe_cls) else maybe_cls.__class__
                return cls, args[1:]
    return None, args

def wrap(func=None, label=None, **kwargs):
    if inspect.isclass(func):
        return _wrap_class(func, label, **kwargs)
    return _wrap_func(func, label, **kwargs)

from .task import Task, Exception
from .background import _start, _stop
from .wrapper import wrap, log
import logberry._globals as _globals
from .printer import Printer

def start(**kwargs):
    if _globals.main:
        return

    _start(**kwargs)

    _globals.main = Task(None, "main", is_component=True)

def stop():
    _globals.main.end()
    _stop()

def main():
    return _globals.main

def attach(**kwargs):
    return log().attach(**kwargs)

def component(*args, **kwargs):
    return log().component(*args, **kwargs)

def task(*args, **kwargs):
    return log().task(*args, **kwargs)

def end(*args, **kwargs):
    return log().end(*args, **kwargs)

def end_success(*args, **kwargs):
    return log().end_success(*args, **kwargs)

def end_exception(*args, **kwargs):
    return log().end_exception(*args, **kwargs)

def end_failure(*args, **kwargs):
    return log().end_failure(*args, **kwargs)

def info(*args, **kwargs):
    return log().info(*args, **kwargs)

def exception(*args, **kwargs):
    return log().exception(*args, **kwargs)

def error(*args, **kwargs):
    return log().error(*args, **kwargs)

def warning(*args, **kwargs):
    return log().warning(*args, **kwargs)

__all__ = ['start', 'stop', 'Exception', 'Printer', 'wrap', 'log', 'main', 'attach', 'component', 'task', 'end', 'end_success', 'end_exception', 'end_failure', 'info', 'exception', 'error', 'warning']

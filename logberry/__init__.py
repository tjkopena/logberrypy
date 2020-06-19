from .task import Task, Exception
from .threading import _start, _stop

main = None

def start():
    global main
    _start()

    main = Task(None, "main", is_component=True)

def stop():
    global main
    main.end()
    _stop()

__all__ = ["start", "stop", "main", "Exception"]

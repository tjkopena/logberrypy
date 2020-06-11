from .task import _start, _stop, Task, Exception

main = None

def start():
    global main
    task._start()

    main = Task(None, "main", is_component=True)

def stop():
    global main
    main.end()
    task._stop()

__all__ = ["start", "stop", "main", "Exception"]

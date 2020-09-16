import jsonpickle

from .event import Event

evt_labels = {
    Event.NOOP:  "NO-OP",
    Event.BEGIN: "BEGIN",
    Event.END:   "END",
    Event.INFO:  "INFO",
    Event.ERROR: "ERROR",
    Event.WARNING: "WARNING",
}

class JSONOutput():
    def __init__(self):
        pass

    def emit(self, event):
        event.code = evt_labels[event.code]
        event.timestamp = event.timestamp.strftime("%Y%m%dT%H:%M:%S.%f")
        print(jsonpickle.encode(event, unpicklable=False))

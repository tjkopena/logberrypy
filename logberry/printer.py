import asyncio
import string

from .event import Event

evt_labels = {
    Event.NOOP:  "NO-OP",
    Event.BEGIN: "BEGIN",
    Event.END:   "END",
    Event.ERROR: "ERROR",
    Event.INFO:  "INFO",
}

held_begins = {}

class Printer():
    def overdue(self, event):
        event = held_begins.pop(event.task.id, None)
        if not event:
            return
        parent = held_begins.pop(event.task.parent_id, None)
        if parent:
            self.recurse_begins(parent)
        self.output(event, type="LATE", msg='Overdue' + (f": {event.msg}" if event.msg else ''))

    def emit(self, event):
        assert(event.task)

        if event.type == Event.BEGIN:
            held_begins[event.task.id] = event
            asyncio.get_event_loop().call_later(2, lambda: self.overdue(event))
            return

        type = None

        begin = held_begins.pop(event.task.id, None)
        if begin:
            if event.type == Event.END:
                type = "DONE"
                event.ephemeral.update(begin.ephemeral)
                parent = held_begins.pop(event.task.parent_id, None)
                if parent:
                    self.recurse_begins(parent)
            else:
                self.recurse_begins(begin)

        self.output(event, type=type)

    def recurse_begins(self, event):
        begin = held_begins.pop(event.task.parent_id, None)
        if begin:
            self.recurse_begins(begin)
        self.output(event)

    def output(self, event, type=None, msg=None):

        tstamp = event.timestamp.isoformat(sep='T', timespec='milliseconds')

        id_parent = f":{event.task.parent_id}" if event.task.parent_id else ''
        id = f"{event.task.id}{id_parent}"

        label_comp = ''
        if event.component:
            idents = ', '.join([f'{k}: {v}' for (k, v) in event.component.identifiers.items()])
            label_comp = f"{event.component.label}[{idents}]::"

        label_task = ''
        idents = ', '.join([f'{k}: {v}' for (k, v) in event.task.identifiers.items()])
        delim = ('(', ')')
        if event.task.is_component:
            delim = ('[', ']')
        label_task = f"{event.task.label}{delim[0]}{idents}{delim[1]}"

        label = f"{label_comp}{label_task}"

        eph = ', '.join([f'{k}: {v}' for (k, v) in event.ephemeral.items()])

        if not type:
            type = evt_labels[event.type]

        if not msg:
            msg = event.msg

        print(f"\r{tstamp} {type:5} {label:<42} {msg:<32} {id:<5} {eph}")

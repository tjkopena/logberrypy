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

        report_class = None

        begin = held_begins.pop(event.task.id, None)
        if begin:
            if event.type == Event.END:
                if event.task.label.startswith('_') and not event.task.failed:
                    return
                report_class = "FAILED" if event.task.failed else "DONE"
                event.ephemeral.update(begin.ephemeral)
                parent = held_begins.pop(event.task.parent_id, None)
                if parent:
                    self.recurse_begins(parent)
            else:
                self.recurse_begins(begin)

        self.output(event, report_class=report_class)

    def recurse_begins(self, event):
        begin = held_begins.pop(event.task.parent_id, None)
        if begin:
            self.recurse_begins(begin)
        self.output(event)

    def output(self, event, report_class=None, msg=None):

        tstamp = event.timestamp.isoformat(sep='T', timespec='milliseconds')

        id_parent = f":{event.task.parent_id}" if event.task.parent_id else ''
        id = f"{event.task.id}{id_parent}"

        label_comp = ''
        if event.component:
            idents = ', '.join([f'{k}: {v}' for (k, v) in event.component.identifiers.items()])
            label_comp = f"{event.component.label}[{idents}]::"

        label_task = ''
        idents = ', '.join([f'{k}: {v}' for (k, v) in event.task.identifiers.items()])
        delim = ('', '')
        if event.task.is_component:
            delim = ('[', ']')
        elif event.task.is_func:
            delim = ('(', ')')
        label_task = f"{event.task.label}{delim[0]}{idents}{delim[1]}"


        eph = ', '.join([f'{k}: {v}' for (k, v) in event.ephemeral.items()])

        if not report_class:
            report_class = evt_labels[event.type]

        text = f"{label_comp}{label_task}"

        if not msg:
            msg = event.msg
        if msg:
            text = text + ": " + msg

        print(f"\r{tstamp} {report_class:5} {text:<80} {id:<5} {eph}")

        if event.blob:
            print(event.blob)

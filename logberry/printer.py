import asyncio
import string
import sys
import shutil

from .event import Event

evt_labels = {
    Event.NOOP:  "NO-OP",
    Event.BEGIN: "BEGIN",
    Event.END:   "END",
    Event.INFO:  "INFO",
    Event.ERROR: "ERROR",
    Event.WARNING: "WARNING",
}

held_begins = {}

class Printer():
    def __init__(self, width=None, timespec=True):
        self.tty = sys.stdout.isatty()

        if width:
            self.width = width
        elif self.tty:
            self.width = shutil.get_terminal_size().columns
        else:
            self.width = 128

        if timespec:
            if isinstance(timespec, str):
                self.timespec = timespec
            elif self.tty and self.width < 128:
                self.timespec = "%H:%m:%S.%f"
            else:
                self.timespec = "%Y%m%dT%H:%M:%S.%f"
        else:
            self.timespec = None

    def overdue(self, event):
        event = held_begins.pop(event.task.id, None)
        if not event:
            return
        parent = held_begins.pop(event.task.parent_id, None)
        if parent:
            self.recurse_begins(parent)
        self.output(event, report_class="LATE", msg='Overdue' + (f": {event.msg}" if event.msg else ''))

    def params_text(params):
        def q(v):
            if isinstance(v, str):
                v = '"' + v + '"'
            return v
        return ', '.join([f'{k}: {q(v)}' for (k, v) in params.items() if not k.startswith('_')])

    def emit(self, event):
        assert(event.task)

        if not event.task.is_component and event.code == Event.BEGIN:
            held_begins[event.task.id] = event
            asyncio.get_event_loop().call_later(2, lambda: self.overdue(event))
            return

        report_class = None

        begin = held_begins.pop(event.task.id, None)
        if begin:
            if event.code == Event.END:
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
        self.output(event, maybelate=False)

    def output(self, event, report_class=None, msg=None, maybelate=True):

        tstamp = (event.timestamp.strftime(self.timespec) + " ") if self.timespec else ""

        id_parent = f":{event.task.parent_id}" if event.task.parent_id else ''
        id = f"{event.task.id}{id_parent}"

        label_comp = ''
        if event.component:
            idents = Printer.params_text(event.component.identifiers)
            label_comp = f"{event.component.label}" + (f"[{idents}]" if idents else '') + '::'

        label_task = ''
        idents = Printer.params_text(event.task.identifiers)
        delim = ('', '')
        if event.task.is_component:
            if idents:
                delim =  ('[', ']')
        elif event.task.is_func:
            delim = ('(', ')')
        elif idents:
            delim = (' {', '}')
        label_task = f"{event.task.label}{delim[0]}{idents}{delim[1]}"


        eph = Printer.params_text(event.ephemeral)

        if not report_class:
            report_class = evt_labels[event.code]

        text = f"{label_comp}{label_task}"

        if not msg:
            msg = event.msg
        if msg:
            msgsep = ' '
            if not event.task.is_func and not event.task.is_component:
                msgsep = ' - '
            text = text + msgsep + msg

        clear = "\r" if self.tty else ''
        w = self.width - (len(tstamp)+1+8+6+32)
        print(f"{clear}{tstamp}{report_class:7} {text:<{w}} {id:<5} {eph}")

        if event.text:
            print(event.text)

        if event.binary:
            print(F"<binary data {len(event.binary)} bytes>")

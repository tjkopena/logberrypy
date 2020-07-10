from copy import deepcopy

class Event:
    NOOP    = 0
    BEGIN   = 1
    END     = 2
    INFO    = 3
    ERROR   = 4
    WARNING = 5

    class Component:
        def __init__(self, component):
            self.id = component.id
            self.label = component.label
            self.identifiers = deepcopy(component.identifiers)

    class Task:
        def __init__(self, task):
            self.id = task.id
            self.parent_id = task.parent.id if task.parent else None
            self.is_func = task.is_func
            self.is_component = task.is_component
            self.label = task.label
            self.identifiers = deepcopy(task.identifiers)
            self.failed = task.failed

    def __init__(self, code, component, task, msg, timestamp, text, binary, ephemeral):
        self.code = code
        self.component = Event.Component(component) if component else None
        self.task = Event.Task(task)
        self.msg = msg
        self.timestamp = timestamp
        self.ephemeral = deepcopy(ephemeral)
        self.text = deepcopy(text)
        self.binary = deepcopy(binary)

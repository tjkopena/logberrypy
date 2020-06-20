from copy import deepcopy

class Event:
    NOOP  = 0
    BEGIN = 1
    END   = 2
    ERROR = 3
    INFO  = 4

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

    def __init__(self, type, component, task, msg, timestamp, blob, ephemeral):
        self.type = type
        self.component = Event.Component(component) if component else None
        self.task = Event.Task(task)
        self.msg = msg
        self.timestamp = timestamp
        self.ephemeral = deepcopy(ephemeral)
        self.blob = deepcopy(blob)

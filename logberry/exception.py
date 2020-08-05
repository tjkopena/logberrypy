from .utils import params_text

def _exception_label(ex, msg, kwargs):
    if isinstance(ex, Exception):
        msg = f'{msg}: {ex.text()}' if msg else ex.text()
        kwargs.update(ex.data())
    else:
        ex_str = str(ex)
        type_str = type(ex).__name__
        type_str = '' if ex_str.startswith(type_str) else (type_str + ': ')
        text = f"{type_str}{ex_str}"
        msg = f"{msg}: {text}" if msg else text
    return msg

class Exception(Exception):
    def __init__(self, msg='',  **kwargs):
        self.msg = msg
        self.identifiers = kwargs
        super().__init__(msg)

    def __str__(self):
        d = params_text(self.identifiers)
        if d:
            d = f" {{{d}}}"
        msg = (': ' if self.msg else '') + self.msg
        return f'{self.msg}{d}'

    def text(self):
        msg = (': ' if self.msg else '') + self.msg
        return f'{type(self).__name__}{msg}'

    def data(self):
        return self.identifiers

class HTTPException(Exception):
    def __init__(self, msg, *args, **kwargs):

        for a in args:
            if isinstance(a, int):
                kwargs['status_code'] == a
            elif isinstance(a, str):
                if 'reason' in kwargs:
                    kwargs['text'] = a
                else:
                    kwargs['reason'] = a
            elif isinstance(a, dict):
                if 'status_code' in a:
                    kwargs['status_code'] = a['status_code']
                if 'reason' in a:
                    kwargs['reason'] = a['reason']
                if 'text' in a:
                    kwargs['text'] = a['text']
            else:
                if hasattr(a, 'status_code'):
                    kwargs['status_code'] == a.status_code
                if hasattr(a, 'reason'):
                    kwargs['reason'] == a.reason
                if hasattr(a, 'text'):
                    kwargs['text'] == a.text

        super().__init__(msg, **kwargs)

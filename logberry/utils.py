
def _q(s):
    return ('"' + s + '"') if isinstance(s, str) else s

def params_text(params):
    return ', '.join([f'{k}: {_q(v)}' for (k, v) in params.items() if not k.startswith('_')])

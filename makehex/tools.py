import logging
from functools import wraps, lru_cache


@lru_cache(1024 * 8)
def import_py_file(name) -> dict:
    logging.debug("Importing py file %s...", name)
    locals_ = {}
    try:
        with open(name) as f:
            exec(compile(f.read(), name, 'exec'), locals_, locals_)
        return locals_
    except:
        logging.exception("Can`t import py file %s", name)
        raise


def xint(v: str) -> int:
    if v[:2] == "0x" or v[:2] == "0X":
        return int(v[2:], 16)
    elif v[:2] == "0b" or v[:2] == "0B":
        return int(v[2:], 2)
    elif v[:1] == "0" and len(v) > 1:
        return int(v[1:], 8)
    else:
        return int(v)


class CB:
    def __init__(self, fn):
        self.eval = fn

    def write(self, args, out, locals_, globals_: dict, body=None) -> None:
        result = self.eval(args, out, locals_, globals_, body)
        if isinstance(result, bytes):
            out.write(result)
        else:
            logging.warning("Result '%s' is not bytes!", result)

    def set_typed_write(self, **kwargs):
        def wrap(fn):
            self.write = CB.typed(cb=False, **kwargs)(fn)
        return wrap

    @staticmethod
    def typed(*_, string_args=False, cb=True, arg_count=None, need_locals=(), need_globals=(), need_body=False, skip=()):
        if isinstance(need_locals, str):
            need_locals = need_locals,

        if isinstance(need_globals, str):
            need_globals = need_globals,

        if isinstance(skip, str):
            skip = skip,

        def decorator(fn):
            @wraps(fn)
            def cb_typed_checker(args: dict, out, locals_: dict, globals_: dict, body=None):
                if need_body:
                    if body is None:
                        logging.error("Can`t call %s as function", fn.__name__)
                        return b''

                    if not (hasattr(body, 'eval') and hasattr(body, 'write')):
                        logging.error("%s is not valid body" % body)
                        return b''

                for i in need_globals:
                    if i not in globals_:
                        logging.error("%s needs global `%s`" % (fn.__name__, i))
                        return b''

                for i in need_locals:
                    if i not in locals_:
                        logging.error("%s needs local `%s`" % (fn.__name__, i))
                        return b''

                if string_args:
                    for k, v in args.items():
                        args[k] = [s.s for s in v]

                if arg_count is not None:
                    args_len = len(args)
                    if isinstance(arg_count, int) and args_len != arg_count:
                        logging.error("%s requires %s arguments, but %s given" % (fn.__name__, arg_count, args_len))
                        return b''

                    if isinstance(arg_count, tuple) and len(arg_count) == 2 and not (arg_count[0] <= args_len <= arg_count[1]):
                        logging.error("%s requires from %s to %s arguments, but %s given" %
                                      (fn.__name__, arg_count[0], arg_count[1], args_len))
                        return b''

                    if isinstance(arg_count, list) and args_len not in arg_count:
                        logging.error("%s requires %s arguments, but %s given" % (fn.__name__, arg_count, args_len))
                        return b''

                args0 = []
                if 'args' not in skip:
                    args0.append(args)
                if 'out' not in skip:
                    args0.append(out)
                if 'locals' not in skip:
                    args0.append(locals_)
                if 'globals' not in skip:
                    args0.append(globals_)
                if 'body' not in skip:
                    args0.append(body)
                result = fn(*args0)

                if result is None:
                    result = b''
                if isinstance(result, str):
                    result = bytes(result, locals_['ENCODING'])
                if not isinstance(result, bytes):
                    try:
                        result = bytes(result)
                    except TypeError:
                        logging.exception("Can`t convert %s to bytes", result)
                        return b''

                return result

            if cb:
                return CB(cb_typed_checker)
            return cb_typed_checker

        return decorator

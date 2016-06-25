import os

from makehex.lexer import lex as __lex
from makehex.parser import parser as __parser
from makehex.tools import xint as __int, CB


def __exec(command: str, out, locals_: dict):
    from os import environ as __env
    from subprocess import Popen, PIPE
    env = __env.copy()
    env["HX_COMMAND"] = command
    env["HX_OUTPUT"] = out
    for k, v in locals_.items():
        env[k] = v

    p = Popen(command, shell=True, universal_newlines=True, stdout=PIPE, bufsize=-1, env=env)
    p.wait()
    return p.stdout.read()


@CB.typed(arg_count=1, need_body=True, skip=('out', 'locals'))
def define_hx(args0: dict, globals_: dict, body0):
    name, args0 = args0.popitem()

    def loc(args: dict, locals_: dict):
        locals_ = locals_.copy()
        for v in args0:
            locals_[v.name] = args[v.name][0]
        return locals_

    @CB.typed(skip='body')
    def wrapper(args: dict, out, locals_: dict, globals__: dict):
        return body0.eval(out, loc(args, locals_), globals__)

    @wrapper.set_typed_write(skip='body')
    def write(args: dict, out, locals_: dict, globals__: dict):
        return body0.write(out, loc(args, locals_), globals__)

    globals_[name] = wrapper


@CB.typed(skip='body', need_locals="INCLUDE_DIR")
def include_hx(args0: dict, out, locals_: dict, globals_: dict):
    for name, args in args0.items():
        if name == "raw" or name == "binary":
            with open(args[0].s, "rb") as input_file:
                data = input_file.read()
            return data
        elif name == "file" or name == "makehex":
            with open(os.path.join(locals_["INCLUDE_DIR"], "%s.hxi" % os.path.basename(args[0].s))) as input_file:
                tokens = __lex(input_file.read())
            return __parser()(tokens, 0).value.eval(out, locals_.copy(), globals_)


@CB.typed(skip='body')
def execute_hx(args0: dict, out, locals_: dict, globals_: dict):
    for name, args in args0.items():
        if name == "shell":
            __exec(args[0].s, "binary", locals_)
        elif name == "bin_out":
            return __exec(args[0].s, "binary", locals_)
        elif name == "hx_out":
            tokens = __lex(__exec(args[0].s, "text", locals_))
            return __parser()(tokens, 0).value.eval(out, locals_.copy(), globals_)


@CB.typed(skip=('body', 'out', 'globals'))
def config_hx(args0: dict, locals_: dict):
    for name, args in args0.items():
        if name == 'encoding':
            if args[0].s == "string":
                locals_["STRING_ENCODING"] = args[1].s
            elif args[0].s == "chars":
                locals_["CHARS_ENCODING"] = args[1].s
            elif args[0].s == "all":
                locals_["CHARS_ENCODING"] = args[1].s
                locals_["STRING_ENCODING"] = args[1].s
        elif name == 'endian':
            if args[0].s.upper() in ("BIG", "NET", "NETWORK", "MOTOROLA"):
                locals_["ENDIAN"] = "BIG"
            elif args[0].s.upper() in ("LITTLE", "VAX", "INTEL"):
                locals_["ENDIAN"] = "LITTLE"
            else:
                print("Warning: Ignored invalid endian '%s'" % args[0])
        elif name == 'align':
            if args[0].s.upper() in ("ON", "ENABLE", "TRUE"):
                locals_["ALIGN"] = "ON"
            elif args[0].s.upper() in ("OFF", "DISABLE", "FALSE"):
                locals_["ALIGN"] = "OFF"


@CB.typed(skip=('body', 'out', 'globals'))
def set_hx(args0: dict, locals_: dict):
    for name, args in args0.items():
        locals_[name] = args[0]


@CB.typed(need_body=True)
def if_hx(args0: dict, out, locals_: dict, globals_: dict, body):
    for name, args in args0.items():
        if name == 'set':
            if args[0].s in locals_:
                body.eval(out, locals_, globals_)
        elif name == 'eq':
            for k, v in enumerate(args):
                args[k] = v.eval(out, locals_, globals_)
            if len(set(args)) == 1:
                body.eval(out, locals_, globals_)
        elif name == 'ne':
            for k, v in enumerate(args):
                args[k] = v.eval(out, locals_, globals_)
            if len(set(args)) != 1:
                body.eval(out, locals_, globals_)
        elif name == 'defined':
            if args[0].s in globals_:
                body.eval(out, locals_, globals_)


@CB.typed(skip='body')
def pos_hx(args0: dict, out, locals_: dict, globals_: dict):
    offset = out.tell()
    fill = __parser()(__lex('00'), 0)
    for name, args in args0.items():
        if name == 'offset':
            offset = __int(args[0].s)
        elif name == 'fill':
            fill = args[0]

    while offset > out.tell():
        fill.value.write(out, locals_, globals_)
    if offset < out.tell():
        while True:
            print("Warning! Too small offset %s, written %s.\nChoose action:\n\t1) Ignore offset.\n\t2) Rewrite chars.\n\t3) Show chars"
                  % (offset, out.tell()))
            a = input("> ")
            if a == '2':
                out.seek(offset)
            if a == '1' or a == '2':
                break
            if a == '3':
                position = out.tell()
                out.seek(offset)
                print(out.read(position - offset).hex())
                out.seek(position)


@CB.typed(skip='body')
def repeat_hx(args: dict, out, locals_: dict, globals_):
    for name, data in args.items():
        for i in range(int(name[1:])):
            for d in data:
                d.write(out, locals_, globals_)


@CB.typed(skip=('body', 'globals', 'out'), string_args=True, need_locals=("ALIGN", "ENDIAN"))
def struct_hx(args0: dict, locals_: dict):
    from struct import pack as __pack
    struct_format = ['@' if locals_["ALIGN"] == "ON" else '>' if locals_["ENDIAN"] == "BIG" else '<']
    struct_args = []
    for name, args in args0.items():
        if name == 'int':
            if args[0] == '1':
                struct_format.append('b')
                struct_args.append(__int(args[1]))
            elif args[0] == '2':
                struct_format.append('h')
                struct_args.append(__int(args[1]))
            elif args[0] == '4':
                struct_format.append('i')
                struct_args.append(__int(args[1]))
            elif args[0] == '8':
                struct_format.append('q')
                struct_args.append(__int(args[1]))
        elif name == 'uint':
            if args[0] == '1':
                struct_format.append('B')
                struct_args.append(__int(args[1]))
            elif args[0] == '2':
                struct_format.append('H')
                struct_args.append(__int(args[1]))
            elif args[0] == '4':
                struct_format.append('I')
                struct_args.append(__int(args[1]))
            elif args[0] == '8':
                struct_format.append('Q')
                struct_args.append(__int(args[1]))
        elif name == 'float':
            if args[0] == '4':
                struct_format.append('f')
                struct_args.append(float(args[1]))
            elif args[0] == '8':
                struct_format.append('d')
                struct_args.append(float(args[1]))
        elif name == 'bool':
            struct_format.append('?')
            struct_args.append(args[0].upper() != "FALSE")
        elif name == 'pad':
            struct_format.append('x')
        elif name == 'char':
            struct_format.append('c')
            struct_args.append(bytes(args[0], locals_["CHARS_ENCODING"]))
        elif name == 'string':
            s = bytes(args[0].s, locals_["STRING_ENCODING"])
            struct_format.append(str(len(s)) + 's')
            struct_args.append(s)

    data = __pack("".join(struct_format), *struct_args)
    print(data)
    return data

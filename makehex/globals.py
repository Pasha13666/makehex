import logging
from makehex.tools import import_py_file


class Globals(dict):
    def __init__(self, libs, **kwargs):
        super().__init__(**kwargs)
        self.libs = libs

    def __missing__(self, key: str):
        logging.info("Looking up for function %s", key)
        if key in self.libs:
            name, local_name = self.libs[key]
        else:
            logging.warning("Can`t resolve file for function %s", key)
            return

        locals_ = import_py_file(name)
        if local_name in locals_:
            self[key] = locals_[local_name]
            return locals_[local_name]
        else:
            logging.warning("Can`t find function %s in library %s", local_name, name)

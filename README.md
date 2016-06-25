# MakeHEX

MakeHEX is a generator of the binary files, written in Python.

## Examples

#### Linux executable example

```bash
python3 -m makehex ./examples/64app.hx ./64app ./makehex.ini
chmod +x ./64app
./64app
```

#### x86 Bootloader example

```bash
python3 -m makehex ./examples/boot.hx ./boot.img ./makehex.ini
qemu-system-i386 ./boot.img
```



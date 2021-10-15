# Generating Volatility symbols (ISF Files) for Linux 

**HINT**: If looking for ubuntu symbols, check out `get_kernel_debug_symbols.py` in this projects `./ubuntu` directory.

Commands are always exemplary, they do not necessarily work if copy-pasted to a terminal!

## Extracting kernel debug symbols from a deb package (.ddeb file)

This was tested for ubuntu, should apply to other debian based distros as well.
If you are facing problems and need to deep dive, [here](https://raphaelhertzog.com/2010/11/08/5-reasons-why-a-debian-package-is-more-than-a-simple-file-archive/) is a good intro on debfiles.


1. Extract the .ddeb file. It is an "archive file", **not** a tar.
```shell
$ ar x path/to/package.ddeb
```
2. You should now see `data.tar.<some-comporession>` in the same dir, extract it (to `./data`)
```shell
$ mkdir ./data
$ tar -xf data.tar.xz -C data
```
**NOTE**: Most tools handle most compressions out of the box. There might be problems with `zst`.
3. Find the actual ELF with the debugging symbols in `./data`.
```shell
$ find ./data | grep vmlinux-
```
Should print something like:
`./data/usr/lib/debug/boot/vmlinux-3.13.0-24-generic`
4. Make sure you actually got an ELF file:
```shell
$ file ./data/usr/lib/debug/boot/vmlinux-3.13.0-24-generic
./data/usr/lib/debug/boot/vmlinux-3.13.0-24-generic: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked, BuildID[sha1]=9a87d34680d3efd31b5d57f56906d8c2fc38fc5e, with debug_info, not stripped
```

## Convert debug symbols files to Volatility ISF json

Follow the instructions here: https://github.com/volatilityfoundation/dwarf2json

## Use the symbols with Volatility

- Make sure you understood [how Volatilty finds symbol tables](https://volatility3.readthedocs.io/en/latest/symbol-tables.html#how-volatility-finds-symbol-tables)
- [Be careful when using `vol -s`](./FMM.md)

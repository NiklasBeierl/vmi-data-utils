# Dependencies:
`get_kernel_debug_symbols.py` requires the following python packages:

```
requests
python-debian
zstandard
bs4
```
 
`get_kernel_ver_from_image.py` only depends on standard lib packages, but needs to be run with root priviledges and
you need to have `qemu-nbd` installed.
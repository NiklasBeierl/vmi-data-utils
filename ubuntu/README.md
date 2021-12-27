# Dependencies:

## `get_kernel_debug_symbols.py`

...requires the following python packages:

```
requests
python-debian
zstandard
bs4
```

## `get_kernel_ver_from_image.py`

...only depends on th python standard lib, but you need to have `qemu-nbd` installed. Since it mounts and unmounts the
image, you need to run it with elevated privileges (sudo).
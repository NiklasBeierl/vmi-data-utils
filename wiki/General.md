# Determining the kernel version installed in a VM image:

You need to know the kernel version, so you can get the right debugging symbols. Below are some instructions to help you
find that version.

## "Online"

Create a vm with that image, get shell access and run `uname -r`.

## "Offline"

[Mount](https://gist.github.com/shamil/62935d9b456a6f9877b5) the vm image. Then:

```
cd <mount-path>/boot
ls vmlinuz-*
```

If the above command only lists one file, its name should indicate the linux kernel version.
[get_kernel_ver_from_image.py](../ubuntu/get_kernel_ver_from_image.py) tries to automate this procedure. So far it has
only been tested on ubuntu cloud images though.

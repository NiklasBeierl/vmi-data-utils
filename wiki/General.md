# Determining the kernel version installed in a VM image:

You need to know the kernel version, so you can get the right debugging symbols.

## "Online"

Create a vm with that image, get shell access and run `uname -r`.

## "Offline"

[Mount](https://gist.github.com/shamil/62935d9b456a6f9877b5) the vm image.
Then:
```
cd <mount-path>/boot
ls vmlinuz-*
```

If the above command only lists one file, its name should indicate the linux kernel version.

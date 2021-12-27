# Cloud images:

... can be downloaded here: http://cloud-images.ubuntu.com/releases/
There is also a (s)ftp server at cloud-images.ubuntu.com, but it apparently only has a subset of the files available and uses a different directory structure. 🤷🏼

**Note**: For some releases, there are image files called `<something>-kvm.img`. Counterintuitively, we did not succeed in setting them up on qemu/kvm. Also note that they are likely not using `-generic` kernels, thus likely require different debugging symbols!

# Kernel debug symbols:
To determine the version of the kernel contained in the image see [General.md](../General.md).  
Debug symbols for ubuntu kernels can be downloaded as part of debian packages here: http://ddebs.ubuntu.com/pool/main/l/linux/  
The symbols for a specific cloud image kernel are contained in:  
`limux-image-<ver>-generic-dbgsym_<ver>_<arch>.ddeb`  
[Here](../VolatiltySymbolFiles.md) is a guide for extracting the actual debugging symbols from the package and processing them further. `ubuntu/get_kernel_debug_symbols.py` tries to do just that automatically for generic x86 kernels.

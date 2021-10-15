from argparse import ArgumentParser
import os
from pathlib import Path
import re
from subprocess import check_output, CalledProcessError
from time import sleep

KERNEL_REGEX = re.compile(".*vmlinuz-(.*-.*)$")
MNT_BASE_DIR = "/mnt/"
MAX_PART = 16


def prepare_nbd():
    cmd = ["modprobe", "nbd", f"max_part={MAX_PART}"]
    try:
        check_output(cmd)
    except CalledProcessError:
        raise Exception(f"Failed to load nbd kernel module with command: {' '.join(cmd)}")


def auto_connect(file_path: str):
    target_device = None

    for drive_no in range(MAX_PART):
        drive_size = check_output(["blockdev", "--getsize64", f"/dev/nbd{drive_no}"])
        if int(drive_size) == 0:
            target_device = f"/dev/nbd{drive_no}"
            break
    if not target_device:
        raise Exception("Could not find any free nbd drives")

    print(f"Connecting image file to: {target_device}")

    cmd = ["qemu-nbd", f"--connect={target_device}", file_path]
    try:
        check_output(cmd)
        print(f"Connected {file_path} with {target_device}")
    except CalledProcessError:
        raise Exception(f"Failed to connect file to nbd device with command: {' '.join(cmd)}")

    return target_device


def disconnect(device: str):
    print(f"Disconnecting {device}")
    cmd = ["qemu-nbd", "-d", device]
    try:
        check_output(cmd)
    except CalledProcessError:
        print(f"Failed to disconnect nbd drive with command: {' '.join(cmd)}")


def mount(device: str, mount_point: str):
    print(f"Mounting {device} to {mount_point}")
    cmd = ["mount", device, mount_point]
    try:
        check_output(cmd)
    except CalledProcessError:
        print(f"Failed to mount nbd drive with command: {' '.join(cmd)}")


def unmount(mount_point: str):
    print(f"Unmounting {mount_point}.")
    cmd = ["umount", mount_point]
    try:
        check_output(cmd)
    except CalledProcessError:
        print(f"Failed to unmount nbd drive with command: {' '.join(cmd)}")


def find_kernel(image_mount_path: Path) -> str:
    candidates = list(Path(image_mount_path, "./boot").glob("vmlinuz-*"))
    if len(candidates) != 1:
        raise ValueError("Could not figure out kernel file. Candidates: "
                         f"{[str(c.relative_to(image_mount_path)) for c in candidates]}")

    print(f"Found kernel: {candidates[0]}")
    return str(candidates[0].relative_to(image_mount_path))


def parse_kernel_version(kernel_path: str) -> str:
    return KERNEL_REGEX.match(kernel_path).group(1)


def main():
    prepare_nbd()
    parser = ArgumentParser(
        description="Mounts a ubuntu cloud image file, tries to determine the kernel version inside it and cleans "
                    "up after itself. (Except for unloading the nbd module, that is up to you.)"
                    "Requires 'qemu-nbd' to be installed and needs to be run with root privileges."
    )
    parser.add_argument("image_file", help="Path to ubuntu cloud image file")
    args = parser.parse_args()
    image_path = Path(args.image_file)

    mount_point = Path(MNT_BASE_DIR, image_path.stem)
    device = auto_connect(str(image_path))
    sleep(2)  # Nbd connects take a few seconds to be recognised
    kernel_version = None
    try:
        print(f"Creating mount point: {mount_point}")
        mount_point.mkdir(parents=True)
        mount(device + "p1", str(mount_point))
        try:
            kernel_path = find_kernel(mount_point)
            kernel_version = parse_kernel_version(kernel_path)
        finally:
            unmount(str(mount_point))
            print(f"Deleting mount point: {mount_point}")
            os.rmdir(mount_point)
    finally:
        disconnect(device)

    if kernel_version:
        print(f"Image runs kernel version: {kernel_version}")


if __name__ == "__main__":
    main()

from argparse import ArgumentParser
import io
import json
import pathlib
import re
import requests
import tarfile

from bs4 import BeautifulSoup
from debian.debfile import ArFile
from zstandard import ZstdDecompressor

GENERIC_KERNEL_REGEX = "^linux-image-(unsigned-)?(.*)-generic-dbgsym.*{}\.ddeb$"

ALL_PACKAGES_URL = "http://ddebs.ubuntu.com/pool/main/l/linux/"
CACHE_PATH = "./ubuntu-generic-kernel-versions.json"
DEB_DATA_MEMBER = "data.tar.xz"
DEFAULT_ARCH = "amd64"


def get_available_symbols(arch: str):
    page = requests.get(ALL_PACKAGES_URL)
    soup = BeautifulSoup(page.content, "html.parser")

    file_list = soup.find_all("tr")
    ddeb_files = [
        tr
        for tr in file_list
        if tr.find("a") and (href := tr.find("a").attrs.get("href")) and "ddeb" in href
    ]
    regex = re.compile(GENERIC_KERNEL_REGEX.format(arch))
    ddeb_linux_images = [
        tr for tr in ddeb_files if regex.search(tr.find("a").attrs.get("href"))
    ]

    version_to_file = {}
    for file in ddeb_linux_images:
        file_name = file.find("a").attrs["href"]
        version = regex.match(file_name).group(2)
        if version in version_to_file:
            raise ValueError(f"Kernel {version} has multiple debug symbols?")
        version_to_file[version.lower()] = file_name
    return version_to_file


def download(file_name: str) -> io.BytesIO:
    url = ALL_PACKAGES_URL + file_name
    print(f"Downloading {url}")
    download = requests.get(url)
    return io.BytesIO(download.content)


def extract(deb_file: io.BytesIO):
    # Can not use the debian.DebFile wrapper because it will fail if the data section has zstd compression.
    # Still, python-debian is the only lib I know that has code to handle "archive files"
    deb_ar = ArFile(fileobj=deb_file)
    data_members = [mem for mem in deb_ar.getmembers() if "data" in mem.name]
    if len(data_members) != 1:
        raise ValueError(
            f"Could not identify data part in ddeb. Parts: {[m.name for m in deb_ar.getmembers()]}"
        )
    data_member = data_members[0]

    if data_member.name.endswith("zst"):
        dcmp = ZstdDecompressor()
        # I could also use data_member._ArMember__fp as input
        # but I don't wanna rely even heavier on python-debians internals
        input = io.BytesIO(data_member.read())
        data_member = io.BytesIO()
        dcmp.copy_stream(input, data_member)
        data_member.seek(0)
    else:
        # tarfile can handle all other compressions transparently
        data_member = io.BytesIO(data_member.read())

    data_tar = tarfile.open(fileobj=data_member)

    print(f"Looking for debugging symbol file")
    potential_kernel_files = [
        mem
        for mem in data_tar.getmembers()
        if pathlib.Path(mem.name).name.endswith("generic") and mem.size > 0
    ]
    if len(potential_kernel_files) != 1:
        raise ValueError(
            f"Could not identify kernel symbol file in debian package: {potential_kernel_files}"
        )
    member = potential_kernel_files[0]

    kernel_file_name = pathlib.Path(member.name).name
    # Avoid nesting when extracting the file
    member.name = kernel_file_name

    out_path = pathlib.Path("./", kernel_file_name)
    print(f"Writing symbol file to {out_path}")
    data_tar.extract(member, path="./")


def main():
    parser = ArgumentParser(
        description="Utility for downloading and extracting debugging symbols for ubuntu kernels."
    )
    parser.add_argument(
        "-a",
        "--arch",
        action="store",
        default=DEFAULT_ARCH,
        help="What architecture identifying string (arm64, amd64, powerpc, ...) to look for in the ddeb file names.",
    )
    parser.add_argument(
        "-r",
        "--rescrape",
        action="store_true",
        default=False,
        help=f"Re-scrape list of debugging symbols from {ALL_PACKAGES_URL}. "
        f"The list is stored and looked for at {CACHE_PATH}",
    )
    parser.add_argument(
        "-l",
        "--list-versions",
        action="store_true",
        default=False,
        help=f"List available kernel versions and exit.",
    )
    parser.add_argument(
        "-k",
        "--kernel-version",
        action="store",
        help="Download and extract debugging symbols for this kernel version. (only -generic kernels.)",
    )
    args = parser.parse_args()

    cache_path = pathlib.Path(CACHE_PATH).resolve()
    if args.rescrape or not cache_path.exists():
        print(f"Scraping packages from {ALL_PACKAGES_URL}...")
        avail_symbols = get_available_symbols(arch=args.arch)
        with open(cache_path, "w+") as f:
            json.dump(avail_symbols, f)
    else:
        print(f"Using package list from {cache_path}")
        with open(cache_path) as f:
            avail_symbols = json.load(f)
    if args.list_versions:
        print("\n".join(avail_symbols.keys()))
        print()
        return
    try:
        file_name = avail_symbols[args.kernel_version.lower()]
        extract(download(file_name))
    except KeyError:
        print(
            "No matching package found. Run with '-l' to list all available versions."
            "Run with '-r' to refresh the list"
        )


if __name__ == "__main__":
    main()

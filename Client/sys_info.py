'''a functions which get available drive names and types'''
from string import ascii_uppercase
from ctypes import windll
from enum import Enum
from shutil import disk_usage
from json import dumps
from platform import system, release
from os import environ, getcwd, getlogin

sys_info = {}


# Enum converts numerical drive_type to readable
class drive_type(Enum):
    Unknown = 0
    DRIVE_NO_ROOT_DIR = 1
    Removable = 2
    HDD = 3
    RemoteConnection = 4
    CDROM = 5
    RamDisk = 6


def get_drives():
    # init a list for drives
    drives = []
    # get binary string represents alpha-letters
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in ascii_uppercase:
        # if a letter is in the mask
        if bitmask & 1:
            try:
                name = letter + ':\\'  # get the letter
                type = drive_type(windll.kernel32.GetDriveTypeA(name.encode('ascii'))).name  # get the drive_type name
                total, used, free = disk_usage(name)  # get space usage info
                # init a dict with needed info
                drive = dict({
                    'drive_name': name,
                    'drive_type': type,
                    'drive_total': (total // (2 ** 30)),
                    'drive_free': (free // (2 ** 30))
                })
                # append the dict to the list
                drives.append(drive)
            except:
                pass
        # get the next bit
        bitmask >>= 1
    # return drives as a json list
    return drives


def get_sys_info():
    # username
    try:
        sys_info["user"] = environ["USERNAME"] if "C:" in getcwd() else environ["USER"]
    except:
        sys_info["user"] = getlogin()
    # os info
    sys_info["os"] = str(system() + ' ' + release())
    return dumps(sys_info, indent=4)


def get_hdd_info():
    # system drives
    sys_info["drives"] = get_drives()
    return dumps(get_drives(), indent=4)

# -*- coding: utf-8 -*-

import os
import sys
import zipfile

import requests
import wget
from bs4 import BeautifulSoup

WOW_DIR = "H:\\Games\\World of Warcraft"
ADDONS_DIR = ""

CONF_FILE = "waw-manage-conf.txt"

URL_ROOT = "https://mods.curse.com"
URL_HOME = URL_ROOT + "/addons/wow/%s"

updatedAddons = []


class Data:
    def __init__(self, name, version):
        self.name = name
        self.version = version

    def to_s(self):
        return "%s %s" % (self.name, self.version)


def print_lv2(param):
    print ("  -> " + param)


def handle():
    list = read_file()
    for v in list:
        name = v.name
        old_version = v.version
        print ("%s(%s)" % (name, old_version))

        # 1.
        print_lv2("check version...")
        r = requests.get(URL_HOME % name)
        bs = BeautifulSoup(r.content, 'html.parser')
        data = bs.find('tr', 'even').find('a', href=True)
        url_down = data['href']
        new_version = data.getText()

        print_lv2("new: %s" % new_version)
        if new_version == old_version:
            print_lv2("PASS")
            continue

        # 2.
        print_lv2("download...")
        r = requests.get(URL_ROOT + url_down)
        bs = BeautifulSoup(r.content, 'html.parser')
        url = bs.find('div', "countdown").find('a')['data-href']
        file_name = wget.download(url, bar="")

        # 3.
        print_lv2("extract...")
        zf = zipfile.ZipFile(file_name)
        zf.extractall(ADDONS_DIR)
        zf.close()
        os.remove(file_name)

        print_lv2("DONE")
        v.version = new_version
        updatedAddons.append(name)
    write_file(list)


def read_file():
    list = []
    for line in open(CONF_FILE):
        arr = line.split()
        if len(arr) == 0:
            continue
        name = arr[0]

        if len(arr) == 1:
            version = ""
        else:
            versionString = ''
            for x in arr[1:]:
                versionString += str(x) + ' '
            version = versionString[:-1]
        list.append(Data(name, version))
    return list


def write_file(list):
    with open(CONF_FILE, "w") as f:
        for v in list:
            f.write(v.to_s() + "\n")


def check():
    global ADDONS_DIR

    if not os.path.exists(WOW_DIR):
        sys.exit("WOW directory error, plz check! -> [%s]." % WOW_DIR)

    ADDONS_DIR = WOW_DIR + "/Interface/AddOns"
    if not os.path.exists(ADDONS_DIR):
        sys.exit("WOW AddOns directory error. -> [%s]." % ADDONS_DIR)

    if not os.path.isfile(CONF_FILE):
        sys.exit("Local config file error, plz check! -> [%s]." % CONF_FILE)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(os.path.abspath(sys.argv[0]))))
    if len(sys.argv) > 1:
        WOW_DIR = sys.argv[1]
    check()
    handle()
    print('Addons updated: %s' % updatedAddons)

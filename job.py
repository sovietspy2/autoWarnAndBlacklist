#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Creates a copy of the log file and name it accoird to the current date
Reads the log and look for IP addresses
Generates ip tables script 
"""
import sys
import shutil

email_address = "hangbarna@gmail.com"
log_path = "/var/log/auth.log"  # default for ubuntu


def current_path():
    if (len(sys.argv) == 1):
        print("No argument passed using default: "+log_path)
        return log_path
    else:
        print("Using supplied path:"+sys.argv[1])
        return sys.argv[1]


if __name__ == "__main__":
    print("script worked"+current_path())


def backup_original_log():
    pass


def read_file(path):
    pass


def send_email():
    pass

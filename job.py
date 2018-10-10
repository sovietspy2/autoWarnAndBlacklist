#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Creates a copy of the log file and name it accoird to the current date
Reads the log and look for IP addresses
Generates ip tables script 
"""
import sys
import shutil
import os.path
import datetime

import smtplib
from email.mime.text import MIMEText

email_address = "hangbarna@gmail.com"
log_path = "/var/log/auth.log"  # default for ubuntu


def backup_original_log(log):
    """ copy log file to script folder """
    now = datetime.datetime.now()
    log_name = "log-"+str(now.strftime("%Y-%m-%d-%H-%M"))+".log"
    shutil.copy(log, log_name)


def read_file(path):
    with open(path) as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    # we need lines that contains the word Failed
    content = [x for x in content if "Failed" in x]
    # for line in content:
    #    print(line)
    return content


def send_email(lines):
    msg = MIMEText(str(lines))
    msg['Subject'] = 'Warning from your server'
    msg['From'] = 'Amadeus <info@wortex.stream>'
    msg['To'] = 'hangbarna@gmail.com'
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    print("email was sent to:" + email_address)
    s.quit()


def current_path():
    if (len(sys.argv) == 1):
        print("No argument passed using default: "+log_path)
        return log_path
    else:
        if (os.path.isfile(sys.argv[1])):
            print("Using supplied path:"+sys.argv[1])
            return sys.argv[1]
        else:
            sys.exit("ERROR: Supplied file on path does not exist!")


if __name__ == "__main__":
    path = current_path()
    print("Using path"+path)
    backup_original_log(path)
    lines = read_file(path)
    send_email(lines)

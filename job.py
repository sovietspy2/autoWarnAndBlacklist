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
import logging
import smtplib
from email.mime.text import MIMEText
import re

whitelisted_ip = ["80.123.385.23"]
email_address = "hangbarna@gmail.com"
log_path = "/var/log/auth.log"  # default for ubuntu
file_not_found_error_message = "ERROR: No file on path!"
program_log = ""
logging.basicConfig(filename='program.log', level=logging.INFO)


def backup_original_log(log):
    """ copy log file to script folder """
    now = datetime.datetime.now()
    log_name = "log-"+str(now.strftime("%Y-%m-%d-%H-%M"))+".log"
    shutil.copy(log, log_name)


def read_file(path):
    with open(path) as f:
        content = f.readlines()

    # delete old log
    os.remove(path)
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    # we need lines that contains the word Failed
    content = [x for x in content if "Failed" in x]
    # for line in content:
    #    print(line)
    return content


def send_email(lines):
    if (lines):
        body = "Here is a list of the latest unsussesful logins"
        for line in lines:
            body += line+"\n"  # more fancy email?

        msg = MIMEText(body)
        msg['Subject'] = 'Warning from your server'
        msg['From'] = 'Amadeus <info@wortex.stream>'
        msg['To'] = email_address
        s = smtplib.SMTP('localhost')
        s.send_message(msg)
        logging.info("email was sent to:" + email_address)
        s.quit()


def current_path():
    if (len(sys.argv) == 1):
        if (os.path.isfile(log_path)):
            logging.info("No argument passed using default: "+log_path)
            return log_path
        else:
            sys.exit(file_not_found_error_message)
            logging.error(file_not_found_error_message)
    else:
        if (os.path.isfile(sys.argv[1])):
            logging.info("Using supplied path:"+sys.argv[1])
            return sys.argv[1]
        else:
            sys.exit(file_not_found_error_message)
            logging.error(file_not_found_error_message)


def generate_iptables_script(lines_array):
    if (lines_array):
        # creates a new script and adds lines to it
        now = datetime.datetime.now()
        f = open("blacklist_ips_{}.sh".format(
            now.strftime("%Y-%m-%d-%H-%M")), "w+")

        for line in lines_array:

            ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', line)
            ip = ip[0]

            if ip not in whitelisted_ip:
                text = "iptables -A INPUT -s {} -j DROP".format(ip)
                f.write(text)
            else:
                logging.info("Whitlisted ip skipped: "+ip)
        f.close()


if __name__ == "__main__":
    path = current_path()
    backup_original_log(path)
    lines = read_file(path)
    send_email(lines)
    generate_iptables_script(lines)
    logging.info("Job finished running at: "+str(datetime.datetime.now()))

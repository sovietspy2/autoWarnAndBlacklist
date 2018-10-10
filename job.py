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
temp_log_path = "/var/log/temp.log"
file_not_found_error_message = "ERROR: No file on path!"
program_log = ""
logging.basicConfig(filename='/home/sovietspy2/program.log', level=logging.INFO)


def get_new_log_entries():

    # unique case! for first run we have to create the temp file after that the program will terminate
    if not os.path.isfile(temp_log_path):
        shutil.copy2(log_path, temp_log_path)
        logging.info("Temp file created, run again to start processing!")
        sys.exit("Temp file created! Run again to process!")
    elif os.path.isfile(temp_log_path) and os.path.isfile(log_path):
        with open(log_path) as f:
            original = f.readlines()

        with open(temp_log_path) as f:
            temp = f.readlines()

        # we need the last lines first
        original_length = len(original)
        temp_length = len(temp)
        original = list(reversed(original))
        temp = list(reversed(temp))

        new_lines = []

        line_number = original_length-temp_length
        
        if (line_number > 0):
            for i in range(0,line_number):
                if ("Failed" in original[i]):
                    new_lines.append(original[i])

        #we have to update the temp log file
        shutil.copy2(log_path, temp_log_path) 
        return new_lines


def send_email(lines):
    if (lines):
        body = "Here is a list of the latest unsussesful logins\n"
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
            try:
                ip = ip[0]
            except IndexError:
                logging.error("Line processed without IP")
                continue

            if ip not in whitelisted_ip:
                text = "iptables -A INPUT -s {} -j DROP".format(ip)
                f.write(text)
            else:
                logging.info("Whitlisted ip skipped: "+ip)
        f.close()


if __name__ == "__main__":
    logging.info("+Job started running at: "+str(datetime.datetime.now()))
    #path = current_path()
    lines = get_new_log_entries()
    send_email(lines)
    generate_iptables_script(lines)
    logging.info("-Job finished running at: "+str(datetime.datetime.now()))

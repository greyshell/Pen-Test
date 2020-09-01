#!/usr/bin/env python3

# author: greyshell
# description: use openvpn to access offensive security labs


import argparse
import json
import subprocess
import sys
import time
import keyring
import pexpect
from colorama import Fore

# global constant variable
PROGRAM_LOGO = """
 _      ____  _____    __  _______  __  _ 
| |__  / () \ | () )   \ \/ /| ()_)|  \| |
|____|/__/\__\|_()_)    \__/ |_|   |_|\__|
"""


class UserInput:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
                description="automate the openvpn lab connection")
        self.parser.add_argument("-c", "--config", metavar="", help="provide a .json file", required=True)


class LoginVpn:
    def __init__(self):
        self._email_to = ""

        self._email_from = ""
        self._email_password = ""
        self._login_message = ""
        self._logout_message = ""

        self._vpn_user = ""
        self._vpn_password = ""
        self._dns = ""

        self._vpn_config = ""
        self._vpn_command = ""

    def get_parameters(self, config_dict):
        """
        retrieve the value from the input
        :param config_dict: dict
        :return: None
        """
        email_keyring_name = config_dict["email_keyring_name"]
        self._email_to = config_dict["email_to"]
        self._email_from = keyring.get_password(email_keyring_name, 'username')

        self._email_password = keyring.get_password(email_keyring_name, self._email_from)
        self._login_message = config_dict["login_message_path"]
        self._logout_message = config_dict["logout_message_path"]

        vpn_keyring_name = config_dict["vpn_keyring_name"]
        self._vpn_user = keyring.get_password(vpn_keyring_name, 'username')
        self._vpn_password = keyring.get_password(vpn_keyring_name, self._vpn_user)

        self._dns = config_dict["dns"]

        self._vpn_config = config_dict["ovpn_file_path"]

        self._vpn_command = "openvpn" + " " + self._vpn_config

        # validate the input
        if not self._vpn_user and self._vpn_password and self._vpn_config and self._email_to and self._email_from and \
                self._email_password and self._login_message and self._logout_message:
            print(f"[x] please fill the input in the json config file !!")
            sys.exit(0)

    def lab_connection(self):
        """
        connect to the vpn
        :return: None
        """
        try:
            if self._dns:
                print(Fore.GREEN, f"[+] set the dns entry {self._dns} into /etc/resolve.conf")
                set_dns_command = "sed -i \'1s/^/nameserver " + self._dns + "\\n/\' /etc/resolv.conf"
                subprocess.check_output(set_dns_command, shell=True)

            print(Fore.GREEN, f"[+] sending email notification to {self._email_to}")
            send_email_command = "sendEmail -f " + self._email_from + " -t " + self._email_to + \
                                 " -u \'logged-In\' -o message-file=" + self._login_message + \
                                 " -s smtp.gmail.com:587 -o tls=yes -xu " + self._email_from + \
                                 " -xp " + self._email_password

            subprocess.check_output(send_email_command, shell=True)

            print(Fore.LIGHTBLUE_EX, f"[*] connected to the lab, press ctrl+c to disconnect from the lab")

            # connect to the lab
            i = pexpect.spawn(self._vpn_command)
            i.expect_exact("Enter")
            i.sendline(self._vpn_user)
            i.expect_exact("Password")
            i.sendline(self._vpn_password)

            # delay for 1 day
            time.sleep(3600 * 24)

        except KeyboardInterrupt:
            print(Fore.RED, f"[*] received ctrl+c, disconnecting from lab ")
            send_email_command = "sendEmail -f " + self._email_from + " -t " + self._email_to + \
                                 " -u \'logged-Out\' -o message-file=" + self._logout_message + \
                                 " -s smtp.gmail.com:587 -o tls=yes -xu " + self._email_from + \
                                 " -xp " + self._email_password
            subprocess.check_output(send_email_command, shell=True)
            print(Fore.GREEN, f"[*] sent email notification  ")

            if self._dns:
                print(Fore.GREEN, f"[+] unset the dns entry ")
                unset_dns_command = "sed -i '1d' /etc/resolv.conf"
                subprocess.check_output(unset_dns_command, shell=True)

        except Exception as e:
            print(Fore.MAGENTA, f"[x] error occurs while connecting vpn !")
            print(e)


if __name__ == "__main__":
    my_input = UserInput()
    args = my_input.parser.parse_args()

    if len(sys.argv) == 1:
        my_input.parser.print_help(sys.stderr)
        sys.exit(0)

    if args.config:
        with open(args.config) as f:
            json_config = json.load(f)

        # display program logo
        print(Fore.GREEN, f"{PROGRAM_LOGO}")

        conn = LoginVpn()
        conn.get_parameters(json_config)
        conn.lab_connection()

    else:
        my_input.parser.print_help(sys.stderr)

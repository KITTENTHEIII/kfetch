#!/usr/bin/env python3

import os
import subprocess
import pwd
import socket

def get_output(command):
    try:
        return subprocess.check_output(command, shell=True, text=True).strip()
    except subprocess.CalledProcessError:
        return ''

def parse_rcs(*files):
    for f in files:
        try:
            with open(f) as file:
                lines = file.readlines()
                if not lines:
                    continue
                last_line = lines[-1]
                parts = last_line.split()
                if len(parts) > 1:
                    wm = parts[1]
                    if wm:
                        return wm
        except FileNotFoundError:
            continue
    return ''

# INFO
user = pwd.getpwuid(os.getuid()).pw_name
host = socket.gethostname()
try:
    with open('/etc/fedora-release') as f:
        os_name = f.read().strip()
except FileNotFoundError:
    os_name = 'Fedora'

kernel = get_output('uname -sr')
uptime = get_output("uptime -p").replace('up ', '')
packages = get_output("dnf list --installed | sed '1d' | wc -l")
shell = os.path.basename(os.environ.get('SHELL', 'unknown'))

# UI DETECTION
rcwm = parse_rcs(os.path.expanduser("~/.xinitrc"), os.path.expanduser("~/.xsession"))

ui = 'unknown'
uitype = 'UI'

de = os.environ.get('DE')
wm = os.environ.get('WM')
xdg_current_desktop = os.environ.get('XDG_CURRENT_DESKTOP')
desktop_session = os.environ.get('DESKTOP_SESSION')
xdg_session_type = os.environ.get('XDG_SESSION_TYPE')

if de:
    ui = de
    uitype = 'DE'
elif wm:
    ui = wm
    uitype = 'WM'
elif xdg_current_desktop:
    ui = xdg_current_desktop
    uitype = 'DE'
elif desktop_session:
    ui = desktop_session
    uitype = 'DE'
elif rcwm:
    ui = rcwm
    uitype = 'WM'
elif xdg_session_type:
    ui = xdg_session_type

ui = os.path.basename(ui)

# COLORS (via tput)
def tput(code):
    return get_output(f'tput {code}')

bold = tput('bold')
blue = tput('setaf 4')
white = tput('setaf 7')
reset = tput('sgr0')

lc = f"{reset}{bold}{blue}"     # labels
nc = f"{reset}{bold}{blue}"     # user and hostname
ic = f"{reset}"                 # info
c0 = f"{reset}{white}"          # first color
c1 = f"{reset}{blue}"           # second color

# OUTPUT
output = f"""
{c0}        _____
{c0}       /   __){c1}\\   {nc}{user}{ic}@{nc}{host}{reset}
{c0}       |  /  {c1}\\ \\  {lc}OS:        {ic}{os_name}{reset}
{c1}    __{c0}_|  |_{c1}_/ /  {lc}KERNEL:    {ic}{kernel}{reset}
{c1}   / {c0}(_    _){c1}_/   {lc}UPTIME:    {ic}{uptime}{reset}
{c1}  / /  {c0}|  |       {lc}PACKAGES:  {ic}{packages}{reset}
{c1}  \\ \\{c0}__/  |       {lc}SHELL:     {ic}{shell}{reset}
{c1}   \\{c0}(_____/       {lc}{uitype}:        {ic}{ui}{reset}
"""

print(output)

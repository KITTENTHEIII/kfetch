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
                last_line = file.readlines()[-1]
                wm = last_line.split()[1] if len(last_line.split()) > 1 else ''
                if wm:
                    return wm
        except (FileNotFoundError, IndexError):
            continue
    return ''

# INFO
user = pwd.getpwuid(os.getuid()).pw_name
host = socket.gethostname()
os_name = 'Arch Linux'
kernel = get_output('uname -sr')
uptime = get_output("uptime -p").replace('up ', '')
packages = get_output("pacman -Q | wc -l")
shell = os.path.basename(os.environ.get('SHELL', 'unknown'))

# UI DETECTION
rcwm = parse_rcs(os.path.expanduser("~/.xinitrc"), os.path.expanduser("~/.xsession"))

ui = 'unknown'
uitype = 'UI'

# Environment variables
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

# COLORS
def tput(code):
    return get_output(f'tput {code}')

bold = tput('bold')
blue = tput('setaf 4')
reset = tput('sgr0')

lc = f"{reset}{bold}{blue}"
nc = f"{reset}{bold}{blue}"
ic = f"{reset}"
c0 = f"{reset}{blue}"

# OUTPUT
output = f"""
{c0}        /\\         {nc}{user}{ic}@{nc}{host}{reset}
{c0}       /  \\        {lc}OS:        {ic}{os_name}{reset}
{c0}      /\\   \\       {lc}KERNEL:    {ic}{kernel}{reset}
{c0}     /  __  \\      {lc}UPTIME:    {ic}{uptime}{reset}
{c0}    /  (  )  \\     {lc}PACKAGES:  {ic}{packages}{reset}
{c0}   / __|  |__\\\\    {lc}SHELL:     {ic}{shell}{reset}
{c0}  /.`        `.\\   {lc}{uitype}:        {ic}{ui}{reset}
"""

print(output)

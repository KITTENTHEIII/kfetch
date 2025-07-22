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

os_name = get_output('uname -sr')
kernel = get_output('uname -v')

# Uptime parsing as in shell (awk+sed)
# uptime command output example:
# 16:21  up  1:24, 3 users, load averages: 1.60 1.38 1.31
uptime_raw = get_output('uptime')
uptime = ''
if uptime_raw:
    # Extract substring after "up "
    try:
        up_part = uptime_raw.split(' up ')[1].split(',')[0]
        uptime = up_part.strip()
    except IndexError:
        uptime = uptime_raw.strip()

# Count installed packages (count dirs in /var/db/pkg)
packages = get_output('ls -d /var/db/pkg/* | wc -l').strip()

shell = os.path.basename(os.environ.get('SHELL', 'unknown'))

# UI detection
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
yellow = tput('setaf 3')
white = tput('setaf 7')
reset = tput('sgr0')

lc = f"{reset}{bold}{yellow}"  # labels
nc = f"{reset}{bold}{yellow}"  # user and hostname
ic = f"{reset}"                # info
c0 = f"{reset}{yellow}"        # first color
c1 = f"{reset}{white}"         # second color
c2 = f"{reset}{bold}{yellow}" # third color

# OUTPUT
output = f"""

{c0}       _____      {nc}{user}{ic}@{nc}{host}{reset}
{c0}     \\-     -/    {lc}OS:        {ic}{os_name}{reset}
{c0}  \\_/         \\   {lc}KERNEL:    {ic}{kernel}{reset}
{c0}  |        {c1}O O {c0}|  {lc}UPTIME:    {ic}{uptime}{reset}
{c0}  |_  {c2}<   {c0})  {c2}3 {c0})  {lc}PACKAGES:  {ic}{packages}{reset}
{c0}  / \\         /   {lc}SHELL:     {ic}{shell}{reset}
{c0}     /-_____-\    {lc}{uitype}:        {ic}{ui}{reset}
"""

print(output)

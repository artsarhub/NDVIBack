#!/usr/bin/python3

activate_this = '/opt/NDVIBack/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

import sys
sys.path.insert(0, '/opt/NDVIBack')

from NDVIBack import app as application
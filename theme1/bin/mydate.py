#!/usr/bin/env python

from __future__ import print_function

from datetime import datetime

import os.path

import sys

try:
    file = sys.argv[1]
    lm = os.path.getmtime(file)
    lm = datetime.fromtimestamp(lm)
    print(lm.strftime('%a %b %d %Y'))

except: 
    print('')




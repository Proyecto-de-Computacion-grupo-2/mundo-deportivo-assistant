# !/usr/bin/env python3

# -*- coding: utf-8 -*-
# imports.py

#

# CODE NUMBERS
"""
1 - 12: Show Coffee Addresses
15: Encrypt mode
20: Decrypt mode
30: Sign mode
40: Verify mode
14: Encrypt message mode
16: Encrypt file mode
24: Manual decrypt mode
25: File decrypt mode
26: Automatic decrypt mode
34: Plaintext sign mode
35: Encrypted message sign mode
36: File sign mode
44: Automatic verify mode
46: Verify file mode
100: Create PGP Keypair
110: Import message mode
112: Import Public Key mode
114: Import Signature mode
200: Choose encrypt mode
300: Choose decrypt mode
250: Choose sign mode
350: Choose verify mode
400: Choose language mode
454: English language
455: Spanish language
500: Show help mode
600: Exit
660: Create custom
666: Show coffee mode
700: Import confirm
800: Show Menu mode
"""

"""Contains all imports necessary."""

import PySimpleGUI as pSG
import io

from PIL import Image, ImageTk
from src.Layouts import main_window
from time import sleep
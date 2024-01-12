# !/usr/bin/env python3

# -*- coding: utf-8 -*-
# main_window.py

#

import Utils.helper as helper
import Utils.routes as route


def login():
    """Create login window."""

    h, w = 210, 320
    new_size = 30
    data_bytes_io = helper.io.BytesIO(helper.base64.b64decode(helper.pSG.EMOJI_BASE64_THINK))
    img = helper.Image.open(data_bytes_io)
    cur_width, cur_height = img.size
    scale = min((new_size / cur_height), (new_size / cur_width))
    img = img.resize((int(cur_width * scale), int(cur_height * scale)), helper.Resampling.LANCZOS)
    bio = helper.io.BytesIO()
    img.save(bio, format = "PNG")
    new_emoji = helper.base64.b64encode(bio.getvalue())
    img = helper.Image.open(route.fantasy_logo)
    fl_w, fl_h = img.size

    layout = [
        [helper.pSG.Column([
            [helper.pSG.Image(filename = route.fantasy_logo, key = "__IMAGE__", size = (fl_w, fl_h))],
            [helper.pSG.Column([[helper.pSG.Text("Login:", justification = "left", size = (10, 1))]]),
             helper.pSG.Column([[helper.pSG.Input(key = "user", size = (25, 10))]])],
            [helper.pSG.Column([[helper.pSG.Text("Password:", justification = "left", size = (10, 1))]],
                               element_justification = "left"),
             helper.pSG.Column([[helper.pSG.Input(enable_events = True, key = "pass", password_char = "*",
                                                  size = (18, 1)),
                                 helper.pSG.Image(new_emoji, enable_events = True, key = "Mostrar"),
                                 helper.pSG.Button("login", bind_return_key = True, size = (0, 0))]])]],
                element_justification = "center")]
    ]

    window = helper.pSG.Window("Bienvenido al asistente deportivo de Liga Fantasy del Mundo Deportivo", layout,
                               element_justification = "center", finalize = True, size = (w, h),
                               text_justification = "center")

    return window

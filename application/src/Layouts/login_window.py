# !/usr/bin/env python3

# -*- coding: utf-8 -*-
# main_window.py

#

import Utils.helper as helper
import Utils.routes as route


def login():
    """Create login window."""

    custom_theme = {
        "BACKGROUND": "#D9D9D9",
        "TEXT":       "#000000",
        "INPUT":      "#ffffff",
        "TEXT_INPUT": "#000000",
        "SCROLL":     "#D9D9D9",
        "BUTTON":     ("#000000", "#ffffff"),
        "PROGRESS":   ("#01826B", "#D0D0D0"),
        "BORDER":     1, "SLIDER_DEPTH": 0, "PROGRESS_DEPTH": 0
    }

    helper.pSG.theme_add_new("MyCustomTheme", custom_theme)

    helper.pSG.theme("MyCustomTheme")

    h, w = 240, 320
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
                                 ]])],
            [helper.pSG.Button("Iniciar Sesión", bind_return_key = True, enable_events = True, size = (0, 0))]],
                element_justification = "center")]
    ]

    window = helper.pSG.Window("Bienvenido al asistente deportivo de Liga Fantasy del Mundo Deportivo", layout,
                               element_justification = "center", finalize = True, size = (w, h),
                               text_justification = "center")

    return window

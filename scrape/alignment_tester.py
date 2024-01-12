# !/usr/bin/env python3

# -*- coding: utf-8 -*-
# alignment_tester.py

#

import logging
import random
import os

import Utils.routes as route


# So it didn't show any warning of variable may be undefined.
logger = "Defined"

# For debugging, this sets up a formatting for a logfile, and where it is.
try:
    if not os.path.exists(route.bot_folder + "tester.log"):
        logging.basicConfig(filename = route.bot_folder + "tester.log", level = logging.ERROR,
                            format = "%(asctime)s %(levelname)s %(name)s %(message)s")
        logger = logging.getLogger(__name__)
    else:
        logging.basicConfig(filename = route.bot_folder + "tester.log", level = logging.ERROR,
                            format = "%(asctime)s %(levelname)s %(name)s %(message)s")
        logger = logging.getLogger(__name__)
except Exception as error:
    logger.exception(error)

try:
    numero_aleatorio = random.choice([244, 154, 334, 343, 253, 145, 235])

    archivos_img = [archivo.split(".")[0].split("_")[-1]
                    for archivo in os.listdir(route.root_folder + "img")
                    if archivo.endswith(".png")]

    nombres_aleatorios = random.sample(archivos_img, 11)

    with open(route.scrape_folder + "data/files/future_alignment", "w", encoding = "utf-8") as a:
        a.write(str(numero_aleatorio) + "\n")
        for nombre in nombres_aleatorios:
            a.write(str(nombre) + "\n")
except Exception as e:
    logger.exception(e)

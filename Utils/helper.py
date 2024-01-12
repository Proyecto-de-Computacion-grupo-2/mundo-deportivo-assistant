# !/usr/bin/env python3

# -*- coding: utf-8 -*-
# helper.py

#


import Utils.routes as route

import PySimpleGUI as pSG
import asyncio, base64, csv, glob, hashlib, http.client, io, json, logging, math, pandas, platform, re, requests, schedule, shutil, sys, threading

from application.src.Layouts import login_window, main_window
from datetime import datetime, timedelta
from random import choice, uniform
from os import chdir, getcwd, listdir, makedirs, path, remove, system
from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Resampling
from PySimpleGUI import WIN_CLOSED
from selenium.webdriver.support import expected_conditions as ec
from selenium import webdriver
from selenium.common import ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException,\
    TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from telegram import Bot, error, Update
from telegram.ext import Application, ApplicationBuilder, CallbackContext, CommandHandler, ContextTypes, filters,\
    JobQueue, InlineQueryHandler, MessageHandler, Updater


# So it didn't show any warning of variable may be undefined.
logger = "Defined"

# For debugging, this sets up a formatting for a logfile, and where it is.

lorca = platform.system()
if lorca != "Windows":
    try:
        if not path.exists(route.root_folder + "helper.log"):
            logging.basicConfig(filename = route.root_folder + "helper.log", level = logging.ERROR,
                                format = "%(asctime)s %(levelname)s %(name)s %(message)s")
            logger = logging.getLogger(__name__)
        else:
            logging.basicConfig(filename = route.root_folder + "helper.log", level = logging.ERROR,
                                format = "%(asctime)s %(levelname)s %(name)s %(message)s")
            logger = logging.getLogger(__name__)
    except Exception as error:
        logger.exception(error)


def automated_commit(who: str):
    while path.exists(route.git_lock_file):
        sleep(uniform(0.2, 0.8))
    if not path.exists(route.git_lock_file):
        sshpass = "sshpass -P passphrase -p geronimo221a5673"

        system("cd " + route.root_folder + "data && git config user.name 'lorca'")
        system("cd " + route.root_folder + "data && git config user.email 'lorca@uem.com'")
        system("cd " + route.root_folder + f"data && {sshpass} git pull --rebase")
        system("cd " + route.root_folder + "data && git add .")
        system("cd " + route.root_folder + "data && git commit -m 'Automatic data commit: '" + who)
        system("cd " + route.root_folder + f"data && {sshpass} git push --set-upstream origin automated")
        with open(route.git_log, "a", encoding = "utf-8") as gl:
            gl.write("Commit: " + who + ", " + datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") + "\n")
        if path.exists(route.git_lock_file):
            system("cd " + route.root_folder + "data/.git && rm index.lock")


def delete_profile():
    temp_f = path.join("/home", "221A5673Geronimo", "temp_folder")
    for i in listdir(temp_f):
        try:
            shutil.rmtree(path.join(temp_f, i))
        except FileNotFoundError as err:
            logger.exception(err)
            pass


def create_image(alignment_file, save_file):
    def calculate_player_positions(al):
        positions = []

        players_per_row = {244: [2, 4, 4], 154: [1, 5, 4], 334: [3, 3, 4], 343: [3, 4, 3], 253: [2, 5, 3],
                           145: [1, 4, 5], 235: [2, 3, 5]}
        x_positions = []
        y_positions = [200, 960, 1790]
        elevation_factor = 110

        rows = players_per_row.get(al)
        if rows is None:
            raise ValueError(f"Unsupported future_alignment: {al}")

        for i, num in enumerate(rows):
            total_width = 3650 // (num + 1)
            x_positions.extend([((total_width * (j + 1)) - 510) for j in range(num)])

        for row in range(len(rows)):
            current_row_positions = []

            for i in range(rows[row]):
                center_offset = 0
                pos_y = i
                if rows[row] % 2 == 0:
                    if rows[row] == 4 and any(ext == i for ext in [0, 3]):  # Jugadores en el centro
                        center_offset = 0
                        pos_y = 0
                    else:
                        center_offset = elevation_factor // 2
                        pos_y = 1

                current_row_positions.append((x_positions[i + sum(rows[:row])],
                                              y_positions[row] - elevation_factor * abs(
                                                  pos_y - rows[row] // 2) + center_offset))
            positions.extend(current_row_positions)

        positions.append((1320, 2425))
        return positions

    def read_alignment(file_path):
        with open(file_path, "r", encoding = "utf-8") as file:
            lines = file.readlines()

        af = int(lines[0])

        ad = [line.strip() + ".png" for line in lines[1:]]
        return af, ad

    background = Image.open(route.background_path).convert("RGBA")
    alignment_format, alignment_data = read_alignment(alignment_file)
    player_positions = calculate_player_positions(alignment_format)

    draw = ImageDraw.Draw(background, "RGBA")

    for player in alignment_data:
        list_images = listdir(route.image_folder)
        image_path = None
        for _ in list_images:
            if player in _:
                image_path = path.join(route.image_folder, _)
                break

        old_image = Image.open(image_path).convert("RGBA")
        image = old_image.resize((400, 400), Resampling.LANCZOS)
        mask = image.split()[3]

        background.paste(image, player_positions[alignment_data.index(player)], mask)

        player_name = image_path.split("img/")[-1].split(".png")[0].split("_")[-1]

        _, _, w, h = draw.textbbox((0, 0), player_name, font = route.font)
        text_position = (player_positions[alignment_data.index(player)][0] + ((image.width - w) // 2),
                         player_positions[alignment_data.index(player)][1] + (image.height + 30))

        draw.text(text_position, player_name, font = route.font, fill = "white")

        image.close()

    background.save(save_file + ".png", format = "PNG")
    background = background.convert("RGB")
    background.save(save_file + ".jpeg", format = "JPEG")

    background.close()


def wait_click(driv, selector, t):
    wait = WebDriverWait(driv, t)
    elemento = None
    try:
        elemento = wait.until(ec.element_to_be_clickable(selector))
    except (NoSuchElementException, ElementClickInterceptedException, TimeoutException):
        pass
    return elemento


def skip_button(d, f):
    s_b = wait_click(d, f, 5)
    if s_b:
        s_b.click()


def copy_bak(file_path_a, file_path_b):
    with open(file_path_a, "rb") as file_a:
        with open(file_path_b, "wb") as file_b:
            file_b.write(file_a.read())


def write_to_csv(file_path, header, data, typ):
    makedirs(path.dirname(file_path), exist_ok = True)

    # Create a CSV with all the previous information mentioned.
    with open(file_path, typ, encoding = "utf-8", newline = "") as csv_file:
        writer = csv.writer(csv_file)
        # Write the header
        if header:
            writer.writerow(header)
        # Append the data
        if data:
            writer.writerows(data)


def read_csv(filname):
    with open(filname, "r", encoding = "utf-8", newline = "") as csv_file:
        csv_reader = csv.reader(csv_file)
        data = []
        for row in csv_reader:
            data.append(row)
    return data


def read_player_url():
    with open(route.player_links_file, "r", encoding = "utf-8") as file:
        # with open("data/auxiliary/fantasy-players-links.csv", "r", encoding = "utf-8") as file:
        reader = csv.reader(file)
        return list(reader)


def read_timeout_url():
    with open(route.timeout_file, "r", encoding = "utf-8") as file:
        reader = csv.reader(file)
        return list(reader)


def extract_player_id(players_info):
    whole_lineup = players_info.find_elements(By.CLASS_NAME, "player-row")
    whole_team_id = []
    for i in whole_lineup:
        player_id = i.find_element(By.CLASS_NAME, "player-pic")
        whole_team_id.append(player_id.get_attribute("data-id_player"))
    return whole_team_id


def scrape_player_info(t_p_i, t_p_ic, team_id):
    # Create an array to save players info.
    players = []
    positions = []
    for player_info in t_p_ic:
        # Split the text to create a list of player information.
        position = player_info.find_element(By.TAG_NAME, "i").get_attribute("class")
        if position == "pos-1":
            position = "0"
        elif position == "pos-2":
            position = "1"
        elif position == "pos-3":
            position = "2"
        elif position == "pos-4":
            position = "3"
        positions.append(position)

    for player_info in t_p_i:
        # Split the text to create a list of player information.
        raw_player_information = player_info.text.split("\n")

        # Clean the data.
        cleaned_player_information = [item.replace("↑", "").replace("↓", "").replace(",", ".").
                                      replace("-", "0.0").strip() for item in raw_player_information]
        temp = [team_id[t_p_i.index(player_info)]]
        temp.extend(cleaned_player_information)
        temp.extend(positions[t_p_i.index(player_info)])
        players.append(temp)
    return players


def login_fantasy_mundo_deportivo():
    makedirs(path.dirname(route.root_folder + "temp_file"), exist_ok = True)
    # with open(route.scrape_folder + "config.json", "r", encoding = "utf-8") as cf:
    with open("config.json", "r", encoding = "utf-8") as cf:
        c = json.load(cf)

    email_fantasy = c["email"]
    password_fantasy = c["password"]

    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    # driver = webdriver.Chrome(options = chrome_options)

    firefox_options = webdriver.FirefoxOptions()
    # firefox_options.add_argument("--headless")
    driver = webdriver.Firefox(options = firefox_options)

    driver.set_page_load_timeout(30)

    navigation_to = True
    while navigation_to:
        try:
            driver.get("https://mister.mundodeportivo.com/new-onboarding/auth/email")
            navigation_to = False
        except TimeoutException as err:
            logger.exception(err)
            sleep(2)
            pass

    # Wait for the cookies to appear and click the button to accept them.
    sleep(uniform(0.4, 0.6))
    intercept = True
    while intercept:
        try:
            disagree = wait_click(driver, (By.ID, "didomi-notice-disagree-button"), 4)
            if disagree:
                disagree.click()
            intercept = False
        except (ElementClickInterceptedException, StaleElementReferenceException):
            sleep(6)
            intercept = True
        except NoSuchElementException:
            pass

    # Enter the email and password.
    email_input = driver.find_element(By.ID, "email")
    email_input.send_keys(email_fantasy)

    password_input = driver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div/form/div[2]/input')
    password_input.send_keys(password_fantasy)

    # Click on the login button.
    submit_button = wait_click(driver, (By.XPATH, '//*[@id="app"]/div/div[2]/div/form/div[3]/button'), 2)
    if submit_button:
        submit_button.click()

    # Special wait to skip the first tutorial, when we start with a new account it will appear, so better to check it.
    skip_button(driver, (By.CLASS_NAME, "btn-tutorial-skip"))

    sleep(uniform(0.4, 0.8))

    return driver


def scrape_backup(folder, backup):
    makedirs(folder, exist_ok = True)
    makedirs(backup, exist_ok = True)
    files = listdir(folder)

    for filename in files:
        original_path = path.join(folder, filename)
        back_path = path.join(backup, filename + "_bak")
        if path.exists(back_path):
            try:
                original_size = path.getsize(original_path)
                backup_size = path.getsize(back_path) if path.exists(back_path) else 0
            except FileNotFoundError as err:
                backup_size, original_size = -1, -1
                print(f"El archivo original '{original_path}' no existe.")
                logger.exception(err)
            try:
                if 0 < original_size > backup_size:
                    shutil.copy(original_path, back_path)
                else:
                    shutil.copy(back_path, original_path)
            except shutil.Error as err:
                print(f"Error al copiar archivos: {err}")
                logger.exception(err)
        else:
            shutil.copy(original_path, back_path)

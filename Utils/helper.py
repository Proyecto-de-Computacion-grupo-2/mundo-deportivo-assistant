# !/usr/bin/env python3

# -*- coding: utf-8 -*-
# helper.py

#


import Utils.routes as route

import asyncio, base64, csv, glob, hashlib, http.client, io, json, logging, math, pandas, re, requests, shutil, sys, \
    threading

from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone, date
import mysql.connector
from random import choice, uniform
from os import chdir, getcwd, getenv, listdir, makedirs, path, remove, system
from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Resampling
from selenium.webdriver.support import expected_conditions as ec
from selenium import webdriver
from selenium.common import ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException, \
    TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from platform import system
from time import sleep


# For debugging, this sets up a formatting for a logfile, and where it is.
def define_logger(file):
    logg = "Defined"
    try:
        if not path.exists(file):
            logging.basicConfig(filename = file, level = logging.ERROR,
                                format = "%(asctime)s %(levelname)s %(name)s %(message)s")
            logg = logging.getLogger(__name__)
        else:
            logging.basicConfig(filename = file, level = logging.ERROR,
                                format = "%(asctime)s %(levelname)s %(name)s %(message)s")
            logg = logging.getLogger(__name__)
        return logg
    except Exception as err:
        #logg.exception(err)
        return logg



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


def extract():
    df = pandas.read_csv(route.players_game_week_stats_file)
    new_df = df.iloc[:, :2]
    new = new_df.drop_duplicates()
    new.to_csv(route.id_mapping, index = False)


def id_name_mapping(entity, typ):
    try:
        df = pandas.read_csv(route.id_mapping)
        if typ == "ID":
            mask = (df["ID"].astype(str) == str(entity))
        else:
            mask = (df["Player full name"].astype(str) == str(entity))
        result_df = df[mask]
        if not result_df.empty:
            result_dict = result_df.iloc[0].to_dict()
            if typ == "ID":
                return result_dict["Player full name"]
            else:
                return result_dict["ID"]
    except Exception as e:
        print(f"Error: {e}")
        return None


def custom_colours():
    return {
        "BACKGROUND": "#D9D9D9",
        "TEXT":       "#000000",
        "INPUT":      "#ffffff",
        "TEXT_INPUT": "#000000",
        "SCROLL":     "#D9D9D9",
        "BUTTON":     ("#000000", "#ffffff"),
        "PROGRESS":   ("#01826B", "#D0D0D0"),
        "BORDER":     1, "SLIDER_DEPTH": 0, "PROGRESS_DEPTH": 0
    }


def create_image(alignment_file, save_file, bot_not, back_height, back_width):
    def calculate_player_positions(al):
        positions = []

        players_per_row = {244: [2, 4, 4], 154: [1, 5, 4], 334: [3, 3, 4], 343: [3, 4, 3], 253: [2, 5, 3],
                           145: [1, 4, 5], 235: [2, 3, 5]}
        x_positions = []
        y_positions = [200, 960, 1790]
        elevation_factor = 110

        rows = players_per_row.get(al)
        if rows is None:
            rows = players_per_row.get(int(str(al)[-1] + str(al)[1] + str(al)[0]))

        for i, num in enumerate(rows):
            total_width = (3250 // (num + 1))
            x_positions.extend([((total_width * (j + 1)) - 310) for j in range(num)])

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

        ad = [line.strip() for line in lines[1:]]
        return af, ad

    background = Image.open(route.background_path).convert("RGBA")
    alignment_format, alignment_data = read_alignment(alignment_file)
    player_positions = calculate_player_positions(alignment_format)

    draw = ImageDraw.Draw(background, "RGBA")
    image_data = [id_name_mapping(int(row.split(", ")[0].strip()), "ID") + ", " + row.split(", ")[1].strip() for row in
                  alignment_data]
    for id_line in alignment_data:
        list_images = listdir(route.image_folder)
        image_path = None
        for _ in list_images:
            if id_name_mapping(id_line.split(", ")[0], "ID") in _:
                image_path = path.join(route.image_folder, _)
                break

        old_image = Image.open(image_path).convert("RGBA")
        image = old_image.resize((400, 400), Resampling.LANCZOS)
        mask = image.split()[3]

        background.paste(image, player_positions[alignment_data.index(id_line)], mask)

        player_name = image_data[alignment_data.index(id_line)]

        _, _, w, h = draw.textbbox((0, 0), player_name, font = route.font)
        text_position = (player_positions[alignment_data.index(id_line)][0] + ((image.width - w) // 2),
                         player_positions[alignment_data.index(id_line)][1] + (image.height + 30))

        draw.text(text_position, player_name, font = route.font, fill = "white")

        image.close()

    if not bot_not:
        background.save(save_file + ".png", format = "PNG")
        background = background.convert("RGB")
        background.save(save_file + ".jpeg", format = "JPEG")
    else:
        background = background.resize((back_height, back_width))
        background.save(save_file + ".png", format = "PNG")
        background = background.convert("RGB")
        background.save(save_file + ".jpeg", format = "JPEG")

    background.close()


def image_resize(img, new, typ, out):
    cur_width, cur_height = img.size
    if typ == 0:
        scale = (new / cur_width)
    else:
        scale = (new / cur_height)
    img = img.resize((int(cur_width * scale), int(cur_height * scale)), Resampling.LANCZOS)
    img.save(out, format = "PNG")


def fix_format():
    with threading.Lock():
        csv1 = pandas.read_csv(route.players_market_temp_info_file)
        csv2 = pandas.read_csv(route.players_market_temp_info_file_new)

        columns_to_add = [col for col in csv2.columns if col not in csv1.columns]

        # Agregar las columnas faltantes al dataframe resultante
        merged_data = pandas.merge(csv1, csv2[columns_to_add + ["Name"]], on = "Name", how = "outer").fillna(int(0))

        merged_data = merged_data.drop_duplicates()

        # Guardar el resultado en un nuevo CSV
        merged_data.to_csv(route.players_market_temp_info_file, index = False)
        try:
            with open(route.players_market_temp_info_file, "r", encoding = "utf-8") as f:
                temp_file = csv.reader(f)
                temp_list = list(temp_file)
                aux = []
                for player in range(1, len(temp_list)):
                    if temp_list[player][0] != "0":
                        for value in range(2, (len(temp_list[player][1:]) + 1)):
                            aux.append([temp_list[player][0], temp_list[player][1], str(int(temp_list[player][value])),
                                        temp_list[0][value]])
            copy_bak(route.players_market_temp_info_file, route.players_market_temp_info_file_bak)
            write_to_csv(route.players_market_info_file, ["ID", "Name", "Value", "Date"], aux, "w")
        except IndexError as err:
            #logger.exception(err)
            pass


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


def scrape_player_info(typ, t_p_i, t_p_ic, team_id):
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

    raw_player_information = None
    for player_info in t_p_i:
        # Split the text to create a list of player information.
        if typ == "f":
            raw_player_information = player_info.text.split("\n")[1:]
        elif typ == "m":
            raw_player_information = player_info.text.split("\n")
            del raw_player_information[1]

        if raw_player_information:
            # Clean the data.
            cleaned_player_information = [item.replace("↑", "").replace("↓", "").replace(",", ".").
                                          replace("-", "0.0").strip() for item in raw_player_information]
            temp = [team_id[t_p_i.index(player_info)]]
            temp.extend(cleaned_player_information)
            temp.extend(positions[t_p_i.index(player_info)])
            players.append(temp)
    return players


def login_fantasy_mundo_deportivo():
    with open("config.json", "r", encoding = "utf-8") as cf:
        c = json.load(cf)

    email_fantasy = c["email"]
    password_fantasy = c["password"]

    if all(system() != ext for ext in ["Linux", "Windows"]):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options = chrome_options)
    else:
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument("--headless")
        driver = webdriver.Firefox(options = firefox_options)

    driver.set_page_load_timeout(30)

    navigation_to = True
    while navigation_to:
        try:
            driver.get("https://mister.mundodeportivo.com/new-onboarding/auth/email")
            navigation_to = False
        except TimeoutException as err:
            #logger.exception(err)
            sleep(2)
            pass
        except WebDriverException as err:
            #logger.exception(err)
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
            driver.get("https://mister.mundodeportivo.com/new-onboarding/auth/email")
            sleep(uniform(0.4, 0.6))
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
                #logger.exception(err)
            try:
                if 0 < original_size > backup_size:
                    shutil.copy(original_path, back_path)
                else:
                    shutil.copy(back_path, original_path)
            except shutil.Error as err:
                print(f"Error al copiar archivos: {err}")
                #logger.exception(err)
        else:
            shutil.copy(original_path, back_path)


# Database
def create_database_connection():
    host = getenv("DB_HOST", "localhost")
    port = getenv("DB_PORT", "3306")
    user = getenv("DB_USER", "root")
    password = getenv("DB_PASSWORD", "root")
    database = getenv("DB_NAME", "pc2")
    conn, connection = False, None
    while not conn:
        try:
            connection = mysql.connector.connect(
                host = host, port = port, user = user, password = password, database = database)
            conn = True
        except mysql.connector.ProgrammingError as e:
            if "Unknown database" in e.msg:
                connection = mysql.connector.connect(host = host, port = port, user = user, password = password)
                cursor = connection.cursor()
                cursor.execute("CREATE DATABASE pc2;")
                connection.close()
            else:
                conn = True
        except Exception as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            conn = True

    if conn and connection is not None:
        return connection
    else:
        return None


def close_database_connection(conn):
    if conn is not None:
        conn.close()

def get_all_attributes_for_points_predicction():
    mariadb = create_database_connection()
    cursor = mariadb.cursor()

    try:
        sql = """SELECT
        player.id_mundo_deportivo AS "ID",
        player.full_name AS "Player full name",
        player.position AS "Position",
        game.game_week AS "Game Week",
        game.team AS "Team",
        game.opposing_team AS "Opposing Team",
        game.mixed AS "Mixed",
        game.as_score AS "AS Score",
        game.marca_score AS "Marca Score",
        game.mundo_deportivo_score AS "Mundo Deportivo Score",
        game.sofa_score AS "Sofa Score",
        game.current_value AS "Current Value",
        game.points AS "Points",
        game.average AS "Average",
        game.matches AS "Matches",
        game.goals_metadata AS "Goals Metadata",
        game.cards AS "Cards",
        game.total_passes AS "Total Passes",
        game.accurate_passes AS "Accurate Passes",
        game.total_long_balls AS "Total Long Balls",
        game.accurate_long_balls AS "Accurate Long Balls",
        game.total_cross AS "Total Crosses",
        game.accurate_cross AS "Accurate Crosses",
        game.total_clearance AS "Total clearances",
        game.clearance_off_line AS "Clearances on goal line",
        game.aerial_lost AS "Aerial Duels Lost",
        game.aerial_won AS "Aerial Duels Won",
        game.duel_lost AS "Duels Lost",
        game.duel_won AS "Duels Won",
        game.dispossessed AS "Dribbled Past",
        game.challenge_lost AS "Losses",
        game.total_contest AS "Total Dribbles",
        game.won_contest AS "Completed dribbles",
        game.good_high_claim AS "High clearances",
        game.punches AS "Fist clearances",
        game.error_lead_to_a_shot AS "Failures that lead to shot",
        game.error_lead_to_a_goal AS "Failures that lead to goal",
        game.shot_off_target AS "Shots Off Target",
        game.on_target_scoring_attempt AS "Shots on Target",
        game.blocked_scoring_attempt AS "Shots blocked in attack",
        game.outfielder_block AS "Shots blocked in defence",
        game.big_chance_created AS "Occasions created",
        game.goal_assist AS "Goal assists",
        game.hit_woodwork AS "Shots to the crossbar",
        game.big_chance_missed AS "Failed obvious occasions",
        game.penalty_conceded AS "Penalties commited",
        game.penalty_won AS "Penalties caused",
        game.penalty_miss AS "Failed penalties",
        game.penalty_save AS "Stopped penalties",
        game.goals AS "Goals",
        game.own_goals AS "Own goals",
        game.saved_shots_from_inside_the_box AS "Stops from inside the area",
        game.saves AS "Stops",
        game.goals_against AS "Goals avoided",
        game.interception_won AS "Interceptions",
        game.total_keeper_sweeper AS "Total outputs",
        game.accurate_keeper_sweeper AS "Precise outputs",
        game.total_tackle AS "Total Tackles",
        game.was_fouled AS "Fouls Received",
        game.fouls AS "Fouls Committed",
        game.total_offside AS "Offsides",
        game.minutes_played AS "Minutes Played",
        game.touches AS "Touches",
        game.last_man_tackle AS "Entries as last man",
        game.possession_lost_control AS "Possessions Lost",
        game.expected_goals AS "Expected Goals",
        game.key_pass AS "Key Passes",
        game.expected_assists AS "Expected Assists",
        player.season_15_16 AS "Average Season 15/16",
        player.season_16_17 AS "Average Season 16/17",
        player.season_17_18 AS "Average Season 17/18",
        player.season_18_19 AS "Average Season 18/19",
        player.season_19_20 AS "Average Season 19/20",
        player.season_20_21 AS "Average Season 20/21",
        player.season_21_22 AS "Average Season 21/22",
        player.season_22_23 AS "Average Season 22/23",
        player.season_23_24 AS "Average Season 23/24",
        game.ts AS "Timestamp"
        FROM game
        JOIN player ON game.id_mundo_deportivo = player.id_mundo_deportivo
        """

        cursor.execute(sql)
        results = cursor.fetchall()

        players_information = []
        for row in results:
            players_information.append(row)

        return players_information

    finally:
        if mariadb.is_connected():
            cursor.close()
            mariadb.close()


def database_insert_prediction(players_id, gameweek, point_predictions):
    mariadb = create_database_connection()
    cursor = mariadb.cursor()
    print(players_id)
    print(gameweek)
    print(point_predictions)
    try:
        for player_id, point_prediction in zip(players_id, point_predictions):
            sql = """INSERT INTO prediction_points(
            id_mundo_deportivo,
            gameweek,
            date_prediction,
            point_prediction
            ) VALUES (%s,%s,%s,%s)"""
            values = (player_id, gameweek, date.today(), point_prediction)
            cursor.execute(sql, values)
            mariadb.commit()
            print(f'Inserted prediction for {player_id} in gameweek {gameweek}')
    finally:
        cursor.close()
        mariadb.close()
    pass


#logger = define_logger(route.helper_log)

# !/usr/bin/env python3

# -*- coding: utf-8 -*-
# helper.py

#


import UA2C.routes as route

import base64, csv, itertools, json, logging, matplotlib.pyplot as plt, mysql.connector, numpy, pandas, platform, \
       re, requests, shutil, tensorflow, threading, warnings

from bs4 import BeautifulSoup
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from datetime import datetime, timedelta, timezone
from deprecated import deprecated
from math import sqrt
from matplotlib import ticker
from random import uniform
from os import chdir, getcwd, getenv, listdir, makedirs, path, remove, system
from PIL import Image, ImageDraw
from PIL.Image import Resampling
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException, \
    TimeoutException, WebDriverException
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.arima.model import ARIMA
from telegram import Bot, error, Update
from telegram.ext import Application, ApplicationBuilder, CallbackContext, CommandHandler, ContextTypes, filters, \
    JobQueue, InlineQueryHandler, MessageHandler, Updater
from time import sleep
from tqdm import tqdm
from transformers import TFBertModel, BertTokenizer


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


class Finder:
    def find_object_by_id(self, objects_list, id_to_find, id_attribute):
        found_object = None
        index = 0
        object_found = False

        while index < len(objects_list) and not object_found:
            obj = objects_list[index]
            if getattr(obj, id_attribute) == id_to_find:
                found_object = obj
                object_found = True
            index += 1

        return found_object


class Base:
    def to_insert_statement(self, table_name):
        columns = []
        values = []

        for attr_name, attr_value in self.__dict__.items():
            columns.append(attr_name)
            if isinstance(attr_value, str):
                values.append(f'"{attr_value}"')
            else:
                values.append(str(attr_value))

        insert_statement = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});"
        return insert_statement

    def to_update_statement(self, table_name, condition):
        updates = []

        for attr_name, attr_value in self.__dict__.items():
            if attr_name != "id":  # Evita actualizar la clave primaria (suponiendo que "id" es la clave primaria)
                if isinstance(attr_value, str):
                    updates.append(f"{attr_name} = '{attr_value}'")
                else:
                    updates.append(f"{attr_name} = {attr_value}")

        update_statement = f"UPDATE {table_name} SET {', '.join(updates)} WHERE {condition};"
        return update_statement


class AIModel:
    """Para los modelos de AI de Jorge. <3"""
    def __init__(self):
        self.player_model = []

    class Player:
        def __init__(self, player_id, full_name, position, game_week, team, opposing_team, mixed, as_score,
                     marca_score, mundo_deportivo_score, sofa_score, current_value, points, average, matches,
                     goals_metadata, cards, yellow_card, double_yellow_card = 0, red_card = 0, total_passes = 0,
                     accurate_passes = 0, total_long_balls = 0, accurate_long_balls = 0, total_cross = 0,
                     accurate_cross = 0, total_clearance = 0, clearance_off_line = 0, aerial_lost = 0, aerial_won = 0,
                     duel_lost = 0, duel_won = 0, challenge_lost = 0, dispossessed = 0, total_contest = 0,
                     won_contest = 0, good_high_claim = 0, punches = 0, error_lead_to_a_shot = 0,
                     error_lead_to_a_goal = 0, shot_off_target = 0, on_target_scoring_attempt = 0, hit_woodwork = 0,
                     blocked_scoring_attempt = 0, outfielder_block = 0, big_chance_created = 0, big_chance_missed = 0,
                     penalty_conceded = 0, penalty_won = 0, penalty_miss = 0, penalty_save = 0, goals = 0,
                     own_goals = 0, saved_shots_from_inside_the_box = 0, saves = 0, goal_assist = 0, goals_against = 0,
                     goals_avoided = 0, interception_won = 0, total_interceptions = 0, total_keeper_sweeper = 0,
                     accurate_keeper_sweeper = 0, total_tackle = 0, was_fouled = 0, fouls = 0, total_offside = 0,
                     minutes_played = 0, touches = 0, last_man_tackle = 0, possession_lost_control = 0,
                     expected_goals = 0, goals_prevented = 0, key_pass = 0, expected_assists = 0,
                     total_season_15_16 = 0, total_season_16_17 = 0, total_season_17_18 = 0, total_season_18_19 = 0,
                     total_season_19_20 = 0, total_season_20_21 = 0, total_season_21_22 = 0, total_season_22_23 = 0,
                     total_season_23_24 = 0, ts = 0):
            self.player_id = player_id
            self.full_name = full_name
            self.position = position
            self.game_week = game_week
            self.team = team
            self.opposing_team = opposing_team
            self.mixed = mixed
            self.as_score = as_score
            self.marca_score = marca_score
            self.mundo_deportivo_score = mundo_deportivo_score
            self.sofa_score = sofa_score
            self.current_value = current_value
            self.points = points
            self.average = average
            self.matches = matches
            self.goals_metadata = goals_metadata
            self.cards = cards
            self.yellow_card = yellow_card
            self.double_yellow_card = double_yellow_card
            self.red_card = red_card
            self.total_passes = total_passes
            self.accurate_passes = accurate_passes
            self.total_long_balls = total_long_balls
            self.accurate_long_balls = accurate_long_balls
            self.total_cross = total_cross
            self.accurate_cross = accurate_cross
            self.total_clearance = total_clearance
            self.clearance_off_line = clearance_off_line
            self.aerial_lost = aerial_lost
            self.aerial_won = aerial_won
            self.duel_lost = duel_lost
            self.duel_won = duel_won
            self.challenge_lost = challenge_lost
            self.dispossessed = dispossessed
            self.total_contest = total_contest
            self.won_contest = won_contest
            self.good_high_claim = good_high_claim
            self.punches = punches
            self.error_lead_to_a_shot = error_lead_to_a_shot
            self.error_lead_to_a_goal = error_lead_to_a_goal
            self.shot_off_target = shot_off_target
            self.on_target_scoring_attempt = on_target_scoring_attempt
            self.hit_woodwork = hit_woodwork
            self.blocked_scoring_attempt = blocked_scoring_attempt
            self.outfielder_block = outfielder_block
            self.big_chance_created = big_chance_created
            self.big_chance_missed = big_chance_missed
            self.penalty_conceded = penalty_conceded
            self.penalty_won = penalty_won
            self.penalty_miss = penalty_miss
            self.penalty_save = penalty_save
            self.goals = goals
            self.own_goals = own_goals
            self.saved_shots_from_inside_the_box = saved_shots_from_inside_the_box
            self.saves = saves
            self.goal_assist = goal_assist
            self.goals_against = goals_against
            self.goals_avoided = goals_avoided
            self.interception_won = interception_won
            self.total_interceptions = total_interceptions
            self.total_keeper_sweeper = total_keeper_sweeper
            self.accurate_keeper_sweeper = accurate_keeper_sweeper
            self.total_tackle = total_tackle
            self.was_fouled = was_fouled
            self.fouls = fouls
            self.total_offside = total_offside
            self.minutes_played = minutes_played
            self.touches = touches
            self.last_man_tackle = last_man_tackle
            self.possession_lost_control = possession_lost_control
            self.expected_goals = expected_goals
            self.goals_prevented = goals_prevented
            self.key_pass = key_pass
            self.expected_assists = expected_assists
            self.total_season_15_16 = total_season_15_16
            self.total_season_16_17 = total_season_16_17
            self.total_season_17_18 = total_season_17_18
            self.total_season_18_19 = total_season_18_19
            self.total_season_19_20 = total_season_19_20
            self.total_season_20_21 = total_season_20_21
            self.total_season_21_22 = total_season_21_22
            self.total_season_22_23 = total_season_22_23
            self.total_season_23_24 = total_season_23_24
            self.ts = ts

    def add_player(self, player_id, full_name, position, game_week, team, opposing_team, mixed, as_score,
                   marca_score, mundo_deportivo_score, sofa_score, current_value, points, average, matches,
                   goals_metadata, cards, yellow_card, double_yellow_card = 0, red_card = 0, total_passes = 0,
                   accurate_passes = 0, total_long_balls = 0, accurate_long_balls = 0, total_cross = 0,
                   accurate_cross = 0, total_clearance = 0, clearance_off_line = 0, aerial_lost = 0, aerial_won = 0,
                   duel_lost = 0, duel_won = 0, challenge_lost = 0, dispossessed = 0, total_contest = 0,
                   won_contest = 0, good_high_claim = 0, punches = 0, error_lead_to_a_shot = 0,
                   error_lead_to_a_goal = 0, shot_off_target = 0, on_target_scoring_attempt = 0, hit_woodwork = 0,
                   blocked_scoring_attempt = 0, outfielder_block = 0, big_chance_created = 0, big_chance_missed = 0,
                   penalty_conceded = 0, penalty_won = 0, penalty_miss = 0, penalty_save = 0, goals = 0, own_goals = 0,
                   saved_shots_from_inside_the_box = 0, saves = 0, goal_assist = 0, goals_against = 0,
                   goals_avoided = 0, interception_won = 0, total_interceptions = 0, total_keeper_sweeper = 0,
                   accurate_keeper_sweeper = 0, total_tackle = 0, was_fouled = 0, fouls = 0, total_offside = 0,
                   minutes_played = 0, touches = 0, last_man_tackle = 0, possession_lost_control = 0,
                   expected_goals = 0, goals_prevented = 0, key_pass = 0, expected_assists = 0, total_season_15_16 = 0,
                   total_season_16_17 = 0, total_season_17_18 = 0, total_season_18_19 = 0, total_season_19_20 = 0,
                   total_season_20_21 = 0, total_season_21_22 = 0, total_season_22_23 = 0, total_season_23_24 = 0,
                   ts = 0):
        player = self.Player(player_id, full_name, position, game_week, team, opposing_team, mixed, as_score,
                             marca_score, mundo_deportivo_score, sofa_score, current_value, points, average, matches,
                             goals_metadata, cards, yellow_card, double_yellow_card, red_card, total_passes,
                             accurate_passes, total_long_balls, accurate_long_balls, total_cross, accurate_cross,
                             total_clearance, clearance_off_line, aerial_lost, aerial_won, duel_lost, duel_won,
                             challenge_lost, dispossessed, total_contest, won_contest, good_high_claim, punches,
                             error_lead_to_a_shot, error_lead_to_a_goal, shot_off_target, on_target_scoring_attempt,
                             hit_woodwork, blocked_scoring_attempt, outfielder_block, big_chance_created,
                             big_chance_missed, penalty_conceded, penalty_won, penalty_miss, penalty_save,
                             goals, own_goals, saved_shots_from_inside_the_box, saves, goal_assist, goals_against,
                             goals_avoided, interception_won, total_interceptions, total_keeper_sweeper,
                             accurate_keeper_sweeper, total_tackle, was_fouled, fouls, total_offside, minutes_played,
                             touches, last_man_tackle, possession_lost_control, expected_goals, goals_prevented,
                             key_pass, expected_assists, total_season_15_16, total_season_16_17, total_season_17_18,
                             total_season_18_19, total_season_19_20, total_season_20_21, total_season_21_22,
                             total_season_22_23, total_season_23_24, ts)
        self.player_model.append(player)

    def save_to_csv(self, filename):
        with open(filename, "w", newline = "") as csvfile:
            fieldnames = vars(self.player_model[0]).keys()
            writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
            writer.writeheader()
            for player in self.player_model:
                writer.writerow(vars(player))


class Users(Finder):
    def __init__(self):
        self.users = []

    def __getitem__(self, index):
        return self.users[index]

    class User(Base):
        def __init__(self, id_user: int, email = "", password = "", team_name = "", team_points = 0, team_average = 0.0,
                     team_value = 0, team_players = 0, current_balance = 0, future_balance = 0, maximum_debt = 0,
                     active = False, admin = False):
            self.id_user = id_user
            self.email = email
            self.password = password
            self.team_name = team_name
            self.team_points = team_points
            self.team_average = team_average
            self.team_value = team_value
            self.team_players = team_players
            self.current_balance = current_balance
            self.future_balance = future_balance
            self.maximum_debt = maximum_debt
            self.active = active
            self.admin = admin

        def to_insert_statements(self):
            return self.to_insert_statement("league_user")

    def fill_from_database(self, local_ddbb: bool):
        connection = None
        cursor = None
        try:
            connection = create_database_connection(local_ddbb)
            if connection.is_connected():
                cursor = connection.cursor()
                query = "SELECT * FROM league_user;"
                cursor.execute(query)
                records = cursor.fetchall()
                progress_bar = tqdm(total = len(records), desc = "Filling League User: ")
                for row in records:
                    (id_user, email, password, team_name, team_points, team_average, team_value, team_players,
                     current_balance, future_balance, maximum_debt, active, admin) = row
                    self.add_user(id_user, email, password, team_name, team_points, team_average, team_value,
                                  team_players, current_balance, future_balance, maximum_debt, active, admin)
                    progress_bar.update(1)
                progress_bar.close()
        except Exception as e:
            print("Error while connecting to MySQL", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def add_user(self, id_user: int, email = "", password = "", team_name = "", team_points = 0, team_average = 0.0,
                 team_value = 0.0, team_players = 0, current_balance = 0, future_balance = 0, maximum_debt = 0,
                 active = False, admin = False):
        user = self.User(id_user, email, password, team_name, team_points, team_average, team_value, team_players,
                         current_balance, future_balance, maximum_debt, active, admin)
        self.users.append(user)

    def to_insert_statements(self):
        insert_statements = []
        for user in self.users:
            insert_statements.extend([user.to_insert_statements()])
        return insert_statements

    def get_all_user_ids(self):
        return [user.id_user for user in self.users]

    def find_user(self, user_id):
        return self.find_object_by_id(self.users, user_id, "id_user")


class Players(Finder):
    def __init__(self):
        self.players = []

    def __getitem__(self, index):
        return self.players[index]

    class Player(Base):
        def __init__(self, id_mundo_deportivo: int, id_sofa_score: int, id_marca: int, id_user: int, full_name: str,
                     position: int, player_value: int, is_in_market = False, sell_price = 0.0, photo_body = 0,
                     photo_face = 0, season_15_16 = 0, season_16_17 = 0, season_17_18 = 0, season_18_19 = 0,
                     season_19_20 = 0, season_20_21 = 0, season_21_22 = 0, season_22_23 = 0, season_23_24 = 0):
            self.id_mundo_deportivo = id_mundo_deportivo
            self.id_sofa_score = id_sofa_score
            self.id_marca = id_marca
            self.id_user = id_user
            self.full_name = full_name
            self.position = position
            self.player_value = player_value
            self.is_in_market = is_in_market
            self.sell_price = sell_price
            self.photo_body = photo_body
            self.photo_face = photo_face
            self.season_15_16 = season_15_16
            self.season_16_17 = season_16_17
            self.season_17_18 = season_17_18
            self.season_18_19 = season_18_19
            self.season_19_20 = season_19_20
            self.season_20_21 = season_20_21
            self.season_21_22 = season_21_22
            self.season_22_23 = season_22_23
            self.season_23_24 = season_23_24

        def to_insert_statements(self):
            return self.to_insert_statement("player")

    def fill_from_database(self, local_ddbb: bool):
        connection = None
        cursor = None
        try:
            connection = create_database_connection(local_ddbb)
            if connection.is_connected():
                cursor = connection.cursor()
                query = "SELECT * FROM player;"
                cursor.execute(query)
                records = cursor.fetchall()
                progress_bar = tqdm(total = len(records), desc = "Filling Player: ")
                for row in records:
                    (id_mundo_deportivo, id_sofa_score, id_marca, id_user, full_name, position, player_value,
                     is_in_market, sell_price, photo_body, photo_face, season_15_16, season_16_17, season_17_18,
                     season_18_19, season_19_20, season_20_21, season_21_22, season_22_23, season_23_24) = row
                    self.add_player(id_mundo_deportivo, id_sofa_score, id_marca, id_user, full_name, position,
                                    player_value, is_in_market, sell_price, photo_body, photo_face, season_15_16,
                                    season_16_17, season_17_18, season_18_19, season_19_20, season_20_21, season_21_22,
                                    season_22_23, season_23_24)
                    progress_bar.update(1)
                progress_bar.close()
        except Exception as e:
            print("Error while connecting to MySQL", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def add_player(self, id_mundo_deportivo: int, id_sofa_score: int, id_marca: int, id_user: int, full_name: str,
                   position: int, player_value: int, is_in_market = False, sell_price = 0.0, photo_body = "",
                   photo_face = "", season_15_16 = 0, season_16_17 = 0, season_17_18 = 0, season_18_19 = 0,
                   season_19_20 = 0, season_20_21 = 0, season_21_22 = 0, season_22_23 = 0, season_23_24 = 0):
        player = self.Player(id_mundo_deportivo, id_sofa_score, id_marca, id_user, full_name, position, player_value,
                             is_in_market, sell_price, photo_body, photo_face, season_15_16, season_16_17, season_17_18,
                             season_18_19, season_19_20, season_20_21, season_21_22, season_22_23, season_23_24)
        self.players.append(player)

    def to_insert_statements(self):
        insert_statements = []
        for player in self.players:
            insert_statements.extend([player.to_insert_statements()])
        return insert_statements

    def get_all_player_ids(self):
        return [int(player.id_mundo_deportivo) for player in self.players]

    def find_player(self, player_id):
        return self.find_object_by_id(self.players, player_id, "id_mundo_deportivo")

    def find_unmatched_players(self):
        unmatched_players = []

        for player in self.players:
            if player.id_marca == 0:
                unmatched_players.append(player.full_name)

        return unmatched_players


class Games:
    def __init__(self):
        self.games = []

    def __getitem__(self, index):
        return self.games[index]

    class Game(Base):
        def __init__(self, id_gw: int, id_mundo_deportivo: int, schedule: int, game_week: int, team: str,
                     opposing_team: str, mixed = 0, as_score = 0, marca_score = 0, mundo_deportivo_score = 0,
                     sofa_score = 0, current_value = 0, points = 0, average = 0, matches = 0, goals_metadata = 0,
                     cards = 0, yellow_card = 0, double_yellow_card = 0, red_card = 0, total_passes = 0,
                     accurate_passes = 0, total_long_balls = 0, accurate_long_balls = 0, total_cross = 0,
                     accurate_cross = 0, total_clearance = 0, clearance_off_line = 0, aerial_lost = 0, aerial_won = 0,
                     duel_lost = 0, duel_won = 0, challenge_lost = 0, dispossessed = 0, total_contest = 0,
                     won_contest = 0, good_high_claim = 0, punches = 0, error_lead_to_a_shot = 0,
                     error_lead_to_a_goal = 0, shot_off_target = 0, on_target_scoring_attempt = 0, hit_woodwork = 0,
                     blocked_scoring_attempt = 0, outfielder_block = 0, big_chance_created = 0, big_chance_missed = 0,
                     penalty_conceded = 0, penalty_won = 0, penalty_miss = 0, penalty_save = 0, goals = 0,
                     own_goals = 0, saved_shots_from_inside_the_box = 0, saves = 0, goal_assist = 0, goals_against = 0,
                     goals_avoided = 0, interception_won = 0, total_interceptions = 0, total_keeper_sweeper = 0,
                     accurate_keeper_sweeper = 0, total_tackle = 0, was_fouled = 0, fouls = 0, total_offside = 0,
                     minutes_played = 0, touches = 0, last_man_tackle = 0, possession_lost_control = 0,
                     expected_goals = 0, goals_prevented = 0, key_pass = 0, expected_assists = 0, ts = 0):
            self.id_gw = id_gw
            self.id_mundo_deportivo = id_mundo_deportivo
            self.schedule = schedule
            self.game_week = game_week
            self.team = team
            self.opposing_team = opposing_team
            self.mixed = mixed
            self.as_score = as_score
            self.marca_score = marca_score
            self.mundo_deportivo_score = mundo_deportivo_score
            self.sofa_score = sofa_score
            self.current_value = current_value
            self.points = points
            self.average = average
            self.matches = matches
            self.goals_metadata = goals_metadata
            self.cards = cards
            self.yellow_card = yellow_card
            self.double_yellow_card = double_yellow_card
            self.red_card = red_card
            self.total_passes = total_passes
            self.accurate_passes = accurate_passes
            self.total_long_balls = total_long_balls
            self.accurate_long_balls = accurate_long_balls
            self.total_cross = total_cross
            self.accurate_cross = accurate_cross
            self.total_clearance = total_clearance
            self.clearance_off_line = clearance_off_line
            self.aerial_lost = aerial_lost
            self.aerial_won = aerial_won
            self.duel_lost = duel_lost
            self.duel_won = duel_won
            self.dispossessed = dispossessed
            self.challenge_lost = challenge_lost
            self.total_contest = total_contest
            self.won_contest = won_contest
            self.good_high_claim = good_high_claim
            self.punches = punches
            self.error_lead_to_a_shot = error_lead_to_a_shot
            self.error_lead_to_a_goal = error_lead_to_a_goal
            self.shot_off_target = shot_off_target
            self.on_target_scoring_attempt = on_target_scoring_attempt
            self.hit_woodwork = hit_woodwork
            self.blocked_scoring_attempt = blocked_scoring_attempt
            self.outfielder_block = outfielder_block
            self.big_chance_created = big_chance_created
            self.big_chance_missed = big_chance_missed
            self.penalty_conceded = penalty_conceded
            self.penalty_won = penalty_won
            self.penalty_miss = penalty_miss
            self.penalty_save = penalty_save
            self.goals = goals
            self.own_goals = own_goals
            self.saved_shots_from_inside_the_box = saved_shots_from_inside_the_box
            self.saves = saves
            self.goal_assist = goal_assist
            self.goals_against = goals_against
            self.goals_avoided = goals_avoided
            self.interception_won = interception_won
            self.total_interceptions = total_interceptions
            self.total_keeper_sweeper = total_keeper_sweeper
            self.accurate_keeper_sweeper = accurate_keeper_sweeper
            self.total_tackle = total_tackle
            self.was_fouled = was_fouled
            self.fouls = fouls
            self.total_offside = total_offside
            self.minutes_played = minutes_played
            self.touches = touches
            self.last_man_tackle = last_man_tackle
            self.possession_lost_control = possession_lost_control
            self.expected_goals = expected_goals
            self.goals_prevented = goals_prevented
            self.key_pass = key_pass
            self.expected_assists = expected_assists
            self.ts = ts

        def to_insert_statements(self):
            return self.to_insert_statement("game")

    def fill_from_database(self, local_ddbb: bool):
        connection = None
        cursor = None
        try:
            connection = create_database_connection(local_ddbb)
            if connection.is_connected():
                cursor = connection.cursor()
                query = "SELECT * FROM game;"
                cursor.execute(query)
                records = cursor.fetchall()
                progress_bar = tqdm(total = len(records), desc = "Filling Game: ")
                for row in records:
                    row = row[1:]
                    (id_gw, id_mundo_deportivo, schedule, game_week, team, opposing_team, mixed, as_score, marca_score,
                     mundo_deportivo_score, sofa_score, current_value, points, average, matches, goals_metadata, cards,
                     yellow_card, double_yellow_card, red_card, total_passes, accurate_passes, total_long_balls,
                     accurate_long_balls, total_cross, accurate_cross, total_clearance, clearance_off_line, aerial_lost,
                     aerial_won, duel_lost, duel_won, challenge_lost, dispossessed, total_contest, won_contest,
                     good_high_claim, punches, error_lead_to_a_shot, error_lead_to_a_goal, shot_off_target,
                     on_target_scoring_attempt, hit_woodwork, blocked_scoring_attempt, outfielder_block,
                     big_chance_created, big_chance_missed, penalty_conceded, penalty_won, penalty_miss,
                     penalty_save, goals, own_goals, saved_shots_from_inside_the_box, saves, goal_assist,
                     goals_against, goals_avoided, interception_won, total_interceptions, total_keeper_sweeper,
                     accurate_keeper_sweeper, total_tackle, was_fouled, fouls, total_offside, minutes_played, touches,
                     last_man_tackle, possession_lost_control, expected_goals, goals_prevented, key_pass,
                     expected_assists, ts) = row
                    self.add_game(id_gw, id_mundo_deportivo, schedule, game_week, team, opposing_team, mixed, as_score,
                                  marca_score, mundo_deportivo_score, sofa_score, current_value, points, average,
                                  matches, goals_metadata, cards, yellow_card, double_yellow_card, red_card,
                                  total_passes, accurate_passes, total_long_balls, accurate_long_balls, total_cross,
                                  accurate_cross, total_clearance, clearance_off_line, aerial_lost, aerial_won,
                                  duel_lost, duel_won, dispossessed, challenge_lost, total_contest, won_contest,
                                  good_high_claim, punches, error_lead_to_a_shot, error_lead_to_a_goal, shot_off_target,
                                  on_target_scoring_attempt, hit_woodwork, blocked_scoring_attempt, outfielder_block,
                                  big_chance_created, big_chance_missed, penalty_conceded, penalty_won, penalty_miss,
                                  penalty_save, goals, own_goals, saved_shots_from_inside_the_box, saves, goal_assist,
                                  goals_against, goals_avoided, interception_won, total_interceptions,
                                  total_keeper_sweeper, accurate_keeper_sweeper, total_tackle, was_fouled, fouls,
                                  total_offside, minutes_played, touches, last_man_tackle, possession_lost_control,
                                  expected_goals, goals_prevented, key_pass, expected_assists, ts)
                    progress_bar.update(1)
                progress_bar.close()
        except Exception as e:
            print("Error while connecting to MySQL", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def add_game(self, id_gw: int, id_mundo_deportivo: int, schedule: int, game_week: int, team: str,
                 opposing_team: str, mixed = 0, as_score = 0, marca_score = 0, mundo_deportivo_score = 0,
                 sofa_score = 0, current_value = 0, points = 0, average = 0, matches = 0, goals_metadata = 0, cards = 0,
                 yellow_card = 0, double_yellow_card = 0, red_card = 0, total_passes = 0, accurate_passes = 0,
                 total_long_balls = 0, accurate_long_balls = 0, total_cross = 0, accurate_cross = 0, total_clearance
                 = 0, clearance_off_line = 0, aerial_lost = 0, aerial_won = 0, duel_lost = 0, duel_won = 0,
                 challenge_lost = 0, dispossessed = 0, total_contest = 0, won_contest = 0, good_high_claim = 0,
                 punches = 0, error_lead_to_a_shot = 0, error_lead_to_a_goal = 0, shot_off_target = 0,
                 on_target_scoring_attempt = 0, hit_woodwork = 0, blocked_scoring_attempt = 0, outfielder_block = 0,
                 big_chance_created = 0, big_chance_missed = 0, penalty_conceded = 0, penalty_won = 0, penalty_miss = 0,
                 penalty_save = 0, goals = 0, own_goals = 0, saved_shots_from_inside_the_box = 0, saves = 0,
                 goal_assist = 0, goals_against = 0, goals_avoided = 0, interception_won = 0, total_interceptions = 0,
                 total_keeper_sweeper = 0, accurate_keeper_sweeper = 0, total_tackle = 0, was_fouled = 0, fouls = 0,
                 total_offside = 0, minutes_played = 0, touches = 0, last_man_tackle = 0, possession_lost_control = 0,
                 expected_goals = 0, goals_prevented = 0, key_pass = 0, expected_assists = 0, ts = 0):
        game = self.Game(id_gw, id_mundo_deportivo, schedule, game_week, team, opposing_team, mixed, as_score,
                         marca_score, mundo_deportivo_score, sofa_score, current_value, points, average, matches,
                         goals_metadata, cards, yellow_card, double_yellow_card, red_card, total_passes,
                         accurate_passes, total_long_balls, accurate_long_balls, total_cross, accurate_cross,
                         total_clearance, clearance_off_line, aerial_lost, aerial_won, duel_lost, duel_won,
                         dispossessed, challenge_lost, total_contest, won_contest, good_high_claim, punches,
                         error_lead_to_a_shot, error_lead_to_a_goal, shot_off_target, on_target_scoring_attempt,
                         hit_woodwork, blocked_scoring_attempt, outfielder_block, big_chance_created,
                         big_chance_missed, penalty_conceded, penalty_won, penalty_miss, penalty_save, goals,
                         own_goals, saved_shots_from_inside_the_box, saves, goal_assist, goals_against, goals_avoided,
                         interception_won, total_interceptions, total_keeper_sweeper, accurate_keeper_sweeper,
                         total_tackle, was_fouled, fouls, total_offside, minutes_played, touches, last_man_tackle,
                         possession_lost_control, expected_goals, goals_prevented, key_pass, expected_assists, ts)
        self.games.append(game)

    def to_insert_statements(self):
        insert_statements = []
        for game in self.games:
            insert_statements.extend([game.to_insert_statements()])
        return insert_statements

    def get_all_games_ids(self):
        return [game.id_gw for game in self.games]

    def get_max_id(self):
        if self.games:
            return max(int(game.id_gw) for game in self.games) + 1
        else:
            return 0


class Absences:
    def __init__(self):
        self.absences = []

    def __getitem__(self, index):
        return self.absences[index]

    class Absence(Base):
        def __init__(self, id_mundo_deportivo: int, type_absence: str, description_absence: str,
                     since: datetime, until: datetime):
            self.id_mundo_deportivo = id_mundo_deportivo
            self.type_absence = type_absence
            self.description_absence = description_absence
            self.since = since
            self.until = until

        def to_insert_statements(self):
            return self.to_insert_statement("absence")

    def fill_from_database(self, local_ddbb: bool):
        connection = None
        cursor = None
        try:
            connection = create_database_connection(local_ddbb)
            if connection.is_connected():
                cursor = connection.cursor()
                query = "SELECT * FROM absence;"
                cursor.execute(query)
                records = cursor.fetchall()
                progress_bar = tqdm(total = len(records), desc = "Filling Absence: ")
                for row in records:
                    row = row[1:]
                    (id_mundo_deportivo, type_absence, description_absence, since, until) = row
                    self.add_absence(id_mundo_deportivo, type_absence, description_absence, since, until)
                    progress_bar.update(1)
                progress_bar.close()
        except Exception as e:
            print("Error while connecting to MySQL", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def add_absence(self, id_mundo_deportivo: int, type_absence: str, description_absence: str,
                    since: datetime, until: datetime):
        absence = self.Absence(id_mundo_deportivo, type_absence, description_absence, since, until)
        self.absences.append(absence)

    def to_insert_statements(self):
        insert_statements = []
        for absence in self.absences:
            insert_statements.extend([absence.to_insert_statements()])
        return insert_statements


class PriceVariations:
    def __init__(self):
        self.price_variations = []

    def __getitem__(self, index):
        return self.price_variations[index]

    class PriceVariation(Base):
        def __init__(self, id_mundo_deportivo: int, price_day: datetime, price: int, is_prediction = False):
            self.id_mundo_deportivo = id_mundo_deportivo
            self.price_day = price_day
            self.price = price
            self.is_prediction = is_prediction

        def to_insert_statements(self):
            return self.to_insert_statement("price_variation")

    def fill_from_database(self, local_ddbb: bool):
        connection = None
        cursor = None
        try:
            connection = create_database_connection(local_ddbb)
            if connection.is_connected():
                cursor = connection.cursor()
                query = "SELECT * FROM price_variation;"
                cursor.execute(query)
                records = cursor.fetchall()
                progress_bar = tqdm(total = len(records), desc = "Filling Price Variation: ")
                for row in records:
                    row = row[1:]
                    (id_mundo_deportivo, price, price_day, is_prediction) = row
                    self.add_price_variation(id_mundo_deportivo, price, price_day, is_prediction)
                    progress_bar.update(1)
                progress_bar.close()
        except Exception as e:
            print("Error while connecting to MySQL", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def add_price_variation(self, id_mundo_deportivo: int, price: int, price_day: datetime,
                            is_prediction = False):
        price_variation = self.PriceVariation(id_mundo_deportivo, price, price_day, is_prediction)
        self.price_variations.append(price_variation)

    def to_insert_statements(self):
        insert_statements = []
        for price_variation in self.price_variations:
            insert_statements.extend([price_variation.to_insert_statements()])
        return insert_statements


class PredictionPoints:
    def __init__(self):
        self.prediction_points = []

    def __getitem__(self, index):
        return self.prediction_points[index]

    class PredictionPoint(Base):
        def __init__(self, id_mundo_deportivo: int, gameweek: int, date_prediction: datetime, point_prediction: int):
            self.id_mundo_deportivo = id_mundo_deportivo
            self.gameweek = gameweek
            self.point_prediction = point_prediction
            self.date_prediction = date_prediction

        def to_insert_statements(self):
            return self.to_insert_statement("prediction_points")

    def fill_from_database(self, local_ddbb: bool):
        connection = None
        cursor = None
        try:
            connection = create_database_connection(local_ddbb)
            if connection.is_connected():
                cursor = connection.cursor()
                query = "SELECT * FROM prediction_points;"
                cursor.execute(query)
                records = cursor.fetchall()
                progress_bar = tqdm(total = len(records), desc = "Filling Prediction Points: ")
                for row in records:
                    row = row[1:]
                    (id_mundo_deportivo, gameweek, date_prediction, point_prediction) = row
                    self.add_prediction(id_mundo_deportivo, gameweek, date_prediction, point_prediction)
                    progress_bar.update(1)
                progress_bar.close()
        except Exception as e:
            print("Error while connecting to MySQL", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def add_prediction(self, id_mundo_deportivo: int, gameweek: int, date_prediction: datetime, point_prediction: int):
        prediction_point = self.PredictionPoint(id_mundo_deportivo, gameweek, date_prediction, point_prediction)
        self.prediction_points.append(prediction_point)

    def to_insert_statements(self):
        insert_statements = []
        for prediction_point in self.prediction_points:
            insert_statements.extend([prediction_point.to_insert_statements()])
        return insert_statements


class UserRecommendations:
    def __init__(self):
        self.user_recommendations = []

    def __getitem__(self, index):
        return self.user_recommendations[index]

    class UserRecommendation(Base):
        def __init__(self, id_user: int, id_mundo_deportivo: int, recommendation_day: datetime,
                     my_team_recommendation: bool, market_team_recommendation: bool, gameweek: int, operation_type: str,
                     expected_value_percentage: str, expected_value_day: datetime):
            self.id_user = id_user
            self.id_mundo_deportivo = id_mundo_deportivo
            self.recommendation_day = recommendation_day
            self.my_team_recommendation = my_team_recommendation
            self.market_team_recommendation = market_team_recommendation
            self.gameweek = gameweek
            self.operation_type = operation_type
            self.expected_value_percentage = expected_value_percentage
            self.expected_value_day = expected_value_day

        def to_insert_statements(self):
            return self.to_insert_statement("user_recommendation")

    def fill_from_database(self, local_ddbb: bool):
        connection = None
        cursor = None
        try:
            connection = create_database_connection(local_ddbb)
            if connection.is_connected():
                cursor = connection.cursor()
                query = "SELECT * FROM user_recommendation"
                cursor.execute(query)
                records = cursor.fetchall()
                progress_bar = tqdm(total = len(records), desc = "Filling User Recommendation: ")
                for row in records:
                    row = row[1:]
                    (id_user, id_mundo_deportivo, recommendation_day, my_team_recommendation,
                     market_team_recommendation, gameweek, operation_type, expected_value_percentage,
                     expected_value_day) = row
                    self.add_recommendation(id_user, id_mundo_deportivo, recommendation_day, my_team_recommendation,
                                            market_team_recommendation, gameweek, operation_type,
                                            expected_value_percentage, expected_value_day)
                    progress_bar.update(1)
                progress_bar.close()
        except Exception as e:
            print("Error while connecting to MySQL", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def add_recommendation(self, id_user: int, id_mundo_deportivo: int, recommendation_day: datetime,
                           my_team_recommendation: bool, market_team_recommendation: bool, gameweek: int,
                           operation_type: str, expected_value_percentage: str, expected_value_day: datetime):
        user_recommendation = self.UserRecommendation(id_user, id_mundo_deportivo, recommendation_day,
                                                      my_team_recommendation, market_team_recommendation, gameweek,
                                                      operation_type, expected_value_percentage, expected_value_day)
        self.user_recommendations.append(user_recommendation)

    def to_insert_statements(self):
        insert_statements = []
        for user_recommendation in self.user_recommendations:
            insert_statements.extend([user_recommendation.to_insert_statements()])
        return insert_statements


class GlobalRecommendations:
    def __init__(self):
        self.global_recommendations = []

    def __getitem__(self, index):
        return self.global_recommendations[index]

    class GlobalRecommendation(Base):
        def __init__(self, id_mundo_deportivo: int, lineup: int, gameweek: int):
            self.id_mundo_deportivo = id_mundo_deportivo
            self.lineup = lineup
            self.gameweek = gameweek

        def to_insert_statements(self):
            return self.to_insert_statement("global_recommendation")

    def fill_from_database(self, local_ddbb: bool):
        connection = None
        cursor = None
        try:
            connection = create_database_connection(local_ddbb)
            if connection.is_connected():
                cursor = connection.cursor()
                query = "SELECT * FROM global_recommendation;"
                cursor.execute(query)
                records = cursor.fetchall()
                progress_bar = tqdm(total = len(records), desc = "Filling Global Recommendation: ")
                for row in records:
                    row = row[1:]
                    (id_mundo_deportivo, lineup, gameweek) = row
                    self.add_recommendation(id_mundo_deportivo, lineup, gameweek)
                    progress_bar.update(1)
                progress_bar.close()
        except Exception as e:
            print("Error while connecting to MySQL", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def add_recommendation(self, id_mundo_deportivo: int, lineup: int, gameweek: int):
        user_recommendation = self.GlobalRecommendation(id_mundo_deportivo, lineup, gameweek)
        self.global_recommendations.append(user_recommendation)

    def to_insert_statements(self):
        insert_statements = []
        for global_recommendation in self.global_recommendations:
            insert_statements.extend([global_recommendation.to_insert_statements()])
        return insert_statements


@deprecated(action = "ignore")
class PlayerGames:
    def __init__(self):
        self.player_games = []

    def __getitem__(self, index):
        return self.player_games[index]

    class PlayerGame(Base):
        def __init__(self, id_play, id_mundo_deportivo, id_game):
            self.id_play = id_play
            self.id_mundo_deportivo = id_mundo_deportivo
            self.id_game = id_game

        def to_insert_statements(self):
            return self.to_insert_statement("player_game")

    def add_player_game(self, id_play, id_mundo_deportivo, id_game):
        player_game = self.PlayerGame(id_play, id_mundo_deportivo, id_game)
        self.player_games.append(player_game)

    def to_insert_statements(self):
        insert_statements = []
        for player_game in self.player_games:
            insert_statements.extend([player_game.to_insert_statements()])
        return insert_statements


@deprecated(action = "ignore")
class Movements:
    def __init__(self):
        self.movements = []

    def __getitem__(self, index):
        return self.movements[index]

    class Movement(Base):
        def __init__(self, from_name, to_name, type_movement, day, price):
            self.id_movement = None  # Este atributo se autoincrementará en la base de datos
            self.from_name = from_name
            self.to_name = to_name
            self.type_movement = type_movement
            self.day = day
            self.price = price

        def to_insert_statements(self):
            return self.to_insert_statement("movement")

    def add_movement(self, from_name, to_name, type_movement, day, price):
        movement = self.Movement(from_name, to_name, type_movement, day, price)
        self.movements.append(movement)

    def to_insert_statements(self):
        insert_statements = []
        for movement in self.movements:
            insert_statements.extend([movement.to_insert_statements()])
        return insert_statements


@deprecated(action = "ignore")
class PlayerMovements:
    def __init__(self):
        self.player_movements = []

    def __getitem__(self, index):
        return self.player_movements[index]

    class PlayerMovement(Base):
        def __init__(self):
            self.player_movement = set()

        def to_insert_statements(self):
            return self.to_insert_statement("player_movement")

    def add_player_movement(self):
        player_movement = self.PlayerMovement()
        self.player_movements.append(player_movement)

    def to_insert_statements(self):
        insert_statements = []
        for player_movement in self.player_movements:
            insert_statements.extend([player_movement.to_insert_statements()])
        return insert_statements


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
        logg.exception(err)
        return logg


def _load_private_key():
    with open(route.prk, "rb") as key_file:
        private_key = RSA.import_key(key_file.read())
    return private_key


def decrypt_pgp(encodedb64: str):
    decoded_message = base64.b64decode(encodedb64)
    prk = _load_private_key()
    cipher = PKCS1_OAEP.new(prk)

    # Desencriptar el mensaje
    try:
        decrypted_message = cipher.decrypt(decoded_message)
        return decrypted_message
    except ValueError as e:
        raise ValueError(f"Error al descifrar el mensaje: {e}")


def extract_login_token(h: dict, u: str, p: str):
    # Definir la URL del endpoint de inicio de sesión
    login_url = "https://mister.mundodeportivo.com/api2/auth/email"

    # Definir la carga útil (payload) con las credenciales
    payload = {"email": u, "password": p}

    failed = True
    res = None

    while failed:
        try:
            # Realizar la solicitud POST para autenticarse
            response = requests.post(login_url, json = payload, headers = h)

            # Verificar si la autenticación fue exitosa
            if response.status_code == 200:
                # Obtener el token de sesión de la respuesta
                response = response.json()
                res = response["token"]
                failed = False
            else:
                # Manejar respuestas de error del servidor
                print(f"Error de autenticación: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            # Manejar errores de conexión
            print(f"Error de conexión: {e}")
        except Exception as e:
            # Manejar cualquier otro error
            print(f"Error: {e}")
    return res


def extract_tokens(h: dict, u: str, p: str):

    token = extract_login_token(h, u, p)

    # Realizamos la segunda solicitud para verificar que el token sea válido
    url = "https://mister.mundodeportivo.com/api2/auth/external/exchange-token"
    payload = {"token": token}
    response = requests.post(url, json = payload, headers = h)
    if response.status_code == 200:
        cookie_list = []
        for _ in response.cookies.items():
            cookie_list.append(_[0] + "=" + _[1])
        return "; ".join(cookie_list[1:])


def extract_auth(h: dict, ua: str, u: str, p: str):
    full_cookie = extract_tokens(h, u, p)

    auth_headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                              "*/*;q=0.8", "Accept-Encoding": "gzip, deflate", "Accept-Language":
                    "es-ES,es;q=0.9", "User-Agent": ua, "Cookie": full_cookie, "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}

    market_url = "https://mister.mundodeportivo.com/market"

    response = requests.get(market_url, headers = auth_headers)

    soup = BeautifulSoup(response.text, "html.parser")
    script = soup.find("script")

    regex_expresion = '"auth":"[a-zA-Z0-9]+"'
    match = re.search(regex_expresion, script.get_text())

    auth_headers["X-AUTH"] = match.group().split(":")[1].replace("\"", "")

    return auth_headers


def extract_balance(h: dict, url: str):
    response = requests.post(url, data = {}, headers = h)
    if response.status_code == 200:
        return {"current_balance": response.json()["data"]["balance"],
                "future_balance": response.json()["data"]["future"],
                "maximum_debt": response.json()["data"]["max_debt"]}
    return None


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
            if any(platform.system() == ext for ext in ["Linux", "Windows"]):
                logger.exception(err)
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
            if any(platform.system() == ext for ext in ["Linux", "Windows"]):
                logger.exception(err)
            sleep(2)
            pass
        except WebDriverException as err:
            if any(platform.system() == ext for ext in ["Linux", "Windows"]):
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
                if any(platform.system() == ext for ext in ["Linux", "Windows"]):
                    logger.exception(err)
            try:
                if 0 < original_size > backup_size:
                    shutil.copy(original_path, back_path)
                else:
                    shutil.copy(back_path, original_path)
            except shutil.Error as err:
                print(f"Error al copiar archivos: {err}")
                if any(platform.system() == ext for ext in ["Linux", "Windows"]):
                    logger.exception(err)
        else:
            shutil.copy(original_path, back_path)


# Database
def create_database_connection(local: bool):
    with open(route.env_file, "r", encoding = "utf-8") as f:
        data = json.load(f)
    host = data["DB_HOST"]
    port = data["DB_PORT"]
    user = data["DB_USERNAME"]
    password = data["DB_PASSWORD"]
    database = data["DB_DATABASE"]
    if local:
        if platform.system() == "Windows":
            host = getenv("DB_HOST", "127.0.0.1")
            port = getenv("DB_PORT", "3306")
            user = getenv("DB_USER", "root")
            password = getenv("DB_PASSWORD", )
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


@deprecated(action = "ignore")
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


@deprecated(action = "ignore")
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


if any(platform.system() == ext for ext in ["Linux", "Windows"]):
    logger = define_logger(route.helper_log)

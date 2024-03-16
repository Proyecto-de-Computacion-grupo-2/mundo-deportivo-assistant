import csv
import json
import re

import mysql.connector
import requests
from json import loads
from os import makedirs, path, remove
from random import uniform
from time import sleep
from tqdm import tqdm

from bs4 import BeautifulSoup
from deprecated import deprecated
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from Utils import helper as helper, routes as route


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


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
                     goal_assist = 0, penalty_conceded = 0, penalty_won = 0, penalty_miss = 0, penalty_save = 0,
                     goals = 0, own_goals = 0, saved_shots_from_inside_the_box = 0, saves = 0, goals_against = 0,
                     interception_won = 0, total_nterceptions = 0, total_keeper_sweeper = 0,
                     accurate_keeper_sweeper = 0, total_tackle = 0, was_fouled = 0, fouls = 0, total_offside = 0,
                     minutes_played = 0, touches = 0, last_man_tackle = 0, possession_lost_control = 0,
                     expected_goals = 0, goals_prevented = 0, key_pass = 0, expected_assists = 0,
                     total_season_15_16 = 0, total_season_16_17 = 0, total_season_17_18 = 0, total_season_18_19 = 0,
                     total_season_19_20 = 0, total_season_20_21 = 0, total_season_21_22 = 0, total_season_22_23 = 0,
                     total_season_23_24 = 0, timestamp = 0):
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
            self.goal_assist = goal_assist
            self.penalty_conceded = penalty_conceded
            self.penalty_won = penalty_won
            self.penalty_miss = penalty_miss
            self.penalty_save = penalty_save
            self.goals = goals
            self.own_goals = own_goals
            self.saved_shots_from_inside_the_box = saved_shots_from_inside_the_box
            self.saves = saves
            self.goals_against = goals_against
            self.interception_won = interception_won
            self.total_nterceptions = total_nterceptions
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
            self.timestamp = timestamp

    def add_player(self, player_id, full_name, position, game_week, team, opposing_team, mixed, as_score,
                   marca_score, mundo_deportivo_score, sofa_score, current_value, points, average, matches,
                   goals_metadata, cards, yellow_card, double_yellow_card = 0, red_card = 0, total_passes = 0,
                   accurate_passes = 0, total_long_balls = 0, accurate_long_balls = 0, total_cross = 0,
                   accurate_cross = 0, total_clearance = 0, clearance_off_line = 0, aerial_lost = 0, aerial_won = 0,
                   duel_lost = 0, duel_won = 0, challenge_lost = 0, dispossessed = 0, total_contest = 0,
                   won_contest = 0, good_high_claim = 0, punches = 0, error_lead_to_a_shot = 0,
                   error_lead_to_a_goal = 0, shot_off_target = 0, on_target_scoring_attempt = 0, hit_woodwork = 0,
                   blocked_scoring_attempt = 0, outfielder_block = 0, big_chance_created = 0, big_chance_missed = 0,
                   goal_assist = 0, penalty_conceded = 0, penalty_won = 0, penalty_miss = 0, penalty_save = 0,
                   goals = 0, own_goals = 0, saved_shots_from_inside_the_box = 0, saves = 0, goals_against = 0,
                   interception_won = 0, total_nterceptions = 0, total_keeper_sweeper = 0, accurate_keeper_sweeper = 0,
                   total_tackle = 0, was_fouled = 0, fouls = 0, total_offside = 0, minutes_played = 0, touches = 0,
                   last_man_tackle = 0, possession_lost_control = 0, expected_goals = 0, goals_prevented = 0,
                   key_pass = 0, expected_assists = 0, total_season_15_16 = 0, total_season_16_17 = 0,
                   total_season_17_18 = 0, total_season_18_19 = 0, total_season_19_20 = 0, total_season_20_21 = 0,
                   total_season_21_22 = 0, total_season_22_23 = 0, total_season_23_24 = 0, timestamp = 0):
        player = self.Player(player_id, full_name, position, game_week, team, opposing_team, mixed, as_score,
                             marca_score, mundo_deportivo_score, sofa_score, current_value, points, average, matches,
                             goals_metadata, cards, yellow_card, double_yellow_card, red_card, total_passes,
                             accurate_passes, total_long_balls, accurate_long_balls, total_cross, accurate_cross,
                             total_clearance, clearance_off_line, aerial_lost, aerial_won, duel_lost, duel_won,
                             challenge_lost, dispossessed, total_contest, won_contest, good_high_claim, punches,
                             error_lead_to_a_shot, error_lead_to_a_goal, shot_off_target, on_target_scoring_attempt,
                             hit_woodwork, blocked_scoring_attempt, outfielder_block, big_chance_created,
                             big_chance_missed, goal_assist, penalty_conceded, penalty_won, penalty_miss, penalty_save,
                             goals, own_goals, saved_shots_from_inside_the_box, saves, goals_against, interception_won,
                             total_nterceptions, total_keeper_sweeper, accurate_keeper_sweeper, total_tackle,
                             was_fouled, fouls, total_offside, minutes_played, touches, last_man_tackle,
                             possession_lost_control, expected_goals, goals_prevented, key_pass, expected_assists,
                             total_season_15_16, total_season_16_17, total_season_17_18, total_season_18_19,
                             total_season_19_20, total_season_20_21, total_season_21_22, total_season_22_23,
                             total_season_23_24, timestamp)
        self.player_model.append(player)

    def save_to_csv(self, filename):
        with open(filename, "w", newline = "") as csvfile:
            fieldnames = vars(self.player_model[0]).keys()
            writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
            writer.writeheader()
            for player in self.player_model:
                writer.writerow(vars(player))


class Users:
    def __init__(self):
        self.users = []

    def __getitem__(self, index):
        return self.users[index]

    class User(Base):
        def __init__(self, id_user, email = "", password = "", team_name = "", team_points = 0, team_average = 0.0,
                     team_value = 0.0, team_players = 0, current_balance = 0, future_balance = 0, maximum_debt = 0):
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

        def to_insert_statements(self):
            return self.to_insert_statement("user")

    def add_user(self, id_user, email = "", password = "", team_name = "", team_points = 0, team_average = 0.0,
                 team_value = 0.0, team_players = 0, current_balance = 0, future_balance = 0, maximum_debt = 0):
        user = self.User(id_user, email, password, team_name, team_points, team_average, team_value, team_players,
                         current_balance, future_balance, maximum_debt)
        self.users.append(user)

    def to_insert_statements(self):
        insert_statements = []
        for user in self.users:
            insert_statements.extend([user.to_insert_statements()])
        return insert_statements

    def get_all_user_ids(self):
        return [user.id_user for user in self.users]


class Players:
    def __init__(self):
        self.players = []

    def __getitem__(self, index):
        return self.players[index]

    class Player(Base):
        def __init__(self, id_mundo_deportivo, id_sofa_score, id_marca, id_user, full_name, position, value,
                     is_in_market = False, sell_price = "", photo_face = "", photo_body = "", season_15_16 = "",
                     season_16_17 = "", season_17_18 = "", season_18_19 = "", season_19_20 = "", season_20_21 = "",
                     season_21_22 = "", season_22_23 = "", season_23_24 = ""):
            self.id_mundo_deportivo = id_mundo_deportivo
            self.id_sofa_score = id_sofa_score
            self.id_marca = id_marca
            self.id_user = id_user
            self.full_name = full_name
            self.position = position
            self.value = value
            self.is_in_market = is_in_market
            self.sell_price = sell_price
            self.photo_face = photo_face
            self.photo_body = photo_body
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

    def add_player(self, id_mundo_deportivo, id_sofa_score, id_marca, id_user, full_name, position, value,
                   is_in_market = False, sell_price = "", photo_face = "", photo_body = "", season_15_16 = "",
                   season_16_17 = "", season_17_18 = "", season_18_19 = "", season_19_20 = "", season_20_21 = "",
                   season_21_22 = "", season_22_23 = "", season_23_24 = ""):
        player = self.Player(id_mundo_deportivo, id_sofa_score, id_marca, id_user, full_name, position, value,
                             is_in_market, sell_price, photo_face, photo_body, season_15_16, season_16_17,
                             season_17_18, season_18_19, season_19_20, season_20_21, season_21_22, season_22_23,
                             season_23_24)
        self.players.append(player)

    def to_insert_statements(self):
        insert_statements = []
        for player in self.players:
            insert_statements.extend([player.to_insert_statements()])
        return insert_statements

    def get_all_player_ids(self):
        return [int(player.id_mundo_deportivo) for player in self.players]

    def find_player(self, i: int):
        index = 0
        found_player = None
        player_found = False

        while index < len(self.players) and not player_found:
            if self.players[index].id_mundo_deportivo == i:
                found_player = self.players[index]
                player_found = True
            index += 1

        return found_player


class Games:
    def __init__(self):
        self.games = []

    def __getitem__(self, index):
        return self.games[index]

    class Game(Base):
        def __init__(self, id_gw, id_player, schedule, game_week, team, opposing_team, mixed, as_score,
                     marca_score, mundo_deportivo_score, sofa_score, current_value, points, average, matches,
                     goals_metadata, cards, yellow_card, double_yellow_card = 0, red_card = 0, total_passes = 0,
                     accurate_passes = 0, total_long_balls = 0, accurate_long_balls = 0, total_cross = 0,
                     accurate_cross = 0, total_clearance = 0, clearance_off_line = 0, aerial_lost = 0, aerial_won = 0,
                     duel_lost = 0, duel_won = 0, challenge_lost = 0, dispossessed = 0, total_contest = 0,
                     won_contest = 0, good_high_claim = 0, punches = 0, error_lead_to_a_shot = 0,
                     error_lead_to_a_goal = 0, shot_off_target = 0, on_target_scoring_attempt = 0,
                     hit_woodwork = 0, blocked_scoring_attempt = 0, outfielder_block = 0, big_chance_created = 0,
                     big_chance_missed = 0, goal_assist = 0, penalty_conceded = 0, penalty_won = 0, penalty_miss = 0,
                     penalty_save = 0, goals = 0, own_goals = 0, saved_shots_from_inside_the_box = 0, saves = 0,
                     goals_against = 0, interception_won = 0, total_nterceptions = 0, total_keeper_sweeper = 0,
                     accurate_keeper_sweeper = 0, total_tackle = 0, was_fouled = 0, fouls = 0, total_offside = 0,
                     minutes_played = 0, touches = 0, last_man_tackle = 0, possession_lost_control = 0,
                     expected_goals = 0, goals_prevented = 0, key_pass = 0, expected_assists = 0, timestamp = 0):
            self.id_gw = id_gw
            self.id_player = id_player
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
            self.goal_assist = goal_assist
            self.penalty_conceded = penalty_conceded
            self.penalty_won = penalty_won
            self.penalty_miss = penalty_miss
            self.penalty_save = penalty_save
            self.goals = goals
            self.own_goals = own_goals
            self.saved_shots_from_inside_the_box = saved_shots_from_inside_the_box
            self.saves = saves
            self.goals_against = goals_against
            self.interception_won = interception_won
            self.total_nterceptions = total_nterceptions
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
            self.timestamp = timestamp

        def to_insert_statements(self):
            return self.to_insert_statement("game")

    def add_game(self, id_gw, id_player, schedule, game_week, team, opposing_team, mixed, as_score,
                 marca_score, mundo_deportivo_score, sofa_score, current_value, points, average, matches,
                 goals_metadata, cards, yellow_card, double_yellow_card = 0, red_card = 0, total_passes = 0,
                 accurate_passes = 0, total_long_balls = 0, accurate_long_balls = 0, total_cross = 0,
                 accurate_cross = 0, total_clearance = 0, clearance_off_line = 0, aerial_lost = 0, aerial_won = 0,
                 duel_lost = 0, duel_won = 0, challenge_lost = 0, dispossessed = 0, total_contest = 0,
                 won_contest = 0, good_high_claim = 0, punches = 0, error_lead_to_a_shot = 0,
                 error_lead_to_a_goal = 0, shot_off_target = 0, on_target_scoring_attempt = 0, hit_woodwork = 0,
                 blocked_scoring_attempt = 0, outfielder_block = 0, big_chance_created = 0, big_chance_missed = 0,
                 goal_assist = 0, penalty_conceded = 0, penalty_won = 0, penalty_miss = 0, penalty_save = 0,
                 goals = 0, own_goals = 0, saved_shots_from_inside_the_box = 0, saves = 0, goals_against = 0,
                 interception_won = 0, total_nterceptions = 0, total_keeper_sweeper = 0,
                 accurate_keeper_sweeper = 0, total_tackle = 0, was_fouled = 0, fouls = 0, total_offside = 0,
                 minutes_played = 0, touches = 0, last_man_tackle = 0, possession_lost_control = 0, expected_goals = 0,
                 goals_prevented = 0, key_pass = 0, expected_assists = 0, timestamp = 0):
        game = self.Game(id_gw, id_player, schedule, game_week, team, opposing_team, mixed, as_score, marca_score,
                         mundo_deportivo_score, sofa_score, current_value, points, average, matches, goals_metadata,
                         cards, yellow_card, double_yellow_card, red_card, total_passes, accurate_passes,
                         total_long_balls, accurate_long_balls, total_cross, accurate_cross, total_clearance,
                         clearance_off_line, aerial_lost, aerial_won, duel_lost, duel_won, dispossessed, challenge_lost,
                         total_contest, won_contest, good_high_claim, punches, error_lead_to_a_shot,
                         error_lead_to_a_goal, shot_off_target, on_target_scoring_attempt, hit_woodwork,
                         blocked_scoring_attempt, outfielder_block, big_chance_created, big_chance_missed, goal_assist,
                         penalty_conceded, penalty_won, penalty_miss, penalty_save, goals, own_goals,
                         saved_shots_from_inside_the_box, saves, goals_against, interception_won, total_nterceptions,
                         total_keeper_sweeper, accurate_keeper_sweeper, total_tackle, was_fouled, fouls,
                         total_offside, minutes_played, touches, last_man_tackle, possession_lost_control,
                         expected_goals, goals_prevented, key_pass, expected_assists, timestamp)
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
        def __init__(self, id_mundo_deportivo, type_absence, since, until, description_absence):
            self.id_mundo_deportivo = id_mundo_deportivo
            self.type_absence = type_absence
            self.since = since
            self.until = until
            self.description_absence = description_absence

        def to_insert_statements(self):
            return self.to_insert_statement("absence")

    def add_absence(self, id_mundo_deportivo, type_absence, since, until, description_absence):
        absence = self.Absence(id_mundo_deportivo, type_absence, since, until, description_absence)
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
        def __init__(self, id_mundo_deportivo, price, day, is_prediction):
            self.id_mundo_deportivo = id_mundo_deportivo
            self.price = price
            self.day = day
            self.is_prediction = is_prediction

        def to_insert_statements(self):
            return self.to_insert_statement("price_variation")

    def add_price_variation(self, id_mundo_deportivo, price, day, is_prediction = False):
        price_variation = self.PriceVariation(id_mundo_deportivo, price, day, is_prediction)
        self.price_variations.append(price_variation)

    def to_insert_statements(self):
        insert_statements = []
        for price_variation in self.price_variations:
            insert_statements.extend([price_variation.to_insert_statements()])
        return insert_statements


class Predictions:
    def __init__(self):
        self.predictions = []

    def __getitem__(self, index):
        return self.predictions[index]

    class Prediction(Base):
        def __init__(self, id_prediction, id_mundo_deportivo, gameweek, point_prediction, price_prediction,
                     date_prediction):
            self.id_prediction = id_prediction
            self.id_mundo_deportivo = id_mundo_deportivo
            self.gameweek = gameweek
            self.point_prediction = point_prediction
            self.price_prediction = price_prediction
            self.date_prediction = date_prediction

        def to_insert_statements(self):
            return self.to_insert_statement("prediction")

    def add_prediction(self, id_prediction, id_mundo_deportivo, gameweek, point_prediction, price_prediction,
                       date_prediction):
        prediction = self.Prediction(id_prediction, id_mundo_deportivo, gameweek, point_prediction, price_prediction,
                                     date_prediction)
        self.predictions.append(prediction)

    def to_insert_statements(self):
        insert_statements = []
        for prediction in self.predictions:
            insert_statements.extend([prediction.to_insert_statements()])
        return insert_statements


class Recommendations:
    def __init__(self):
        self.recommendations = []

    def __getitem__(self, index):
        return self.recommendations[index]

    class Recommendation(Base):
        def __init__(self, id_user, id_player, recommendation_type, market_team_recommendation, my_team_recommendation):
            self.id_recommendation = None  # Este atributo se autoincrementará en la base de datos
            self.id_user = id_user
            self.id_player = id_player
            self.recommendation_type = recommendation_type
            self.market_team_recommendation = market_team_recommendation
            self.my_team_recommendation = my_team_recommendation

        def to_insert_statements(self):
            return self.to_insert_statement("recommendation")

    def add_recommendation(self, id_user, id_player, recommendation_type, market_team_recommendation,
                           my_team_recommendation):
        movement = self.Recommendation(id_user, id_player, recommendation_type, market_team_recommendation,
                                       my_team_recommendation)
        self.recommendations.append(movement)

    def to_insert_statements(self):
        insert_statements = []
        for recommendation in self.recommendations:
            insert_statements.extend([recommendation.to_insert_statements()])
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


def multi_stmt_insert(name: str, create: bool, file: bool,  cur: mysql.connector.connection.MySQLCursorBuffered):
    if create and file:
        try:
            with open(name, "r", encoding = "utf-8") as file:
                sql_script = file.read()

            for result in cur.execute(sql_script, multi = True):
                if result.with_rows:
                    print("Rows produced by statement '{}':".format(result.statement))
                    print(result.fetchall())
                else:
                    print("Number of rows affected by statement '{}': {}".format(result.statement, result.rowcount))

            cursor.close()
        except Exception as e:
            print(e)
        finally:
            cursor.close()
    elif not create and file:
        progress_bar = None
        try:
            with open(name, "r", encoding = "utf-8") as file:
                sql_script = file.readlines()

            progress_bar = tqdm(total = len(sql_script), desc = "Inserting")

            for ins in sql_script:
                cur.execute(ins.replace("\"", "").strip())
                progress_bar.update(1)
        except Exception as e:
            print(e)
        finally:
            progress_bar.close()
            cursor.close()


def extract_login_token(h: dict, u: str, p: str):
    # Definir la URL del endpoint de inicio de sesión
    login_url = "https://mister.mundodeportivo.com/api2/auth/email"

    # Definir la carga útil (payload) con las credenciales
    payload = {"email": u, "password": p}

    # Realizar la solicitud POST para autenticarse
    response = requests.post(login_url, json = payload, headers = h)

    # Verificar si la autenticación fue exitosa
    if response.status_code == 200:
        # Obtener el token de sesión de la respuesta
        response = response.json()
        return response["token"]
    return None


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


def extract_auth_marca():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options = chrome_options)
    driver.get("https://laligafantasy.relevo.com/leagues")

    WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.CLASS_NAME, "main-season")))

    # Obtener el localStorage
    local_storage = driver.execute_script("return window.localStorage")
    data = loads(local_storage["auth"])

    # Acceder al token de acceso dentro del objeto "auth_data"
    access_token = data["status"]["authenticateGuest"]["access_token"]

    driver.quit()

    return access_token


def extract_marca_all_p():
    auth = extract_auth_marca()

    url = "https://api-fantasy.llt-services.com/api/v3/players?x-lang=es"
    res = requests.get(url, auth = BearerAuth(auth), headers = marca_header, timeout = request_timeout)
    if res.status_code == 200:
        return auth, res.json()
    return None


def extract_marca_all_p_id(marca_h: dict, rt: int):
    auth, players_info_res = extract_marca_all_p()

    marca = []
    if players_info_res:
        for _ in players_info_res:
            url = "https://api-fantasy.llt-services.com/api/v3/player/" + _["id"] + "?x-lang=es"
            p = requests.get(url, auth = BearerAuth(auth), headers = marca_h, timeout = rt).json()
            if p:
                if p["position"] != "Entrenador":
                    temp_dict = {"id_md": "0", "id_marca": p["id"], "id_ss": "0", "full_name": p["name"],
                                 "nickname": p["nickname"], "slug": p["slug"].replace("-", " ")}
                    marca.append(temp_dict)
        return marca
    return None


def extract_marca_img(marca_h: dict, rt: int):
    auth, players_info_res = extract_marca_all_p()
    faulty = []

    if players_info_res:
        for _ in players_info_res:
            url = "https://api-fantasy.llt-services.com/api/v3/player/" + _["id"] + "?x-lang=es"
            img_url = "https://assets-fantasy.llt-services.com/players/"
            p_data = requests.get(url, auth = BearerAuth(auth), headers = marca_h, timeout = rt).json()
            player_image = img_url + p_data["team"]["badgeColor"].split("/")[-1].split("_")[0] + "/p" + \
                p_data["id"] + "/256x256/p" + p_data["id"] + "_" + \
                p_data["team"]["badgeColor"].split("/")[-1].split("_")[0] + "_1_001_000.png"
            res = requests.get(player_image)
            if res.status_code != 200:
                player_image = img_url + p_data["team"]["badgeColor"].split("/")[-1].split("_")[0] + "/p" + \
                               p_data["id"] + "/128x128/p" + p_data["id"] + "_" + \
                               p_data["team"]["badgeColor"].split("/")[-1].split("_")[0] + "_1_001_000.png"
                res = requests.get(player_image)
                if res.status_code != 200:
                    player_image = img_url + p_data["team"]["badgeColor"].split("/")[-1].split("_")[0] + "/p" + \
                                   p_data["id"] + "/64x64/p" + p_data["id"] + "_" + \
                                   p_data["team"]["badgeColor"].split("/")[-1].split("_")[0] + "_1_001_000.png"
                    res = requests.get(player_image)
            if res.status_code == 200:
                img_file = path.join("marca_img",
                                     p_data["id"] + "_" + "".join(p_data["nickname"].split(" ")) + ".png")
                makedirs(path.dirname(img_file), exist_ok = True)
                with open(img_file, "wb") as img:
                    img.write(res.content)
            else:
                faulty.append(p_data["id"] + ", " + p_data["name"] + ", " + p_data["nickname"] + ", " +
                              p_data["slug"] + ", " + p_data["team"]["badgeColor"].split("/")[-1].split("_")[0])
            return faulty


def extracmd(h: dict, url: str):
    payload = {"post": "competition"}
    response = requests.post(url, data = payload, headers = h)
    gw = []
    if response.status_code == 200:
        for clave, valor in response.json()["data"]["games"].items():
            for _ in valor:
                if _["id_gameweek"] not in gw:
                    gw.append(_["id_gameweek"])
        return gw
    return None


def extract_all_players_value_and_gw_md(h: dict, ai: AIModel, ab: Absences, gw: Games, players: Players,
                                        pv: PriceVariations, users: Users, url: str, url2: str):
    for _ in range(0, 601, 50):
        sleep(uniform(10, 20))
        payload = {
            "post": "players", "filters[ position ]": 0, "filters[ value ]": 0, "filters[ team ]": 0,
            "filters[ injured ]": 0, "filters[ favs ]": 0, "filters[ owner ]": 0, "filters[ benched ]": 0, "offset": _,
            "order": 0, "name": "", "filtered": 0, "parentElement": ".sw-content"}
        res = requests.post(url, data = payload, headers = h)
        if res.status_code == 200:
            aux = res.json()
            if aux["data"]["players"]:
                for _ in aux["data"]["owners"]:
                    if _["id"] not in users.get_all_user_ids():
                        users.add_user(_["id"], team_name = _["name"])
                for _ in aux["data"]["players"]:
                    if _["id"] not in players.get_all_player_ids():
                        payload_2 = {"post": "players", "id": _["id"]}
                        sleep(uniform(10, 20))
                        res_2 = requests.post(url, data = payload_2, headers = h)
                        if res_2.status_code == 200:
                            res_json_2 = res_2.json()["data"]
                            if res_json_2:
                                res_json_h_points = res_json_2["points_history"]
                                res_json_p_repo = res_json_2["playerRepo"]
                                res_json_p_injuries = res_json_p_repo["injuries"]
                                res_json_values = res_json_2["values_chart"]["points"]
                                s56, s67, s78, s89, s1920, s2021, s2122, s2223, s2324 = 0, 0, 0, 0, 0, 0, 0, 0, 0
                                for i in res_json_h_points:
                                    if i["season"] == "15/16":
                                        s56 = i["points"]
                                    elif i["season"] == "16/17":
                                        s67 = i["points"]
                                    elif i["season"] == "17/18":
                                        s78 = i["points"]
                                    elif i["season"] == "18/19":
                                        s89 = i["points"]
                                    elif i["season"] == "19/20":
                                        s1920 = i["points"]
                                    elif i["season"] == "20/21":
                                        s2021 = i["points"]
                                    elif i["season"] == "21/22":
                                        s2122 = i["points"]
                                    elif i["season"] == "22/23":
                                        s2223 = i["points"]
                                    elif i["season"] == "23/24":
                                        s2324 = i["points"]
                                res = requests.get(res_2.json()["data"]["player"]["photoUrl"])
                                img_file = helper.path.join(route.image_folder, str(_["id"]) + "_" + _["name"].
                                                            replace(" ", "_") + ".png")
                                helper.makedirs(helper.path.dirname(img_file), exist_ok = True)
                                with open(img_file, "wb") as img:
                                    img.write(res.content)
                                # Insertar imágenes:
                                with open(img_file, "rb") as file:
                                    binary_data = file.read()
                                players.add_player(_["id"], res_json_p_repo["sofaScoreId"], 0, _["id_uc"], _["name"],
                                                   _["position"], _["value"], True if _["id_market"] is not None else
                                                   False, 0, binary_data, 0, s56, s67, s78, s89, s1920, s2021, s2122,
                                                   s2223, s2324)
                                # _["is_mine"] Para usuarios y balance.
                                # current_balance = extract_balance(new_header, md_balance_url)
                                remove(img_file)
                                for value in res_json_values:
                                    pv.add_price_variation(_["id"], value["value"], value["date"])
                                for injury in res_json_p_injuries:
                                    ab.add_absence(_["id"], injury["category"], injury["since"], injury["until"],
                                                   injury["description"])
                                res_json_player = res_json_2["player"]
                                gameweeks = res_json_2["points"]
                                gameweeks.reverse()
                                for gameweek in gameweeks:
                                    gw_number = gameweek["gameweek"]
                                    payload_3 = {"id_gameweek": gameweek["id_gameweek"], "id_player": _["id"]}
                                    res_3 = requests.post(url2, data = payload_3, headers = h)
                                    res_json_3 = None
                                    if res_3.status_code == 200:
                                        res_json_3 = res_3.json()["data"]
                                    if res_json_3 is not None:
                                        print(res_json_2["player"]["name"], gameweek["id_gameweek"],
                                              gameweek["gameweek"])
                                        own_team = res_json_3["id_team"]
                                        if res_json_3["id_home"] == own_team:
                                            opposing_team = res_json_3["id_away"]
                                        else:
                                            opposing_team = res_json_3["id_home"]
                                        if res_json_3["marca_stats_rating_detailed"]:
                                            test = res_json_3["marca_stats_rating_detailed"]
                                            special = False
                                        else:
                                            test = res_json_3["stats"]
                                            special = True
                                        data_str = test.replace("'", "\"")
                                        exclude = ["rating", "marca"]
                                        include = ["goals"]
                                        original_data_dict = {
                                            "yellowCard": {"value": 0, "rating": 0},
                                            "doubleYellowCard": {"value": 0, "rating": 0},
                                            "redCard": {"value": 0, "rating": 0},
                                            "totalPass": {"value": 0, "rating": 0},
                                            "accuratePass": {"value": 0, "rating": 0},
                                            "totalLongBalls": {"value": 0, "rating": 0},
                                            "accurateLongBalls": {"value": 0, "rating": 0},
                                            "totalCross": {"value": 0, "rating": 0},
                                            "accurateCross": {"value": 0, "rating": 0},
                                            "totalClearance": {"value": 0, "rating": 0},
                                            "clearanceOffLine": {"value": 0, "rating": 0},
                                            "aerialLost": {"value": 0, "rating": 0},
                                            "aerialWon": {"value": 0, "rating": 0},
                                            "duelLost": {"value": 0, "rating": 0},
                                            "duelWon": {"value": 0, "rating": 0},
                                            "dispossessed": {"value": 0, "rating": 0},
                                            "challengeLost": {"value": 0, "rating": 0},
                                            "totalContest": {"value": 0, "rating": 0},
                                            "wonContest": {"value": 0, "rating": 0},
                                            "goodHighClaim": {"value": 0, "rating": 0},
                                            "punches": {"value": 0, "rating": 0},
                                            "errorLeadToAShot": {"value": 0, "rating": 0},
                                            "errorLeadToAGoal": {"value": 0, "rating": 0},
                                            "shotOffTarget": {"value": 0, "rating": 0},
                                            "onTargetScoringAttempt": {"value": 0, "rating": 0},
                                            "blockedScoringAttempt": {"value": 0, "rating": 0},
                                            "outfielderBlock": {"value": 0, "rating": 0},
                                            "bigChanceCreated": {"value": 0, "rating": 0},
                                            "goalAssist": {"value": 0, "rating": 0},
                                            "hitWoodwork": {"value": 0, "rating": 0},
                                            "bigChanceMissed": {"value": 0, "rating": 0},
                                            "penaltyConceded": {"value": 0, "rating": 0},
                                            "penaltyWon": {"value": 0, "rating": 0},
                                            "penaltyMiss": {"value": 0, "rating": 0},
                                            "penaltySave": {"value": 0, "rating": 0},
                                            "goals": {"value": 0, "rating": 0}, "ownGoals": {"value": 0, "rating": 0},
                                            "savedShotsFromInsideTheBox": {"value": 0, "rating": 0},
                                            "saves": {"value": 0, "rating": 0},
                                            "goalsAvoided": {"value": 0, "rating": 0},
                                            "interceptionWon": {"value": 0, "rating": 0},
                                            "totalInterceptions": {"value": 0, "rating": 0},
                                            "goalsAgainst": {"value": 0, "rating": 0},
                                            "totalKeeperSweeper": {"value": 0, "rating": 0},
                                            "accurateKeeperSweeper": {"value": 0, "rating": 0},
                                            "totalTackle": {"value": 0, "rating": 0},
                                            "wasFouled": {"value": 0, "rating": 0}, "fouls": {"value": 0, "rating": 0},
                                            "totalOffside": {"value": 0, "rating": 0},
                                            "minutesPlayed": {"value": 0, "rating": 0},
                                            "touches": {"value": 0, "rating": 0},
                                            "lastManTackle": {"value": 0,  "rating": 0},
                                            "possessionLostCtrl": {"value": 0, "rating": 0},
                                            "expectedGoals": {"value": 0, "rating": 0},
                                            "goalsPrevented": {"value": 0, "rating": 0},
                                            "keyPass": {"value": 0, "rating": 0},
                                            "expectedAssists": {"value": 0, "rating": 0},
                                            "timestamp": {"value": 0, "rating": 0}
                                        }

                                        # Convert to dictionary
                                        data_dict = json.loads(data_str)
                                        for key, value in data_dict.items():
                                            if not special:
                                                if key in original_data_dict:
                                                    original_data_dict[key].update(data_dict[key])
                                                if (any(ext in res_json_3["stats"] for ext in include) or
                                                        "goals" in data_str) and all(key != ext for ext in exclude):
                                                    print(key + " in MD.")
                                                elif key not in original_data_dict and \
                                                        all(key != ext for ext in exclude):
                                                    print(key)
                                            if special:
                                                if key in original_data_dict:
                                                    original_data_dict[key] = {"value": data_dict[key], "rating": 0}
                                        player_value = players.find_player(_["id"])
                                        game_count = sum(1 for game in gameweeks if game["points"] is not None
                                                         and game["points"] > 0)
                                        goal_count = sum(game["events"].count("goal") for game in gameweeks
                                                         if game["events"] is not False)
                                        card_count = sum(game["events"].count("red") for game in gameweeks
                                                         if game["events"] is not False) + \
                                            sum(game["events"].count("yellow") for game in gameweeks
                                                if game["events"] is not False)
                                        gw.add_game(gameweek["id_gameweek"], _["id"], res_json_3["as_graded_date"],
                                                    gw_number, own_team, opposing_team, res_json_3["points_mix"],
                                                    res_json_3["points_as"], res_json_3["points_marca"],
                                                    res_json_3["points_md"], res_json_3["points_mr"],
                                                    player_value.value, res_json_player["points"],
                                                    res_json_player["avg"], game_count, goal_count, card_count,
                                                    original_data_dict["yellowCard"]["value"],
                                                    original_data_dict["doubleYellowCard"]["value"],
                                                    original_data_dict["redCard"]["value"],
                                                    original_data_dict["totalPass"]["value"],
                                                    original_data_dict["accuratePass"]["value"],
                                                    original_data_dict["totalLongBalls"]["value"],
                                                    original_data_dict["accurateLongBalls"]["value"],
                                                    original_data_dict["totalCross"]["value"],
                                                    original_data_dict["accurateCross"]["value"],
                                                    original_data_dict["totalClearance"]["value"],
                                                    original_data_dict["clearanceOffLine"]["value"],
                                                    original_data_dict["aerialLost"]["value"],
                                                    original_data_dict["aerialWon"]["value"],
                                                    original_data_dict["duelLost"]["value"],
                                                    original_data_dict["duelWon"]["value"],
                                                    original_data_dict["dispossessed"]["value"],
                                                    original_data_dict["challengeLost"]["value"],
                                                    original_data_dict["totalContest"]["value"],
                                                    original_data_dict["wonContest"]["value"],
                                                    original_data_dict["goodHighClaim"]["value"],
                                                    original_data_dict["punches"]["value"],
                                                    original_data_dict["errorLeadToAShot"]["value"],
                                                    original_data_dict["errorLeadToAGoal"]["value"],
                                                    original_data_dict["shotOffTarget"]["value"],
                                                    original_data_dict["onTargetScoringAttempt"]["value"],
                                                    original_data_dict["blockedScoringAttempt"]["value"],
                                                    original_data_dict["outfielderBlock"]["value"],
                                                    original_data_dict["bigChanceCreated"]["value"],
                                                    original_data_dict["goalAssist"]["value"],
                                                    original_data_dict["hitWoodwork"]["value"],
                                                    original_data_dict["bigChanceMissed"]["value"],
                                                    original_data_dict["penaltyConceded"]["value"],
                                                    original_data_dict["penaltyWon"]["value"],
                                                    original_data_dict["penaltyMiss"]["value"],
                                                    original_data_dict["penaltySave"]["value"],
                                                    original_data_dict["goals"]["value"],
                                                    original_data_dict["ownGoals"]["value"],
                                                    original_data_dict["savedShotsFromInsideTheBox"]["value"],
                                                    original_data_dict["saves"]["value"],
                                                    original_data_dict["goalsAvoided"]["value"],
                                                    original_data_dict["interceptionWon"]["value"],
                                                    original_data_dict["totalInterceptions"]["value"],
                                                    original_data_dict["totalKeeperSweeper"]["value"],
                                                    original_data_dict["accurateKeeperSweeper"]["value"],
                                                    original_data_dict["totalTackle"]["value"],
                                                    original_data_dict["wasFouled"]["value"],
                                                    original_data_dict["fouls"]["value"],
                                                    original_data_dict["totalOffside"]["value"],
                                                    original_data_dict["minutesPlayed"]["value"],
                                                    original_data_dict["touches"]["value"],
                                                    original_data_dict["lastManTackle"]["value"],
                                                    original_data_dict["possessionLostCtrl"]["value"],
                                                    original_data_dict["expectedGoals"]["value"],
                                                    original_data_dict["goalsPrevented"]["value"],
                                                    original_data_dict["keyPass"]["value"],
                                                    original_data_dict["expectedAssists"]["value"],
                                                    original_data_dict["timestamp"]["value"])
                                        ai.add_player(_["id"], _["name"], _["position"], gameweek["id_gameweek"],
                                                      own_team, opposing_team, res_json_3["points_mix"],
                                                      res_json_3["points_as"], res_json_3["points_marca"],
                                                      res_json_3["points_md"], res_json_3["points_mr"],
                                                      player_value.value, res_json_player["points"],
                                                      res_json_player["avg"], game_count, goal_count, card_count,
                                                      original_data_dict["yellowCard"]["value"],
                                                      original_data_dict["doubleYellowCard"]["value"],
                                                      original_data_dict["redCard"]["value"],
                                                      original_data_dict["totalPass"]["value"],
                                                      original_data_dict["accuratePass"]["value"],
                                                      original_data_dict["totalLongBalls"]["value"],
                                                      original_data_dict["accurateLongBalls"]["value"],
                                                      original_data_dict["totalCross"]["value"],
                                                      original_data_dict["accurateCross"]["value"],
                                                      original_data_dict["totalClearance"]["value"],
                                                      original_data_dict["clearanceOffLine"]["value"],
                                                      original_data_dict["aerialLost"]["value"],
                                                      original_data_dict["aerialWon"]["value"],
                                                      original_data_dict["duelLost"]["value"],
                                                      original_data_dict["duelWon"]["value"],
                                                      original_data_dict["dispossessed"]["value"],
                                                      original_data_dict["challengeLost"]["value"],
                                                      original_data_dict["totalContest"]["value"],
                                                      original_data_dict["wonContest"]["value"],
                                                      original_data_dict["goodHighClaim"]["value"],
                                                      original_data_dict["punches"]["value"],
                                                      original_data_dict["errorLeadToAShot"]["value"],
                                                      original_data_dict["errorLeadToAGoal"]["value"],
                                                      original_data_dict["shotOffTarget"]["value"],
                                                      original_data_dict["onTargetScoringAttempt"]["value"],
                                                      original_data_dict["blockedScoringAttempt"]["value"],
                                                      original_data_dict["outfielderBlock"]["value"],
                                                      original_data_dict["bigChanceCreated"]["value"],
                                                      original_data_dict["goalAssist"]["value"],
                                                      original_data_dict["hitWoodwork"]["value"],
                                                      original_data_dict["bigChanceMissed"]["value"],
                                                      original_data_dict["penaltyConceded"]["value"],
                                                      original_data_dict["penaltyWon"]["value"],
                                                      original_data_dict["penaltyMiss"]["value"],
                                                      original_data_dict["penaltySave"]["value"],
                                                      original_data_dict["goals"]["value"],
                                                      original_data_dict["ownGoals"]["value"],
                                                      original_data_dict["savedShotsFromInsideTheBox"]["value"],
                                                      original_data_dict["saves"]["value"],
                                                      original_data_dict["goalsAvoided"]["value"],
                                                      original_data_dict["interceptionWon"]["value"],
                                                      original_data_dict["totalInterceptions"]["value"],
                                                      original_data_dict["totalKeeperSweeper"]["value"],
                                                      original_data_dict["accurateKeeperSweeper"]["value"],
                                                      original_data_dict["totalTackle"]["value"],
                                                      original_data_dict["wasFouled"]["value"],
                                                      original_data_dict["fouls"]["value"],
                                                      original_data_dict["totalOffside"]["value"],
                                                      original_data_dict["minutesPlayed"]["value"],
                                                      original_data_dict["touches"]["value"],
                                                      original_data_dict["lastManTackle"]["value"],
                                                      original_data_dict["possessionLostCtrl"]["value"],
                                                      original_data_dict["expectedGoals"]["value"],
                                                      original_data_dict["goalsPrevented"]["value"],
                                                      original_data_dict["keyPass"]["value"],
                                                      original_data_dict["expectedAssists"]["value"], s56, s67, s78,
                                                      s89, s1920, s2021, s2122, s2223, s2324,
                                                      original_data_dict["timestamp"]["value"])
    print()


def find_id_marca_to_md(h: dict, pl: list, player_md: Players, url: str):
    faulty = []
    payload = {"post": "players", "filters[ position ]": 0, "filters[ value ]": 0, "filters[ team ]": 0,
               "filters[ injured]": 0, "filters[ favs ]": 0, "filters[ owner ]": 0, "filters[ benched ]": 0,
               "offset": 0, "order": 0, "name": "", "filtered": 0, "parentElement": ".sw-content"}
    for p in pl:
        if "fdez" in p["full_name"].lower():
            p["full_name"] = p["full_name"].replace("Fdez", "Fernandez")
        elif "fdez" in p["nickname"].lower():
            p["nickname"] = p["nickname"].replace("Fdez", "Fernandez")
        if "fdez" in p["slug"].lower():
            p["slug"] = p["slug"].replace("Fdez", "Fernandez")
        elif "-1" in p["slug"].lower():
            p["slug"] = p["slug"].replace("-1", "")
        elif "-2" in p["slug"].lower():
            p["slug"] = p["slug"].replace("-2", "")
        elif "-3" in p["slug"].lower():
            p["slug"] = p["slug"].replace("-3", "")
        elif "-4" in p["slug"].lower():
            p["slug"] = p["slug"].replace("-4", "")
        elif "-5" in p["slug"].lower():
            p["slug"] = p["slug"].replace("-5", "")
        elif "-6" in p["slug"].lower():
            p["slug"] = p["slug"].replace("-6", "")
        payload["name"] = p["full_name"]
        res = requests.post(url, data = payload, headers = h)
        if res.status_code == 200:
            final_player = None
            res_json = res.json()
            if len(res_json["data"]["players"]) != 1:
                payload["name"] = p["nickname"]
                res = requests.post(url, data = payload, headers = h)
                if res.status_code == 200:
                    res_json = res.json()
                    if len(res_json["data"]["players"]) != 1:
                        payload["name"] = p["slug"].replace("-", " ")
                        res = requests.post(url, data = payload, headers = h)
                        if res.status_code == 200:
                            res_json = res.json()
                            if len(res_json["data"]["players"]) != 1:
                                faulty.append(p["id_marca"] + ", " + p["full_name"] + ", " + p["nickname"] + ", " +
                                              p["slug"])
                                print(p["id_marca"])
                            else:
                                final_player = res_json["data"]["players"][0]
                    else:
                        final_player = res_json["data"]["players"][0]
            else:
                final_player = res_json["data"]["players"][0]
            if final_player is not None:
                p["id_md"] = final_player["id"]
    return faulty, pl


@deprecated(action = "ignore")
def player_movements(h: dict, m: Movements, p_id: list, url: str):
    for p in p_id:
        payload = {"post": "players", "id": p}
        res = requests.post(url, data = payload, headers = h).json()
        for r in res["data"]["owners"]:
            m.add_movement(str(r["from"]), str(r["to"]), str(r["transferType"]), str(r["date"]), str(r["price"]))
    return m


def extract_market(h: dict):
    url = "https://mister.mundodeportivo.com/ajax/sw"
    payload = {"post": "offer"}
    response = requests.post(url, data = payload, headers = h)
    soup = BeautifulSoup(response.text, "html.parser")

    # Encontrar la tabla de jugadores por su ID
    market_players_table = soup.find("table", {"id": "list-on-sale"})

    # Extraer el ID del equipo completo
    whole_team_id = helper.extract_player_id(market_players_table)

    # Encontrar todos los iconos de jugadores
    market_players_icons = market_players_table.find_all("div", {"class": "icons"})

    # Encontrar todas las filas de información de jugadores
    market_players_info = market_players_table.find_all("tr", {"class": "player-row"})

    # Llamar a la función para scrape de información de jugadores
    players = helper.scrape_player_info("m", market_players_info, market_players_icons, whole_team_id)

    # ------ Start process to save all the information in a CSV. ------
    market_structure_header = ["ID", "Points", "Market value", "Average value", "Ante penultimate match score",
                               "Penultimate match score", "Last match score", "Attempt to buy", "Position"]
    helper.write_to_csv("test-api-player-in-market", market_structure_header, players, "w")


def extract_balance(h: dict, url: str):
    response = requests.post(url, data = {}, headers = h)
    if response.status_code == 200:
        return {"balance": response.json()["data"]["balance"], "future balance": response.json()["data"]["future"],
                "max debt": response.json()["data"]["max_debt"]}
    return None


def extract_all(ail: AIModel, ul: Users, pl: Players, gwl: Games, al: Absences, pvl: PriceVariations, sw_url: str,
                gw_url: str):
    extract_all_players_value_and_gw_md(new_header, ail, al, gwl, pl, pvl, ul, sw_url, gw_url)


mariadb = helper.create_database_connection()
cursor = mariadb.cursor(buffered = True)
try:
    sql = "SELECT * FROM users;"
    cursor.execute(sql)

    results = cursor.fetchall()
except helper.mysql.connector.Error as err:
    if "doesn\'t exist" in err.msg and err.errno == 1146:
        try:
            multi_stmt_insert("pc2-database.sql", True, True, cursor)
            mariadb.commit()
        except Exception as err:
            print(err)
finally:
    mariadb.close()

md_balance_url = "https://mister.mundodeportivo.com/ajax/balance"
md_gw_url = "https://mister.mundodeportivo.com/ajax/player-gameweek"
md_sw_url = "https://mister.mundodeportivo.com/ajax/sw"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 " \
             "Safari/537.36"

headers = {"Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest", "User-Agent": user_agent}

new_header = extract_auth(headers, user_agent, "", "")

request_timeout = 30

marca_header = {"User-Agent": user_agent, "Origin": "https://fantasy.laliga.com", "Referer":
                "https://fantasy.laliga.com/", "X-App": "Fantasy-web", "X-Lang": "es"}

failed_img = extract_marca_img(marca_header, request_timeout)

ai_list = AIModel()
users_list = Users()
players_list = Players()
gameweeks_list = Games()
absences_list = Absences()
price_variations_list = PriceVariations()
# extract_all(ai_list, users_list, players_list, gameweeks_list, absences_list, price_variations_list, md_sw_url,
            # md_gw_url)

# extract_market(new_header, md_ajax_url)

y = extract_marca_all_p_id(marca_header, request_timeout)
unkown, player_list = find_id_marca_to_md(new_header, y, players_list, md_sw_url)

all_tables = [users_list.to_insert_statements(), players_list.to_insert_statements(),
              gameweeks_list.to_insert_statements(), absences_list.to_insert_statements(),
              price_variations_list.to_insert_statements()]

if path.exists("insert_statements.sql"):
    remove("insert_statements.sql")
with open("insert_statements.sql", mode = "a", newline = "", encoding = "utf-8") as f:
    f_write = csv.writer(f)
    for table in all_tables:
        for row in table:
            f_write.writerow([row.replace("\"", "")])

mariadb = helper.create_database_connection()
cursor = mariadb.cursor(buffered = True)
try:
    multi_stmt_insert("insert_statements.sql", False, True, cursor)
except Exception as err:
    print(err)
finally:
    mariadb.close()

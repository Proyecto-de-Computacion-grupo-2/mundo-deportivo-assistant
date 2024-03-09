import json, re, requests

from bs4 import BeautifulSoup
from deprecated import deprecated
from json import loads
from os import makedirs, path
from random import uniform
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
# from Utils import helper as helper
# from Utils import routes as route


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


class Users:
    def __init__(self):
        self.users = set()

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
        self.users.add(user)

    def to_insert_statements(self):
        insert_statements = []
        for user in self.users:
            insert_statements.extend([user.to_insert_statements()])
        return insert_statements

    def get_all_user_ids(self):
        return [user.id_user for user in self.users]


class Players:
    def __init__(self):
        self.players = set()

    class Player(Base):
        def __init__(self, id_mundo_deportivo, id_sofa_score, id_marca, id_user, full_name, position,
                     is_in_market = False, sell_price = None, photo_face = None, photo_body = None,
                     average_season_15_16 = None, average_season_16_17 = None, average_season_17_18 = None,
                     average_season_18_19 = None, average_season_19_20 = None, average_season_20_21 = None,
                     average_season_21_22 = None, average_season_22_23 = None, average_season_23_24 = None):
            self.id_mundo_deportivo = id_mundo_deportivo
            self.id_sofa_score = id_sofa_score
            self.id_marca = id_marca
            self.id_user = id_user
            self.full_name = full_name
            self.position = position
            self.is_in_market = is_in_market
            self.sell_price = sell_price
            self.photo_face = photo_face
            self.photo_body = photo_body
            self.average_season_15_16 = average_season_15_16
            self.average_season_16_17 = average_season_16_17
            self.average_season_17_18 = average_season_17_18
            self.average_season_18_19 = average_season_18_19
            self.average_season_19_20 = average_season_19_20
            self.average_season_20_21 = average_season_20_21
            self.average_season_21_22 = average_season_21_22
            self.average_season_22_23 = average_season_22_23
            self.average_season_23_24 = average_season_23_24

        def to_insert_statements(self):
            return self.to_insert_statement("player")

    def add_player(self, id_mundo_deportivo, id_sofa_score, id_marca, id_user, full_name, position,
                   is_in_market = False, sell_price = None, photo_face = None, photo_body = None,
                   average_season_15_16 = None, average_season_16_17 = None, average_season_17_18 = None,
                   average_season_18_19 = None, average_season_19_20 = None, average_season_20_21 = None,
                   average_season_21_22 = None, average_season_22_23 = None, average_season_23_24 = None):
        player = self.Player(id_mundo_deportivo, id_sofa_score, id_marca, id_user, full_name, position,
                             is_in_market, sell_price, photo_face, photo_body, average_season_15_16,
                             average_season_16_17, average_season_17_18, average_season_18_19, average_season_19_20,
                             average_season_20_21, average_season_21_22, average_season_22_23, average_season_23_24)
        self.players.add(player)

    def to_insert_statements(self):
        insert_statements = []
        for player in self.players:
            insert_statements.extend([player.to_insert_statements()])
        return insert_statements

    def get_all_player_ids(self):
        return [player.id_mundo_deportivo for player in self.players]


class Recommendations:
    def __init__(self):
        self.recommendations = set()

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
        self.recommendations.add(movement)

    def to_insert_statements(self):
        insert_statements = []
        for recommendation in self.recommendations:
            insert_statements.extend([recommendation.to_insert_statements()])
        return insert_statements


class Games:
    def __init__(self):
        self.games = set()

    class Game(Base):
        def __init__(self, id_game, id_gw, id_player, schedule, game_week, team, opposing_team, mixed, as_score,
                     marca_score, mundo_deportivo_score, sofa_score, current_value, points, average, matches,
                     goals_metadata, cards, total_passes, accurate_passes, total_long_balls, accurate_long_balls,
                     total_crosses, accurate_crosses, total_clearances, clearances_on_goal_line, aerial_duels_lost,
                     aerial_duels_won, duels_lost, duels_won, dribbled_past, losses, total_dribbles, completed_dribbles,
                     high_clearances, fist_clearances, failures_that_lead_to_shot, failures_that_lead_to_goal,
                     shots_off_target, shots_on_target, shots_blocked_in_attack, shots_blocked_in_defence,
                     occasions_created, goal_assists, shots_to_the_crossbar, failed_obvious_occasions,
                     penalties_committed, penalties_caused, failed_penalties, stopped_penalties, goals, own_goals,
                     stops_from_inside_the_area, stops, goals_avoided, interceptions, total_outputs, precise_outputs,
                     total_tackles, fouls_received, fouls_committed, offsides, minutes_played, touches,
                     entries_as_last_man, possessions_lost, expected_goals, key_passes, expected_assists, timestamp):
            self.id_game = id_game
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
            self.total_passes = total_passes
            self.accurate_passes = accurate_passes
            self.total_long_balls = total_long_balls
            self.accurate_long_balls = accurate_long_balls
            self.total_crosses = total_crosses
            self.accurate_crosses = accurate_crosses
            self.total_clearances = total_clearances
            self.clearances_on_goal_line = clearances_on_goal_line
            self.aerial_duels_lost = aerial_duels_lost
            self.aerial_duels_won = aerial_duels_won
            self.duels_lost = duels_lost
            self.duels_won = duels_won
            self.dribbled_past = dribbled_past
            self.losses = losses
            self.total_dribbles = total_dribbles
            self.completed_dribbles = completed_dribbles
            self.high_clearances = high_clearances
            self.fist_clearances = fist_clearances
            self.failures_that_lead_to_shot = failures_that_lead_to_shot
            self.failures_that_lead_to_goal = failures_that_lead_to_goal
            self.shots_off_target = shots_off_target
            self.shots_on_target = shots_on_target
            self.shots_blocked_in_attack = shots_blocked_in_attack
            self.shots_blocked_in_defence = shots_blocked_in_defence
            self.occasions_created = occasions_created
            self.goal_assists = goal_assists
            self.shots_to_the_crossbar = shots_to_the_crossbar
            self.failed_obvious_occasions = failed_obvious_occasions
            self.penalties_committed = penalties_committed
            self.penalties_caused = penalties_caused
            self.failed_penalties = failed_penalties
            self.stopped_penalties = stopped_penalties
            self.goals = goals
            self.own_goals = own_goals
            self.stops_from_inside_the_area = stops_from_inside_the_area
            self.stops = stops
            self.goals_avoided = goals_avoided
            self.interceptions = interceptions
            self.total_outputs = total_outputs
            self.precise_outputs = precise_outputs
            self.total_tackles = total_tackles
            self.fouls_received = fouls_received
            self.fouls_committed = fouls_committed
            self.offsides = offsides
            self.minutes_played = minutes_played
            self.touches = touches
            self.entries_as_last_man = entries_as_last_man
            self.possessions_lost = possessions_lost
            self.expected_goals = expected_goals
            self.key_passes = key_passes
            self.expected_assists = expected_assists
            self.timestamp = timestamp

        def to_insert_statements(self):
            return self.to_insert_statement("game")

    def add_game(self, id_game, id_gw, id_player, schedule, game_week, team, opposing_team, mixed, as_score,
                 marca_score, mundo_deportivo_score, sofa_score, current_value, points, average, matches,
                 goals_metadata, cards, total_passes, accurate_passes, total_long_balls, accurate_long_balls,
                 total_crosses, accurate_crosses, total_clearances, clearances_on_goal_line, aerial_duels_lost,
                 aerial_duels_won, duels_lost, duels_won, dribbled_past, losses, total_dribbles, completed_dribbles,
                 high_clearances, fist_clearances, failures_that_lead_to_shot, failures_that_lead_to_goal,
                 shots_off_target, shots_on_target, shots_blocked_in_attack, shots_blocked_in_defence,
                 occasions_created, goal_assists, shots_to_the_crossbar, failed_obvious_occasions, penalties_committed,
                 penalties_caused, failed_penalties, stopped_penalties, goals, own_goals, stops_from_inside_the_area,
                 stops, goals_avoided, interceptions, total_outputs, precise_outputs, total_tackles, fouls_received,
                 fouls_committed, offsides, minutes_played, touches, entries_as_last_man, possessions_lost,
                 expected_goals, key_passes, expected_assists, timestamp):
        game = self.Game(id_game, id_gw, id_player, schedule, game_week, team, opposing_team, mixed, as_score,
                         marca_score, mundo_deportivo_score, sofa_score, current_value, points, average, matches,
                         goals_metadata, cards, total_passes, accurate_passes, total_long_balls, accurate_long_balls,
                         total_crosses, accurate_crosses, total_clearances, clearances_on_goal_line, aerial_duels_lost,
                         aerial_duels_won, duels_lost, duels_won, dribbled_past, losses, total_dribbles,
                         completed_dribbles, high_clearances, fist_clearances, failures_that_lead_to_shot,
                         failures_that_lead_to_goal, shots_off_target, shots_on_target, shots_blocked_in_attack,
                         shots_blocked_in_defence, occasions_created, goal_assists, shots_to_the_crossbar,
                         failed_obvious_occasions, penalties_committed, penalties_caused, failed_penalties,
                         stopped_penalties, goals, own_goals, stops_from_inside_the_area, stops, goals_avoided,
                         interceptions, total_outputs, precise_outputs, total_tackles, fouls_received, fouls_committed,
                         offsides, minutes_played, touches, entries_as_last_man, possessions_lost, expected_goals,
                         key_passes, expected_assists, timestamp)
        self.games.add(game)

    def to_insert_statements(self):
        insert_statements = []
        for game in self.games:
            insert_statements.extend([game.to_insert_statements()])
        return insert_statements

    def get_all_games_ids(self):
        return [game.id_gw for game in self.games]

    def get_max_id(self):
        if self.games:
            return max(game.id_gw for game in self.games)
        else:
            return None


class Absences:
    def __init__(self):
        self.absences = set()

    class Absence(Base):
        def __init__(self, id_absence, id_mundo_deportivo, type_absence, since, until, description_absence):
            self.id_absence = id_absence
            self.id_mundo_deportivo = id_mundo_deportivo
            self.type_absence = type_absence
            self.since = since
            self.until = until
            self.description_absence = description_absence

        def to_insert_statements(self):
            return self.to_insert_statement("absence")

    def add_absence(self, id_absence, id_mundo_deportivo, type_absence, since, until, description_absence):
        absence = self.Absence(id_absence, id_mundo_deportivo, type_absence, since, until, description_absence)
        self.absences.add(absence)

    def to_insert_statements(self):
        insert_statements = []
        for absence in self.absences:
            insert_statements.extend([absence.to_insert_statements()])
        return insert_statements


class PlayerGames:
    def __init__(self):
        self.player_games = set()

    class PlayerGame(Base):
        def __init__(self, id_play, id_mundo_deportivo, id_game):
            self.id_play = id_play
            self.id_mundo_deportivo = id_mundo_deportivo
            self.id_game = id_game

        def to_insert_statements(self):
            return self.to_insert_statement("player_game")

    def add_player_game(self, id_play, id_mundo_deportivo, id_game):
        player_game = self.PlayerGame(id_play, id_mundo_deportivo, id_game)
        self.player_games.add(player_game)

    def to_insert_statements(self):
        insert_statements = []
        for player_game in self.player_games:
            insert_statements.extend([player_game.to_insert_statements()])
        return insert_statements


@deprecated(action = "ignore")
class Movements:
    def __init__(self):
        self.movements = set()

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
        self.movements.add(movement)

    def to_insert_statements(self):
        insert_statements = []
        for movement in self.movements:
            insert_statements.extend([movement.to_insert_statements()])
        return insert_statements


@deprecated(action = "ignore")
class PlayerMovements:
    def __init__(self):
        self.player_movements = set()

    class PlayerMovement(Base):
        def __init__(self):
            self.player_movement = set()

        def to_insert_statements(self):
            return self.to_insert_statement("player_movement")

    def add_player_movement(self):
        player_movement = self.PlayerMovement()
        self.player_movements.add(player_movement)

    def to_insert_statements(self):
        insert_statements = []
        for player_movement in self.player_movements:
            insert_statements.extend([player_movement.to_insert_statements()])
        return insert_statements


class Predictions:
    def __init__(self):
        self.predictions = set()

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
        self.predictions.add(prediction)

    def to_insert_statements(self):
        insert_statements = []
        for prediction in self.predictions:
            insert_statements.extend([prediction.to_insert_statements()])
        return insert_statements


class PriceVariations:
    def __init__(self):
        self.price_variations = set()

    class PriceVariation(Base):
        def __init__(self, id_player_price_variation, id_mundo_deportivo, price_variation, price, day):
            self.id_player_price_variation = id_player_price_variation
            self.id_mundo_deportivo = id_mundo_deportivo
            self.price_variation = price_variation
            self.price = price
            self.day = day

        def to_insert_statements(self):
            return self.to_insert_statement("price_variation")

    def add_price_variation(self, id_player_price_variation, id_mundo_deportivo, price_variation, price, day):
        price_variation = self.PriceVariation(id_player_price_variation, id_mundo_deportivo, price_variation, price,
                                              day)
        self.price_variations.add(price_variation)

    def to_insert_statements(self):
        insert_statements = []
        for price_variation in self.price_variations:
            insert_statements.extend([price_variation.to_insert_statements()])
        return insert_statements


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
                temp_dict = {"id_md": "0", "id_marca": p["id"], "id_ss": "0", "full_name": p["name"],
                             "nickname": p["nickname"], "slug": p["slug"].replace("_", " ")}
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


def extract_all_gw_id_md(h: dict, url: str):
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


def extract_all_players_id_md(h: dict, players: Players, users: Users, url: str):
    for _ in range(0, 601, 50):
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
                        players.add_player(_["id"], 0, 0, _["uc_name"], _["name"], _["position"], True
                                           if _["id_market"] is not None else False)


def find_id_marca_to_md(h: dict, pl: list, url: str):
    faulty = []
    payload = {"post": "players", "filters[ position ]": 0, "filters[ value ]": 0, "filters[ team ]": 0,
               "filters[ injured]": 0, "filters[ favs ]": 0, "filters[ owner ]": 0, "filters[ benched ]": 0,
               "offset": 0, "order": 0, "name": "", "filtered": 0, "parentElement": ".sw-content"}

    for p in pl:
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
                        payload["name"] = p["slug"]
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
            if final_player:
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


def extract_all_gw_data_md(h: dict, url: str, p: Players, gw: Games, g: list):
    gw_data, gw_stats = [], []
    for i in p.get_all_player_ids():
        for j in g:
            sleep(uniform(10, 20))
            print(i, j)
            payload = {"id_gameweek": j, "id_player": i}
            response = requests.post(url, data = payload, headers = h)
            if response.status_code == 200:
                x = response.json()["data"]
                gw.add_game(gw.get_max_id, j, i, x["as_graded_date"])
                test = x["marca_stats_rating_detailed"]
                data_str = test.replace("'", "\"")

                # Convert to dictionary
                data_dict = json.loads(data_str)
                for clave, valor in data_dict.items():
                    if clave not in gw_stats and clave != "marca":
                        gw_stats.append(clave)
                # Print the dictionary
                for clave, valor in response.json()["data"].items():
                    print(clave, valor)
    return


def extract_balance(h: dict, url: str):
    response = requests.post(url, data = {}, headers = h)
    if response.status_code == 200:
        return {"balance": response.json()["data"]["balance"], "future balance": response.json()["data"]["future"],
                "max debt": response.json()["data"]["max_debt"]}
    return None


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

# failed_img = extract_marca_img(marca_header, request_timeout)

# extract_market(new_header, md_ajax_url)
# current_balance = extract_balance(new_header, md_balance_url)
# y = extract_marca_all_p_id(marca_header, request_timeout)
# find_id_marca_to_md(new_header, y, md_sw_url)
players_list = Players()
users_list = Users()
gw_list = Games()
extract_all_players_id_md(new_header, players_list, users_list, md_sw_url)
gw_id_list = extract_all_gw_id_md(new_header, md_sw_url)
if len(players_list.players) > 0 and len(gw_id_list) > 0:
    extract_all_gw_data_md(new_header, md_gw_url, players_list, gw_list, gw_id_list)

# print(failed_img)

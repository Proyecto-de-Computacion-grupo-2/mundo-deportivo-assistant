import random
from datetime import datetime, date
import Utils.helper as helper
# ------------ Value -------------


def get_player_latest_value(player_id, prediction_bool):
    mariadb = helper.create_database_connection()
    cursor = mariadb.cursor()

    try:
        sql = "SELECT id_mundo_deportivo,price,price_day from price_variation WHERE id_mundo_deportivo = (%s) AND is_prediction = (%s) ORDER BY price_day DESC LIMIT 1;"
        cursor.execute(sql, [player_id,prediction_bool])
        results = cursor.fetchone()


        if results:
            id_mundo_deportivo = results[0]
            price = results[1]
            price_day = results[2]
            return id_mundo_deportivo, price, price_day
    finally:
        if mariadb.is_connected():
            cursor.close()
            mariadb.close()

def get_player_sell_price(player_id):
    mariadb = helper.create_database_connection()
    cursor = mariadb.cursor()

    try:
        sql = "SELECT sell_price from player WHERE id_mundo_deportivo = (%s);"
        cursor.execute(sql, [player_id])
        results = cursor.fetchone()


        if results:
            return results[0]

    finally:
        if mariadb.is_connected():
            cursor.close()
            mariadb.close()

def get_player_latest_prediction(player_id):
    mariadb = helper.create_database_connection()
    cursor = mariadb.cursor()

    try:
        sql = "SELECT price from price_variation WHERE id_mundo_deportivo = (%s) AND is_prediction = 1 ORDER BY price_day DESC LIMIT 1 ;"
        cursor.execute(sql, [player_id])
        results = cursor.fetchone()

        if results:
            return results[0]

    finally:
        if mariadb.is_connected():
            cursor.close()
            mariadb.close()


# ------------ Points -------------

def get_40_best_players_ids_points_predictions(gameweek):
    mariadb = helper.create_database_connection()
    cursor = mariadb.cursor()

    try:
        sql = "SELECT id_mundo_deportivo,point_prediction FROM prediction_points WHERE gameweek = (%s) ORDER BY point_prediction DESC LIMIT 50"
        cursor.execute(sql, [gameweek])
        results = cursor.fetchall()

        if results:
            return results
    finally:
        if mariadb.is_connected():
            cursor.close()
            mariadb.close()


def get_players_id_in_market():
    mariadb = helper.create_database_connection()
    cursor = mariadb.cursor()
    try:
        sql = "SELECT id_mundo_deportivo FROM player WHERE is_in_market = TRUE"
        cursor.execute(sql)
        results = cursor.fetchall()

        id_mundo_deportivo_list = []
        for row in results:
            id_mundo_deportivo_list.append(row[0])

    finally:
        if mariadb.is_connected():
            cursor.close()
            mariadb.close()

    return id_mundo_deportivo_list


def get_players_in_market():
    mariadb = helper.create_database_connection()
    cursor = mariadb.cursor()
    try:
        sql = "SELECT id_mundo_deportivo,sell_price FROM player WHERE is_in_market = TRUE"
        cursor.execute(sql)
        results = cursor.fetchall()

        players_in_market = [(row[0], row[1]) for row in results]

    finally:
        if mariadb.is_connected():
            cursor.close()
            mariadb.close()

    return players_in_market


def get_user_current_balance(user_id):
    mariadb = helper.create_database_connection()
    cursor = mariadb.cursor()
    try:
        sql = "SELECT current_balance FROM league_user WHERE id_user = %s"
        cursor.execute(sql, [user_id])
        result = cursor.fetchone()
        if result:
            return result[0]
    finally:
        if mariadb.is_connected():
            cursor.close()
            mariadb.close()


def get_all_players_id():
    mariadb = helper.create_database_connection()
    cursor = mariadb.cursor()
    try:
        sql = "SELECT id_mundo_deportivo FROM player"
        cursor.execute(sql)
        results = cursor.fetchall()

        id_mundo_deportivo_list = []
        for row in results:
            id_mundo_deportivo_list.append(row[0])

    finally:
        if mariadb.is_connected():
            cursor.close()
            mariadb.close()
    return id_mundo_deportivo_list


def get_player_points_prediction(players_id, gameweek):
    mariadb = helper.create_database_connection()
    cursor = mariadb.cursor()

    players_prediction = []

    try:
        for player_id in players_id:
            sql = "SELECT point_prediction FROM prediction_points WHERE id_mundo_deportivo = (%s) AND gameweek = (%s)"
            cursor.execute(sql, [player_id, gameweek])
            result = cursor.fetchone()

            if result:
                players_prediction.append(result[0])

    finally:
        if mariadb.is_connected():
            cursor.close()
            mariadb.close()

    return players_prediction


def get_players_id_in_a_team(id_user):
    mariadb = helper.create_database_connection()
    cursor = mariadb.cursor()
    try:
        sql = "SELECT id_mundo_deportivo FROM player WHERE id_user =(%s)"
        cursor.execute(sql, [id_user])
        results = cursor.fetchall()

        players_in_a_team = []
        for row in results:
            players_in_a_team.append(row[0])

    finally:
        if mariadb.is_connected():
            cursor.close()
            mariadb.close()
    return players_in_a_team


def get_players_position(players_id):
    mariadb = helper.create_database_connection()
    cursor = mariadb.cursor()
    players_positions = []

    try:
        for player_id in players_id:
            sql = "SELECT position FROM player WHERE id_mundo_deportivo =(%s)"
            cursor.execute(sql, [player_id])
            result = cursor.fetchone()

            if result:
                players_positions.append(result[0])

    finally:
        if mariadb.is_connected():
            cursor.close()
            mariadb.close()

    return players_positions


# def insert_random_predictions(id_list):
#     mariadb = helper.create_database_connection()
#     cursor = mariadb.cursor()
#
#     gameweek = 30
#     points_range = (0, 20)
#
#     try:
#         for id_mundo_deportivo in id_list:
#             points_prediction = random.randint(*points_range)
#             date_prediction = datetime.now().strftime('%Y-%m-%d')
#
#             sql = """INSERT INTO prediction_points (id_mundo_deportivo, gameweek, date_prediction, point_prediction) VALUES (%s, %s, %s, %s)"""
#             values = (id_mundo_deportivo, gameweek, date_prediction, points_prediction)
#             cursor.execute(sql, values)
#         mariadb.commit()
#         print(f"{len(id_list)} predictions inserted successfully.")
#
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         mariadb.rollback()
#     finally:
#         cursor.close()
#         mariadb.close()


def insert_global_recommendation(id_mundo_deportivo, gameweek, lineup):
    mariadb = helper.create_database_connection()
    cursor = mariadb.cursor()
    try:
        sql = """INSERT INTO global_recommendation (id_mundo_deportivo, gameweek , lineup) VALUES (%s,%s,%s)"""
        values = (id_mundo_deportivo, gameweek, lineup)
        cursor.execute(sql, values)
        mariadb.commit()
    finally:
        cursor.close()
        mariadb.close()


def database_insert_user_recommendation(id_user, id_mundo_deportivo, market_team_recommendation, my_team_recommendation,
                                        gameweek, operation_type):
    mariadb = helper.create_database_connection()
    cursor = mariadb.cursor()
    try:
        sql = """INSERT INTO user_recommendation (id_user,id_mundo_deportivo,recommendation_day,market_team_recommendation,my_team_recommendation, gameweek , operation_type) VALUES (%s, %s,%s, %s,%s,%s,%s)"""
        values = (id_user, id_mundo_deportivo,date.today() ,market_team_recommendation, my_team_recommendation, gameweek, operation_type)
        cursor.execute(sql, values)
        mariadb.commit()
    finally:
        cursor.close()
        mariadb.close()

def database_insert_user_recommendations(id_user,player_id, date, percentage,my_team_recommendation,market_team_recommendation,operation_type):
    mariadb = helper.create_database_connection()
    cursor = mariadb.cursor()
    try:
        sql = """INSERT INTO user_recommendation(
        id_user,
        id_mundo_deportivo,
        recommendation_day,
        expected_value_day,
        expected_value_percentage,
        my_team_recommendation,
        market_team_recommendation,
        operation_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
        values = (
        id_user, player_id, date.today(), date, percentage, my_team_recommendation, market_team_recommendation,
        operation_type)
        cursor.execute(sql, values)
        mariadb.commit()
    finally:
        cursor.close()
        mariadb.close()



def avaiable_lineups():
    return [(4, 4, 2), (4, 5, 1), (4, 3, 3), (3, 4, 3), (3, 5, 2), (5, 4, 1), (5, 3, 2)]

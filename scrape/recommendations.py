from datetime import datetime, date
import Utils.helper as helper

def query_database(sql, params=None, fetch='one'):
    """Execute a SELECT query and fetch results."""
    with helper.create_database_connection() as mariadb:
        cursor = mariadb.cursor()
        cursor.execute(sql, params or ())
        if fetch == 'one':
            return cursor.fetchone()
        elif fetch == 'all':
            return cursor.fetchall()


def execute_database_operation(sql, params=None):
    """Execute a database operation like INSERT, UPDATE, DELETE and commit the changes."""
    with helper.create_database_connection() as mariadb:
        cursor = mariadb.cursor()
        cursor.execute(sql, params or ())
        mariadb.commit()


def get_player_latest_value(player_id, prediction_bool):
    sql = """SELECT id_mundo_deportivo, price, price_day 
             FROM price_variation 
             WHERE id_mundo_deportivo = %s AND is_prediction = %s 
             ORDER BY price_day DESC 
             LIMIT 1;"""
    return query_database(sql, [player_id, prediction_bool])


def get_player_sell_price(player_id):
    sql = "SELECT sell_price FROM player WHERE id_mundo_deportivo = %s;"
    return query_database(sql, [player_id])


def get_player_latest_prediction(player_id):
    sql = """SELECT price FROM price_variation 
             WHERE id_mundo_deportivo = %s AND is_prediction = 1 
             ORDER BY price_day DESC 
             LIMIT 1;"""
    return query_database(sql, [player_id])


def get_40_best_players_ids_points_predictions(gameweek):
    sql = """SELECT id_mundo_deportivo, point_prediction 
             FROM prediction_points 
             WHERE gameweek = %s 
             ORDER BY point_prediction DESC 
             LIMIT 50"""
    return query_database(sql, [gameweek], fetch='all')


def get_players_id_in_market():
    sql = "SELECT id_mundo_deportivo FROM player WHERE is_in_market = TRUE"
    return [row[0] for row in query_database(sql, fetch='all')]


def get_players_in_market():
    sql = "SELECT id_mundo_deportivo, sell_price FROM player WHERE is_in_market = TRUE"
    return query_database(sql, fetch='all')


def get_user_current_balance(user_id):
    sql = "SELECT current_balance FROM league_user WHERE id_user = %s"
    return query_database(sql, [user_id])[0]


def get_all_players_id():
    sql = "SELECT id_mundo_deportivo FROM player"
    return [row[0] for row in query_database(sql, fetch='all')]


def get_player_points_prediction(players_id, gameweek):
    positions = []
    for player_id in players_id:
        sql = "SELECT point_prediction FROM prediction_points WHERE id_mundo_deportivo = %s AND gameweek = %s"
        result = query_database(sql, [player_id, gameweek], fetch='one')
        if result is not None:
            positions.append(result[0])
    return positions


def get_players_id_in_a_team(id_user):
    sql = "SELECT id_mundo_deportivo FROM player WHERE id_user = %s"
    return [row[0] for row in query_database(sql, [id_user], fetch='all')]


def get_players_position(players_id):
    positions = []
    for player_id in players_id:
        result = query_database(
            "SELECT position FROM player WHERE id_mundo_deportivo = %s",
            [player_id],
            fetch='one'
        )
        if result is not None:
            positions.append(result[0])
    return positions


def insert_global_recommendation(id_mundo_deportivo, gameweek, lineup):
    sql = """INSERT INTO global_recommendation (id_mundo_deportivo, gameweek, lineup) VALUES (%s, %s, %s)"""
    execute_database_operation(sql, [id_mundo_deportivo, gameweek, lineup])


def database_insert_user_recommendation(id_user, id_mundo_deportivo, market_team_recommendation, my_team_recommendation,gameweek, operation_type):
    sql = """INSERT INTO user_recommendation (id_user, id_mundo_deportivo, recommendation_day, market_team_recommendation, my_team_recommendation, gameweek, operation_type) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    execute_database_operation(sql, [id_user, id_mundo_deportivo, date.today(), market_team_recommendation, my_team_recommendation,
                         gameweek, operation_type])


def database_insert_user_recommendations(id_user, player_id, date, percentage, my_team_recommendation,market_team_recommendation, operation_type):
    sql = """INSERT INTO user_recommendation(
                id_user,
                id_mundo_deportivo,
                recommendation_day,
                expected_value_day,
                expected_value_percentage,
                my_team_recommendation,
                market_team_recommendation,
                operation_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    execute_database_operation(sql, [id_user, player_id, date.today(), date, percentage, my_team_recommendation,
                                     market_team_recommendation, operation_type])


def avaiable_lineups():
    return [(4, 4, 2), (4, 5, 1), (4, 3, 3), (3, 4, 3), (3, 5, 2), (5, 4, 1), (5, 3, 2)]

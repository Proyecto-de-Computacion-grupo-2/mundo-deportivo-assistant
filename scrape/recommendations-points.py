import recommendations


def optimise_user_team(players_id, positions, predictions):
    players_info = sorted(zip(players_id, positions, predictions), key=lambda x: x[2], reverse=True)
    available_lineups = recommendations.avaiable_lineups()

    best_lineup = None
    max_points = -1
    best_team = []
    best_lineup_formation = ""

    for lineup in available_lineups:
        lineup_counts = {1: 1, 2: lineup[0], 3: lineup[1], 4: lineup[2]}
        current_team = []

        for player in players_info:
            player_id, position, prediction = player
            if lineup_counts[position] > 0:
                current_team.append(player)
                lineup_counts[position] -= 1

        current_points = sum([player[2] for player in current_team])
        if current_points > max_points:
            max_points = current_points
            best_team = current_team
            best_lineup = lineup

    best_team_sorted_by_position = sorted(best_team, key=lambda x: x[1])
    optimized_team_ids = [player[0] for player in best_team_sorted_by_position]
    total_predicted_points = sum([player[2] for player in best_team_sorted_by_position])
    best_lineup_formation = f"{best_lineup[0]}-{best_lineup[1]}-{best_lineup[2]}"

    return optimized_team_ids, total_predicted_points, best_lineup_formation


def optimise_user_team_market(players_id, positions, predictions, prices, current_money):
    players_info = sorted(zip(players_id, positions, predictions, prices), key=lambda x: x[2], reverse=True)
    available_lineups = recommendations.avaiable_lineups()

    best_lineup = None
    max_points = -1
    best_team = []
    best_lineup_formation = ""
    best_budget_left = current_money

    for lineup in available_lineups:
        lineup_counts = {1: 1, 2: lineup[0], 3: lineup[1], 4: lineup[2]}
        current_team = []
        budget_left = current_money

        for player in players_info:
            player_id, position, prediction, price = player
            if lineup_counts[position] > 0 and budget_left - price >= 0:
                current_team.append(player)
                lineup_counts[position] -= 1
                budget_left -= price

        current_points = sum(player[2] for player in current_team)
        if current_points > max_points or (current_points == max_points and budget_left > best_budget_left):
            max_points = current_points
            best_team = current_team
            best_lineup = lineup
            best_budget_left = budget_left

    best_team_sorted_by_position = sorted(best_team, key=lambda x: x[1])
    optimized_market_ids = [player[0] for player in best_team_sorted_by_position]
    total_predicted_points = sum(player[2] for player in best_team_sorted_by_position)
    best_lineup_formation = f"{best_lineup[0]}-{best_lineup[1]}-{best_lineup[2]}"

    return optimized_market_ids, total_predicted_points, best_lineup_formation, best_budget_left


def best_team_user_current_players(user_id, gameweek):
    players_id = recommendations.get_players_id_in_a_team(user_id)
    players_position = recommendations.get_players_position(players_id)
    players_points_prediction = recommendations.get_player_points_prediction(players_id, gameweek)

    optimized_team_ids = optimise_user_team(players_id, players_position, players_points_prediction)

    for optimized_player_id in optimized_team_ids[0]:
        recommendations.database_insert_user_recommendation(user_id, optimized_player_id, False, True, gameweek)


def best_team_user_market(user_id, gameweek):
    players_id = recommendations.get_players_id_in_a_team(user_id)

    players_in_market = recommendations.get_players_in_market()

    ids_market = [player[0] for player in players_in_market]
    prices_market = [player[1] for player in players_in_market]

    players_in_team_price = [0 for _ in range(len(players_id))]

    players_id = players_id + ids_market
    positions = recommendations.get_players_position(players_id)
    predictions = recommendations.get_player_points_prediction(players_id, gameweek)
    prices = players_in_team_price + prices_market
    current_money = recommendations.get_user_current_balance(user_id)

    optimized_market_ids = optimise_user_team_market(players_id, positions, predictions, prices, current_money)

    for optimized_player_id in optimized_market_ids[0]:
        recommendations.database_insert_user_recommendation(user_id, optimized_player_id, True, False, gameweek)


def best_team_league(gameweek):
    players_id_points = recommendations.get_40_best_players_ids_points_predictions(gameweek)
    players_ids = []
    players_prediction = []

    for player in players_id_points:
        players_ids.append(player[0])
        players_prediction.append(player[1])

    players_position = recommendations.get_players_position(players_ids)
    best_players = optimise_user_team(players_ids, players_position, players_prediction)
    best_players_id = best_players[0]
    lineup = best_players[2]
    for best_player_id in best_players_id:
        recommendations.insert_global_recommendation(best_player_id, gameweek,lineup)


if __name__ == '__main__':
    best_team_user_current_players(12705845, 30)
    best_team_user_market(12705845, 30)
    best_team_league(30)

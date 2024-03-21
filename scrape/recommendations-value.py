import recommendations

def value_recommendations_team(user_id):
    players_teams_ids = recommendations.get_players_id_in_a_team(user_id)

    recommend_sell = create_value_change_recommendations(players_teams_ids,20,False)
    return recommend_sell


def create_value_change_recommendations(players_id, percentage_threshold, seeking_profit=True):
    recommend_player_info = []

    for player_id in players_id:
        latest_real_value = recommendations.get_player_latest_value(player_id, False)
        latest_prediction_value = recommendations.get_player_latest_value(player_id, True)

        if latest_real_value is not None and latest_prediction_value is not None:
            aux, last_real_value, real_value_date = latest_real_value
            aux2, last_prediction_value, prediction_value_date = latest_prediction_value

            if last_real_value > 0:
                percentage_change = ((last_prediction_value - last_real_value) / last_real_value) * 100

                if seeking_profit and percentage_change >= percentage_threshold:
                    recommend_player_info.append((player_id, prediction_value_date, int(percentage_change)))
                elif not seeking_profit and percentage_change <= -percentage_threshold:
                    recommend_player_info.append((player_id, prediction_value_date, int(percentage_change)))

    recommend_player_info.sort(key=lambda x: abs(x[2]), reverse=True)

    return recommend_player_info

def value_recommendations_market(user_id):
    user_current_balance = recommendations.get_user_current_balance(user_id)
    players_market_ids = recommendations.get_players_id_in_market()

    recommend_buy = suggest_players_to_buy(user_current_balance, players_market_ids, 20)

    if recommend_buy:
        return recommend_buy


def suggest_players_to_buy(user_current_balance, players_id, minimum_profit_percentage):
    player_profit_info = []
    suggested_purchases = []

    for player_id in players_id:
        latest_real_value = recommendations.get_player_latest_value(player_id, False)
        latest_prediction_value = recommendations.get_player_latest_value(player_id, True)
        player_sell_price = recommendations.get_player_sell_price(player_id)

        if latest_real_value is not None and latest_prediction_value is not None:
            _, last_real_value, _ = latest_real_value
            _, last_prediction_value, prediction_value_date = latest_prediction_value

            if last_real_value > 0:
                profit_percentage = ((last_prediction_value - player_sell_price) / player_sell_price) * 100
                if profit_percentage >= minimum_profit_percentage:
                    player_profit_info.append((player_id, player_sell_price, last_prediction_value, profit_percentage, prediction_value_date))

    player_profit_info.sort(key=lambda x: x[3], reverse=True)

    total_spent = 0
    for player_info in player_profit_info:
        player_id, sell_price, _, profit_percentage, value_date = player_info
        if total_spent + sell_price <= user_current_balance:
            suggested_purchases.append((player_id, value_date, int(profit_percentage)))
            total_spent += sell_price
        else:
            break

    return suggested_purchases

def get_recommendations(id_user):

    def process_suggestions(id_user, suggestions, is_sell):
        action = "Vender" if is_sell else "Comprar"
        for player_id, date_suggestion, percentage_suggestion in suggestions:
            recommendations.database_insert_user_recommendations(
                id_user,player_id, date_suggestion, percentage_suggestion, is_sell, not is_sell, action)

    suggestions_sell = value_recommendations_team(id_user)
    suggestions_buy = value_recommendations_market(id_user)

    print(suggestions_sell)
    print(suggestions_buy)

    process_suggestions(id_user,suggestions_sell, True)
    process_suggestions(id_user,suggestions_buy, False)


if __name__ == '__main__':
    get_recommendations(12705845)

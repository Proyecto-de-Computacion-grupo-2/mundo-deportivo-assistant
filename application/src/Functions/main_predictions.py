import Utils.routes as route
import Utils.helper as helper


def merge_csv_by_id(csv_1, csv_2):
    # Load the CSV files into pandas DataFrames
    csv_1_df = helper.pandas.read_csv(csv_1)
    csv_2_df = helper.pandas.read_csv(csv_2)
    csv_2_df.drop("Position", axis = 1, inplace = True)

    # Perform a left join to keep all rows from the fantasy team data and
    # only add matching IDs from the players prediction data
    merged_data = csv_1_df.merge(csv_2_df, on = "ID", how = "left")
    merged_data['PredictedValue'] = merged_data['PredictedValue'].fillna(0).astype(int)
    return merged_data


def delete_impossible_formations(df_team_predictions, fantasy_l):
    available_lineups = []
    strikers = []
    midfielders = []
    defenders = []
    goalkeepers = []

    # Iterate over the DataFrame
    for index, row in df_team_predictions.iterrows():
        if row["Position"] == 3:
            strikers.append(row)
        elif row["Position"] == 2:
            midfielders.append(row)
        elif row["Position"] == 1:
            defenders.append(row)
        elif row["Position"] == 0:
            goalkeepers.append(row)
        else:
            continue

    # Discards useless lineups.
    num_strikers = len(strikers)
    num_midfielders = len(midfielders)
    num_defenders = len(defenders)
    num_goalkeepers = len(goalkeepers)
    players = num_strikers + num_midfielders + num_defenders + num_goalkeepers

    if players < 11:
        print("Not enough players to create enough players.")

    # Check against each fantasy lineup
    for lineup in fantasy_l:
        if num_defenders >= lineup[0] and num_midfielders >= lineup[1] and num_strikers >= lineup[2]:
            available_lineups.append(lineup)

    if len(available_lineups) == 0:
        print("It is not possible to form any lineup with the current players.")
        return 0
    # available_lineups now contains all the lineups you can create with the current players.
    else:
        # print("Available Lineups:", available_lineups)
        return available_lineups


def optimise_lineup_greedy(df, lineups):
    # Sort players by predicted value within each position
    df_sorted = df.sort_values(by = ["Position", "PredictedValue"], ascending = [True, False])
    best_lineup = None
    best_value = float("-inf")
    best_formation = None

    for lineup in lineups:
        fwds = df_sorted[df_sorted["Position"] == 3].head(lineup[2])
        mids = df_sorted[df_sorted["Position"] == 2].head(lineup[1])
        defs = df_sorted[df_sorted["Position"] == 1].head(lineup[0])
        gk = df_sorted[df_sorted["Position"] == 0].head(1)

        current_lineup = helper.pandas.concat([fwds, mids, defs, gk])
        total_value = current_lineup["PredictedValue"].sum()

        if total_value > best_value:
            best_value = total_value
            best_lineup = current_lineup
            best_formation = lineup

    return best_lineup, best_formation


def best_lineup_my_team(user, fantasy_l, predictions, filename):
    final_save = []
    # Create new CSV with my team joined to predictions.
    df_team_predictions = merge_csv_by_id(helper.path.join(route.users_folder, user + "_" +
                                                           route.app_personal_team_file), predictions)

    available_lineups = delete_impossible_formations(df_team_predictions, fantasy_l)

    best_lineup_df, best_formation = optimise_lineup_greedy(df_team_predictions, available_lineups)
    best_formation[0], best_formation[-1] = best_formation[-1], best_formation[0]
    save_line_up = helper.path.join(route.output_folder, "optimise_my_team_" + filename)

    # Save predictions to another file for later use
    save_line_predictions = helper.path.join(route.output_folder, "optimise_my_team_predictions_" + filename)
    slp_df = best_lineup_df[["ID", "PredictedValue"]]
    slp_df.to_csv(save_line_predictions, index = False, header = False)

    formation_str = "".join(str(item) for item in best_formation)  # Convert formation to string
    players_list = best_lineup_df["ID"].tolist()  # List of player names

    # Combine formation and player names into one list
    combined_list = [formation_str] + players_list

    # Create a DataFrame with a single column
    final_save_df = helper.pandas.DataFrame(combined_list, columns = ["Lineup"])
    final_save.append(best_lineup_df["ID"].tolist())
    final_save_df.to_csv(save_line_up, index = False, header = False)


def create_df_team_market_players(user, predictions):
    # Create new DF with my team and predictions joined.
    df_team_predictions_complete = merge_csv_by_id(helper.path.join(route.users_folder, user + "_" +
                                                                    route.app_personal_team_file), predictions)
    df_team_predictions = df_team_predictions_complete[["ID", "Position", "PredictedValue", "GameWeek"]]

    # Create new DF with market and predictions joined.
    df_market_predictions_complete = merge_csv_by_id(helper.path.join(route.users_folder, user + "_" +
                                                                      route.app_personal_market_file), predictions)
    df_market_predictions = df_market_predictions_complete[["ID", "Position", "PredictedValue", "GameWeek"]]

    df_market_team_players = helper.pandas.DataFrame(columns = df_team_predictions.columns)
    df_market_team_players = helper.pandas.concat([df_market_team_players, df_team_predictions], ignore_index = True)

    for index, row in df_market_predictions.iterrows():
        if row["ID"] not in df_market_team_players["ID"].values:
            df_market_team_players = helper.pandas.concat([df_market_team_players, helper.pandas.DataFrame([row])],
                                                          ignore_index = True)

    df_market_team_players.fillna(0, inplace = True)
    df_market_team_players["ID"] = df_market_team_players["ID"].astype(int)

    return df_market_team_players


def best_lineup_market(user, fantasy_l, predictions, filename):
    final_save = []

    df_market_team_players = create_df_team_market_players(user, predictions)
    available_lineups = delete_impossible_formations(df_market_team_players, fantasy_l)

    best_lineup_df, best_formation = optimise_lineup_greedy(df_market_team_players, available_lineups)
    # best_formation[0], best_formation[-1] = best_formation[-1], best_formation[0]

    save_line_up = helper.path.join(route.output_folder, "optimise_market_" + filename)
    # Save predictions to another file for later use
    save_line_predictions = helper.path.join(route.output_folder, "optimise_market_predictions_" + filename)
    slp_df = best_lineup_df[["ID", "PredictedValue"]]
    slp_df.to_csv(save_line_predictions, index = False, header = False)

    formation_str = "".join(str(item) for item in best_formation)  # Convert formation to string
    players_list = best_lineup_df["ID"].tolist()  # List of player names

    # Combine formation and player names into one list
    combined_list = [formation_str] + players_list

    # Create a DataFrame with a single column
    final_save_df = helper.pandas.DataFrame(combined_list, columns = ["Lineup"])
    final_save.append(best_lineup_df["ID"].tolist())
    final_save_df.to_csv(save_line_up, index = False, header = False)

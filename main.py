import itertools
import pandas as pd
import Utils.routes as route
import Utils.helper as helper


def merge_csv_by_id(csv_1, csv_2):
    # Load the CSV files into pandas DataFrames
    csv_1_df = pd.read_csv(csv_1)
    csv_2_df = pd.read_csv(csv_2)
    csv_2_df.drop('Position', axis=1, inplace=True)

    # Perform a left join to keep all rows from the fantasy team data and only add matching IDs from the players prediction data
    merged_data = csv_1_df.merge(csv_2_df, on='ID', how='left')

    return merged_data

def delete_impossible_formations(df_team_predictions, fantasy_lineups):
    available_lineups = []
    strikers = []
    midfielders = []
    defenders = []
    goalkeepers = []

    # Iterate over the DataFrame
    for index, row in df_team_predictions.iterrows():
        if row['Position'] == 3:
            strikers.append(row)
        elif row['Position'] == 2:
            midfielders.append(row)
        elif row['Position'] == 1:
            defenders.append(row)
        elif row['Position'] == 0:
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
        print('Not enough players to create enough players.')

    # Check against each fantasy lineup
    for lineup in fantasy_lineups:
        if num_defenders >= lineup[0] and num_midfielders >= lineup[1] and num_strikers >= lineup[2]:
            available_lineups.append(lineup)

    if len(available_lineups) == 0:
        print('It is not possible to form any lineup with the current players.')
        return 0
    # available_lineups now contains all the lineups you can create with the current players.
    else:
        print("Available Lineups:", available_lineups)
        return available_lineups

def optimise_lineup_greedy(df, lineups):
    # Sort players by predicted value within each position
    df_sorted = df.sort_values(by=['Position', 'PredictedValue'], ascending=[True, False])
    best_lineup = None
    best_value = float('-inf')
    best_formation = None

    for lineup in lineups:
        gk = df_sorted[df_sorted['Position'] == 0].head(1)
        defs = df_sorted[df_sorted['Position'] == 1].head(lineup[0])
        mids = df_sorted[df_sorted['Position'] == 2].head(lineup[1])
        fwds = df_sorted[df_sorted['Position'] == 3].head(lineup[2])

        current_lineup = pd.concat([gk, defs, mids, fwds])
        total_value = current_lineup['PredictedValue'].sum()

        if total_value > best_value:
            best_value = total_value
            best_lineup = current_lineup
            best_formation = lineup

    return best_lineup, best_formation

def format_lineup(df_lineup):
    id_column = df_lineup['ID']
    players_name = []
    for id in id_column:
        players_name.append(helper.id_name_mapping(id,"ID"))

    return players_name


def best_lineup_my_team(fantasy_lineups,predictions,filename):
    final_save = []
    # Create new CSV with my team joined to predictions.
    df_team_predictions = merge_csv_by_id(route.personal_team_file, predictions)

    available_lineups = delete_impossible_formations(df_team_predictions, fantasy_lineups)

    best_lineup_df, best_formation = optimise_lineup_greedy(df_team_predictions, available_lineups)
    best_formation[0], best_formation[-1] = best_formation[-1], best_formation[0]
    save_line_up = route.output_folder + '/optimise_my_team_' + filename + '.csv'

    formation_str = '-'.join(str(item) for item in best_formation)  # Convert formation to string
    players_list = best_lineup_df['Name'].tolist()  # List of player names

    # Combine formation and player names into one list
    combined_list = [formation_str] + players_list

    # Create a DataFrame with a single column
    final_save_df = pd.DataFrame(combined_list, columns=['Lineup'])
    final_save.append(best_lineup_df['Name'].tolist())
    final_save_df.to_csv(save_line_up, index=False, header=False)


def create_df_team_market_players():
    # Create new CSV with my team and market predictions joined.
    df_team_predictions_complete = merge_csv_by_id(route.personal_team_file,  route.players_predictions_mundo_deportivo)
    df_team_predictions = df_team_predictions_complete[['ID', 'Position', 'PredictedValue', 'GameWeek']]

    df_market_predictions_complete = merge_csv_by_id(route.market_file,  route.players_predictions_mundo_deportivo)
    df_market_predictions = df_market_predictions_complete[['ID', 'Position', 'PredictedValue', 'GameWeek']]

    df_market_team_players = pd.DataFrame(columns=df_team_predictions.columns)

    df_market_team_players = pd.concat([df_market_team_players, df_team_predictions], ignore_index=True)

    for index, row in df_market_predictions.iterrows():
        if row['ID'] not in df_market_team_players['ID'].values:
            df_market_team_players = pd.concat([df_market_team_players, pd.DataFrame([row])], ignore_index=True)

    df_market_team_players.fillna(0, inplace=True)
    df_market_team_players['ID'] = df_market_team_players['ID'].astype(int)

    return df_market_team_players


def best_lineup_market(fantasy_lineups):
    df_market_team_players = create_df_team_market_players()
    available_lineups = delete_impossible_formations(df_market_team_players, fantasy_lineups)

    best_lineup_df, best_formation = optimise_lineup_greedy(df_market_team_players, available_lineups)
    best_formation[0], best_formation[-1] = best_formation[-1], best_formation[0]

    best_line_up_path = route.output_folder + 'optimise_my_team_and_market-{}.csv'.format('-'.join(map(str, best_formation)))
    best_lineup_df.to_csv(best_line_up_path, index=False)

if __name__ == '__main__':
    fantasy_lineups = [[4, 4, 2], [4, 5, 1], [4, 3, 3], [3, 4, 3], [3, 5, 2], [5, 4, 1],
                       [5, 3, 2]]  # Free lineups in the Mundo deportivo Fantasy League.
    best_lineup_my_team(fantasy_lineups,route.players_predictions_mundo_deportivo,'mundo_deportivo')
    best_lineup_my_team(fantasy_lineups,route.players_predictions_sofascore,'sofascore')

    best_lineup_market(fantasy_lineups)


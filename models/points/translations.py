import pandas as pd

id_matching_table = pd.read_csv('ID_matching_table.csv')

def translate_id_to_sofascore(fantasy_game_id):
    match = id_matching_table[id_matching_table['Fantasy_Game_ID'] == fantasy_game_id]
    if not match.empty:
        return match.iloc[0]['Sofascore_ID']
    return None

def translate_id_to_fantasy(sofascore_id):
    match = id_matching_table[id_matching_table['Sofascore_ID'] == sofascore_id]
    if not match.empty:
        return match.iloc[0]['Fantasy_Game_ID']
    return None

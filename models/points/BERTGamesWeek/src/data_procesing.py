# data_processing.py

import pandas as pd
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()

def load_data(path):
    return pd.read_csv(path)

def preprocess_data(df):
    num_features = ['age', 'minutes_played', 'goals_scoreed', 'assists', 'clean_sheets', 'yellow_cards', 'red_cards', 'shots_per_game', 'key_passes_per_game', 'upcoming_fixture_difficulty']
    df[num_features] = scaler.fit_transform(df[num_features])
    return df

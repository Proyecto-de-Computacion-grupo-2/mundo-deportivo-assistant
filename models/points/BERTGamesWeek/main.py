from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from src.data_procesing import load_data, preprocess_data
from src.model_training import build_model, tokenizer
from src.model_evaluation import evaluate_model
from src.prediction import predict_fantasy_points
from pulp import LpMaximize, LpProblem, LpVariable, lpSum
import pandas as pd

NUM_FEATURES = 9  # This corresponds to the number of numerical features we're using.

# Function to convert dataframe for model input
def get_model_input(df, tokenizer):
    sentences = df['player_name'] + " " + df['team'] + " " + df['position']
    encoded = tokenizer(sentences.tolist(), padding='max_length', max_length=128, truncation=True, return_tensors='tf')
    return [encoded['input_ids'], encoded['attention_mask']]

# Load and preprocess data
data_path = './data/raw/sample_data.csv'
data = load_data(data_path)
data = preprocess_data(data)

# Split data into training and test sets
train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)

numerical_features = train_data[[
    "minutes_played",
    "goals_scoreed",
    "assists",
    "clean_sheets",
    "yellow_cards",
    "red_cards",
    "shots_per_game",
    "key_passes_per_game",
    "upcoming_fixture_difficulty"
]].values

numerical_features_test = test_data[[
    "minutes_played",
    "goals_scoreed",
    "assists",
    "clean_sheets",
    "yellow_cards",
    "red_cards",
    "shots_per_game",
    "key_passes_per_game",
    "upcoming_fixture_difficulty"
]].values

scaler = StandardScaler()
numerical_features = scaler.fit_transform(numerical_features)
numerical_features_test = scaler.transform(numerical_features_test)

X_train = [get_model_input(train_data, tokenizer), numerical_features]
X_test = [get_model_input(test_data, tokenizer), numerical_features_test]
y_train = train_data['upcoming_fixture_difficulty'].values
y_test = test_data['upcoming_fixture_difficulty'].values

# Build and train the model
model = build_model()
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.1)

# Evaluate the model
evaluate_model(model, X_test, y_test)

# Load current team and available players
current_team_data = load_data('./data/raw/current_team.csv')
available_players_data = load_data('./data/raw/available_players.csv')

budget = 300  # Budget in millions

if budget < sum(available_players_data.nsmallest(11, 'price')['price']):
    print("Insufficient budget to form a team.")
    exit()

# Obtain predictions
current_team_predictions = predict_fantasy_points(model, current_team_data, tokenizer, scaler, NUM_FEATURES)
available_players_predictions = predict_fantasy_points(model, available_players_data, tokenizer, scaler, NUM_FEATURES)

# Optimization
lp_model = LpProblem(name="fantasy-football", sense=LpMaximize)

# Create player variables for both current players and available players
all_players = pd.concat([current_team_data, available_players_data], ignore_index=True)
all_players_predictions = predict_fantasy_points(model, all_players, tokenizer, scaler, NUM_FEATURES)

player_vars = {player: LpVariable(name=str(player), cat="Binary") for player in all_players['player_name']}
for player in current_team_data['player_name']:
    player_vars[player].setInitialValue(1)  # Set the initial value to 1 (i.e., you already have them)
    player_vars[player].upBound = 1         # Ensure they cannot be "unpurchased"

# Objective
lp_model += lpSum(player_vars[player_name] * all_players_predictions[idx] for idx, player_name in enumerate(all_players['player_name'])), "Total_Predicted_Points"

# Budget Constraint
lp_model += lpSum(player_vars[row['player_name']] * row['price'] for idx, row in all_players.iterrows()) <= budget + sum(current_team_data['price']), "Budget"

# Ensure exactly 11 players are selected
lp_model += lpSum(player_vars[player] for player in player_vars) == 11, "Exactly_11_players"

# Solve and display results
lp_model.solve()
optimized_team = [i for i in all_players['player_name'] if player_vars[i].value() == 1]
buy_players = set(optimized_team) - set(current_team_data['player_name'])
sell_players = set(current_team_data['player_name']) - set(optimized_team)

print("Players to Buy:", buy_players)
print("Players to Sell:", sell_players)
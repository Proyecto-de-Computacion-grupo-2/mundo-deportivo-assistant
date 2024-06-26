# inferenceGW.py

import pandas as pd
import tensorflow as tf
from sklearn.metrics import mean_squared_error
from math import sqrt
import csv
from UA2C import helper as helper, routes as route

from sklearn.preprocessing import StandardScaler

from transformers import TFBertModel, BertTokenizer

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

num_features = [
    'Position', 'Game Week', 'Mixed', 'Average', 'Matches', 'Goals Metadata', 'Cards', 'Total Passes',
    'Accurate Passes', 'Total Long Balls', 'Accurate Long Balls', 'Total Crosses',
    'Accurate Crosses', 'Total clearances', 'Clearances on goal line', 'Aerial Duels Lost',
    'Aerial Duels Won', 'Duels Lost', 'Duels Won', 'Dribbled Past', 'Losses',
    'Total Dribbles', 'Completed dribbles', 'High clearances', 'Fist clearances',
    'Failures that lead to shot', 'Failures that lead to goal', 'Shots Off Target',
    'Shots on Target', 'Shots blocked in attack', 'Shots blocked in defence',
    'Occasions created', 'Goal assists', 'Shots to the crossbar', 'Failed obvious occasions',
    'Penalties commited', 'Penalties caused', 'Failed penalties', 'Stopped penalties',
    'Goals', 'Own goals', 'Stops from inside the area', 'Stops', 'Goals avoided',
    'Interceptions', 'Total outputs', 'Precise outputs', 'Total Tackles', 'Fouls Received',
    'Fouls Committed', 'Offsides', 'Minutes Played', 'Touches', 'Entries as last man',
    'Possessions Lost', 'Expected Goals', 'Key Passes', 'Expected Assists',
    'Average Season 15/16', 'Average Season 16/17', 'Average Season 17/18',
    'Average Season 18/19', 'Average Season 19/20', 'Average Season 20/21',
    'Average Season 21/22', 'Average Season 22/23', 'Average Season 23/24'
]


def preprocess_data(df):
    required_features = ['ID'] + num_features
    missing_features = [f for f in required_features if f not in df.columns]
    if missing_features:
        raise ValueError(f"Missing features in the dataframe: {missing_features}")

    df = df[required_features]
    return df


# Function to convert dataframe for model input (updated for new dataset)
def get_new_model_input(df, tokenizer, text_columns):
    text_columns = [col for col in text_columns if col != 'Mixed']
    # Convert specified columns to string type and concatenate them
    df_text = df[text_columns].astype(str).agg(' '.join, axis=1)

    # Tokenize the concatenated text
    encoded = tokenizer(df_text.tolist(), padding='max_length', max_length=128, truncation=True, return_tensors='tf')
    return [encoded['input_ids'], encoded['attention_mask']]


# Function to evaluate the model
def evaluate_model(model, test_features, true_values):
    # Generate predictions
    predictions = model.predict(test_features)
    # Calculate MSE and then RMSE
    mse = mean_squared_error(true_values, predictions)
    rmse = sqrt(mse)
    print(f"Model MSE: {mse}")
    print(f"Model RMSE: {rmse}")

    # Save real vs predicted values in a CSV file
    with open('model_predictions_comparison2.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Real Value', 'Predicted Value'])

        for real, predicted in zip(true_values, predictions):
            writer.writerow([real, predicted[0]])

    return rmse


def predict_dataset():
    # convert the current structure to pandas dataframes.
    players_information = helper.get_all_attributes_for_points_predicction()

    column_names = [
        "ID", "Player full name", "Position", "Game Week", "Team", "Opposing Team",
        "Mixed", "AS Score", "Marca Score", "Mundo Deportivo Score", "Sofa Score",
        "Current Value", "Points", "Average", "Matches", "Goals Metadata", "Cards",
        "Total Passes", "Accurate Passes", "Total Long Balls", "Accurate Long Balls",
        "Total Crosses", "Accurate Crosses", "Total clearances", "Clearances on goal line",
        "Aerial Duels Lost", "Aerial Duels Won", "Duels Lost", "Duels Won",
        "Dribbled Past", "Losses", "Total Dribbles", "Completed dribbles",
        "High clearances", "Fist clearances", "Failures that lead to shot",
        "Failures that lead to goal", "Shots Off Target", "Shots on Target",
        "Shots blocked in attack", "Shots blocked in defence", "Occasions created",
        "Goal assists", "Shots to the crossbar", "Failed obvious occasions",
        "Penalties commited", "Penalties caused", "Failed penalties", "Stopped penalties",
        "Goals", "Own goals", "Stops from inside the area", "Stops", "Goals avoided",
        "Interceptions", "Total outputs", "Precise outputs", "Total Tackles",
        "Fouls Received", "Fouls Committed", "Offsides", "Minutes Played", "Touches",
        "Entries as last man", "Possessions Lost", "Expected Goals", "Key Passes",
        "Expected Assists", "Average Season 15/16", "Average Season 16/17",
        "Average Season 17/18", "Average Season 18/19", "Average Season 19/20",
        "Average Season 20/21", "Average Season 21/22", "Average Season 22/23",
        "Average Season 23/24", "Timestamp"
    ]

    df_players_information_database = pd.DataFrame(players_information, columns=column_names)

    original_df = df_players_information_database.copy()
    df = preprocess_data(df_players_information_database)

    print("unmodified")
    print(len(df))

    maxgame = df['Game Week'].max()
    print(maxgame)

    # get the numbers of rows for the last game week only
    print("last game week")
    print(len(df[df['Game Week'] == maxgame]))

    # Sort the dataframe by 'Game Week' in descending order
    df = df.sort_values('Game Week', ascending=False)
    original_df = original_df.sort_values('Game Week', ascending=False)

    # Drop duplicates based on 'ID', but keep the first occurrence (which is the latest game week data)
    df = df.drop_duplicates(subset=['ID'], keep='first')
    original_df = original_df.drop_duplicates(subset=['ID'], keep='first')

    selected_features = num_features
    numerical_features = original_df[selected_features].values

    print(numerical_features)
    print("original size")
    print(len(original_df))

    # Scaling features
    scaler = StandardScaler()
    numerical_features = scaler.fit_transform(numerical_features)

    print(numerical_features)

    model_input = [get_new_model_input(original_df, tokenizer, num_features), numerical_features]
    print("Data loaded and preprocessed successfully!")

    print(model_input)

    print("Loading model...")
    # Load the TensorFlow SavedModel
    model = tf.keras.models.load_model(
        'models/best_model.h5',
        custom_objects={'TFBertModel': TFBertModel}
    )
    print("Model loaded successfully!")

    # Extract 'Mixed' column and drop it from features
    true_values = df.pop('Mixed').values
    true_values = true_values.astype('int')
    print("True values extracted successfully!")

    # Evaluate the model
    predictions = model.predict(model_input).flatten()  # Flatten if predictions are in a multi-dimensional array

    # round predictions
    predictions = [round(x) for x in predictions]

    # make negative predictions positive
    predictions = [abs(x) for x in predictions]

    # print all sizes
    print(len(predictions))
    print(len(original_df['ID']))
    print(len(original_df['Position']))

    # Create a DataFrame with the predictions
    results_df = pd.DataFrame({
        'ID': original_df['ID'],
        'Position': original_df['Position'],
        'PredictedValue': predictions
    })

    print(results_df)
    helper.database_insert_prediction(original_df['ID'], int(maxgame) + 1, predictions)
    return results_df


if __name__ == "__main__":
    results_df = predict_dataset()

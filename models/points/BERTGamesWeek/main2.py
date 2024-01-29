import os
from datetime import datetime

import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from src.data_procesing import load_data
from src.model_evaluation import evaluate_model
from src.model_training import build_model, tokenizer

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
    missing_features = [f for f in num_features if f not in df.columns]
    if missing_features:
        raise ValueError(f"Missing features in the dataframe: {missing_features}")

    df = df[num_features]


    return df


# Function to convert dataframe for model input (updated for new dataset)
def get_new_model_input(df, tokenizer, text_columns):
    text_columns = [col for col in text_columns if col != 'Mixed']
    # Convert specified columns to string type and concatenate them
    df_text = df[text_columns].astype(str).agg(' '.join, axis=1)

    # Tokenize the concatenated text
    encoded = tokenizer(df_text.tolist(), padding='max_length', max_length=128, truncation=True, return_tensors='tf')
    return [encoded['input_ids'], encoded['attention_mask']]

# Load and preprocess new data (updated for new dataset)
data_path = '/Users/jorge/Downloads/fantasy-games-week-players-stats.csv'
data = load_data(data_path)

with open(data_path, 'r', encoding="utf-8-sig") as f:
    column_names = f.readline().strip().split(',')
    f.close()


data = preprocess_data(data)


# Split data into training and test sets (updated feature selection)
# Assuming 'Mixed' is a target feature
train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)


# Selecting new numerical features for the model
selected_features = num_features
numerical_features = train_data[selected_features].values
numerical_features_test = test_data[selected_features].values

# Scaling features
scaler = StandardScaler()
numerical_features = scaler.fit_transform(numerical_features)
numerical_features_test = scaler.transform(numerical_features_test)

X_train = [get_new_model_input(train_data, tokenizer, num_features), numerical_features]
X_test = [get_new_model_input(test_data, tokenizer, num_features), numerical_features_test]
y_train = train_data.pop('Mixed').values
y_test = test_data.pop('Mixed').values

y_train = y_train.astype('int')
y_test = y_test.astype('int')

# Build and train the model
model, model_info, model_callbacks = build_model(len(selected_features))


history = model.fit(
    X_train, y_train,
    epochs=8,
    batch_size=32,
    validation_split=0.1,
    verbose=1,
    shuffle=True,
    callbacks=model_callbacks  # Use the callbacks here
)


# Evaluate the model
model.summary()
rmse = evaluate_model(model, X_test, y_test)
print(f"RMSE: {rmse}")



# Plotting training and validation loss
plt.figure(figsize=(8, 6))
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss Over Epochs')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend()
plt.show()


current_date = datetime.now()

# Generate the filename using the specified format
date_str = current_date.strftime("%m%d")
base_model_filename = f"GamesWeekTFDL{date_str}"
extension = ".h5"

# Create the directory if it doesn't exist
os.makedirs("models", exist_ok=True)

# Check if the file exists and update the filename
i = 0
model_filename = base_model_filename + extension
while os.path.exists(os.path.join("models", model_filename)):
    i += 1
    model_filename = f"{base_model_filename}-{i}{extension}"

# Save the model
model.save(os.path.join("models", model_filename))

# Print the path where the model is saved
print(f"Model saved as: {os.path.join('models', model_filename)}")


filename = f"model_data_{date_str}.txt"

# Write model details to a text file
with open(os.path.join("models", filename), 'w') as f:
    f.write(f"Model name: {filename}\n")
    f.write(f"RMSE: {rmse}\n")
    print(f"Model name: {filename}")
    print(f"RMSE: {rmse}")
    for key, value in model_info.items():
        line = f"{key}: {value}\n"
        f.write(line)
        print(line, end='')  # Print each line


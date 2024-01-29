# prediction.py

def predict_fantasy_points(model, new_data, tokenizer, scaler, NUM_FEATURES):
    sentences = new_data['player_name'] + " " + new_data['team'] + " " + new_data['position']
    encoded = tokenizer(sentences.tolist(), padding='max_length', max_length=128, truncation=True, return_tensors='tf')

    numerical_features = new_data[[
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
    numerical_features = scaler.transform(numerical_features)

    # Extract input tensors from the 'encoded' dictionary
    input_ids = encoded['input_ids']
    attention_mask = encoded['attention_mask']

    return model.predict([input_ids, attention_mask, numerical_features])



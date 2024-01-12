# model_evaluation.py

import os
from datetime import datetime
import csv
from sklearn.metrics import mean_squared_error
from math import sqrt

def evaluate_model(model, test_data, true_values):
    # Generate predictions
    predictions = model.predict(test_data)

    # Calculate MSE and then RMSE
    mse = mean_squared_error(true_values, predictions)
    rmse = sqrt(mse)
    print(f"Model MSE: {mse}")
    print(f"Model RMSE: {rmse}")
    return rmse

"""
    # Generate the filename using the current date
    current_date = datetime.now()
    date_str = current_date.strftime("%m%d")
    base_filename = f"model_predictions_comparison_{date_str}"
    extension = ".csv"

    # Check if the file exists and update the filename
    i = 0
    filename = base_filename + extension
    while os.path.exists(filename):
        i += 1
        filename = f"{base_filename}-{i}{extension}"

    # Save real vs predicted values in a CSV file
    with open(os.path.join("models", filename), mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Real Value', 'Predicted Value'])

        for real, predicted in zip(true_values, predictions):
            writer.writerow([real, predicted])
"""

# Note: Ensure you have the necessary data and model to run this function.

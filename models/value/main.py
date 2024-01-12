import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
import itertools
import time
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
import warnings
from collections import Counter
import numpy as np

warnings.filterwarnings("ignore")


def save_prediction(player_id, date, value):
    # Create a DataFrame from the provided data
    df = pd.DataFrame({
        'ID': [player_id],
        'Date': [date],
        'PredictedValue': [int(value)]
    })

    # Define the file name
    prediction_csv = "auxiliary/fantasy_market_value_prediction_unsorted.csv"

    # Check if the file exists to decide whether to write header
    file_exists = os.path.exists(prediction_csv)

    # Save the DataFrame to a CSV file in append mode
    df.to_csv(prediction_csv, mode='a', index=False, header=not file_exists)

    print(f"Predictions appended to {prediction_csv}")

def sort_prediction_by_id(prediction_file):
    df = pd.read_csv(f"{prediction_file}")

    # Sort the DataFrame by the 'ID' column
    df_sorted = df.sort_values(by='ID')

    # Optionally, reset the index if you want a new sequential index after sorting
    df_sorted = df_sorted.reset_index(drop=True)

    # If you want to save the sorted DataFrame to a new file
    df_sorted.to_csv('predictions/fantasy_market_value_prediction_sorted.csv', index=False)


def evaluate_arima_model(data, arima_order):
    try:
        model = ARIMA(data, order=arima_order)
        model_fit = model.fit()
        error = mean_squared_error(data, model_fit.fittedvalues)
        return (arima_order, error)
    except Exception as e:
        print(f"Error in model evaluation for order {arima_order}: {e}")
        return (arima_order, float("inf"))


def plot_arima_predictions(data, order, player_id, forecast_days):
    try:
        model = ARIMA(data, order=order)
        model_fit = model.fit()

        # In-sample prediction
        in_sample_pred = model_fit.predict(start=data.index[0], end=data.index[-1])

        # Out-of-sample forecast
        forecast = model_fit.get_forecast(steps=forecast_days)
        forecast_index = pd.date_range(start=data.index[-1], periods=forecast_days + 1, freq=data.index.freq)[1:]
        forecast_values = forecast.predicted_mean

        # Plot actual data, in-sample predictions, and out-of-sample forecast
        plt.figure(figsize=(12, 6))
        #plt.plot(data, label='Actual Data', color='blue')
        #plt.plot(in_sample_pred, label='In-sample Prediction', alpha=0.7, color='green')
        plt.plot(forecast_index, forecast_values, label=f'{forecast_days}-day Forecast', alpha=0.7, color='orange')
        plt.title(f'ARIMA Model Validation and {forecast_days}-day Forecast for {player_id}')
        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.legend()
        plt.savefig(f'predictions/plots/{player_id}_market_value_prediction_plot.png')
        plt.close()
        print(f"Plot saved for {player_id}")

        # Print the forecast values
        print(f"\n{forecast_days}-day Forecast for {player_id}:")
        for date, value in zip(forecast_index, forecast_values):
            print(f"{date.date()}: {value}")
            # Save players prediction to CSV file.
            save_prediction(player_id, date, value)

    except Exception as e:
        print(f"Error in plotting for {player_id}: {e}")


def arima_grid_search(data, p_values, d_values, q_values, player_id):
    # Initialize the best score to infinity and the best ARIMA order to None
    best_score, best_order = float("inf"), None

    # Iterate over all combinations of p, d, q values
    for order in itertools.product(p_values, d_values, q_values):
        # Evaluate the ARIMA model for the current combination of parameters
        # The function 'evaluate_arima_model' returns an error score for the model
        _, error = evaluate_arima_model(data, order)

        # If the current model's error is lower than the best score found so far,
        # update the best score and the best model order
        if error < best_score:
            best_score, best_order = error, order

        # Print the progress: player ID, current ARIMA order being evaluated, and the current best order
        # 'end='\r'' makes sure the output is overwritten each time, showing only the latest status
        print(f"Processing {player_id}, ARIMA order: {order}, Current Best: {best_order}", end='\r')

    # Once the best ARIMA parameters are found, plot the predictions
    # The function 'plot_arima_predictions' plots the actual data, in-sample prediction,
    # and out-of-sample forecast using the best ARIMA model
    plot_arima_predictions(data, best_order, player_id, 7)

    # Return the best ARIMA model order found for the data
    return best_order


def process_batch(batch_id, players_id, df, p_values, d_values, q_values):
    # Initialize a dictionary to store results for each player
    results = {}

    # Print a message indicating the start of processing for this batch
    print(f"\nStarting batch {batch_id} processing with {len(players_id)} players.")

    # Iterate over each player ID in the batch
    for player in players_id:
        # Print a message indicating the start of ARIMA grid search for the current player
        print(f"\nStarting ARIMA grid search for {player}...")

        # Extract the data related to the current player from the DataFrame
        # 'ID' is assumed to be a column in 'df' that contains player IDs
        # 'Value' is assumed to be the column containing the data to be analyzed
        player_data = df[df['ID'] == player]['Value']

        # Check if the player has enough data points for analysis
        # In this case, 30 data points are required for a valid analysis
        if len(player_data) < 30:
            # Print a message and skip this player if the data is insufficient
            print(f"Skipping {player} due to insufficient data.")
            continue

        # Perform the ARIMA grid search for the current player's data
        # 'arima_grid_search' is a function that finds the best ARIMA model parameters
        # It takes the player's data and the specified ranges of ARIMA parameters (p, d, q)
        best_order = arima_grid_search(player_data, p_values, d_values, q_values, player)

        # Store the best ARIMA model parameters found for this player in the results dictionary
        results[player] = best_order

        # Print a completion message for the current player with the best ARIMA order
        print(f"\nCompleted ARIMA grid search for {player}. Best order: {best_order}")

    # Print a completion message for the entire batch
    print(f"Completed processing batch {batch_id}.")

    # Return the dictionary of results containing the best ARIMA orders for each player
    return results

if __name__ == '__main__':
    # Read CSV with Pandas and import it.
    df = pd.read_csv('../../scrape/data/players/fantasy-market-variation.csv')

    # Prepare the data frame.
    # Convert column into a datetime format.
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)

    # Set the column 'Date' as an index.
    # By setting the 'Date' column as the index, each row can be efficiently accessed or referenced by its date.
    df.set_index('Date', inplace=True)

    # Extracts all the unique values from the 'ID' column of df and assigns them to the variable players
    players_id = df['ID'].unique()

    # Extracts all the unique values from the 'name' column of df and assigns them to the variable players
    players_name = df['Name'].unique()

    # Define ML hyper parameters for ARIMA model to use.
    p_values = range(0, 3)
    d_values = range(0, 2)
    q_values = range(0, 3)

    # ------ Parallel processing -------

    # Define parallel programming.
    num_cores = os.cpu_count() - 2

    # Calculate batch size for parallel processing
    batch_size = int(np.ceil(len(players_id) / num_cores))

    # Create batches of players
    player_batches = []
    for start in range(0, len(players_id), batch_size):
        end = start + batch_size
        player_batches.append(players_id[start:end])

    for pb in player_batches:
        print(pb)

    all_params = []
    player_best_params = {}

    print(f"Number of cores available: {num_cores}")
    print("Starting parallel ARIMA grid search across batches...")
    start_time = time.time()

    try:
        # Start with Parallel processing with the Process Pool Executor.
        with ProcessPoolExecutor(max_workers=num_cores) as executor:
            # Submit the process_batch function to the executor for parallel execution.
            futures = {}
            for batch_id, players_batch in enumerate(player_batches):
                # Call the process_batch function with all it parameters.
                future = executor.submit(process_batch, batch_id, players_batch, df, p_values, d_values, q_values)
                futures[future] = batch_id

            for future in as_completed(futures):
                batch_id = futures[future]
                batch_results = future.result()
                player_best_params.update(batch_results)
                all_params.extend(batch_results.values())
                print(
                    f"\nCompleted processing for batch {batch_id}. Total progress: {len(player_best_params)}/{len(players_id)} players.")
    except Exception as e:
        print(f"Error in parallel processing: {e}")
        print("Reverting to sequential processing...")
        for i, batch in enumerate(player_batches):
            results = process_batch(i, batch, df, p_values, d_values, q_values)
            player_best_params.update(results)
            all_params.extend(results.values())

    elapsed_time = time.time() - start_time
    print(f"\nCompleted ARIMA grid search for all players in {elapsed_time:.2f} seconds.")

    for player, params in player_best_params.items():
        print(f"{player}: {params}")

    most_common_params = Counter(all_params).most_common(1)[0][0]
    print("\nMost Common ARIMA Parameters (Generic Model) for All Players:")
    print(f"P: {most_common_params[0]}, D: {most_common_params[1]}, Q: {most_common_params[2]}")

    # Sort predictions CSV by ID.
    sort_prediction_by_id('auxiliary/fantasy_market_value_prediction_unsorted.csv')
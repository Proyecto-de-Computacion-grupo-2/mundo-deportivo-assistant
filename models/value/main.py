import itertools
import platform
import time
import warnings
import os

import numpy as np
import pandas as pd

from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
import helper as helper
import routes as route

warnings.filterwarnings("ignore")


class Base:
    def to_insert_statement(self, table_name):
        columns = []
        values = []

        for attr_name, attr_value in self.__dict__.items():
            columns.append(attr_name)
            if isinstance(attr_value, str):
                values.append(f'"{attr_value}"')
            else:
                values.append(str(attr_value))

        insert_statement = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});"
        return insert_statement


class PriceVariations:
    def __init__(self):
        self.price_variations = []

    def __getitem__(self, index):
        return self.price_variations[index]

    class PriceVariation(Base):
        def __init__(self, id_mundo_deportivo: int, price_day: helper.datetime, price: int, is_prediction = True):
            self.id_mundo_deportivo = id_mundo_deportivo
            self.price_day = price_day
            self.price = price
            self.is_prediction = is_prediction

        def to_insert_statements(self):
            return self.to_insert_statement("price_variation")

    def add_price_variation(self, id_mundo_deportivo: int, price: int, price_day: helper.datetime,
                            is_prediction = True):
        price_variation = self.PriceVariation(id_mundo_deportivo, price, price_day, is_prediction)
        self.price_variations.append(price_variation)

    def to_insert_statements(self):
        insert_statements = []
        for price_variation in self.price_variations:
            insert_statements.extend([price_variation.to_insert_statements()])
        return insert_statements

def insert_prediction_database(file_path):
    try:
        connection = helper.mysql.connector.connect()
        cursor = connection.cursor()

        with open(file_path, mode='r', encoding='utf-8') as f:
            sql_file = f.read()

        sql_commands = sql_file.split(';')

        for command in sql_commands:
            if command.strip():
                cursor.execute(command)

        connection.commit()

    except helper.mysql.connector.Error as error:
        print("Failed to execute commands from file", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def evaluate_arima_model(data, arima_order):
    try:
        model = ARIMA(data, order=arima_order)
        model_fit = model.fit()
        error = mean_squared_error(data, model_fit.fittedvalues)
        return arima_order, error
    except Exception as err:
        print(f"Error in model evaluation for order {arima_order}: {err}")
        return arima_order, float("inf")

def plot_arima_predictions(data, order, player_id, forecast_days, pv: PriceVariations):
    try:
        model = ARIMA(data, order=order)
        model_fit = model.fit()

        # Out-of-sample forecast
        forecast = model_fit.get_forecast(steps = forecast_days)
        forecast_index = pd.date_range(start = data.index[-1], periods = forecast_days + 1, freq = data.index.freq)[1:]
        forecast_values = forecast.predicted_mean

        print(f"\n{forecast_days}-day Forecast for {player_id}:")
        for date, value in zip(forecast_index, forecast_values):
            print(forecast_values)
            pv.add_price_variation(player_id, date.strftime('%Y/%m/%d'), int(value))

    except Exception as err:
        print(f"Error in plotting for {player_id}: {err}")


def arima_grid_search(data, p_values_1, d_values_1, q_values_1, player_id, price_v: PriceVariations):
    best_score, best_order = float("inf"), None

    for order in itertools.product(p_values_1, d_values_1, q_values_1):
        _, error = evaluate_arima_model(data, order)

        if error < best_score:
            best_score, best_order = error, order

        #print(f"Processing {player_id}, ARIMA order: {order}, Current Best: {best_order}", end = "\r")

    plot_arima_predictions(data, best_order, player_id, 7, price_v)

    return best_order

def process_batch(batch_id_1, players_id_1, df_1, p_values_1, d_values_1, q_values_1, p_var: PriceVariations):
    results_1 = {}

    print(f"\nStarting batch {batch_id_1} processing with {len(players_id_1)} players.")

    # Iterate over each player ID in the batch
    for player_1 in players_id_1:
        player_data = df_1[df_1['ID'] == player_1]['Value']

        if len(player_data) < 30:
            continue

        best_order = arima_grid_search(player_data, p_values_1, d_values_1, q_values_1, player_1, p_var)

        results_1[player_1] = best_order

    print(f"Completed processing batch {batch_id_1}.")

    return results_1


if __name__ == "__main__":

    mariadb = helper.create_database_connection()
    cursor = mariadb.cursor()
    try:
        sql = "SELECT * FROM price_variation"
        cursor.execute(sql)

        prices_columns = cursor.column_names
        prices = cursor.fetchall()

    finally:
        if mariadb.is_connected():
            cursor.close()
            mariadb.close()
    # Read CSV with Pandas and import it.
    df = pd.DataFrame(prices, columns = prices_columns)
    df = df.drop(["id_price_variation", "is_prediction"], axis = 1)

    # Rename the columns
    df.rename(columns={
        'id_mundo_deportivo': 'ID',
        'price_day': 'Date',
        'price': 'Value'
    }, inplace=True)

    # Prepare the data frame.
    # Convert column into a datetime format.
    df["Date"] = pd.to_datetime(df["Date"], dayfirst = True)

    # Convert 'Value' column to numeric, setting non-numeric values to NaN
    df["Value"] = pd.to_numeric(df["Value"], errors = "coerce")
    df['Value'] = df['Value'].astype(int)

    # Drop rows where "Value" is NaN
    df = df.dropna(subset = ["Value"])

    # Set the column 'Date' as an index.
    # By setting the 'Date' column as the index, each row can be efficiently accessed or referenced by its date.
    df.set_index("Date", inplace = True)

    # Extracts all the unique values from the 'ID' column of df and assigns them to the variable players
    players_id = df["ID"].unique()

    price_variations_list = PriceVariations()

    # Define ML hyper parameters for ARIMA model to use.
    p_values = range(0, 3)
    d_values = range(0, 2)
    q_values = range(0, 3)

    # ------ Parallel processing -------

    # Define parallel programming.
    system = platform.system()

    if system == "Linux":
        print("Running on Linux")
        num_cores = 1
    else:
        print("Running on Mac")
        num_cores = os.cpu_count() - 1

    batch_size = int(np.ceil(len(players_id) / num_cores))

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
        with ProcessPoolExecutor(max_workers = num_cores) as executor:
            futures = {}
            for batch_id, players_batch in enumerate(player_batches):
                future = executor.submit(process_batch, batch_id, players_batch, df, p_values, d_values, q_values)
                futures[future] = batch_id

            for future in as_completed(futures):
                batch_id = futures[future]
                batch_results = future.result()
                player_best_params.update(batch_results)
                all_params.extend(batch_results.values())
                print(
                    f"\nCompleted processing for batch {batch_id}. Total progress: "
                    f"{len(player_best_params)}/{len(players_id)} players.")
    except Exception as e:
        print(f"Error in parallel processing: {e}")
        print("Reverting to sequential processing...")
        for i, batch in enumerate(player_batches):
            results = process_batch(i, batch, df, p_values, d_values, q_values, price_variations_list)
            player_best_params.update(results)
            all_params.extend(results.values())

    if helper.path.exists("prediction_inserts.sql"):
        helper.remove("prediction_inserts.sql")
    with open("prediction_inserts.sql", mode = "w", newline = "", encoding = "utf-8") as f:
        for row in price_variations_list.to_insert_statements():
            f.write(row + "\n")
    elapsed_time = time.time() - start_time
    print(f"\nCompleted ARIMA grid search for all players in {elapsed_time:.2f} seconds.")

    for player, params in player_best_params.items():
        print(f"{player}: {params}")

    most_common_params = Counter(all_params).most_common(1)[0][0]
    print("\nMost Common ARIMA Parameters (Generic Model) for All Players:")
    print(f"P: {most_common_params[0]}, D: {most_common_params[1]}, Q: {most_common_params[2]}")

    insert_prediction_database("prediction_inserts.sql")



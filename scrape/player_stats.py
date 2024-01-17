# !/usr/bin/env python3

# -*- coding: utf-8 -*-
# player_stats.py

#

import Utils.helper as helper
import Utils.routes as route

# Gameweek headers.
players_meta_data_header = ["ID", "Player full name", "Position", "Current Value", "Points", "Average", "Matches",
                            "Goals", "Cards", "Time Stamp"]
spanish_map_list = ["id", "player full name", "posición", "game week", "equipo", "contrincante", "mixto", "as score",
                    "marca score", "mundo deportivo score", "sofa score", "valor actual", "puntos", "media", "partidos",
                    "goles metadata", "tarjetas", "pases totales", "pases precisos", "balones en largo totales",
                    "balones en largo precisos", "centros totales", "centros precisos", "despejes totales",
                    "despejes en la línea de gol", "duelos aéreos perdidos", "duelos aéreos ganados", "duelos perdidos",
                    "duelos ganados", "regateado", "pérdidas", "regates totales", "regates completados",
                    "despejes por alto", "despejes con los puños", "errores que llevan a disparo",
                    "errores que llevan a gol", "tiros fuera", "tiros a puerta", "tiros bloqueados en ataque",
                    "tiros bloqueados en defensa", "ocasiones creadas", "asistencias de gol", "tiros al palo",
                    "ocasiones claras falladas", "penaltis cometidos", "penaltis provocados", "penaltis fallados",
                    "penaltis parados", "goles", "goles en propia puerta", "paradas desde dentro del área", "paradas",
                    "goles evitados", "intercepciones", "salidas totales", "salidas precisas", "entradas totales",
                    "faltas recibidas", "faltas cometidas", "fueras de juego", "minutos jugados", "toques",
                    "entradas como último hombre", "posesiones perdidas", "goles esperados", "pases clave",
                    "match_stat_expectedassists", "15/16", "16/17", "17/18", "18/19", "19/20", "20/21", "21/22",
                    "22/23", "23/24"]
spanish_checklist = ["pases totales", "pases precisos", "balones en largo totales", "balones en largo precisos",
                     "centros totales", "centros precisos", "despejes totales", "despejes en la línea de gol",
                     "duelos aéreos perdidos", "duelos aéreos ganados", "duelos perdidos", "duelos ganados",
                     "regateado", "pérdidas", "regates totales", "regates completados", "despejes por alto",
                     "despejes con los puños", "errores que llevan a disparo", "errores que llevan a gol",
                     "tiros fuera", "tiros a puerta", "tiros bloqueados en ataque", "tiros bloqueados en defensa",
                     "ocasiones creadas", "asistencias de gol", "tiros al palo", "ocasiones claras falladas",
                     "penaltis cometidos", "penaltis provocados", "penaltis fallados", "penaltis parados", "goles",
                     "goles en propia puerta", "paradas desde dentro del área", "paradas", "goles evitados",
                     "intercepciones", "salidas totales", "salidas precisas", "entradas totales", "faltas recibidas",
                     "faltas cometidas", "fueras de juego", "minutos jugados", "toques", "entradas como último hombre",
                     "posesiones perdidas", "goles esperados", "pases clave", "match_stat_expectedassists"]
english_list = ["ID", "Player full name", "Position", "Game Week", "Team", "Opposing Team", "Mixed", "AS Score",
                "Marca Score", "Mundo Deportivo Score", "Sofa Score", "Current Value", "Points", "Average", "Matches",
                "Goals Metadata", "Cards", "Total Passes", "Accurate Passes", "Total Long Balls", "Accurate Long Balls",
                "Total Crosses", "Accurate Crosses", "Total clearances", "Clearances on goal line", "Aerial Duels Lost",
                "Aerial Duels Won", "Duels Lost", "Duels Won", "Dribbled Past", "Losses", "Total Dribbles",
                "Completed dribbles", "High clearances", "Fist clearances", "Failures that lead to shot",
                "Failures that lead to goal", "Shots Off Target", "Shots on Target", "Shots blocked in attack",
                "Shots blocked in defence", "Occasions created", "Goal assists", "Shots to the crossbar",
                "Failed obvious occasions", "Penalties commited", "Penalties caused", "Failed penalties",
                "Stopped penalties", "Goals", "Own goals", "Stops from inside the area", "Stops", "Goals avoided",
                "Interceptions", "Total outputs", "Precise outputs", "Total Tackles", "Fouls Received",
                "Fouls Committed", "Offsides", "Minutes Played", "Touches", "Entries as last man", "Possessions Lost",
                "Expected Goals", "Key Passes", "Expected Assists", "Average Season 15/16", "Average Season 16/17",
                "Average Season 17/18", "Average Season 18/19", "Average Season 19/20", "Average Season 20/21",
                "Average Season 21/22", "Average Season 22/23", "Average Season 23/24", "Timestamp"]


# So it didn't show any warning of variable may be undefined.
logger = "Defined"

# For debugging, this sets up a formatting for a logfile, and where it is.
try:
    if not helper.path.exists(route.player_log):
        helper.logging.basicConfig(filename = route.player_log, level = helper.logging.ERROR,
                                   format = "%(asctime)s %(levelname)s %(name)s %(message)s")
        logger = helper.logging.getLogger(__name__)
    else:
        helper.logging.basicConfig(filename = route.player_log, level = helper.logging.ERROR,
                                   format = "%(asctime)s %(levelname)s %(name)s %(message)s")
        logger = helper.logging.getLogger(__name__)
except Exception as error:
    logger.exception(error)


def scrape_fantasy_players_meta_data(driver, u):
    # Get all the information to call the CSV according to the player name and surname.
    players_info = driver.find_element(helper.By.XPATH, '//*[@id="content"]/div[5]/div[1]/div/div[1]')
    position = players_info.find_element(
        helper.By.XPATH, '//*[@id="content"]/div[5]/div[1]/div/div[1]/div[1]/i').get_attribute("class").split(" ")[0]
    if position == "pos-1":
        position = "0"
    elif position == "pos-2":
        position = "1"
    elif position == "pos-3":
        position = "2"
    elif position == "pos-4":
        position = "3"
    players_name = players_info.find_element(helper.By.CLASS_NAME, "name").text
    players_surname = players_info.find_element(helper.By.CLASS_NAME, "surname").text
    player_complete_name = players_name + players_surname
    player_image = driver.find_element(helper.By.CSS_SELECTOR, ".player-pic img").get_attribute("src").split("?version")
    response = helper.requests.get(player_image[0])
    data_id = u.split("/")[-2]
    img_file = helper.path.join(route.image_folder, data_id + "_" + player_complete_name + ".png")
    helper.makedirs(helper.path.dirname(img_file), exist_ok = True)
    with open(img_file, "wb") as img:
        img.write(response.content)

    # Get all the player's metadata.
    player_wrapper = driver.find_elements(helper.By.CSS_SELECTOR, "div.player-stats-wrapper div.value")

    valor_actual = player_wrapper[0].text
    puntos = player_wrapper[1].text
    media = player_wrapper[2].text.replace(",", ".")
    partidos = player_wrapper[3].text
    goles = player_wrapper[4].text
    tarjetas = player_wrapper[5].text
    time_stamp = str(helper.datetime.now())

    return [data_id, player_complete_name, position, valor_actual, puntos, media, partidos, goles, tarjetas,
            time_stamp], position, player_complete_name


def scrape_fantasy_players_value_table(driver, player_complete_name, data_id):
    def extract_date(extract):
        meses = {"ene": "jan", "abr": "apr", "ago": "aug", "sept": "sep", "dic": "dec"}
        parts = extract["date"].split()
        parts[0] = parts[0].zfill(2)
        parts[1] = meses.get(parts[1].lower(), parts[1])
        return " ".join(parts)

    helper.sleep(helper.uniform(0.4, 0.6))
    content = driver.find_element(helper.By.CLASS_NAME, "sw-content")
    script_element = content.find_elements(helper.By.TAG_NAME, "script")
    script_content = script_element.get_attribute("text")
    try:
        value_content = script_content.split("playerVideoOffset")[0].split(";")[1].strip()
    except IndexError as err:
        value_content = None
        logger.exception(player_complete_name, err)

    helper.sleep(helper.uniform(0.4, 0.6))
    # Transform the "Valor" table into a JSON so that it can be later store into a CSV.
    if value_content:
        try:
            json_str = value_content[value_content.index("(") + 1:-1]
            data = helper.json.loads(json_str)
            points = data["points"]
        except ValueError as err:
            points = None
            logger.exception(player_complete_name, err)

        helper.sleep(helper.uniform(0.4, 0.6))

        corrected = extract_date(points[-1])
        date_today = helper.datetime.strptime(corrected, "%d %b %Y").strftime("%m/%d/%Y")
        date_year = (helper.datetime.strptime(corrected, "%d %b %Y") - helper.timedelta(days = 365)).strftime(
            "%m/%d/%Y")
        date_range = helper.pandas.date_range(start = date_year, end = date_today, freq = "D")
        dates = ["ID", "Name"] + date_range.strftime("%d/%m/%Y").to_list()
        values = ["0"] * len(dates)
        values[0] = data_id
        values[1] = player_complete_name
        for point in points:
            date_to_find = helper.datetime.strptime(extract_date(point), "%d %b %Y").strftime("%d/%m/%Y")
            for date in dates:
                if date == date_to_find:
                    values[dates.index(date)] = point["value"]
                    break

        return dates, values


def process_row(fila):
    mapping = dict(zip(spanish_map_list, english_list))

    datos_procesados = ["0"] * (len(english_list))

    aplicar_mapeo, i = False, 0
    for valor in fila:
        if " ".join(str(valor).split(" ")[:-1]).lower() in spanish_checklist and not \
                all(ext in str(valor) for ext in ["2023", ":"]):
            aplicar_mapeo = True
        elif all(ext in str(valor) for ext in ["2023", ":"]):
            datos_procesados[int(english_list.index("Timestamp"))] = str(valor)
        if " ".join(str(valor).split(" ")[:-1]).lower() == "valoración" or \
                str(valor).lower() == "nan" or all(ext in str(valor) for ext in ["2023", ":"]):
            yeet = True
        else:
            yeet = False

        if not yeet:
            if aplicar_mapeo:
                columna = " ".join(str(valor).split(" ")[:-1]).lower()
                column = mapping.get(columna.lower(), columna)
                if str(valor).split(" ")[-1] == "0.1":
                    pass
                if column in english_list:
                    datos_procesados[int(english_list.index(column))] = str(valor).split(" ")[-1]
                else:
                    print(columna)
                    print(column)
            else:
                datos_procesados[i] = str(valor)
                i += 1

    return datos_procesados


def scrape_fantasy_players_game_week(driver, player_complete_name, position, value, points, average, matches, goals,
                                     cards, data_id, player_url):
    first_box = driver.find_element(helper.By.CLASS_NAME, "boxes-2")
    second_box = first_box.find_elements(helper.By.CLASS_NAME, "box-records")[1]

    pattern = r"(\d{2}/\d{2}.*?)\n(\d+,\d+)"
    averages = helper.re.findall(pattern, second_box.text)

    # Crea las sublistas deseadas
    processed_average = [[match[0], match[1].replace(",", ".")] for match in averages]
    temporal_averages = []
    for result in processed_average:
        temporal_averages.append(" ".join(result))

    # Find the points box.
    players_game_weeks = driver.find_elements(helper.By.CLASS_NAME, "btn-player-gw")

    # Go through each game week
    temp_list = []
    for player_game_week in players_game_weeks:
        # Define an array where all the information will be stored in order to save everything into the CSV
        # later, first element is the full name of the player.
        player_game_week_data = [data_id, player_complete_name, position]

        # Get the data of which game week has the statics happened.
        game_week = player_game_week.find_element(helper.By.CLASS_NAME, "gw")

        played = True
        player_gw = None
        try:
            player_gw = player_game_week.find_element(helper.By.CLASS_NAME, "score")
        except helper.NoSuchElementException:
            played = False
            pass
        helper.sleep(helper.uniform(0.2, 0.4))
        if played and player_gw.text.isdigit():
            intercept = True
            while intercept:
                try:
                    gw_button = helper.wait_click(driver, player_gw, 6)
                    gw_button.click()
                    intercept = False
                except helper.TimeoutException as err:
                    print("Timeout: ", player_game_week_data)
                    helper.write_to_csv(route.timeout_file, False, [player_url], "a")
                    logger.exception(err)
                except helper.ElementClickInterceptedException as err:
                    print("Intercepted: ", player_game_week_data)
                    helper.sleep(6)
                    intercept = True
                    logger.exception(err)

            # Append the game week to the data array.
            if "j" in game_week.text.lower():
                player_game_week_data.append(game_week.text[1:])
            elif "gw" in game_week.text.lower():
                player_game_week_data.append(game_week.text[2:])
            helper.sleep(helper.uniform(0.4, 0.6))
            team_id = {
                1: "Athletic Club", 2: "Atlético", 3: "Barcelona", 4: "Betis", 5: "Celta", 9: "Getafe",
                10: "Granada", 11: "Las Palmas", 14: "Rayo Vallecano", 15: "Real Madrid", 16: "Real Sociedad",
                17: "Sevilla", 19: "Valencia", 20: "Villareal", 21: "Almería", 48: "Alavés", 50: "Osasuna",
                222: "Girona", 408: "Mallorca", 499: "Cádiz"
            }
            sub_player = None
            try:
                overlay = driver.find_element(helper.By.ID, "overlay")
                popup = overlay.find_element(helper.By.ID, "popup")
                sub_player = popup.find_element(helper.By.CLASS_NAME, "sub-player")
            except helper.NoSuchElementException as err:
                print(player_complete_name + " ".join(player_game_week_data), err)
                # logger.exception(player_complete_name + " ".join(player_game_week_data), err)
            if sub_player:
                get_team = sub_player.find_element(
                    helper.By.CLASS_NAME, "team-logo").get_attribute("src").split(".png")[0].split("/")[-1]
                player_match = driver.find_element(helper.By.CLASS_NAME, "player-match")
                left = player_match.find_element(helper.By.CLASS_NAME, "left")
                right = player_match.find_element(helper.By.CLASS_NAME, "right")
                left_team = left.find_element(
                    helper.By.CLASS_NAME, "team-logo").get_attribute("src").split(".png")[0].split("/")[-1]
                right_team = right.find_element(
                    helper.By.CLASS_NAME, "team-logo").get_attribute("src").split(".png")[0].split("/")[-1]
                if get_team == left_team:
                    opposing_team = team_id.get(int(right_team))
                else:
                    opposing_team = team_id.get(int(left_team))
                own_team = team_id.get(int(get_team))
            else:
                own_team = "N/A"
                opposing_team = "N/A"
            player_game_week_data.append(own_team)
            player_game_week_data.append(opposing_team)
            stats_sports_providers_div = driver.find_element(helper.By.CLASS_NAME, "providers")
            stats_sports_providers = stats_sports_providers_div.find_elements(helper.By.CLASS_NAME, "points")

            suma = 0
            for stats in stats_sports_providers:
                stats_filtered = stats.text.replace(",", ".")
                suma += int(stats_filtered)
            player_game_week_data.append(suma // 4)
            for stats in stats_sports_providers:
                stats_filtered = stats.text.replace(",", ".")
                player_game_week_data.append(stats_filtered)

            player_game_week_data.extend([value, points, average, matches, goals, cards])

            # Click on player "View more stats" button.
            player_view_more_stats = helper.wait_click(
                driver, (helper.By.XPATH, '//*[@id="popup-content"]/div[4]/div/button'), 5)
            player_view_more_stats.click()

            helper.sleep(0.2)

            player_stats = driver.find_element(helper.By.XPATH, "/html/body/div[4]/div[1]/div/div[2]/table")
            player_stats_breakdown = player_stats.find_elements(helper.By.TAG_NAME, "tr")

            for player in player_stats_breakdown:
                player_filter = player.text.replace(",", ".")
                player_game_week_data.append(player_filter)

            for i in temporal_averages:
                player_game_week_data.append(i)

            # Add a timestamp to the data array.
            formatted_date_time = helper.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            player_game_week_data.append(formatted_date_time)
            processed_data = process_row(player_game_week_data)
            temp_list.append(processed_data)

            helper.sleep(0.2)
            close_player_game_week = helper.wait_click(driver, (helper.By.XPATH, '//*[@id="popup"]/button'), 4)
            close_player_game_week.click()

    return temp_list


def process_urls(am, av, aw, header, url):
    driver = helper.login_fantasy_mundo_deportivo()
    driver.get(url)
    # ------ Store players metadata ------
    meta_data, position, player_complete_name = scrape_fantasy_players_meta_data(driver, url)
    am.append(meta_data)
    # print(player_complete_name)
    # ------ Store players value table ------
    head, values = scrape_fantasy_players_value_table(driver, player_complete_name, meta_data[0])
    av.append(values)
    header.append(head)
    # ------ Store players game week ------
    gw = scrape_fantasy_players_game_week(driver, player_complete_name, position, meta_data[2], meta_data[3],
                                          meta_data[4], meta_data[5], meta_data[6], meta_data[7], meta_data[0], url)
    if gw:
        aw.append(gw)
    driver.quit()


def scrape_players_stats_fantasy():
    url_csv_file = helper.read_player_url()
    if helper.path.exists(route.timeout_file):
        helper.remove(route.timeout_file)

    am, av, aw, header = [], [], [], []

    for url in url_csv_file:
        process_urls(am, av, aw, header, url[0])

    if helper.path.exists(route.timeout_file):
        for i in helper.read_timeout_url():
            process_urls(am, av, aw, header, i[0])
    o_all_meta = sorted(am, key = lambda x: x[0])
    o_all_value = sorted(av, key = lambda x: x[0])
    o_all_week = sorted(aw, key = lambda x: (x[0][0], x[0][1:]))
    helper.write_to_csv(route.players_meta_data_file, players_meta_data_header, o_all_meta, "w")
    helper.write_to_csv(route.players_market_temp_info_file_new, header, o_all_value, "w")
    helper.fix_format()
    helper.write_to_csv(route.players_game_week_stats_file, english_list, False, "w")
    for p in o_all_week:
        p.reverse()
        for week in p:
            helper.write_to_csv(route.players_game_week_stats_file, False, [week], "a")


if __name__ == "__main__":
    # it = helper.datetime.now()
    scrape_players_stats_fantasy()
    helper.delete_profile()
    for folder in route.all_folders:
        helper.scrape_backup(folder, route.backup_folder)
    helper.automated_commit("Players.")
    # print(str(helper.datetime.now() - it))

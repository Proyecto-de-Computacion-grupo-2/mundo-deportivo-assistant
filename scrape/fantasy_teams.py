# !/usr/bin/env python3

# -*- coding: utf-8 -*-
# fantasy_teams.py

#

import Utils.helper as helper
import Utils.routes as route

# todo PENDNING TO FINISH FUNCTION.
def database_insert_players_users(teams_data):
    """Once all players have been added to the database, we need to run this code to identify where each player is."""
    pass

def database_get_id_by_name(team_name):
    connection = helper.create_database_connection()
    data = [team_name]
    try:
        cursor = connection.cursor()
        sql = "SELECT id_user FROM user WHERE team_name=%s;"

        cursor.execute(sql, data)

        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def database_get_all_users():
    connection = helper.create_database_connection()
    try:
        cursor = connection.cursor()
        sql = "SELECT team_name FROM user;"
        cursor.execute(sql)

        results = cursor.fetchall()

        teams_title = [result[0] for result in results]

        return teams_title

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def database_insert_users(teams_data):
    connection = helper.create_database_connection()
    teams_in_db = database_get_all_users()
    try:
        cursor = connection.cursor()
        sql_insert = """
        INSERT INTO user (
            team_name,team_points,team_average,team_value,team_players
        ) VALUES (%s, %s, %s,%s,%s)
        """

        sql_update = """
        UPDATE user
        SET team_points = %s, team_average = %s, team_value = %s, team_players = %s
        WHERE id_user = %s;
        """
        for team_data in teams_data:
            team_name = team_data[0]
            team_id = database_get_id_by_name(team_name)
            team_data[1] = int(team_data[1])
            team_data[2] = float(team_data[2])
            team_data[3] = float(team_data[3].replace("M", ""))
            team_data[4] = int(team_data[4])
            if team_name not in teams_in_db:
                cursor.execute(sql_insert, team_data)
            else:
                data_update = team_data[1:5]
                data_update.append(team_id)
                cursor.execute(sql_update, data_update)
        connection.commit()

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def scrape_all_players_fantasy():
    """
    Function that gets all the fantasy players URLs and save them into a CSV file.
    """
    driver = helper.login_fantasy_mundo_deportivo()

    # Go directly to URL
    driver.get("https://mister.mundodeportivo.com/more#players")

    # Set a maximum number of attempts to click the button (optional)
    max_attempts = 12
    attempt = 1
    button_exists = True

    # Create a loop to continuously check for the button's existence
    while button_exists and attempt <= max_attempts:
        try:
            # Now, wait for the button to be clickable
            more_players_button = helper.wait_click(driver, (helper.By.CLASS_NAME, "search-players-more"), 4)
            # Click the button
            more_players_button.click()
            # Give some time for content to load (you can adjust this sleep duration as needed)
            helper.sleep(2.5)
            # Increment the attempt counter
            attempt += 1
        except (AttributeError, helper.NoSuchElementException, helper.ElementClickInterceptedException,
                helper.TimeoutException):
            # The button is not found, set the flag to False
            button_exists = False

    # After the loop, perform another action if the button no longer exists
    if not button_exists:
        # Wait for the players' table to be clickable
        players_table = helper.wait_click(driver, (helper.By.CLASS_NAME, "player-list"), 4)
        link_elements = players_table.find_elements(helper.By.CSS_SELECTOR, "a.btn-sw-link")
        hrefs = [link.get_attribute("href") for link in link_elements]
        data = [[url] for url in hrefs]

        helper.write_to_csv(route.player_links_file, False, data, "w")
    driver.quit()


def scrape_personal_team_fantasy():
    driver = helper.login_fantasy_mundo_deportivo()

    driver.get("https://mister.mundodeportivo.com/team")

    team_players_table = driver.find_element(helper.By.CLASS_NAME, "player-list")
    whole_team_id = helper.extract_player_id(team_players_table)

    # Select each player.
    team_players_icons = team_players_table.find_elements(helper.By.CLASS_NAME, "icons")
    team_players_info = team_players_table.find_elements(helper.By.CLASS_NAME, "info")

    players = helper.scrape_player_info("f", team_players_info, team_players_icons, whole_team_id)

    # ------- Start process to save all the information in a CSV. --------
    team_players_header = ["ID", "Market value", "Average value", "Ante penultimate match score",
                           "Penultimate match score", "Last match score", "Position"]
    helper.write_to_csv(route.personal_team_file, team_players_header, players, "w")
    driver.quit()


def scrape_teams_information():
    """
    Function that gets all the teams competing in the fantasy league, along with their corresponding players.
    Also, the code gets basic information on every team (money, average, etc.).
    """
    driver = helper.login_fantasy_mundo_deportivo()

    driver.get("https://mister.mundodeportivo.com/standings")

    table_elements = driver.find_elements(by = helper.By.CSS_SELECTOR, value = "ul.user-list li a.btn.btn-sw-link.user")

    user_hrefs = [user.get_attribute("href") for user in table_elements]

    user_hrefs = list(set(user_hrefs))

    teams_players_header = ["Team Name", "Player id"]
    original_labels = ["Team Name", "Puntos", "Media", "Valor", "Jugadores"]
    team_data_header = ["Team Name", "Points", "Average", "Value", "Players"]
    label_mapping = dict(zip(original_labels, team_data_header))

    teams_players_data = []
    team_data_data = []

    # Goes through all the userTeams and gets each teams players
    for user_element in user_hrefs:
        driver.get(user_element)
        h1_element = driver.find_element(by = helper.By.TAG_NAME, value = "h1")
        team_name = h1_element.text
        # Navigate to the userTeam's individual page
        try:
            # Find the parent element that contains all the starting player links
            lineup_players = driver.find_element(helper.By.CLASS_NAME, "lineup-starting")
            # Find all the player links the ones that are playing
            player_links = lineup_players.find_elements(helper.By.TAG_NAME, "a")
        except helper.NoSuchElementException:
            player_links = []
        try:
            lineup_subs = driver.find_element(helper.By.CLASS_NAME, "lineup-subs")
            # Find all the player links the ones that are subs
            playersubs_links = lineup_subs.find_elements(helper.By.TAG_NAME, "a")
        except helper.NoSuchElementException:
            playersubs_links = []
        # put them all together and only get the links from the Hrefs
        player_links = player_links + playersubs_links
        player_hrefs = [player_link.get_attribute("href") for player_link in player_links]

        # In this for once with all players links we get the name, surname and position
        for player in player_hrefs:
            player_id = helper.re.findall(r'\d+', player)
            teams_players_data.append([team_name, player_id])



        soup = helper.BeautifulSoup(driver.page_source, "html.parser")

        # Select the parent div element with the class "wrapper" to narrow down the search
        parent_div = soup.find(name = "div", class_ = "wrapper items thin-scrollbar")

        # Find all div elements with class "item" within the parent div
        items = parent_div.find_all(name = "div", class_ = "item")

        # Initialize a dictionary to store label-value pairs
        label_value_dict = {}

        # Extract data from each item and set each label with each corresponding value
        for item in items:
            label = item.find("div", class_ = "label").text
            translated_label = label_mapping.get(label, team_data_header)
            value = item.find("div", class_ = "value").text
            label_value_dict[translated_label] = value

        points = label_value_dict.get("Points")
        average = (label_value_dict.get("Average")).replace(",", ".")
        team_value = (label_value_dict.get("Value")).replace(",", ".")
        players_count = label_value_dict.get("Players")

        # Write the data to the CSV file
        team_data_data.append([team_name, points, average, team_value, players_count])

    database_insert_users(team_data_data)
    helper.write_to_csv(route.team_data_file, team_data_header, sorted(team_data_data, key = lambda x: x[0][0]), "w")
    helper.write_to_csv(route.teams_players_file, teams_players_header,
                        sorted(teams_players_data, key = lambda x: x[0][0]), "w")
    # Close the WebDriver when done
    driver.quit()


if __name__ == "__main__":
    logger = helper.define_logger(route.teams_log)
    #scrape_all_players_fantasy()
    #scrape_personal_team_fantasy()
    scrape_teams_information()
    for folder in route.all_folders:
        helper.scrape_backup(folder, route.backup_folder)
    # helper.automated_commit("Teams.")

# !/usr/bin/env python3

# -*- coding: utf-8 -*-
# fantasy_teams.py

#

import Utils.helper as helper
import Utils.routes as route


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

    # Select the markets section, wait ten seconds as it usually takes some time to load the page.
    driver.get("https://mister.mundodeportivo.com/standings")

    # Get the table with all the teams' information.
    # Find all the user elements
    table_elements = driver.find_elements(by = helper.By.CSS_SELECTOR, value = "ul.user-list li a.btn.btn-sw-link.user")

    # Extract the href values from each userTeam element
    user_hrefs = [user.get_attribute("href") for user in table_elements]
    # Since each player can have different positon, this is so that we can find depending on which pos the player is at
    position_mapping = {"pos-1": "Goalkeeper", "pos-2": "Defence", "pos-3": "Midfielder", "pos-4": "Forward"}

    user_hrefs = list(set(user_hrefs))

    teams_players_header = ["Team Name", "Position", "Name", "Surname"]
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
            driver.get(player)
            soup = helper.BeautifulSoup(driver.page_source, "html.parser")

            # Extract class = pos-" text
            position_class = soup.select_one(".team-position i")["class"][0]

            # Find the "left" div
            left_div = soup.find("div", class_ = "left")

            # Extract the name from within the "left" div
            name = left_div.find("div", class_ = "name").text
            surname = left_div.find("div", class_ = "surname").text

            # Map the position class to the corresponding position
            position = position_mapping.get(position_class, "Unknown")

            teams_players_data.append([team_name, position, name, surname])
        driver.get(user_element)
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

    helper.write_to_csv(route.team_data_file, team_data_header, sorted(team_data_data, key = lambda x: x[0][0]), "w")
    helper.write_to_csv(route.teams_players_file, teams_players_header,
                        sorted(teams_players_data, key = lambda x: x[0][0]), "w")
    # Close the WebDriver when done
    driver.quit()


if __name__ == "__main__":
    logger = helper.define_logger(route.teams_log)
    scrape_all_players_fantasy()
    scrape_personal_team_fantasy()
    scrape_teams_information()
    for folder in route.all_folders:
        helper.scrape_backup(folder, route.backup_folder)
    # helper.automated_commit("Teams.")

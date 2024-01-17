# !/usr/bin/env python3

# -*- coding: utf-8 -*-
# market.py

#

import Utils.helper as helper
import Utils.routes as route


# So it didn't show any warning of variable may be undefined.
logger = "Defined"

# For debugging, this sets up a formatting for a logfile, and where it is.
try:
    if not helper.path.exists(route.market_log):
        helper.logging.basicConfig(filename = route.market_log, level = helper.logging.ERROR,
                                   format = "%(asctime)s %(levelname)s %(name)s %(message)s")
        logger = helper.logging.getLogger(__name__)
    else:
        helper.logging.basicConfig(filename = route.market_log, level = helper.logging.ERROR,
                                   format = "%(asctime)s %(levelname)s %(name)s %(message)s")
        logger = helper.logging.getLogger(__name__)
except Exception as error:
    logger.exception(error)


def scrape_market_section_fantasy(app: bool, driver, user):
    if not app:
        driver = helper.login_fantasy_mundo_deportivo()

    if driver is not None:
        # Select the markets section, wait ten seconds as it usually takes some time to load the page.
        driver.get("https://mister.mundodeportivo.com/market")

        # Get the players' data table.
        market_players_table = driver.find_element(helper.By.ID, "list-on-sale")
        whole_team_id = helper.extract_player_id(market_players_table)

        # Select each player.
        market_players_icons = market_players_table.find_elements(helper.By.CLASS_NAME, "icons")
        market_players_info = market_players_table.find_elements(helper.By.CLASS_NAME, "player-row")

        players = helper.scrape_player_info(market_players_info, market_players_icons, whole_team_id)

        # ------ Start process to save all the information in a CSV. ------
        market_structure_header = ["ID", "Points", "Full name", "Market value", "Average value",
                                   "Ante penultimate match score", "Penultimate match score", "Last match score",
                                   "Attempt to buy"]
        if app:
            helper.write_to_csv(helper.path.join(route.users_folder, user + "_" + route.app_personal_market_file),
                                market_structure_header, players, "w")
        else:
            helper.write_to_csv(route.market_file, market_structure_header, players, "w")
        driver.quit()


def scrape_personal_lineup_fantasy():
    driver = helper.login_fantasy_mundo_deportivo()

    driver.get("https://mister.mundodeportivo.com/team")

    team_players_lineup = driver.find_element(helper.By.CLASS_NAME, "team__lineup")

    aux_formation = team_players_lineup.text.split("\nMedia total")[-1].split("\n")
    r_formation = [i for i in aux_formation if "-" in i][0].replace("-", "")
    formation = r_formation[2] + r_formation[1] + r_formation[0]
    whole_lineup = team_players_lineup.find_elements(helper.By.TAG_NAME, "button")
    whole_lineup_id = [i.get_attribute("data-id_player") for i in whole_lineup if
                       i.get_attribute("data-id_player") is not None if i.get_attribute("data-id_player").isdigit()]

    whole_lineup_points = [_.find_element(helper.By.CLASS_NAME, "points").get_attribute("data-points") for _ in
                           whole_lineup if "slot" in _.get_attribute("id")]

    current = [[formation]] + [[i + ", " + j] for i, j in zip(whole_lineup_id, whole_lineup_points)]

    with open(route.personal_lineup_file, "w", newline = "") as csv_file:
        csv_file.writelines(", ".join(row) + "\n" for row in current)
    driver.quit()


if __name__ == "__main__":
    scrape_market_section_fantasy(False, None, None)
    scrape_personal_lineup_fantasy()
    helper.delete_profile()
    for folder in route.all_folders:
        helper.scrape_backup(folder, route.backup_folder)
    helper.automated_commit("Market.")

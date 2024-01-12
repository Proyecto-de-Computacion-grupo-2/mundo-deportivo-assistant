# !/usr/bin/env python3

# -*- coding: utf-8 -*-
# api_scrape.py

#

import Utils.routes as route
import Utils.helper as helper


# So it didn't show any warning of variable may be undefined.
logger = "Defined"

# For debugging, this sets up a formatting for a logfile, and where it is.
try:
    if not helper.path.exists(route.scrape_folder + "api_scrape.log"):
        helper.logging.basicConfig(filename = route.scrape_folder + "api_scrape.log", level = helper.logging.ERROR,
                                   format = "%(asctime)s %(levelname)s %(name)s %(message)s")
        logger = helper.logging.getLogger(__name__)
    else:
        helper.logging.basicConfig(filename = route.scrape_folder + "api_scrape.log", level = helper.logging.ERROR,
                                   format = "%(asctime)s %(levelname)s %(name)s %(message)s")
        logger = helper.logging.getLogger(__name__)
except Exception as error:
    logger.exception(error)


def call_sofascore_instructions(y):
    data = fetch_data(y)
    save_to_csv(data, y, filename = route.sofascore_data + str(y) + ".csv")


def scrape_la_liga_standings(api_key):
    conn = helper.http.client.HTTPSConnection("v3.football.api-sports.io")

    headers = {"x-rapidapi-host": "v3.football.api-sports.io", "x-rapidapi-key": api_key}

    # Specify the type of API request to make, league = 140 stands for La Liga,
    # and season = 2023 stands for the current date of the league.
    conn.request("GET", "/standings?league=140&season=2023", headers = headers)

    # Get the API response.
    res = conn.getresponse()
    data_stand = res.read()

    # Decode the data and load it as a JSON object
    json_data = helper.json.loads(data_stand.decode("utf-8"))

    """
    JSON file includes a bunch of information we will not use, so we just get the important information we need 
    that being made by only getting the response object inside the JSON file
    and inside the response object we get the league, and inside the league we get the standings object, 
    the standing object has the information we need in this case.
    """
    standings = json_data.get("response", [])[0].get("league", {}).get("standings", [])[0]

    # Create a CSV file to store La Liga standings.
    header = ["Rank", "Team Name", "Total Points", "Goals Difference", "Games Played", "Games Won", "Games Draw",
              "Games Lost", "All goals for", "All Goals Against", "Home games wins", "Home games draws",
              "Home games loses", "Home games goals for", "Home games Goals Against", "Away games Wins",
              "Away games Draws", "Away games Loses", "Away games goals for", "Away games goals Against", "Date"]

    # List to append all teams information.
    team_data_list = []

    # Loop through each teams
    for standing in standings:
        values = [standing["rank"], standing["team"]["name"], standing["points"], standing["goalsDiff"],
                  standing["all"]["played"], standing["all"]["win"], standing["all"]["draw"], standing["all"]["lose"],
                  standing["all"]["goals"]["for"], standing["all"]["goals"]["against"], standing["home"]["win"],
                  standing["home"]["draw"], standing["home"]["lose"], standing["home"]["goals"]["for"],
                  standing["home"]["goals"]["against"], standing["away"]["win"], standing["away"]["draw"],
                  standing["away"]["lose"], standing["away"]["goals"]["for"], standing["away"]["goals"]["against"],
                  helper.datetime.now()]

        # Append values to the team_data_list
        team_data_list.append(values)

    helper.makedirs(helper.path.dirname(route.standings_file), exist_ok = True)
    # Writing data to CSV file
    with open(route.standings_file, "w", encoding = "utf-8", newline = "") as csv_file:
        writer = helper.csv.writer(csv_file)
        writer.writerow(header)
        writer.writerows(team_data_list)


def fetch_data(year_get = 23):
    conn = helper.http.client.HTTPSConnection("api.sofascore.com")
    headers = {}
    payload = ""

    consolidated_data = []
    max_offset = 460
    step = 20

    for offset in range(0, max_offset + 1, step):
        # example
        # endpoint = f"/api/v1/unique-tournament/8/season/52376/statistics?limit=20&order=-rating&offset={offset}
        # &accumulation=perGame&group=summary"

        fields = f"statistics?limit=20&order=-rating&offset" \
                 f"={offset}&accumulation=total&fields=goals%2CbigChancesMissed%2CsuccessfulDribbles" \
                 f"%2CsuccessfulDribblesPercentage%2CtotalShots%2CshotsOnTarget%2CshotsOffTarget%2CblockedShots" \
                 f"%2CgoalConversionPercentage%2CpenaltiesTaken%2CpenaltyGoals%2CpenaltyWon%2CshotsFromSetPiece" \
                 f"%2CfreeKickGoals%2CgoalsFromInsideTheBox%2CgoalsFromOutsideTheBox%2CheadedGoals%2CleftFootGoals" \
                 f"%2CrightFootGoals%2ChitWoodwork%2Coffsides%2CpenaltyConversion%2CsetPieceConversion%2Crating" \
                 f"%2Ctackles%2Cinterceptions%2CpenaltyCommitted%2Cclearances%2CerrorsLeadToGoal%2CerrorsLeadToShot" \
                 f"%2CownGoals%2CdribbledPast%2CcleanSheets%2CbigChancesCreated%2Cassists%2CaccuratePasses" \
                 f"%2CinaccuratePasses%2CtotalPasses%2CaccuratePassesPercentage%2CaccurateOwnHalfPasses" \
                 f"%2CaccurateOppositionHalfPasses%2CaccurateFinalThirdPasses%2CkeyPasses%2CaccurateCrosses" \
                 f"%2CaccurateCrossesPercentage%2CaccurateLongBalls%2CaccurateLongBallsPercentage%2Csaves" \
                 f"%2CpenaltiesFaced%2CpenaltiesSaved%2CsavesFromInsideBox%2CsavedShotsFromOutsideTheBox" \
                 f"%2CgoalsConcededInsideTheBox%2CgoalsConcededOutsideTheBox%2Cpunches%2CrunsOut%2CsuccessfulRunsOut" \
                 f"%2ChighClaims%2CcrossesNotClaimed%2CyellowCards%2CredCards%2CgroundDuelsWon" \
                 f"%2CgroundDuelsWonPercentage%2CaerialDuelsWon%2CaerialDuelsWonPercentage%2CtotalDuelsWon" \
                 f"%2CtotalDuelsWonPercentage%2CminutesPlayed%2CwasFouled%2Cfouls%2Cdispossessed%2CpossessionLost" \
                 f"%2Cappearances%2CStarted&filers=position.in.G~D~M~F"

        year_endpoints = {
            23: f"/api/v1/unique-tournament/8/season/52376/" + fields,
            22: f"/api/v1/unique-tournament/8/season/42409/" + fields,
            21: f"/api/v1/unique-tournament/8/season/37223/" + fields,
            20: f"/api/v1/unique-tournament/8/season/32501/" + fields,
            19: f"/api/v1/unique-tournament/8/season/24127/" + fields,
            18: f"/api/v1/unique-tournament/8/season/18020/" + fields,
            17: f"/api/v1/unique-tournament/8/season/13662/" + fields,
            16: f"/api/v1/unique-tournament/8/season/11906/" + fields,
            15: f"/api/v1/unique-tournament/8/season/10495/" + fields,
        }

        if year_get in year_endpoints:
            endpoint = year_endpoints[year_get]
            conn.request("GET", endpoint, payload, headers)

        res = conn.getresponse()
        d = helper.json.loads(res.read().decode("utf-8"))

        # consolidated_data.append(data)

        # Assuming each "data" is a list of dictionaries, we extend the list.
        if "results" in d:
            consolidated_data.extend(d["results"])

    return consolidated_data


def save_to_csv(d, year_data, filename = route.sofascore_data):
    # Check if data is not empty
    if not d:
        print("No data to save to CSV")
        return

    # Flatten the data and prepare it for CSV
    flattened_data = []
    for entry in d:
        player_info = entry.pop("player", {})
        team_info = entry.pop("team", {})

        # Renaming for distinction
        player_info = {f"player_{key}": value for key, value in player_info.items()}
        team_info = {f"team_{key}": value for key, value in team_info.items() if
                     key in ["name", "slug"]}  # Excluding other team attributes

        new_entry = {**entry, **player_info, **team_info}  # Merge dictionaries
        flattened_data.append(new_entry)

    # Get the header from the first element and reorder it
    header = list(flattened_data[0].keys())
    header.insert(0, header.pop(header.index("player_id")))  # Move player_id to the front
    header.insert(1, header.pop(header.index("player_name")))  # Move player_name to second position

    # Add year to header
    year_data = 2000 + year_data
    header.insert(0, "season")

    with open(filename, mode = "w", encoding = "utf-8", newline = "") as file:
        writer = helper.csv.DictWriter(file, fieldnames = header)

        writer.writeheader()
        for row in flattened_data:
            row["season"] = year_data

            writer.writerow(row)


def consolidate_all_csv():
    helper.chdir(route.sofascore_folder)
    all_filenames = [f for f in helper.glob.glob("*.{}".format("csv"))]
    if not all_filenames:
        print("No CSV files found in the current project folder.")
        return
    combined_csv = helper.pandas.concat([helper.pandas.read_csv(f) for f in all_filenames])
    combined_csv = combined_csv.sort_values(by = ["season"])
    combined_csv.to_csv(route.players_s_data, index = False, encoding = "utf-8-sig")


if __name__ == "__main__":
    with open("config.json", "r", encoding = "utf-8") as config_file:
        config = helper.json.load(config_file)

    api_football = config["api-football"]

    # it = datetime.now()
    scrape_la_liga_standings(api_football)

    yearlist = [15, 16, 17, 18, 19, 20, 21, 22]
    for i in yearlist:
        try:
            if not helper.path.exists(
                    helper.path.join(route.sofascore_data + str(i) + ".csv")) and \
                    helper.path.exists(helper.path.getsize(helper.path.join(route.sofascore_data + str(i) + ".csv"))
                                       > 110000):
                call_sofascore_instructions(i)
        except FileNotFoundError:
            call_sofascore_instructions(i)
            pass
    call_sofascore_instructions(23)
    try:
        helper.remove(route.players_s_data)
    except FileNotFoundError:
        pass
    consolidate_all_csv()
    helper.delete_profile()
    for folder in route.all_folders:
        helper.scrape_backup(folder, route.backup_folder)
    helper.automated_commit("API.")
    # print(str(helper.datetime.now() - it))

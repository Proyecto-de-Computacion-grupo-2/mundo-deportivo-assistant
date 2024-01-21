# !/usr/bin/env python3

# -*- coding: utf-8 -*-
# routes.py

#


from PIL import ImageFont
from os import getcwd, path
from threading import Lock

TOKEN = "6586916577:AAEskwTGX0vjQBZVOCtrfOAg_gQiG9nFcJ8"

if any(ext in getcwd() for ext in ["application", "bot", "src", "Functions", "img", "Layouts", "models", "scrape",
                                   "temp_folder", "users", "Utils"]):
    root_folder = path.abspath(path.join(getcwd(), ".."))
else:
    root_folder = getcwd()
application_folder = path.join(root_folder, "application")
bot_folder = path.join(root_folder, "bot")
src_folder = path.join(application_folder, "src")
function_folder = path.join(src_folder, "Functions")
image_folder = path.join(root_folder, "img")
layout_folder = path.join(src_folder, "Layouts")
models_folder = path.join(root_folder, "models")
scrape_folder = path.join(root_folder, "scrape")
temp_folder = path.join(root_folder, "temp_folder")
users_folder = path.join(application_folder, "users")
utils_folder = path.join(root_folder, "Utils")

# Scrape folders.
data_folder = path.join(scrape_folder, "data")
aux_folder = path.join(data_folder, "auxiliary")
files_folder = path.join(data_folder, "files")
league_folder = path.join(data_folder, "league")
players_folder = path.join(data_folder, "players")
football_folder = path.join(data_folder, "football")
output_folder = path.join(data_folder, "output")
sofascore_folder = path.join(data_folder, "sofascore")
backup_folder = path.join(data_folder, "backup")
all_folders = [aux_folder, league_folder, players_folder, football_folder, sofascore_folder]

# Scrape file list.
api_log = path.join(bot_folder, "api.log")
helper_log = path.join(bot_folder, "helper.log")
teams_log = path.join(bot_folder, "teams.log")
market_log = path.join(bot_folder, "market.log")
player_log = path.join(bot_folder, "player.log")
player_links_file = path.join(aux_folder, "fantasy-players-links.csv")
id_mapping = path.join(aux_folder, "id_names.csv")
timeout_file = path.join(aux_folder, "timeout.csv")
market_file = path.join(players_folder, "fantasy-players-in-market.csv")
personal_lineup_file = path.join(files_folder, "current_alignment")
personal_team_file = path.join(league_folder, "fantasy-personal-team-data.csv")
team_data_file = path.join(league_folder, "fantasy-teams-data.csv")
teams_players_file = path.join(league_folder, "fantasy-teams-players.csv")
players_meta_data_file = path.join(players_folder, "fantasy-metadata-players.csv")
players_market_info_file = path.join(players_folder, "fantasy-market-variation.csv")
players_market_temp_info_file = path.join(players_folder, "fantasy-temp-market-variation.csv")
players_market_temp_info_file_new = path.join(players_folder, "fantasy-temp-market-variation_new.csv")
players_market_temp_info_file_bak = path.join(players_folder, "fantasy-temp-market-variation.csv_bak")
players_game_week_stats_file = path.join(players_folder, "fantasy-games-week-players-stats.csv")
standings_file = path.join(football_folder, "standings-la-liga.csv")
sofascore_data = path.join(sofascore_folder, "data")
players_s_route = path.join(sofascore_folder, "players-data-sofascore.csv")
players_s_data = "players-data-sofascore.csv"
git_lock_file = path.join(data_folder, ".git", "index.lock")
git_log = path.join(data_folder, "git_log")

# Models folders.
players_predictions = path.join(models_folder, "points")
players_predictions_sofascore = path.join(players_predictions, "predictions_sofascore.csv")
players_predictions_bert = path.join(players_predictions, "BERTGamesWeek")
players_predictions_mundo_deportivo = path.join(players_predictions_bert, "predictions_mundo_deportivo.csv")
values_folder = path.join(models_folder, "value", "predictions")
plots_folder = path.join(values_folder, "plots")
op_market_md = path.join(output_folder, "optimise_market_mundo_deportivo")
op_market_p_md = path.join(output_folder, "optimise_market_predictions_mundo_deportivo")
op_market_ss = path.join(output_folder, "optimise_market_sofascore")
op_market_p_ss = path.join(output_folder, "optimise_market_predictions_sofascore")
op_my_team_md = path.join(output_folder, "optimise_my_team_mundo_deportivo")
op_my_team_p_md = path.join(output_folder, "optimise_my_team_predictions_mundo_deportivo")
op_my_team_ss = path.join(output_folder, "optimise_my_team_sofascore")
op_my_team_p_ss = path.join(output_folder, "optimise_my_team_predictions_sofascore")
merge_market_md = path.join(files_folder, "future_market_md")
merge_my_team_md = path.join(files_folder, "future_my_team_md")
merge_market_ss = path.join(files_folder, "future_market_ss")
merge_my_team_ss = path.join(files_folder, "future_my_team_ss")


git_lock = Lock()

# Bot folders.
JSON_FILE = path.join(bot_folder, "jobfile.json")
bot_log = path.join(bot_folder, "bot.log")
background_path = path.join(image_folder, "background.png")
index_current_path = path.join(image_folder, "index_current")
current_path = path.join(image_folder, "current")
font = ImageFont.truetype(path.join(utils_folder, "DejaVuSerifCondensed-Italic.ttf"), 70)
font_market = ImageFont.truetype(path.join(utils_folder, "DejaVuSerifCondensed-Italic.ttf"), 18)
current_alignment = path.join(files_folder, "current_alignment")
current_alignment_bak = path.join(backup_folder, "current_alignment_bak")
merge_market_md_bak = path.join(files_folder, "future_market_md_bak")
merge_my_team_md_bak = path.join(files_folder, "future_my_team_md_bak")
merge_market_ss_bak = path.join(files_folder, "future_market_ss_bak")
merge_my_team_ss_bak = path.join(files_folder, "future_my_team_ss_bak")
market = path.join(players_folder, "fantasy-players-in-market.csv")
market_players = path.join(image_folder, "market_players.jpeg")
market_bak = path.join(backup_folder, "fantasy-players-in-market_bot.csv_bak")

# Application folders.
fantasy_logo = path.join(image_folder, "mister-fantasy-md-logo_mod.png")
football_loading = path.join(image_folder, "football_loading.gif")
app_personal_team_file = "fantasy-personal-team-data.csv"
app_personal_lineup_file = "personal_lineup"
app_personal_market_file = "fantasy-market-data.csv"
market_md_img = path.join(image_folder, "future_market_md")
my_team_md_img = path.join(image_folder, "future_my_team_md")
market_ss_img = path.join(image_folder, "future_market_ss")
my_team_ss_img = path.join(image_folder, "future_my_team_ss")
temp_img_show = path.join(application_folder, "temp_img.png")
temp2_img_show = path.join(application_folder, "temp2_img.png")
font_popup = (path.join(utils_folder, "DejaVuSerifCondensed-Italic.ttf"), 18)



from UA2C import helper as helper, routes as route


def multi_stmt_insert(name: str, create: bool, file: bool, cur: helper.mysql.connector.connection.MySQLCursorBuffered):
    if create and file:
        try:
            with open(name, "r", encoding = "utf-8") as file:
                sql_script = file.read()

            for result in cur.execute(sql_script, multi = True):
                if result.with_rows:
                    print("Rows produced by statement '{}':".format(result.statement))
                    print(result.fetchall())
                else:
                    print("Number of rows affected by statement '{}': {}".format(result.statement, result.rowcount))

            cur.close()
        except Exception as e:
            print(e)
    elif not create and file:
        progress_bar = None
        try:
            with open(name, "r", encoding = "utf-8") as file:
                sql_script = file.readlines()

            progress_bar = helper.tqdm(total = len(sql_script), desc = "Inserting")

            for ins in sql_script:
                cur.execute(ins)
                progress_bar.update(1)
        except Exception as e:
            print(e)
        finally:
            progress_bar.close()
            cur.close()


def extract_login_token(h: dict, u: str, p: str):
    # Definir la URL del endpoint de inicio de sesión
    login_url = "https://mister.mundodeportivo.com/api2/auth/email"

    # Definir la carga útil (payload) con las credenciales
    payload = {"email": u, "password": p}

    failed = True
    res = None

    while failed:
        try:
            # Realizar la solicitud POST para autenticarse
            response = helper.requests.post(login_url, json = payload, headers = h)

            # Verificar si la autenticación fue exitosa
            if response.status_code == 200:
                # Obtener el token de sesión de la respuesta
                response = response.json()
                res = response["token"]
                failed = False
            else:
                # Manejar respuestas de error del servidor
                print(f"Error de autenticación: {response.status_code}")
        except helper.requests.exceptions.ConnectionError as e:
            # Manejar errores de conexión
            print(f"Error de conexión: {e}")
        except Exception as e:
            # Manejar cualquier otro error
            print(f"Error: {e}")
    return res


def extract_tokens(h: dict, u: str, p: str):

    token = extract_login_token(h, u, p)

    # Realizamos la segunda solicitud para verificar que el token sea válido
    url = "https://mister.mundodeportivo.com/api2/auth/external/exchange-token"
    payload = {"token": token}
    response = helper.requests.post(url, json = payload, headers = h)
    if response.status_code == 200:
        cookie_list = []
        for _ in response.cookies.items():
            cookie_list.append(_[0] + "=" + _[1])
        return "; ".join(cookie_list[1:])


def extract_auth(h: dict, ua: str, u: str, p: str):
    full_cookie = extract_tokens(h, u, p)

    auth_headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                              "*/*;q=0.8", "Accept-Encoding": "gzip, deflate", "Accept-Language":
                    "es-ES,es;q=0.9", "User-Agent": ua, "Cookie": full_cookie, "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}

    market_url = "https://mister.mundodeportivo.com/market"

    response = helper.requests.get(market_url, headers = auth_headers)

    soup = helper.BeautifulSoup(response.text, "html.parser")
    script = soup.find("script")

    regex_expresion = '"auth":"[a-zA-Z0-9]+"'
    match = helper.re.search(regex_expresion, script.get_text())

    auth_headers["X-AUTH"] = match.group().split(":")[1].replace("\"", "")

    return auth_headers


def extract_auth_marca():
    chrome_options = helper.webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    driver = helper.webdriver.Chrome(options = chrome_options)
    driver.get("https://laligafantasy.relevo.com/leagues")
    helper.sleep(helper.uniform(0.2, 0.6))

    helper.WebDriverWait(driver, 5).until(helper.ec.element_to_be_clickable((helper.By.CLASS_NAME,
                                                                             "main-season")))
    helper.sleep(helper.uniform(0.2, 0.6))

    # Obtener el localStorage
    local_storage = driver.execute_script("return window.localStorage")
    data = helper.json.loads(local_storage["auth"])

    # Acceder al token de acceso dentro del objeto "auth_data"
    access_token = data["status"]["authenticateGuest"]["access_token"]

    driver.quit()

    return access_token


def extract_marca_all_p(h: dict, r: int):
    again = True
    auth = None
    while again:
        try:
            auth = extract_auth_marca()
            again = False
        except TypeError:
            again = True

    url = "https://api-fantasy.llt-services.com/api/v3/players?x-lang=es"
    res = helper.requests.get(url, auth = helper.BearerAuth(auth), headers = h, timeout = r)
    if res.status_code == 200:
        return auth, res.json()
    return None


def extract_marca_all_p_id(marca_h: dict, rt: int):
    auth, players_info_res = extract_marca_all_p(marca_h, rt)

    marca = []
    if players_info_res:
        for _ in players_info_res:
            url = "https://api-fantasy.llt-services.com/api/v3/player/" + _["id"] + "?x-lang=es"
            p = helper.requests.get(url, auth = helper.BearerAuth(auth), headers = marca_h, timeout = rt).json()
            if p:
                if p["position"] != "Entrenador":
                    temp_dict = {"id_marca": p["id"], "id_ss": "0", "full_name": p["name"], "nickname": p["nickname"],
                                 "slug": p["slug"]}
                    marca.append(temp_dict)
        return marca
    return None


def extract_marca_img(marca_h: dict, rt: int):
    auth, players_info_res = extract_marca_all_p(marca_h, rt)
    faulty = []

    if players_info_res:
        for _ in players_info_res:
            url = "https://api-fantasy.llt-services.com/api/v3/player/" + _["id"] + "?x-lang=es"
            img_url = "https://assets-fantasy.llt-services.com/players/"
            p_data = helper.requests.get(url, auth = helper.BearerAuth(auth), headers = marca_h, timeout = rt).json()
            player_image = img_url + p_data["team"]["badgeColor"].split("/")[-1].split("_")[0] + "/p" + \
                p_data["id"] + "/256x256/p" + p_data["id"] + "_" + \
                p_data["team"]["badgeColor"].split("/")[-1].split("_")[0] + "_1_001_000.png"
            res = helper.requests.get(player_image)
            if res.status_code != 200:
                player_image = img_url + p_data["team"]["badgeColor"].split("/")[-1].split("_")[0] + "/p" + \
                               p_data["id"] + "/128x128/p" + p_data["id"] + "_" + \
                               p_data["team"]["badgeColor"].split("/")[-1].split("_")[0] + "_1_001_000.png"
                res = helper.requests.get(player_image)
                if res.status_code != 200:
                    player_image = img_url + p_data["team"]["badgeColor"].split("/")[-1].split("_")[0] + "/p" + \
                                   p_data["id"] + "/64x64/p" + p_data["id"] + "_" + \
                                   p_data["team"]["badgeColor"].split("/")[-1].split("_")[0] + "_1_001_000.png"
                    res = helper.requests.get(player_image)
            if res.status_code == 200:
                img_file = helper.path.join("marca_img", p_data["id"] + ".png")
                helper.makedirs(helper.path.dirname(img_file), exist_ok = True)
                with open(img_file, "wb") as img:
                    img.write(res.content)
            else:
                faulty.append(p_data["id"] + ", " + p_data["name"] + ", " + p_data["nickname"] + ", " +
                              p_data["slug"] + ", " + p_data["team"]["badgeColor"].split("/")[-1].split("_")[0])
    return faulty


def extract_all_players_value_and_gw_md(u: str, p: str, h: dict, ai: helper.AIModel, ab: helper.Absences,
                                        gw: helper.Games, players: helper.Players, pv: helper.PriceVariations,
                                        users: helper.Users,url: str, url2: str):
    def date_formatting(date: str):
        date_mapping = {
            # Meses en inglés
            "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06", "jul": "07", "aug": "08",
            "sep": "09", "oct": "10", "nov": "11", "dec": "12",
            # Meses en español sin repetir anteriores.
            "ene": "01", "abr": "04", "ago": "08", "sept": "09", "dic": "12"
        }
        month = date.split(" ")[1]
        return "-".join([date.split(" ")[-1]] + [date_mapping[month]] + [date.split(" ")[0]])

    progress_bar_1 = helper.tqdm(total = 600, desc = "Scraping")
    for num in range(0, 601, 50):
        helper.sleep(helper.uniform(5, 12))
        payload = {
            "post": "players", "filters[ position ]": 0, "filters[ value ]": 0, "filters[ team ]": 0,
            "filters[ injured ]": 0, "filters[ favs ]": 0, "filters[ owner ]": 0, "filters[ benched ]": 0,
            "offset": num, "order": 0, "name": "", "filtered": 0, "parentElement": ".sw-content"}
        res = helper.requests.post(url, data = payload, headers = h)
        if res.status_code == 200:
            res_json_1 = res.json()
            if res_json_1["data"]["players"]:
                progress_bar_2 = helper.tqdm(total = len(res_json_1["data"]["owners"]), desc = "Users: ")
                for aux_owner in res_json_1["data"]["owners"]:
                    if aux_owner["id"] not in users.get_all_user_ids():
                        payload_2 = {"post": "users", "id": aux_owner["id"]}
                        helper.sleep(helper.uniform(5, 12))
                        res_2 = helper.requests.post(url, data = payload_2, headers = h)
                        if res_2.status_code == 200:
                            res_json_2 = res_2.json()["data"]
                            if res_json_2:
                                res_json_season = res_json_2["season"]
                                users.add_user(res_json_2["id"], "", "", res_json_2["user"]["name"],
                                               res_json_season["points"], res_json_season["avg"], res_json_2["value"],
                                               len(res_json_2["team_now"]), 0, 0, 0)
                    progress_bar_2.update(1)
                progress_bar_2.close()
                progress_bar_3 = helper.tqdm(total = len(res_json_1["data"]["players"]),
                                             desc = "Segment " + str((num // 50) + 1))
                for aux_players in res_json_1["data"]["players"]:
                    if aux_players["id"] not in players.get_all_player_ids():
                        payload_3 = {"post": "players", "id": aux_players["id"]}
                        helper.sleep(helper.uniform(5, 12))
                        res_3 = helper.requests.post(url, data = payload_3, headers = h)
                        if res_3.status_code == 200:
                            res_json_3 = res_3.json()["data"]
                            if res_json_3:
                                res_json_h_points = res_json_3["points_history"]
                                res_json_market = res_json_3["player"]["market"]
                                res_json_p_repo = res_json_3["playerRepo"]
                                res_json_p_injuries = res_json_p_repo["injuries"]
                                res_json_player = res_json_3["player"]
                                res_json_values = res_json_3["values_chart"]["points"]
                                s56, s67, s78, s89, s1920, s2021, s2122, s2223, s2324 = 0, 0, 0, 0, 0, 0, 0, 0, 0
                                for history in res_json_h_points:
                                    if "season" in helper.json.dumps(history).split(":")[0]:
                                        if history["season"] == "15/16":
                                            if history["points"] is not None:
                                                s56 = history["points"]
                                            else:
                                                s56 = 0
                                        elif history["season"] == "16/17":
                                            if history["points"] is not None:
                                                s67 = history["points"]
                                            else:
                                                s67 = 0
                                        elif history["season"] == "17/18":
                                            if history["points"] is not None:
                                                s78 = history["points"]
                                            else:
                                                s78 = 0
                                        elif history["season"] == "18/19":
                                            if history["points"] is not None:
                                                s89 = history["points"]
                                            else:
                                                s89 = 0
                                        elif history["season"] == "19/20":
                                            if history["points"] is not None:
                                                s1920 = history["points"]
                                            else:
                                                s1920 = 0
                                        elif history["season"] == "20/21":
                                            if history["points"] is not None:
                                                s2021 = history["points"]
                                            else:
                                                s2021 = 0
                                        elif history["season"] == "21/22":
                                            if history["points"] is not None:
                                                s2122 = history["points"]
                                            else:
                                                s2122 = 0
                                        elif history["season"] == "22/23":
                                            if history["points"] is not None:
                                                s2223 = history["points"]
                                            else:
                                                s2223 = 0
                                        elif history["season"] == "23/24":
                                            if history["points"] is not None:
                                                s2324 = history["points"]
                                            else:
                                                s2324 = 0
                                res = helper.requests.get(res_3.json()["data"]["player"]["photoUrl"])
                                img_file = helper.path.join(route.image_folder, str(aux_players["id"]) + "_" +
                                                            aux_players["name"].replace(" ", "_") + ".png")
                                helper.makedirs(helper.path.dirname(img_file), exist_ok = True)
                                with open(img_file, "wb") as img:
                                    img.write(res.content)
                                with (open(img_file, "rb") as file):
                                    image = helper.Image.open(file)
                                    b64_image = helper.base64.b64encode(image.tobytes()).decode("utf-8")
                                if aux_players["id_uc"] is None:
                                    team_id = 1010
                                else:
                                    team_id = aux_players["id_uc"]
                                players.add_player(res_json_player["id"], res_json_p_repo["sofaScoreId"], 0,
                                                   team_id, res_json_player["name"], res_json_player["position"],
                                                   res_json_player["value"], True if res_json_market["active"] == 1
                                                   else False, res_json_market["input"], 0, b64_image, s56,
                                                   s67, s78, s89, s1920,s2021, s2122, s2223, s2324)
                                if aux_players["is_mine"] == 1:
                                    user_team = users.find_user(team_id)
                                    if user_team.email == "" and user_team.password == "":
                                        user_team.email = u
                                        user_team.password = p
                                    balance = extract_balance(new_header, md_balance_url)
                                    user_team.current_balance = balance["current_balance"]
                                    user_team.future_balance = balance["future_balance"]
                                    user_team.maximum_debt = balance["maximum_debt"]
                                for value in res_json_values:
                                    pv.add_price_variation(aux_players["id"], date_formatting(value["date"]),
                                                           value["value"])
                                for injury in res_json_p_injuries:
                                    if injury["since"] is not None:
                                        since = injury["since"]
                                    else:
                                        since = "None"
                                    if injury["until"] is not None:
                                        until = injury["until"]
                                    else:
                                        until = "None"
                                    ab.add_absence(aux_players["id"], injury["category"], injury["description"],
                                                   since, until)
                                gameweeks = res_json_3["points"]
                                gameweeks.reverse()
                                for gameweek in gameweeks:
                                    gw_number = gameweek["gameweek"]
                                    payload_3 = {"id_gameweek": gameweek["id_gameweek"], "id_player": aux_players["id"]}
                                    res_3 = helper.requests.post(url2, data = payload_3, headers = h)
                                    res_json_3 = None
                                    if res_3.status_code == 200:
                                        res_json_3 = res_3.json()["data"]
                                    if res_json_3 is not None:
                                        special = False
                                        test = None
                                        own_team = res_json_3["id_team"]
                                        if res_json_3["id_home"] == own_team:
                                            opposing_team = res_json_3["id_away"]
                                        else:
                                            opposing_team = res_json_3["id_home"]
                                        if res_json_3["marca_stats_rating_detailed"]:
                                            test = res_json_3["marca_stats_rating_detailed"]
                                            special = False
                                        elif res_json_3["stats"] is not None:
                                            test = res_json_3["stats"]
                                            special = True
                                        if test is not None:
                                            data_str = test.replace("'", "\"")
                                            exclude = ["rating", "marca", "ratingVersions"]
                                            include = ["goalsAgainst", "goalsAssist", "goalsAvoided", "goalAvoided"]
                                            original_data_dict = {
                                                "yellowCard": {"value": 0, "rating": 0},
                                                "doubleYellowCard": {"value": 0, "rating": 0},
                                                "redCard": {"value": 0, "rating": 0},
                                                "totalPass": {"value": 0, "rating": 0},
                                                "accuratePass": {"value": 0, "rating": 0},
                                                "totalLongBalls": {"value": 0, "rating": 0},
                                                "accurateLongBalls": {"value": 0, "rating": 0},
                                                "totalCross": {"value": 0, "rating": 0},
                                                "accurateCross": {"value": 0, "rating": 0},
                                                "totalClearance": {"value": 0, "rating": 0},
                                                "clearanceOffLine": {"value": 0, "rating": 0},
                                                "aerialLost": {"value": 0, "rating": 0},
                                                "aerialWon": {"value": 0, "rating": 0},
                                                "duelLost": {"value": 0, "rating": 0},
                                                "duelWon": {"value": 0, "rating": 0},
                                                "dispossessed": {"value": 0, "rating": 0},
                                                "challengeLost": {"value": 0, "rating": 0},
                                                "totalContest": {"value": 0, "rating": 0},
                                                "wonContest": {"value": 0, "rating": 0},
                                                "goodHighClaim": {"value": 0, "rating": 0},
                                                "punches": {"value": 0, "rating": 0},
                                                "errorLeadToAShot": {"value": 0, "rating": 0},
                                                "errorLeadToAGoal": {"value": 0, "rating": 0},
                                                "shotOffTarget": {"value": 0, "rating": 0},
                                                "onTargetScoringAttempt": {"value": 0, "rating": 0},
                                                "blockedScoringAttempt": {"value": 0, "rating": 0},
                                                "outfielderBlock": {"value": 0, "rating": 0},
                                                "bigChanceCreated": {"value": 0, "rating": 0},
                                                "hitWoodwork": {"value": 0, "rating": 0},
                                                "bigChanceMissed": {"value": 0, "rating": 0},
                                                "penaltyConceded": {"value": 0, "rating": 0},
                                                "penaltyWon": {"value": 0, "rating": 0},
                                                "penaltyMiss": {"value": 0, "rating": 0},
                                                "penaltySave": {"value": 0, "rating": 0},
                                                "goals": {"value": 0, "rating": 0},
                                                "ownGoals": {"value": 0, "rating": 0},
                                                "savedShotsFromInsideTheBox": {"value": 0, "rating": 0},
                                                "saves": {"value": 0, "rating": 0},
                                                "interceptionWon": {"value": 0, "rating": 0},
                                                "totalInterceptions": {"value": 0, "rating": 0},
                                                "goalAssist": {"value": 0, "rating": 0},
                                                "goalsAvoided": {"value": 0, "rating": 0},
                                                "goalsAgainst": {"value": 0, "rating": 0},
                                                "totalKeeperSweeper": {"value": 0, "rating": 0},
                                                "accurateKeeperSweeper": {"value": 0, "rating": 0},
                                                "totalTackle": {"value": 0, "rating": 0},
                                                "wasFouled": {"value": 0, "rating": 0},
                                                "fouls": {"value": 0, "rating": 0},
                                                "totalOffside": {"value": 0, "rating": 0},
                                                "minutesPlayed": {"value": 0, "rating": 0},
                                                "touches": {"value": 0, "rating": 0},
                                                "lastManTackle": {"value": 0,  "rating": 0},
                                                "possessionLostCtrl": {"value": 0, "rating": 0},
                                                "expectedGoals": {"value": 0, "rating": 0},
                                                "goalsPrevented": {"value": 0, "rating": 0},
                                                "keyPass": {"value": 0, "rating": 0},
                                                "expectedAssists": {"value": 0, "rating": 0}
                                            }

                                            # Convert to dictionary
                                            data_dict = helper.json.loads(data_str)
                                            for key, value in data_dict.items():
                                                if not special:
                                                    if key in original_data_dict:
                                                        original_data_dict[key].update(data_dict[key])
                                                    # if any(ext in res_json_3["stats"] for ext in include) and \
                                                    #         key in include:
                                                    if any(ext in res_json_3["stats"] for ext in include):  # key in
                                                        # include or
                                                        print(key + " in MD.")
                                                    elif key not in original_data_dict and \
                                                            all(key != ext for ext in exclude):
                                                        print(key)
                                                if special:
                                                    if key in original_data_dict:
                                                        original_data_dict[key] = {"value": data_dict[key], "rating": 0}
                                            player_value = players.find_player(aux_players["id"])
                                            game_count = sum(1 for game in gameweeks if game["points"] is not None
                                                             and game["points"] > 0)
                                            goal_count = sum(game["events"].count("goal") for game in gameweeks
                                                             if game["events"] is not False)
                                            card_count = sum(game["events"].count("red") for game in gameweeks
                                                             if game["events"] is not False) + \
                                                sum(game["events"].count("yellow") for game in gameweeks
                                                    if game["events"] is not False)
                                            if res_json_3["as_graded_date"] is not None:
                                                gw_schedule = res_json_3["as_graded_date"]
                                            else:
                                                gw_schedule = "None"
                                            if res_json_3["points_mix"] is not None:
                                                points_mix = res_json_3["points_mix"]
                                            else:
                                                points_mix = 0
                                            if res_json_3["points_as"] is not None:
                                                points_as = res_json_3["points_as"]
                                            else:
                                                points_as = 0
                                            if res_json_3["points_marca"] is not None:
                                                points_marca = res_json_3["points_marca"]
                                            else:
                                                points_marca = 0
                                            if res_json_3["points_md"] is not None:
                                                points_md = res_json_3["points_md"]
                                            else:
                                                points_md = 0
                                            if res_json_3["points_mr"] is not None:
                                                points_mr = res_json_3["points_mr"]
                                            else:
                                                points_mr = 0
                                            gw.add_game(gameweek["id_gameweek"], aux_players["id"],
                                                        gw_schedule, gw_number, own_team, opposing_team,
                                                        points_mix, points_as, points_marca, points_md,
                                                        points_mr, player_value.player_value,
                                                        res_json_player["points"], res_json_player["avg"],
                                                        game_count, goal_count, card_count,
                                                        original_data_dict["yellowCard"]["value"],
                                                        original_data_dict["doubleYellowCard"]["value"],
                                                        original_data_dict["redCard"]["value"],
                                                        original_data_dict["totalPass"]["value"],
                                                        original_data_dict["accuratePass"]["value"],
                                                        original_data_dict["totalLongBalls"]["value"],
                                                        original_data_dict["accurateLongBalls"]["value"],
                                                        original_data_dict["totalCross"]["value"],
                                                        original_data_dict["accurateCross"]["value"],
                                                        original_data_dict["totalClearance"]["value"],
                                                        original_data_dict["clearanceOffLine"]["value"],
                                                        original_data_dict["aerialLost"]["value"],
                                                        original_data_dict["aerialWon"]["value"],
                                                        original_data_dict["duelLost"]["value"],
                                                        original_data_dict["duelWon"]["value"],
                                                        original_data_dict["dispossessed"]["value"],
                                                        original_data_dict["challengeLost"]["value"],
                                                        original_data_dict["totalContest"]["value"],
                                                        original_data_dict["wonContest"]["value"],
                                                        original_data_dict["goodHighClaim"]["value"],
                                                        original_data_dict["punches"]["value"],
                                                        original_data_dict["errorLeadToAShot"]["value"],
                                                        original_data_dict["errorLeadToAGoal"]["value"],
                                                        original_data_dict["shotOffTarget"]["value"],
                                                        original_data_dict["onTargetScoringAttempt"]["value"],
                                                        original_data_dict["blockedScoringAttempt"]["value"],
                                                        original_data_dict["outfielderBlock"]["value"],
                                                        original_data_dict["bigChanceCreated"]["value"],
                                                        original_data_dict["hitWoodwork"]["value"],
                                                        original_data_dict["bigChanceMissed"]["value"],
                                                        original_data_dict["penaltyConceded"]["value"],
                                                        original_data_dict["penaltyWon"]["value"],
                                                        original_data_dict["penaltyMiss"]["value"],
                                                        original_data_dict["penaltySave"]["value"],
                                                        original_data_dict["goals"]["value"],
                                                        original_data_dict["ownGoals"]["value"],
                                                        original_data_dict["savedShotsFromInsideTheBox"]["value"],
                                                        original_data_dict["saves"]["value"],
                                                        original_data_dict["goalAssist"]["value"],
                                                        original_data_dict["goalsAgainst"]["value"],
                                                        original_data_dict["goalsAvoided"]["value"],
                                                        original_data_dict["interceptionWon"]["value"],
                                                        original_data_dict["totalInterceptions"]["value"],
                                                        original_data_dict["totalKeeperSweeper"]["value"],
                                                        original_data_dict["accurateKeeperSweeper"]["value"],
                                                        original_data_dict["totalTackle"]["value"],
                                                        original_data_dict["wasFouled"]["value"],
                                                        original_data_dict["fouls"]["value"],
                                                        original_data_dict["totalOffside"]["value"],
                                                        original_data_dict["minutesPlayed"]["value"],
                                                        original_data_dict["touches"]["value"],
                                                        original_data_dict["lastManTackle"]["value"],
                                                        original_data_dict["possessionLostCtrl"]["value"],
                                                        original_data_dict["expectedGoals"]["value"],
                                                        original_data_dict["goalsPrevented"]["value"],
                                                        original_data_dict["keyPass"]["value"],
                                                        original_data_dict["expectedAssists"]["value"],
                                                        helper.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                                            ai.add_player(aux_players["id"], aux_players["name"],
                                                          aux_players["position"], gameweek["id_gameweek"], own_team,
                                                          opposing_team, points_mix, points_as, points_marca, points_md,
                                                          points_mr, player_value.player_value,
                                                          res_json_player["points"], res_json_player["avg"], game_count,
                                                          goal_count, card_count,
                                                          original_data_dict["yellowCard"]["value"],
                                                          original_data_dict["doubleYellowCard"]["value"],
                                                          original_data_dict["redCard"]["value"],
                                                          original_data_dict["totalPass"]["value"],
                                                          original_data_dict["accuratePass"]["value"],
                                                          original_data_dict["totalLongBalls"]["value"],
                                                          original_data_dict["accurateLongBalls"]["value"],
                                                          original_data_dict["totalCross"]["value"],
                                                          original_data_dict["accurateCross"]["value"],
                                                          original_data_dict["totalClearance"]["value"],
                                                          original_data_dict["clearanceOffLine"]["value"],
                                                          original_data_dict["aerialLost"]["value"],
                                                          original_data_dict["aerialWon"]["value"],
                                                          original_data_dict["duelLost"]["value"],
                                                          original_data_dict["duelWon"]["value"],
                                                          original_data_dict["dispossessed"]["value"],
                                                          original_data_dict["challengeLost"]["value"],
                                                          original_data_dict["totalContest"]["value"],
                                                          original_data_dict["wonContest"]["value"],
                                                          original_data_dict["goodHighClaim"]["value"],
                                                          original_data_dict["punches"]["value"],
                                                          original_data_dict["errorLeadToAShot"]["value"],
                                                          original_data_dict["errorLeadToAGoal"]["value"],
                                                          original_data_dict["shotOffTarget"]["value"],
                                                          original_data_dict["onTargetScoringAttempt"]["value"],
                                                          original_data_dict["blockedScoringAttempt"]["value"],
                                                          original_data_dict["outfielderBlock"]["value"],
                                                          original_data_dict["bigChanceCreated"]["value"],
                                                          original_data_dict["hitWoodwork"]["value"],
                                                          original_data_dict["bigChanceMissed"]["value"],
                                                          original_data_dict["penaltyConceded"]["value"],
                                                          original_data_dict["penaltyWon"]["value"],
                                                          original_data_dict["penaltyMiss"]["value"],
                                                          original_data_dict["penaltySave"]["value"],
                                                          original_data_dict["goals"]["value"],
                                                          original_data_dict["ownGoals"]["value"],
                                                          original_data_dict["savedShotsFromInsideTheBox"]["value"],
                                                          original_data_dict["saves"]["value"],
                                                          original_data_dict["goalAssist"]["value"],
                                                          original_data_dict["goalsAvoided"]["value"],
                                                          original_data_dict["goalsAgainst"]["value"],
                                                          original_data_dict["interceptionWon"]["value"],
                                                          original_data_dict["totalInterceptions"]["value"],
                                                          original_data_dict["totalKeeperSweeper"]["value"],
                                                          original_data_dict["accurateKeeperSweeper"]["value"],
                                                          original_data_dict["totalTackle"]["value"],
                                                          original_data_dict["wasFouled"]["value"],
                                                          original_data_dict["fouls"]["value"],
                                                          original_data_dict["totalOffside"]["value"],
                                                          original_data_dict["minutesPlayed"]["value"],
                                                          original_data_dict["touches"]["value"],
                                                          original_data_dict["lastManTackle"]["value"],
                                                          original_data_dict["possessionLostCtrl"]["value"],
                                                          original_data_dict["expectedGoals"]["value"],
                                                          original_data_dict["goalsPrevented"]["value"],
                                                          original_data_dict["keyPass"]["value"],
                                                          original_data_dict["expectedAssists"]["value"], s56, s67, s78,
                                                          s89, s1920, s2021, s2122, s2223, s2324,
                                                          helper.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    progress_bar_3.update(1)
                progress_bar_3.close()
        progress_bar_1.update(50)
    progress_bar_1.close()
    print()


def find_id_marca_to_md(h: dict, pl: list, player_md: helper.Players, url: str):

    def find_exact_matches(results, search_name):
        index = 0
        player_not_found = True
        matching_results = None
        while index < len(results) and player_not_found:
            if results[index]["name"] == search_name:
                matching_results = results[index]
                player_not_found = False
            index += 1
        return matching_results, player_not_found

    faulty = []
    payload = {"post": "players", "filters[ position ]": 0, "filters[ value ]": 0, "filters[ team ]": 0,
               "filters[ injured]": 0, "filters[ favs ]": 0, "filters[ owner ]": 0, "filters[ benched ]": 0,
               "offset": 0, "order": 0, "name": "", "filtered": 0, "parentElement": ".sw-content"}

    progress_bar = helper.tqdm(total = len(pl), desc = "ID Marca mapping: ")
    for p in pl:
        if "fdez" in p["full_name"].lower():
            p["full_name"] = p["full_name"].replace("Fdez", "Fernandez")
        elif "fdez" in p["nickname"].lower():
            p["nickname"] = p["nickname"].replace("Fdez", "Fernandez")
        if "fdez" in p["slug"].lower():
            p["slug"] = p["slug"].replace("Fdez", "Fernandez")
        elif "-1" in p["slug"].lower():
            p["slug"] = p["slug"].replace("-1", "")
        elif "-2" in p["slug"].lower():
            p["slug"] = p["slug"].replace("-2", "")
        elif "-3" in p["slug"].lower():
            p["slug"] = p["slug"].replace("-3", "")
        elif "-4" in p["slug"].lower():
            p["slug"] = p["slug"].replace("-4", "")
        elif "-5" in p["slug"].lower():
            p["slug"] = p["slug"].replace("-5", "")
        elif "-6" in p["slug"].lower():
            p["slug"] = p["slug"].replace("-6", "")
        payload["name"] = p["full_name"]
        res = helper.requests.post(url, data = payload, headers = h)
        if res.status_code == 200:
            final_player = None
            res_json = res.json()
            fail = True
            if len(res_json["data"]["players"]) >= 1:
                res_json["data"]["players"][0], fail = find_exact_matches(res_json["data"]["players"], p["full_name"])
            if fail:
                payload["name"] = p["nickname"]
                res = helper.requests.post(url, data = payload, headers = h)
                if res.status_code == 200:
                    res_json = res.json()
                    if len(res_json["data"]["players"]) >= 1:
                        res_json["data"]["players"][0], fail = find_exact_matches(res_json["data"]["players"],
                                                                                  p["nickname"])
                    if fail:
                        payload["name"] = p["slug"].replace("-", " ")
                        res = helper.requests.post(url, data = payload, headers = h)
                        if res.status_code == 200:
                            res_json = res.json()
                            if len(res_json["data"]["players"]) >= 1:
                                res_json["data"]["players"][0], fail = find_exact_matches(res_json["data"]["players"],
                                                                                          p["slug"].replace("-", " "))
                            if fail:
                                faulty.append(p["id_marca"] + ", " + p["full_name"] + ", " + p["nickname"] + ", " +
                                              p["slug"])
                                print(p["id_marca"], p["full_name"])
                            else:
                                final_player = res_json["data"]["players"][0]
                    else:
                        final_player = res_json["data"]["players"][0]
            else:
                final_player = res_json["data"]["players"][0]
            if final_player is not None:
                found_player = player_md.find_player(int(final_player["id"]))
                found_player.id_marca = int(p["id_marca"])
        progress_bar.update(1)
    progress_bar.close()
    return faulty, player_md


@helper.deprecated(action = "ignore")
def player_movements(h: dict, m: helper.Movements, p_id: list, url: str):
    for p in p_id:
        payload = {"post": "players", "id": p}
        res = helper.requests.post(url, data = payload, headers = h).json()
        for r in res["data"]["owners"]:
            m.add_movement(str(r["from"]), str(r["to"]), str(r["transferType"]), str(r["date"]), str(r["price"]))
    return m


def extract_market(h: dict):
    url = "https://mister.mundodeportivo.com/ajax/sw"
    payload = {"post": "offer"}
    response = helper.requests.post(url, data = payload, headers = h)
    soup = helper.BeautifulSoup(response.text, "html.parser")

    # Encontrar la tabla de jugadores por su ID
    market_players_table = soup.find("table", {"id": "list-on-sale"})

    # Extraer el ID del equipo completo
    whole_team_id = helper.extract_player_id(market_players_table)

    # Encontrar todos los iconos de jugadores
    market_players_icons = market_players_table.find_all("div", {"class": "icons"})

    # Encontrar todas las filas de información de jugadores
    market_players_info = market_players_table.find_all("tr", {"class": "player-row"})

    # Llamar a la función para scrape de información de jugadores
    players = helper.scrape_player_info("m", market_players_info, market_players_icons, whole_team_id)

    # ------ Start process to save all the information in a CSV. ------
    market_structure_header = ["ID", "Points", "Market value", "Average value", "Ante penultimate match score",
                               "Penultimate match score", "Last match score", "Attempt to buy", "Position"]
    helper.write_to_csv("test-api-player-in-market", market_structure_header, players, "w")


def extract_balance(h: dict, url: str):
    response = helper.requests.post(url, data = {}, headers = h)
    if response.status_code == 200:
        return {"balance": response.json()["data"]["balance"], "future balance": response.json()["data"]["future"],
                "max debt": response.json()["data"]["max_debt"]}
    return None


mariadb = helper.create_database_connection()
cursor1 = mariadb.cursor(buffered = True)
cursor2 = mariadb.cursor(buffered = True)
ai_list = helper.AIModel()
users_list = helper.Users()
players_list = helper.Players()
gameweeks_list = helper.Games()
absences_list = helper.Absences()
price_variations_list = helper.PriceVariations()
predictions_points_list = helper.PredictionPoints()
user_recommendation_list = helper.UserRecommendations()
global_recommendation_list = helper.GlobalRecommendations()

empty = True
try:
    cursor1.execute("SELECT * FROM league_user;")
    cursor2.execute("SELECT * FROM global_recommendation;")
    if len(cursor1.fetchall()) == 0 and len(cursor2.fetchall()) == 0:
        empty = True
    else:
        empty = False
except helper.mysql.connector.Error as err:
    if "doesn\'t exist" in err.msg and err.errno == 1146:
        try:
            multi_stmt_insert("pc2-database.sql", True, True, mariadb)
            empty = True
            mariadb.commit()
        except Exception as err:
            print(err)
finally:
    cursor1.close()
    cursor2.close()
    mariadb.close()

user, password = "uem.ua2c@gmail.com", "uruguaychina"
md_balance_url = "https://mister.mundodeportivo.com/ajax/balance"
md_gw_url = "https://mister.mundodeportivo.com/ajax/player-gameweek"
md_sw_url = "https://mister.mundodeportivo.com/ajax/sw"
md_team_url = "https://mister.mundodeportivo.com/team"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 " \
             "Safari/537.36"

headers = {"Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest", "User-Agent": user_agent}

new_header = extract_auth(headers, user_agent, user, password)

request_timeout = 30

marca_header = {"User-Agent": user_agent, "Origin": "https://fantasy.laliga.com", "Referer":
                "https://fantasy.laliga.com/", "X-App": "Fantasy-web", "X-Lang": "es"}


if empty:
    users_list.add_user(1010, team_name = "Mister")
    extract_all_players_value_and_gw_md(user, password, new_header, ai_list, absences_list, gameweeks_list,
                                        players_list, price_variations_list, users_list, md_sw_url, md_gw_url)
else:
    users_list.fill_from_database(), players_list.fill_from_database(), gameweeks_list.fill_from_database(),
    absences_list.fill_from_database(), price_variations_list.fill_from_database(),
    predictions_points_list.fill_from_database(), user_recommendation_list.fill_from_database(),
    global_recommendation_list.fill_from_database()

# extract_market(new_header, md_ajax_url)

failed_img = extract_marca_img(marca_header, request_timeout)
# y = extract_marca_all_p_id(marca_header, request_timeout)
# unkown, player_list = find_id_marca_to_md(new_header, y, players_list, md_sw_url)

all_i_tables = [users_list.to_insert_statements(), players_list.to_insert_statements(),
              gameweeks_list.to_insert_statements(), absences_list.to_insert_statements(),
              price_variations_list.to_insert_statements()]
# all_u_tables = [users_list.to_insert_statements(), players_list.to_insert_statements(),
#               gameweeks_list.to_insert_statements(), absences_list.to_insert_statements(),
#               price_variations_list.to_insert_statements()]

if helper.path.exists(helper.path.join(route.scrape_folder, "insert_statements.sql")):
    helper.remove(helper.path.join(route.scrape_folder, "insert_statements.sql"))
with open(helper.path.join(route.scrape_folder, "insert_statements.sql"), mode = "w", newline = "",
          encoding = "utf-8") as f:
    for table in all_i_tables:
        for row in table:
            f.write(row + "\n")

# if helper.path.exists(route.scrape_folder + "update_statements.sql"):
#     helper.remove(route.scrape_folder + "update_statements.sql")
# with open(route.scrape_folder + "update_statements.sql", mode = "w", newline = "", encoding = "utf-8") as f:
#     for table in all_u_tables:
#         for row in table:
#             f.write(row + "\n")

mariadb = helper.create_database_connection()
cursor = mariadb.cursor(buffered = True)
multi_stmt_insert(route.scrape_folder + "insert_statements.sql", False, True, cursor)
# multi_stmt_insert(route.scrape_folder + "update_statements.sql", False, True, cursor)
mariadb.commit()
mariadb.close()

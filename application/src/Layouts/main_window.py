# !/usr/bin/env python3

# -*- coding: utf-8 -*-
# main_window.py

#

import application.src.Functions.main_predictions as main_p
import Utils.helper as helper
import Utils.routes as route


def filter_df(archivo_csv, lista):
    df = helper.pandas.read_csv(archivo_csv)

    filtered = df[df.iloc[:, 0].isin(lista)]

    return filtered


def read_personal_team(nombre_archivo):
    try:
        df = []
        for i in [route.app_personal_team_file, route.app_personal_market_file]:
            df.append(helper.pandas.read_csv(helper.path.join(route.users_folder, nombre_archivo + "_" + i)))

        with open(helper.path.join(route.users_folder,
                                   nombre_archivo + "_" + route.app_personal_team_file), "r") as file:
            reader = helper.csv.reader(file)
            list_id = [fila[0] for fila in reader]
        return df[0], df[1], list_id
    except Exception as e:
        helper.pSG.popup_error(f"Error al leer el archivo CSV: {e}")
        return None, None


def tab_layout(dataframe, typ):
    datos = []

    if dataframe is not None:
        if typ == "team":
            datos.append([dataframe.columns[0], dataframe.columns[1], dataframe.columns[2], dataframe.columns[3],
                          dataframe.columns[5], dataframe.columns[6]])
        elif typ == "market":
            datos.append([dataframe.columns[0], dataframe.columns[1], dataframe.columns[2], dataframe.columns[3],
                          dataframe.columns[4], dataframe.columns[6], dataframe.columns[7], dataframe.columns[8]])

        for _, row in dataframe.iterrows():
            fila = None
            if typ == "team":
                fila = [row["ID"], row["Name"], row["Market value"], row["Average value"],
                        row["Penultimate match score"], row["Last match score"]]
            elif typ == "market":
                fila = [row["ID"], row["Points"], row["Full name"], row["Market value"],
                        row["Average value"], row["Penultimate match score"], row["Last match score"],
                        row["Attempt to buy"]]
            datos.append(fila)

    return datos


def test_tab(u):
    def merger(input1, input2, output):
        with open(input1, "r") as file1:
            lines1 = file1.read().splitlines()

        # Leer el contenido del segundo archivo
        with open(input2, "r") as file2:
            lines2 = file2.read().splitlines()

        # Crear un diccionario para almacenar la información del segundo archivo
        data_dict = {}
        for line in lines2:
            parts = line.split(",")
            if len(parts) == 2:
                key = int(parts[0])
                value = int(float(parts[1]))
                data_dict[key] = value

        # Combina la información de ambos archivos
        result = [lines1[0]]
        for line1 in lines1[1:]:
            key = line1
            if int(key) in data_dict.keys():
                result.append(f"{key}, {data_dict[int(key)]}")
            else:
                result.append(key)

        with open(output, "w", newline = "") as csv_file:
            csv_file.writelines(", ".join([row]) + "\n" for row in result)

    helper.pSG.theme_add_new("MyCustomTheme", helper.custom_colours())

    helper.pSG.theme("MyCustomTheme")

    height, width = (((helper.pSG.Window.get_screen_size()[1] // 100) * 100) - 50), \
                    (((helper.pSG.Window.get_screen_size()[0] // 100) * 100) - 50)

    fantasy_lineups = [[4, 4, 2], [4, 5, 1], [4, 3, 3], [3, 4, 3], [3, 5, 2], [5, 4, 1], [5, 3, 2]]

    main_p.best_lineup_my_team(u, fantasy_lineups, route.players_predictions_mundo_deportivo, "mundo_deportivo")
    main_p.best_lineup_my_team(u, fantasy_lineups, route.players_predictions_sofascore, "sofascore")
    main_p.best_lineup_market(u, fantasy_lineups, route.players_predictions_mundo_deportivo, "mundo_deportivo")
    main_p.best_lineup_market(u, fantasy_lineups, route.players_predictions_sofascore, "sofascore")

    merger_list = [[route.op_my_team_md, route.op_my_team_p_md, route.merge_my_team_md],
                   [route.op_my_team_ss, route.op_my_team_p_ss, route.merge_my_team_ss],
                   [route.op_market_md, route.op_market_p_md, route.merge_market_md],
                   [route.op_market_ss, route.op_market_p_ss, route.merge_market_ss]]

    index = route.index_current_path + str(height) + str(width) + ".png"
    my_team_md = route.my_team_md_img + str(height) + str(width) + ".png"
    market_md = route.my_team_ss_img + str(height) + str(width) + ".png"
    my_team_ss = route.market_md_img + str(height) + str(width) + ".png"
    market_ss = route.market_ss_img + str(height) + str(width) + ".png"

    for i in merger_list:
        merger(i[0], i[1], i[2])

    o_list = [route.merge_my_team_md, route.merge_market_md, route.merge_my_team_ss,
              route.merge_market_ss]
    i_list = [my_team_md, market_md, my_team_ss, market_ss]

    helper.create_image(route.current_alignment, index.split(".png")[0], True, (width // 3), (height - 80))

    for i in i_list:
        helper.create_image(o_list[i_list.index(i)], i.split(".png")[0], True, (width // 2), (height - 80))

    team_df, market_df, team_list = read_personal_team(u)
    data_team = tab_layout(team_df, "team")
    data_market = tab_layout(market_df, "market")

    tab1_layout = [
        [
            helper.pSG.Column([
                [helper.pSG.Image(filename = index, key = "personal_team")]
            ], element_justification = "center", size = ((width // 3), height)),
            helper.pSG.Column([[helper.pSG.Table(values = data_team[1:], auto_size_columns = True,
                                                 headings = data_team[0], display_row_numbers = False,
                                                 justification = "center", num_rows = min(25, len(data_team) - 1),
                                                 enable_events = True, expand_x = True, expand_y = True,
                                                 enable_click_events = True, alternating_row_color = "green",
                                                 selected_row_colors = "green on black", key = "-TABLE1-")],
                               [helper.pSG.Image(filename = None, key = "team_values")]],
                              element_justification = "left", size = (2 * (width // 3), height))
        ]
    ]

    tab2_layout = [[
            helper.pSG.Column([
                [helper.pSG.Text("Predicción de equipo con jugadores en plantilla.")],
                [helper.pSG.Image(filename = my_team_ss, key = "personal_team_s")]
            ], element_justification = "center", size = (width // 2, height)),
            helper.pSG.Column([
                [helper.pSG.Text("Predicción de equipo con jugadores en plantilla y jugadores de mercado.")],
                [helper.pSG.Image(filename = market_ss, key = "market_team_s")]
            ], element_justification = "center", size = (width // 2, height))
        ]
    ]

    tab3_layout = [[
            helper.pSG.Column([
                [helper.pSG.Text("Predicción de equipo con jugadores en plantilla")],
                [helper.pSG.Image(filename = my_team_md, key = "personal_team_m")]
            ], element_justification = "center", size = (width // 2, height)),
            helper.pSG.Column([
                [helper.pSG.Text("Predicción de equipo con jugadores en plantilla y jugadores de mercado.")],
                [helper.pSG.Image(filename = market_md, key = "market_team_m")]
            ], element_justification = "center", size = (width // 2, height))
        ]]

    tab4_layout = [
        [helper.pSG.Table(values = data_market[1:], auto_size_columns = True, headings = data_market[0],
                          display_row_numbers = False, justification = "center",
                          num_rows = min(25, len(data_market) - 1), enable_events = True, expand_x = True,
                          expand_y = False, enable_click_events = True, alternating_row_color = "green",
                          selected_row_colors = "green on black", key = "-TABLE2-")],
        [helper.pSG.Image(filename = None, key = "market_values")]
    ]

    # Diseño principal con pestañas
    layout = [
        [helper.pSG.TabGroup([
            [helper.pSG.Tab("Mi equipo", tab1_layout, element_justification = "center", key = "tab1")],
            [helper.pSG.Tab("Predicción ideal Sofascore", tab2_layout, element_justification = "center", key = "tab2")],
            [helper.pSG.Tab("Predicción ideal Mundo Deportivo", tab3_layout, element_justification = "center",
                            key = "tab3")],
            [helper.pSG.Tab("Predicciones de valor jugadores de mercado", tab4_layout, element_justification = "center",
                            key = "tab4")]
        ], enable_events = True, key = "-TABS-", size = (width, (height - 50)))]
    ]

    window = helper.pSG.Window("UA2C", layout, location = (20, 20), size = (width, height))

    return window, data_team, data_market, width

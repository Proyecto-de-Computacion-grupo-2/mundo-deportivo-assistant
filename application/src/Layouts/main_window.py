# !/usr/bin/env python3

# -*- coding: utf-8 -*-
# main_window.py

#

import application.src.Functions.main_predictions as main_p
import Utils.helper as helper
import Utils.routes as route


def filter_df(archivo_csv, lista):
    # Lee el CSV completo en un DataFrame
    df = helper.pandas.read_csv(archivo_csv)

    # Filtra el DataFrame basado en la lista proporcionada
    filtered = df[df.iloc[:, 0].isin(lista)]

    return filtered


def read_personal_team(nombre_archivo):
    # Lee el CSV usando pandas y devuelve un DataFrame
    try:
        df = helper.pandas.read_csv(helper.path.join(route.users_folder, nombre_archivo + "_" +
                                                     route.app_personal_team_file))

        with open(helper.path.join(route.users_folder,
                                   nombre_archivo + "_" + route.app_personal_team_file), "r") as file:
            reader = helper.csv.reader(file)
            list_id = [fila[0] for fila in reader]
        return df, list_id
    except Exception as e:
        helper.pSG.popup_error(f"Error al leer el archivo CSV: {e}")
        return None, None


def tab_layout(dataframe):
    datos = []

    if dataframe is not None:
        # Agrega la cabecera del CSV como etiquetas de texto
        encabezado = [col for col in dataframe.columns]
        datos.append(encabezado)

        # Agrega una lista de Listbox para cada fila de datos
        for _, row in dataframe.iterrows():
            fila = [row["ID"], row["Name"], row["Market value"], row["Average value"],
                    row["Ante penultimate match score"], row["Penultimate match score"], row["Last match score"]]
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

    height, width = (((helper.pSG.Window.get_screen_size()[1] // 100) * 100) - 100), \
                    (((helper.pSG.Window.get_screen_size()[0] // 100) * 100) - 100)

    fantasy_lineups = [[4, 4, 2], [4, 5, 1], [4, 3, 3], [3, 4, 3], [3, 5, 2], [5, 4, 1], [5, 3, 2]]

    main_p.best_lineup_my_team(fantasy_lineups, route.players_predictions_mundo_deportivo, "mundo_deportivo")
    main_p.best_lineup_my_team(fantasy_lineups, route.players_predictions_sofascore, "sofascore")
    main_p.best_lineup_market(fantasy_lineups, route.players_predictions_mundo_deportivo, "mundo_deportivo")
    main_p.best_lineup_market(fantasy_lineups, route.players_predictions_sofascore, "sofascore")

    merger_list = [[route.op_my_team_md, route.op_my_team_p_md, route.merge_my_team_md],
                   [route.op_my_team_ss, route.op_my_team_p_ss, route.merge_my_team_ss],
                   [route.op_market_md, route.op_market_p_md, route.merge_market_md],
                   [route.op_market_ss, route.op_market_p_ss, route.merge_market_ss]]
    for i in merger_list:
        merger(i[0], i[1], i[2])

    helper.create_image(route.current_alignment, route.index_current_path + str(height) + str(width), True,
                        (width // 3), (height - 80))
    helper.create_image(route.merge_my_team_md, route.my_team_md_img + str(height) + str(width), True,
                        ((width // 2) - 100), (height - 100))
    helper.create_image(route.merge_my_team_ss, route.my_team_ss_img + str(height) + str(width), True,
                        ((width // 2) - 100), (height - 100))
    helper.create_image(route.merge_market_md, route.market_md_img + str(height) + str(width), True,
                        ((width // 2) - 100), (height - 100))
    helper.create_image(route.merge_market_ss, route.market_ss_img + str(height) + str(width), True,
                        ((width // 2) - 100), (height - 100))

    index = route.index_current_path + str(height) + str(width) + ".png"
    my_team_md = route.my_team_md_img + str(height) + str(width) + ".png"
    market_md = route.my_team_ss_img + str(height) + str(width) + ".png"
    my_team_ss = route.market_md_img + str(height) + str(width) + ".png"
    market_ss = route.market_ss_img + str(height) + str(width) + ".png"

    team_df, team_list = read_personal_team(u)
    data = tab_layout(team_df)

    tab1_layout = [
        [
            helper.pSG.Column([
                [helper.pSG.Image(filename = index, key = "personal_team")]
            ], element_justification = "center", size = ((width // 3), height)),
            helper.pSG.Column([[helper.pSG.Table(values = data[1:], auto_size_columns = True, headings = data[0],
                                                 display_row_numbers = False, justification = "center",
                                                 num_rows = min(25, len(data) - 1), enable_events = True,
                                                 expand_x = True, expand_y = False, enable_click_events = True,
                                                 alternating_row_color = "red", selected_row_colors = "green on black",
                                                 key = "-TABLE-")]],
                              element_justification = "center", size = (2 * (width // 3), height)),
        ]
    ]

    tab2_layout = [[
            helper.pSG.Column([
                [helper.pSG.Text("Personal Team Title")],
                [helper.pSG.Image(filename = my_team_ss, key = "personal_team_s")]
            ], element_justification = "center", size = (width // 2, height), background_color = "green"),
            helper.pSG.Column([
                [helper.pSG.Text("Market Team Title")],
                [helper.pSG.Image(filename = market_ss, key = "market_team_s")]
            ], element_justification = "center", size = (width // 2, height), background_color = "red")
        ]
    ]

    tab3_layout = [[
            helper.pSG.Column([
                [helper.pSG.Text("Personal Team Title")],
                [helper.pSG.Image(filename = my_team_md, key = "personal_team_m")]
            ], element_justification = "center", size = (width // 2, height), background_color = "red"),
            helper.pSG.Column([
                [helper.pSG.Text("Market Team Title")],
                [helper.pSG.Image(filename = market_md, key = "market_team_m")]
            ], element_justification = "center", size = (width // 2, height), background_color = "green")
        ]]

    tab4_layout = [
        [helper.pSG.Text("Contenido inicial de la pestaña 4", key = "tab4_text")],
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
        ], enable_events = True, key = "-TABS-", size = (width, (height - 50)))],
        [helper.pSG.Button("Salir")]
    ]

    window = helper.pSG.Window("Ejemplo de Pestañas en PySimpleGUI", layout, background_color = "yellow",
                               location = (10, 10), size = (width, height))

    return window, data

# !/usr/bin/env python3

# -*- coding: utf-8 -*-
# main_window.py

#

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

    custom_theme = {
        "BACKGROUND": "#D9D9D9",
        "TEXT":       "#000000",
        "INPUT":      "#ffffff",
        "TEXT_INPUT": "#000000",
        "SCROLL":     "#D9D9D9",
        "BUTTON":     ("#000000", "#ffffff"),
        "PROGRESS":   ("#01826B", "#D0D0D0"),
        "BORDER":     1, "SLIDER_DEPTH": 0, "PROGRESS_DEPTH": 0
    }

    helper.pSG.theme_add_new("MyCustomTheme", custom_theme)

    helper.pSG.theme("MyCustomTheme")

    height, width = (((helper.pSG.Window.get_screen_size()[1] // 100) * 100) - 100), \
                    (((helper.pSG.Window.get_screen_size()[0] // 100) * 100) - 100)
    # Definir el contenido de las pestañas
    helper.create_image(route.current_alignment, route.index_current_path + str(height) + str(width), True,
                        (width // 3), (height - 80))
    helper.create_image(route.current_alignment, route.current_path + str(height) + str(width), True,
                        ((width // 2) - 100), (height - 100))
    helper.create_image(route.future_alignment, route.recommendation_path + str(height) + str(width), True,
                        ((width // 2) - 100), (height - 100))

    index = route.index_current_path + str(height) + str(width) + ".png"
    current = route.current_path + str(height) + str(width) + ".png"
    recommendation = route.recommendation_path + str(height) + str(width) + ".png"

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
                [helper.pSG.Image(filename = current, key = "personal_team_s")]
            ], element_justification = "center", size = (width // 2, height), background_color = "green"),
            helper.pSG.Column([
                [helper.pSG.Text("Market Team Title")],
                [helper.pSG.Image(filename = recommendation, key = "market_team_s")]
            ], element_justification = "center", size = (width // 2, height), background_color = "red")
        ]
    ]

    tab3_layout = [[
            helper.pSG.Column([
                [helper.pSG.Text("Personal Team Title")],
                [helper.pSG.Image(filename = current, key = "personal_team_m")]
            ], element_justification = "center", size = (width // 2, height), background_color = "red"),
            helper.pSG.Column([
                [helper.pSG.Text("Market Team Title")],
                [helper.pSG.Image(filename = recommendation, key = "market_team_m")]
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

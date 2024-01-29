import csv
import time

from time import sleep

# from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


def obtener_datos_personales(drive, url, w):
    datos_personales = []
    for jug in url:
        drive.get(jug)
        try:
            datos_pers = w.until(
                ec.presence_of_element_located((By.XPATH, '//div[@class="styled__TableData-sc-yr5r72-13 jQgbxa"]')))
            fn = datos_pers.find_element(By.XPATH,
                                         './/div[@class="styled__TableDataCell-sc-yr5r72-14 jGwTZz cell-birth"]')
            altura = datos_pers.find_element(By.XPATH,
                                             './/div[@class="styled__TableDataCell-sc-yr5r72-14 jGwTZz cell-height"]')
            peso = datos_pers.find_element(By.XPATH,
                                           './/div[@class="styled__TableDataCell-sc-yr5r72-14 jGwTZz cell-weight"]')
            posicion = datos_pers.find_element(By.XPATH, '//p[@class="styled__TextRegularStyled-sc-1raci4c-0 fiTkPc"]')
            datos_personales.append([fn.text.split("\n")[1], altura.text.split("\n")[1].split(" ")[0],
                                     peso.text.split("\n")[1].split(" ")[0], posicion.text])
        except TimeoutException:
            print(jug)
            datos_personales.append(["0", "0", "0", "0"])
    return datos_personales


time_start = int(time.time())

# Configura el navegador (en este caso, Firefox)
firefox_options = webdriver.FirefoxOptions()
#firefox_options.add_argument("--headless")  # Esta línea oculta el navegador
driver = webdriver.Firefox(options = firefox_options)

# Abre la URL
driver.get("https://www.laliga.com/estadisticas-avanzadas")

# Espera a que se cargue el contenido (puedes ajustar el tiempo de espera según sea necesario)
wait = WebDriverWait(driver, 10)

elements = driver.find_elements("css selector", "p.styled__TextRegularStyled-sc-1raci4c-0.kzAXGN")


num = []

# Now, you can iterate over "elements" and extract the desired data
for element in elements:
    if element.text.isdigit():
        num.append(int(element.text))

# Inicializa una lista para almacenar los datos por categoría
categorias = ["Clásicas", "Eficiencia", "Disciplina", "Ataques", "Defensivas"]
categoria_pers, enlaces_jugadores = ["Fecha de nacimiento", "Altura (cm)", "Peso (kg)", "Posición"], []
datos_por_categoria = {categoria: [] for categoria in categorias}

c, c_max, categoria_actual_index, i = 1, max(num), 0, 0

while c < c_max:

    # Itera a través de las categorías
    while i < 5:
        # Encuentra el selector de categorías
        selector_categorias = driver.find_elements(By.CSS_SELECTOR, 'ul[class^="styled__ItemsList-sc-d9k1bl-"]')
        # visualizar_categorias = driver.find_element(By.XPATH,
        #                                             '//div[@class="styled__BreadCrumbContainer-sc-zvm62g-0 jOpRUj"]')

        # Selecciona la categoría actual
        if c == 1:
            # Realiza un scroll hacia arriba de la página
            # driver.execute_script("window.scrollTo(0, 0);")

            driver.execute_script(f"arguments[0].click();",
                                  driver.find_element(By.CSS_SELECTOR, 'ul[class^="styled__ItemsList-sc-d9k1bl-"]'))
            categoria_selector = wait.until(ec.element_to_be_clickable(
                (By.XPATH, f'//li[contains(@class, "styled__Item-sc-d9k1bl-3") and text()="{categorias[i]}"]')))

            # Usa ActionChains para mover el cursor sobre el elemento antes de hacer click.
            # sleep(0.5)
            # ActionChains(driver).move_to_element(categoria_selector).perform()
            # sleep(0.5)

            driver.execute_script("arguments[0].click();", categoria_selector)

        # Espera a que se cargue la tabla
        tabla = wait.until(
            ec.presence_of_element_located((By.XPATH, '//table[@class="styled__TableStyled-sc-57jgok-1 kvoOOd"]')))
        # driver.execute_script("arguments[0].scrollIntoView(true);", tabla)

        if c == 1:
            # Encuentra todas las filas de la tabla.
            filas = tabla.find_elements(By.TAG_NAME, "th")
            nombres_cabecera = []
            for fila in filas:

                if fila.get_dom_attribute("data-tip"):
                    nombres_cabecera.append(fila.get_dom_attribute("data-tip"))
            datos_por_categoria[categorias[i]].append(nombres_cabecera)

        # Recorre todas las filas y obtiene los datos de cada celda.
        filas = tabla.find_elements(By.TAG_NAME, "tr")
        for fila in filas:
            celdas = fila.find_elements(By.TAG_NAME, "td")
            fila_datos = []
            for celda in celdas:
                try:
                    elemento_a = celda.find_element(By.XPATH, './/a[@class="link"]')
                    enlace_href = elemento_a.get_attribute("href")
                    if "jugador" in enlace_href and enlace_href not in enlaces_jugadores:
                        enlaces_jugadores.append(enlace_href)
                except NoSuchElementException:
                    pass
                fila_datos = [celda.text]
                if fila_datos:
                    datos_por_categoria[categorias[i]].append(fila_datos[1:])

        # Incrementa página (c).
        c += 1
        if c != 30:
            elemento = wait.until(ec.visibility_of_element_located(
                (By.XPATH, '//div[@class="styled__PaginationArrow-sc-1c62lz0-5 dTBfXp"]')))
            driver.execute_script("arguments[0].scrollIntoView(true);", elemento)
            driver.execute_script("arguments[0].click();", elemento)
            sleep(0.8)
        else:
            # Pasa a la siguiente categoría y resetea a la primera página.
            c, i = 1, i + 1
    if i == 5:
        c = c_max + 1

dato_categoria_pers = obtener_datos_personales(driver, enlaces_jugadores, wait)

# Cierra el navegador al finalizar
driver.quit()

# Crear una lista única de encabezado a partir de las claves.
encabezado_1 = categoria_pers
encabezado_2 = datos_por_categoria["Clásicas"][0][1:]
encabezado_3 = datos_por_categoria["Eficiencia"][0][2:]
encabezado_4 = datos_por_categoria["Disciplina"][0][2:]
encabezado_5 = datos_por_categoria["Ataques"][0][2:]
encabezado_6 = datos_por_categoria["Defensivas"][0][2:]
encabezado = []
for i in encabezado_1:
    print(i)
for i in encabezado_2:
    print(i)
for i in encabezado_3:
    print(i)
for i in encabezado_4:
    print(i)
for i in encabezado_5:
    print(i)
for i in encabezado_6:
    print(i)

todos_los_jugadores = []
dato_por_jugador = dato_categoria_pers.copy()

for categoria in categorias:
    max_longitud = len(datos_por_categoria[categoria])
    for i in range(1, max_longitud):
        if categoria == "Clásicas":
            dato_por_jugador.extend(datos_por_categoria[categoria][i][1:])
        else:
            dato_por_jugador.extend(datos_por_categoria[categoria][i][2:])
    todos_los_jugadores.append(dato_por_jugador)

for jugador in todos_los_jugadores:
    # Crea un archivo CSV con el nombre del jugador.
    with open(f'jugadores/{jugador[0].replace(" ", "_")}.csv', "w", newline = "") as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        # Escribe el encabezado en el archivo CSV
        escritor_csv.writerow(encabezado)
        # Escribe los datos en el archivo CSV
        escritor_csv.writerow(jugador)

print(str((time.time() - time_start) / 60) + " minutos")

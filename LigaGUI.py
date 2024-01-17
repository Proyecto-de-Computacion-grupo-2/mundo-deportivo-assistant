# !/usr/bin/env python3

# -*- coding: utf-8 -*-
# LigaGUI.py

#

import Utils.helper as helper
import Utils.routes as route

from scrape.fantasy_teams import scrape_personal_team_fantasy
from scrape.market import scrape_market_section_fantasy


def custom_login(user, pwd):
    helper.makedirs(helper.path.dirname(route.root_folder + "temp_file"), exist_ok = True)

    chrome_options = helper.webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    driver = helper.webdriver.Chrome(options = chrome_options)

    # firefox_options = helper.webdriver.FirefoxOptions()
    # firefox_options.add_argument("--headless")
    # driver = helper.webdriver.Firefox(options = firefox_options)

    driver.set_page_load_timeout(300)

    navigation_to = True
    while navigation_to:
        try:
            driver.get("https://mister.mundodeportivo.com/new-onboarding/auth/email")
            navigation_to = False
        except helper.TimeoutException:
            helper.sleep(2)
            pass

    # Wait for the cookies to appear and click the button to deny them.
    helper.sleep(helper.uniform(0.4, 0.6))
    intercept = True
    while intercept:
        try:
            disagree = helper.wait_click(driver, (helper.By.ID, "didomi-notice-disagree-button"), 4)
            if disagree:
                disagree.click()
            intercept = False
        except (helper.ElementClickInterceptedException, helper.StaleElementReferenceException):
            helper.sleep(6)
            intercept = True
        except helper.NoSuchElementException:
            pass

    # Enter the email and password.
    email_input = driver.find_element(helper.By.ID, "email")
    email_input.send_keys(user)

    password_input = driver.find_element(helper.By.XPATH, '//*[@id="app"]/div/div[2]/div/form/div[2]/input')
    password_input.send_keys(pwd)

    # Click on the login button.
    submit_button = helper.wait_click(driver, (helper.By.XPATH, '//*[@id="app"]/div/div[2]/div/form/div[3]/button'), 2)
    if submit_button:
        submit_button.click()

    if email_input.get_attribute("class") == "error":
        driver.quit()
        return True
    else:
        helper.skip_button(driver, (helper.By.CLASS_NAME, "btn-tutorial-skip"))

        helper.sleep(helper.uniform(0.4, 0.8))

        scrape_personal_team_fantasy(True, driver, user)

        helper.sleep(helper.uniform(0.4, 0.8))

        scrape_market_section_fantasy(True, driver, user)

        driver.quit()

        return False


login = helper.login_window.login()
c, chosen_gif, event, incorrect, mostrar_password, u = None, None, "Aceptar", True, False, None

while event != "Aceptar" and event != helper.WIN_CLOSED:
    if event == "inc":
        login = helper.login_window.login()
    event, values = login.read()
    if event == "Mostrar":
        mostrar_password = not mostrar_password
        if mostrar_password:
            login["pass"].update(password_char = "")
        else:
            login["pass"].update(password_char = "*")
    elif event == "Iniciar Sesión":
        if values["user"] and values["pass"]:
            event = "inc"
            u = values["user"]
            c = values["pass"]
            login.close()
            helper.pSG.popup_no_buttons("Checking credentials and downloading data...please be patient...",
                                        auto_close = True, auto_close_duration = 4)
            incorrect = custom_login(u, c)
            if not incorrect:
                event = "Aceptar"
            else:
                helper.pSG.popup_no_buttons("Wrong credentials, try again.", auto_close = True, auto_close_duration = 2)
        else:
            if values["user"] == "":
                login["user"].set_focus()
            elif values["pass"] == "":
                login["pass"].set_focus()

u = "uem.ua2c@gmail.com"
window, datos_team, datos_market, w = helper.main_window.test_tab(u)

# Bucle principal
k = 0
while True:
    event, values = window.read()
    if event == helper.pSG.WIN_CLOSED or event == 'Salir':
        break
    elif "+CLICKED+" in event and "-TABLE1-" in event:
        if not any(ext in event[2] for ext in [-1, None]):
            new_size = (2 * (w // 3)) - 50
            img = helper.Image.open(helper.path.join(route.plots_folder, str(datos_market[(event[2][0] + 1)][0]) +
                                                     "_market_value_prediction_plot.png"))
            helper.image_resize(img, new_size, helper.path.join(route.temp_img_show))
            window["team_values"].update(filename = helper.path.join(route.temp_img_show))
    elif "+CLICKED+" in event and "-TABLE2-" in event:
        if not any(ext in event[2] for ext in [-1, None]):
            window["market_values"].update(filename = helper.path.join(route.plots_folder,
                                                                       str(datos_market[(event[2][0] + 1)][0]) +
                                                                       "_market_value_prediction_plot.png"))

    k += 1
window.close()

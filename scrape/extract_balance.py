from UA2C import helper as helper, routes as route


mariadb = helper.create_database_connection(False)
cursor = mariadb.cursor(buffered = True)
users_list = helper.Users()
try:
    cursor.execute("SELECT * FROM league_user;")
    users = cursor.fetchall()
    for user in users:
        users_list.add_user(user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7], user[8], user[9],
                            user[10], user[11], user[12])
except helper.mysql.connector.Error as err:
    print(err)

md_balance_url = "https://mister.mundodeportivo.com/ajax/balance"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 " \
             "Safari/537.36"

headers = {"Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest", "User-Agent": user_agent}

while True:
    for user in users_list:
        if (user.email is not None and user.email != "") and (user.password is not None and user.password != ""):
            if any(ext == user.id_user for ext in [12705845]):
                clear_pass = helper.decrypt_pgp(user.password.encode("utf-8"))
                new_header = helper.extract_auth(headers, user_agent, user.email, clear_pass)
                user_balance = helper.extract_balance(new_header, md_balance_url)
                mariadb = helper.create_database_connection(False)
                cursor = mariadb.cursor(buffered = True)
                try:
                    cursor.execute("UPDATE league_user SET current_balance = %s, future_balance = %s,"
                                   "maximum_debt = %s WHERE id_user = %s", (user_balance["current_balance"],
                                                                            user_balance["future_balance"],
                                                                            user_balance["maximum_debt"], user.id_user))
                    mariadb.commit()
                    print('------')
                except helper.mysql.connector.Error as err:
                    print(err)
                helper.sleep(20)

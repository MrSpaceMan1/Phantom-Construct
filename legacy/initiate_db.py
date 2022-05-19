# import sqlite3
# db_conn = sqlite3.connect("botstorage.db")
#
# c = db_conn.cursor()
#
# c.execute("""CREATE TABLE""")
import json

with open("bot_data.json", "w") as file:
    json.dump({
        "rules": [],
        "ignored_channels": [123123123]
    }, file)

with open("bot_data.json", "r") as file:
    data = json.load(file)
    print(data)

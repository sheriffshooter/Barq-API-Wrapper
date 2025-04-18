from time import sleep
from random import randint
from barqAuth import BarqAuth
import json
import os

# This probably works and this was written before i started taking organization a little more seriously
# this will produce duplicates which is why you should clean the output using cleanJSON.py
# debug ssddddddfdfewsesdfesdfe

if __name__ == "__main__":
    auth = BarqAuth()
    auth.autoAuth()

    # auth.getLogins returns a list of accountRequestManagers
    account = auth.getLogins()[0]

    with open("City Sorting\\cityData.json", "r") as cityDataFile:
        cityDatas = json.load(cityDataFile)

    for city in cityDatas:
        cityName = next(iter(cityDatas[city]))
        cityInfo = cityDatas[city][cityName]

        currentUserCount = 0
        cursor = 0

        while True:
            users = account.getUsersByDistance((cityInfo["Lat"], cityInfo["Long"]), cursor=cursor, limit=limit, interests=["VRChat"])

            if len(users) == 0:

                break
            elif len(users["data"]["profiles"]) < 1:
                print("Ran out of profiles")

                break
            
            print(f"On file #{currentUserCount} ({cityName}), cursor: {cursor}")

            try:
                os.makedirs(f"users\\{cityName}\\", exist_ok=True)
                with open(f"users\\{cityName}\\{currentUserCount}.json", "w", encoding="utf-8") as jsonFile:
                    json.dump(users, jsonFile, indent=4)
            except:
                print("Json dump failed")

                break
            
            cursor = cursor + limit
            currentUserCount = currentUserCount + 1
            
            sleep(20 + randint(0, 3))

            if cursor > 1300:
                print(f"Cursor greator than 1000 on {cityName}")
                break

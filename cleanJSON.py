import json
import os

usersFolder = "users\\"
tempUsersFolder = "userstemp"

# this probably works, didnt read the code to make sure i didnt make any changes but ya good luck youll need it

# slow
def doesUserAlreadyExistInDataSet(uuid):
    for item in os.listdir(tempUsersFolder):
        if not os.path.isfile(os.path.join(tempUsersFolder, item)): continue

        with open(os.path.join(tempUsersFolder, item), "r", encoding="utf-8") as jsonFile:
            jsonFileData = json.load(jsonFile)
        
        for profile in jsonFileData["data"]["profiles"]:
            if profile["uuid"] == uuid:
                return True
          
    return False

uuids = []
jfn = 1
profilesWritten = 0
totaldupeuuid = 0
if __name__ == "__main__":
    outData =  {}
    outData["data"] = {}
    outData["data"]["profiles"] = []

    os.makedirs(tempUsersFolder, exist_ok=True)

    for cityFolder in os.listdir(usersFolder):
        if not os.path.isdir(os.path.join(usersFolder, cityFolder)): continue

        for userJson in os.listdir(os.path.join(usersFolder, cityFolder)):
            if not os.path.isfile(os.path.join(usersFolder, cityFolder, userJson)): continue

            with open(os.path.join(usersFolder, cityFolder, userJson), "r") as file:
                data = json.load(file)
            
            for profile in data["data"]["profiles"]:
                # slow
                #if doesUserAlreadyExistInDataSet(profile["uuid"]): continue
                if profile["uuid"] in uuids:
                    #with open("lol2.txt", "a", encoding="utf-8") as file:
                        #file.write(f"{profile['uuid']}:{profile['username']}:{profile['displayName']}\n")
                    
                    continue
                totaldupeuuid = totaldupeuuid + 1
                uuids.append(profile["uuid"])

                outData["data"]["profiles"].append(profile)
                profilesWritten = profilesWritten + 1

                if profilesWritten >= 1000:
                    with open(os.path.join(tempUsersFolder, str(jfn) + ".json"), "w", encoding="utf-8") as jsonFile:
                        json.dump(outData, jsonFile, indent=4)
                    
                    jfn = jfn + 1
                    profilesWritten = 0
                    outData["data"]["profiles"] = []
    print(totaldupeuuid)


                    
                    

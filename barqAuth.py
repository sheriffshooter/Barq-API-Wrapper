import requests
import os
from json import load, dump
from uuid import uuid4
from hashlib import md5
from accountRequestmanager import BarqUser

relPath = os.path.dirname(os.path.realpath(__file__))

class BarqAuth:
    generalHeaders = {
        "host": "api.barq.app",
        "user-agent": "BarqNext/2.6.0+236"
    }

    def __init__(self):
        self.logins = []
    
    def autoAuth(self, ignoreExistingLoginFiles=False, sessionAmountOveride=0): # Ignore existing login files if you want to create a new one with autoAuth
        loginFiles = self.__getLoginFilesinRelPath()

        if ignoreExistingLoginFiles or len(loginFiles) < 1:
            if (len(loginFiles) < 1): print("No barq login files were found.\n")

            if sessionAmountOveride == 0:
                amountOfLoginFilesToCreate = self.__getUserIntInput("How many login files would you like to make? ")
            else:
                amountOfLoginFilesToCreate = sessionAmountOveride
            
            for i in range(amountOfLoginFilesToCreate):
                print(f"Login file #{i + 1}: ")
                email = input("Email: ")
                authToken = "Bearer " + self.__loginToBarq(email)

                self.__writeToLoginFile(email, authToken)

                self.logins.append(BarqUser(email, authToken))
        else:
            print(f"Found {len(loginFiles)} login files!")

            # Barq is weird in the way they do not use session cookies but rather an auth header that does not need to be re-evulated when "logging in" (You dont actually log in after its been a while. I assume this token expires).
            for loginFile in loginFiles:
                email, auth = self.__getLoginFromFile(loginFile)

                if email == None and auth == None: continue
                
                self.logins.append(BarqUser(email, auth))

    def getLogins(self):
        return self.logins

    def __loginToBarq(self, email):
        res = requests.post("https://api.barq.app/account-provider/email/request-code", headers=self.generalHeaders, json={"email": email})

        if res.status_code == 200:
            print("Check email, code was sent!")
        else:
            print("Code was not send. Quitting.")
            print(res.status_code, res.text)
            quit()
        
        while True:
            data = {
                "email": email,
                "code": input("Code: ")
            }
            
            res = requests.post("https://api.barq.app/account-provider/email/login", headers=self.generalHeaders, json=data)
            
            if res.status_code == 200:
                print("Successfully logged in!")
                return res.json()

    def __getLoginFilesinRelPath(self):
        loginFiles = []

        for item in os.listdir(relPath):
            fulllItemPath = os.path.join(relPath, item)

            if os.path.isdir(fulllItemPath): continue

            if item[-4:] == "_BQA" and len(item) == 36: # Test this func
                loginFiles.append(fulllItemPath)
        
        return loginFiles
    
    def __getUserIntInput(self, prompt):
        while True:
            userInput = input(prompt)
            
            try:
                return int(userInput)
            except:
                print("Enter a number please.")

    def __generateHash(self, stringToHash: str):
        return md5(stringToHash.encode("utf-8")).hexdigest()

    def __writeToLoginFile(self, email, auth):
        try:
            with open(os.path.join(relPath, f"{self.__generateHash(email)}_BQA"), "w") as file:
                dump({"email": email, "authorization": auth}, file)
            print("Wrote to login file")
        except Exception as e:
            print("Error writing to file", e)

    def __getLoginFromFile(self, path):
        try:
            with open(path, "r") as file:
                fileContents = load(file)

                email = fileContents["email"]
                authToken = fileContents["authorization"]

                return (email, authToken)
        except Exception as e:
            print("Error getting login file:\n", e, "\n")

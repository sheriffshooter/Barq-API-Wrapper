import os
import json

class DBManager:
    def __init__(self, datasLocation):
        """Init
        
        Args:
            datasLocation: Location of the json datas"""
        
        self.datasLocation = datasLocation

    def enumFiles(self):
        """Enum through the json files. yields for each file."""

        for userJson in os.listdir(self.datasLocation):
            fullJsonFilePath = os.path.join(self.datasLocation, userJson)
            if not os.path.isfile(fullJsonFilePath): continue

            yield fullJsonFilePath
    
    def getUser(self, uuid=None, id=None, userName=None, displayName=None):
        """Finds user from either uuid, id, displayName, or userName"""

        filters = {
            "uuid": uuid,
            "id": id,
            "username": userName,
            "displayName": displayName
        }

        # Remove items that are None from filters
        filters = {key: value for key, value in filters.items() if value is not None}

        for jsonFile in self.enumFiles():
            with open(jsonFile, "r", encoding="utf-8") as file:
                profiles = json.load(file)["data"]["profiles"]
            
            for profile in profiles:
                allFiltersMatch = True

                for key in filters:
                    # If the item in the profile is not equal to the filter param then its not a match
                    if profile[key] != filters[key]:
                        allFiltersMatch = False
                        break

                if allFiltersMatch:
                    return profile
        
        # The profile was not found
        return None

            

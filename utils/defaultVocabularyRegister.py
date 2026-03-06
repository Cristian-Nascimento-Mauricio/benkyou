import json
from pathlib import Path
from repositories.configRepository import configRepository
from repositories.cardRepository import cardRepository

class  defaultVocabularyRegister:
    def __init__(self,pathJson,pathDB):
        self.pathJson = pathJson
        self.pathDB = pathDB
        self.configRepository = configRepository(pathDB)
        self.cardRepository = cardRepository(pathDB)
        pass

    def openJsonFile(self):
        for file in self.getFile():
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if self.check_version(data):
                    for item in data["content"]:
                        self.cardRepository.create_or_update_card(item["word"],data["category"],item["reading"],item["meaning"])
            
    def getFile(self):
        jsonPath = Path(self.pathJson)
        return list(jsonPath.glob("*.json"))

    def check_version(self,data):
        register = self.configRepository.get_by_key(f"cheap-{data['category']}")

        if register == None:
            self.configRepository.add("db",f"cheap-{data['category']}",data["version"])
            return True 

        current_version = list(map(int,register["value"].split(".")))
        new_version = list(map(int,data["version"].split(".") ))

        if(new_version > current_version):
            self.configRepository.update_value(f"cheap-{data['category']}",data["version"])
            return True
        
        return False
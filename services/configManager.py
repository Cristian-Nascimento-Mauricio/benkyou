from repositories.configRepository import configRepository

class configManager:
    def __init__(self,path):
        self.configRepository = configRepository(path)
        pass

    def update_range(self,value):
        if value >= 1.0:
            value = 1.01

        if value < 0.50:
            value = 0.50
            
        self.configRepository.update_value("range-select-card", str(value))    
        print(f"Range atualizado para {value}")

    def get_config_of_select_card(self):
        range = self.configRepository.get_by_key("range-select-card")
        levels = self.configRepository.get_all_by_context("levels")

        return [range, levels]    
    
    def get_range(self):
        return self.configRepository.get_by_key("range-select-card")["value"]

    def get_levels(self):

        list = []
    
        for item in self.configRepository.get_all_by_context("levels"):
            if item["value"] == "ON":
                list.append(item["key"])

        return list

    def update_level(self, level, value):
        self.configRepository.update_value(level, "ON" if value else "OFF")
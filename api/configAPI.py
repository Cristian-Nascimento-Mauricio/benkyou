from flask import Flask, request, jsonify
from types import SimpleNamespace
from services.configManager import configManager

class configAPI:
    def __init__(self, app):
        self.register_routes(app)
        self.cardConfig = configManager("./db/database.db")
    
    def register_routes(self, app):
        @app.route("/api/update_ratio", methods=['POST'])
        def save_config():
            data = request.get_json()
 
            config = SimpleNamespace(**data)
            
            self.cardConfig.update_range(float( config.ratio ))
            return jsonify({
                "message": "Configuração salva com sucesso"
            }), 201
        
        @app.route("/api/update_level", methods=['POST'])
        def update_level():
            data = request.get_json()
            level = data.get("level")
            value = data.get("value")

            self.cardConfig.update_level(level, value)
            return jsonify({
                "message": f"Nível {level} atualizado para {value}"
            }), 200
        
        @app.route("/api/get_config_of_select_card", methods=['GET'])
        def get_config_card():
            [range,levels] = self.cardConfig.get_config_of_select_card()
            return jsonify({
                "massage": "Configurações atuais do seletor de cards",
                "content": {
                    "range": range,
                    "levels": levels
                }
            }), 200
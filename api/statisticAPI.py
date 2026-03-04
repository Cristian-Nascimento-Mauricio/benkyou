from services.statisticManager import statisticManager
from services.cardManager import cardManager
from flask import request, jsonify


class statisticAPI:
    def __init__(self, app):
        self.statisticManager = statisticManager("./db/database.db")
        self.cardManager = cardManager("./db/database.db")
        self.register_routes(app)
    
    def register_routes(self, app):
        @app.route("/api/card/statistic/activity", methods=['GET'])
        def get_activity_statistic():
            days = request.args.get("day", type=int, default=7)

            return jsonify({
                "message": 'Okay',
                "content": self.statisticManager.lastActivity(days)
            }), 200

        @app.route("/api/statistic/attempt", methods=['GET'])
        def get_attempt_statistic():
            category = request.args.get("category")
            data = self.statisticManager.get_att(category)

            if list is None:
                return jsonify({
                    "message": "Erro ao retornar a lista de estatiscas dos cards",
                    "content": None
                }), 500

            return jsonify({
                "message": "Estátisticas retornadas com sucesso",
                "content": data
            }), 200


        @app.route("/api/statistic/card", methods=['GET'])
        def test():
            category = request.args.get("category")
            list = self.statisticManager.get_attempt(category)


            if list is None:
                return jsonify({
                    "message": "Erro ao retornar a lista de estatiscas dos cards",
                    "content": None
                }), 500

            return jsonify({
                "message": "Lista de estatisticas dos cards",
                "content": list
            }), 200                

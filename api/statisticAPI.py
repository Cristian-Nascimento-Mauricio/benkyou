from services.statisticManager import statisticManager
from flask import request, jsonify


class statisticAPI:
    def __init__(self, app):
        self.statisticManager = statisticManager("./db/database.db")
        self.register_routes(app)
    
    def register_routes(self, app):
        @app.route("/api/card/statistic/activity", methods=['GET'])
        def get_activity_statistic():
            days = request.args.get("day", type=int, default=7)

            return jsonify({
                "message": 'Okay',
                "content": self.statisticManager.lastActivity(days)
            }), 200

                

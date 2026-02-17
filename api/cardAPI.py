from flask import Flask, request, jsonify
from types import SimpleNamespace
from repositories.cardRepository import cardRepository  
from services.cardManager import cardManager

class cardAPI:
    def __init__(self, app):
        self.cardManager = cardManager("./db/database.db")
        self.register_routes(app)
    
    def register_routes(self, app):
        @app.route("/api/card", methods=['POST'])
        def add_card():
            data = request.get_json()
 
            card = SimpleNamespace(**data)
            
            card_id = self.cardManager.addCard(card)
            
            if card_id:
                return jsonify({
                    "message": "Card criado com sucesso",
                    "id": card_id
                }), 201
            else:
                return jsonify({"error": "Falha ao salvar card"}), 500

        @app.route("/api/card/statistic", methods=['GET'])
        def test():
            list = self.cardManager.cardStasticAll()


            if list is None:
                return jsonify({
                    "message": "Erro ao retornar a lista de estatiscas dos cards",
                    "content": None
                }), 500

            return jsonify({
                "message": "Teste",
                "content": list
            }), 200

        @app.route('/api/card/<path:card_id>')
        def get_card(card_id:int):
            if(int(card_id) <= -1):
                card = self.cardManager.getCardToStudy(card_id)

            return card
        
        @app.route('/api/my_answer', methods=['POST'])
        def post_my_answer():
            myAnswer = request.get_json()

            newCard = self.cardManager.answeCard(myAnswer)
            
            return jsonify({
                "message": "Resposta processada com sucesso",
                "content": newCard
            }), 200
        
        @app.route("/api/cards", methods=['GET'])
        def get_cards():
            category = request.args.get('category')
            cards = self.cardManager.getCards(category)

            return jsonify({
                "message": "Cards retornados com sucesso",
                "content": cards
            }), 200
            return jsonify({"cards": cards})
        
        @app.route("/api/card", methods=['PUT'])
        def update_card():
            data = request.get_json()
     
            card = SimpleNamespace(**data)
                
            updated_card = self.cardManager.updateCard(card)
            return jsonify({
                    "message": "Card atualizado com sucesso",
                    "card": updated_card
            }), 200
                
        @app.route("/api/answer", methods=['POST'])
        def add_new_correct_answer():
            data = request.get_json()

            self.cardManager.addNewCorrectAnswer(data)
            
            return '',200

        @app.route("/api/card/<int:card_id>", methods=['DELETE'])
        def delete_card(card_id):
    
            self.cardManager.deleteById(card_id)
            return jsonify({"message": "Card deletado com sucesso"}), 200
                
                

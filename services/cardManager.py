from repositories.cardRepository import cardRepository
from repositories.currentCardRepository import currentCardRepository
from repositories.attemptRepository import attemptRepository
from services.configManager import configManager

class cardManager:
    def __init__(self,path):
        self.repoCard = cardRepository(path)
        self.configManager = configManager(path)
        self.repoCurrentCard = currentCardRepository(path)
        self.repoAttempt = attemptRepository(path)

    def lenCurrent(self):
        return self.repoCurrentCard.len_current()
    
    def deleteCardIfNecessary(self,cardId):
        cards = self.repoCurrentCard.select_first_three_static()
        range = self.configManager.get_range()

        if cardId is not None:
            myCard = self.repoCurrentCard.get_already_learned(cardId)
            if myCard["count"] >= 10 and myCard["porcent"] >= range:
                self.repoCurrentCard.delete(cardId)
                return

        for card in cards:
            if card['average'] >= (2.5/3) and card['count'] >= 3:
                self.repoCurrentCard.delete(card['card_id'])

    def addCardToCurrentCard(self):
        count = self.lenCurrent()
        print("count: ", count)
        if(count >= 10):
            return 

        range = self.configManager.get_range()
        categories = self.configManager.get_levels()
        print("categories: ", categories)
        listId = self.repoCard.selectCards((10 - count),categories, range)
        
        for id in listId:
            self.repoCurrentCard.create(id)

    def answeCard(self,myAnswer):

        cardId = myAnswer["cardId"]
        read = myAnswer["reading"]
        mean = myAnswer["meaning"]

        r = read if read is not None else mean
        m = mean

        self.repoAttempt.create_attempt(read,mean,cardId)
        if (r + m)/2.0 >= 1.0:            
            self.deleteCardIfNecessary(cardId)
        else:
            self.deleteCardIfNecessary(None)    
        self.addCardToCurrentCard()

        return self.getCardToStudy(cardId)
    
    def selectCard(self,amount, category, range):
        return self.repoCard.selectCards(amount)
 
    def getCardToStudy(self,lastID):
        count = self.repoCurrentCard.len_current()
        print("test: ", count)

        if(count <= 0):
            self.addCardToCurrentCard()

        id = self.repoCurrentCard.get_randon_card_in_currentCard(lastID)

        card = self.repoCard.get_card_by_id(id)

        return card



    def getCards(self,category):

        list = []

        if category in ("N5","N4","N3","N2","N1"):
            list = self.repoCard.get_cards_by_category(category)
        elif category == "ALL":
            list = self.repoCard.get_all_cards()
        
        

        return list

    def addCard(self,card):
        word = card.word 
        category = card.category
        readings = card.reading 
        meanings = card.meaning

        return  self.repoCard.create_card(word,category,readings,meanings)

    def addNewCorrectAnswer(self,newAnswer):
        if newAnswer["TAG"] == "READING":
            return self.repoCard.create_reading(newAnswer["CARDID"],newAnswer["WORD"])
        elif newAnswer["TAG"] == "MEANING":
            return self.repoCard.create_meaning(newAnswer["CARDID"],newAnswer["WORD"])
        return False    
    
    def updateCard(self,card):

        cardId = card.id
        word = card.word 
        category = card.category
        readings = card.reading 
        meanings = card.meaning

        return self.repoCard.update_card(cardId,word,category,readings,meanings)    

    def deleteById(self,cardId):
        return self.repoCard.delete_card(cardId)
            


    def cardStasticAll(self):
        return self.repoCard.card_stastic_all()
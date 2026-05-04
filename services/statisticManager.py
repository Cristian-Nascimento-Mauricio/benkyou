from repositories.cardRepository import cardRepository
from repositories.currentCardRepository import currentCardRepository
from repositories.attemptRepository import attemptRepository
from datetime import date, timedelta,datetime
import statistics

class statisticManager:
    def __init__(self,path):
        self.repoCard = cardRepository(path)
        self.repoCurrentCard = currentCardRepository(path)
        self.repoAttempt = attemptRepository(path)


    def get_statistics(self, category: str):
        med_list = self.repoAttempt.get_med(category)
        average = self.repoAttempt.get_average(category)
        count = self.repoAttempt.get_count(category)

        if not med_list:
            med = None
            mode = None
        else:
            med = statistics.median(med_list)
            mode = statistics.multimode(med_list)[0]

        return {
            "med": med,
            "mode": mode,
            "average": average,
            "count": count
        }

    def get_attempt(self,category):
        if category == "ALL":
            return self.repoCard.card_stastic_all()
        
        return self.repoCard.card_stastic_by_category(category)

    def lastActivity(self, days):

        today = datetime.strptime(
            self.repoAttempt.get_date_today(),
            "%Y-%m-%d"
        ).date()

        beforeDay = [
            today - timedelta(days=i)
            for i in range(days-1, -1, -1)
        ]

        data = self.repoAttempt.get_activity_statistics(days)
        if len(data) in (7,15,30):
            return data

        data_map = {
            datetime.strptime(item["day"], "%Y-%m-%d").date(): item
            for item in data
        }

        result = []

        for day in beforeDay:
            if day in data_map:
                result.append(data_map[day])
            else:
                result.append({
                    "day": day.strftime("%Y-%m-%d"),
                    "read": 0,
                    "mean": 0,
                    "attempt": 0
                })

        result.sort(key=lambda x: x["day"])
        return result
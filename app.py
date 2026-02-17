from flask import *
from api.cardAPI import cardAPI
from api.statisticAPI import statisticAPI
from api.configAPI import configAPI
from repositories.databaseCreator import databaseCreator
from services.cardManager import cardManager
from services.statisticManager import statisticManager

app = Flask(__name__)

card_api = cardAPI(app)
statistic_api = statisticAPI(app)
config_api = configAPI(app)

creater = databaseCreator("../db/database.db")
creater.create_database()
cardManager = cardManager("./db/database.db")
statisticManager = statisticManager("./db/database.db")

@app.route("/")
@app.route("/study")
def home():
    content = cardManager.getCardToStudy(-1)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {
            'html':render_template("components/study.html"),
            'module':"static/js/study.js",
            'content':content
        }

    return render_template("index.html",path="study")

@app.route("/administration")
def administration():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {
            'html':render_template("components/administration.html"),
            'module':"static/js/administration.js"
        }

    return render_template("index.html",path="administration")

@app.route("/statistic")
def statistic():
    statisticGrafic = statisticManager.lastActivity(7)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {
            'html':render_template("components/statistic.html"),
            'module':"static/js/statistic.js",
            'content':{'statistics':statisticGrafic }
        }

    return render_template("index.html",path="static")

if __name__ == "__main__":
    app.run(debug=True,port=80)
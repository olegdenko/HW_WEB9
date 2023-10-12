from mongoengine import connect
from pymongo import MongoClient
from pymongo.server_api import ServerApi

client = MongoClient(
    'mongodb+srv://userweb8:567234@cluster0.vsujqym.mongodb.net/?retryWrites=true&w=majority', server_api=ServerApi('1'))
db = client['hw_web8']

connect(
    db='hw_web8',
    host='mongodb+srv://userweb8:567234@cluster0.vsujqym.mongodb.net/hw_web8?retryWrites=true&w=majority',
    alias='default',
    server_api=ServerApi('1')
)


if __name__ == "__main__":
    print("Connection MongoDB")

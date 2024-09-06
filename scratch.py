import typing
import pymysql

mydb = pymysql.connect(
    host="localhost",
    user="root",
    password="yos",
    database="movieDB"
)

aCursor = mydb.cursor()

print(typing.reveal_type(aCursor))

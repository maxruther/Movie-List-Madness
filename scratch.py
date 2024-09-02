# print([1] * 5)
import typing

import pymysql
from pymysql import cursors

mydb = pymysql.connect(
    host="localhost",
    user="root",
    password="yos",
    database="movieDB"
)

aCursor = mydb.cursor()

print(typing.reveal_type(aCursor))

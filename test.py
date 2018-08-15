import sys
import time
import json
import requests
from pymongo import MongoClient

def add_user(i):
	user_temp = {
		"username" : "admin",
		"password" : "admin",
		"roles" : ["admin"],
		"first_name" : "admin",
		"last_name" : "",
		"email" : "abc@def.com",
		"phone" : "1234567890",
		"eid" : 123456,
		"address" : "420 Bakers Street, London",
		"zipcode" : 1234567
	}
	user_temp["username"] = "admin{}".format(i)
	data = requests.post('http://localhost:5000/user-management', user_temp)

def del_user(i):
	username = "admin{}".format(i)
	data = requests.delete('http://localhost:5000/user-management?username={}'.format(username))


if __name__ == '__main__':
	client = MongoClient('localhost',27017)  # 27017 is the default port number for mongodb
	db = client.MyDb
	col = db.Users

    # testing user addition and deletion rate per second
	t_end = time.time() + 60 * 1

	while time.time() < t_end:
		for i in range(1,101):
			add_user(i)
			del_user(i)


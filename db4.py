import pymysql

db_name = 'test'

def database_create_connection():
	connection = pymysql.connect(
	host = '127.0.0.1',
	user = 'root',
	password = 'new_password',
	database = db_name
	)
	return connection

#... [rest of the db4.py content] ...
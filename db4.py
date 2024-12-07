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
	
	
def database_create_tables():
	conn_create_table = database_create_connection()
	cursor = conn_create_table.cursor()
	
	cursor.execute("SHOW TABLES LIKE 'users'")
	results_db = cursor.fetchone()
	
	if not results_db:
		print('ok create tables')
		cursor.execute('''
		CREATE TABLE IF NOT EXISTS users (
        ID INT AUTO_INCREMENT PRIMARY KEY,
        Chat_Id BIGINT,
        Language_Code VARCHAR(10),
        First_Name VARCHAR(50),
        Last_Name VARCHAR(50),
        User_Name VARCHAR(50),
        Phone_Number VARCHAR(15),
        Country_Code_for_Phone_Number VARCHAR(5),
        Email VARCHAR(100),
        Account_Activity_Status ENUM('active', 'inactive', 'suspended'),
        Login_Date DATE,
        Login_Time TIME,
        General_User_Name VARCHAR(50),
        Password VARCHAR(255),
        Total_Payment_Links INT DEFAULT 0,
        Total_Referral_Links INT DEFAULT 0,
        Total_Purchase_Links_v2 INT DEFAULT 0,
        Total_Downloadrs_Links INT DEFAULT 0,
        Total_File_Conversion_Links INT DEFAULT 0,
        Total_Free_Links_v2 INT DEFAULT 0,
        Total_Group_Links INT DEFAULT 0,
        Total_Channel_Links INT DEFAULT 0,
        Total_Follower_IDs INT DEFAULT 0,
        Total_Member_IDs INT DEFAULT 0
	    )
		''')
	conn_create_table.commit()
	conn_create_table.close()
	
database_create_tables()
#print('not ok')
	
def database_insert_data(chat_id_user, first_name_user, last_name_user, user_name_user, data):
	conn_insert = database_create_connection()
	cursor = conn_insert.cursor()
	
	sql_query = '''
	INSERT INTO users(
	Chat_Id,
	First_Name,
	Last_Name,
	User_Name,
	Language_Code
	) VALUES (%s, %s, %s, %s, %s)
	'''
	values_insert = (chat_id_user, first_name_user, last_name_user, user_name_user, data)
	
	cursor.execute(sql_query, values_insert)
	conn_insert.commit()
	conn_insert.close()
	
	
#database_insert_data(123,'fa','ali','moradi','@alimiri')
#print('ok insert data')

def user_exists(chat_id_user_start):
	conn_check_exists = database_create_connection()
	cursor = conn_check_exists.cursor()
	sql_query_check = '''
    SELECT Chat_Id FROM users WHERE Chat_Id = %s
    '''
	values_check_db = chat_id_user_start
	cursor.execute(sql_query_check, values_check_db)
	result_check_exists_chat_id_user = cursor.fetchone()
	conn_check_exists.close()
	if result_check_exists_chat_id_user:
		chat_id = result_check_exists_chat_id_user
		#print('yes chat id')
		#print(f'result: {result}')
		return True, chat_id
	else:
		return False, None
		


def check_for_existence_in_the_database(chat_id_user_click_callback):
	conn_check_exists = database_create_connection()
	cursor = conn_check_exists.cursor()
	sql_query_check = '''
    SELECT Chat_Id, First_Name, Last_Name, User_Name, Language_Code FROM users WHERE Chat_Id = %s
    '''
	values_check_db = chat_id_user_click_callback
	cursor.execute(sql_query_check, values_check_db)
	result = cursor.fetchone()
	conn_check_exists.close()

	if result:
		chat_id,first_name,last_name,user_name,language_code = result
		#print('yes chat id')
		#print(f'result: {result}')
		return True, chat_id,first_name,last_name,user_name,language_code
	else:
		print('no chat id')
		return False, None , None, None, None, None

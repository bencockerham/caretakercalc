#this is an install file that creates the sqlite3 db for nanny_simple_db_test.py


import sqlite3 as lite 
import sys
import datetime as dt
from datetime import datetime 

def clear():
	print(' \n' *25)

def launch_alert():
	clear()
	print 'WELCOME! -- You are installing the Caretaker Calculator program'
	print '\n'
	print 'This insall file will create and populate the initial database'
	print 'Any existing data will be erased.' 
	proceeding = False
	choosing = True
	while choosing:
		choice = raw_input('Do you wish to proceed (Y/N)? ')
		if choice.upper() == 'Y':
			proceeding = True
			choosing = False
		elif choice.upper() == 'N':
			proceeding = False
			choosing = False
		else:
			print 'please only enter Y or N'
	return proceeding


def db_setup():
	con = lite.connect('caretakercalc.db')
	with con:
		cur = con.cursor()
		cur.execute('DROP TABLE IF EXISTS caretaker')
		cur.execute('DROP TABLE IF EXISTS children')
		cur.execute('DROP TABLE IF EXISTS rates')
		cur.execute('DROP TABLE IF EXISTS rate_mapping')
		cur.execute('DROP TABLE IF EXISTS day_entry')
		#cur.execute('DROP TABLE IF EXISTS week_close')
		#cur.execute('DROP TABLE IF EXISTS payment')
		cur.execute('DROP TABLE IF EXISTS day_entry_child_mapping')
		cur.execute('DROP TABLE IF EXISTS preferences')
		cur.execute('DROP TABLE IF EXISTS child_pref_mapping')
		cur.execute('DROP TABLE IF EXISTS pref_enabled')
		cur.execute('CREATE TABLE caretaker(ID INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, phone INTEGER, address TEXT, email TEXT, is_deleted INTEGER)')
		cur.execute('CREATE TABLE children(ID INTEGER PRIMARY KEY, First_Name TEXT, Last_Name TEXT, Birthday TEXT)')
		cur.execute('CREATE TABLE rates(ID INTEGER PRIMARY KEY, rate_name TEXT)')
		cur.execute('CREATE TABLE rate_mapping(rate_map_ID INTEGER PRIMARY KEY, rate_id INTEGER, caretaker_id INTEGER, rate_amt FLOAT, FOREIGN KEY(rate_id) REFERENCES ID(rate), FOREIGN KEY(caretaker_id) REFERENCES ID(caretaker))')
		cur.execute('CREATE TABLE day_entry(entry_ID INTEGER PRIMARY KEY, date DATE, rate_map_ID INTEGER, hours FLOAT, misc_expense_amt FLOAT, misc_expense_note TEXT, entry_total FLOAT, week_close_ID INTEGER, FOREIGN KEY(week_close_ID) REFERENCES close_ID(week_close), FOREIGN KEY(rate_map_id) REFERENCES rate_map_id(rate_mapping))')
		#cur.execute('CREATE TABLE week_close(close_ID INTEGER PRIMARY KEY, close_date DATE, date_start DATE, date_end DATE, close_total FLOAT, payment_ID INTEGER, FOREIGN KEY(payment_ID) REFERENCES payment_ID(payment))')
		cur.execute('CREATE TABLE day_entry_child_mapping(ID INTEGER PRIMARY KEY, day_entry_id INTEGER, child_ID INTEGER, FOREIGN KEY(child_id) REFERENCES ID(children), FOREIGN KEY(day_entry_id) REFERENCES entry_ID(day_entry))')
		#cur.execute('CREATE TABLE payment(payment_ID INTEGER PRIMARY KEY, type TEXT, week_close_id INTEGER, payment_amount FLOAT, balance FLOAT, FOREIGN KEY(week_close_id) REFERENCES close_id(week_close))')
		cur.execute('CREATE TABLE preferences(pref_ID INTEGER PRIMARY KEY, week_day_ID INTEGER, rate_map_ID INTEGER, hours FLOAT, misc FLOAT, misc_note TEXT, FOREIGN KEY(rate_map_ID) REFERENCES ID(rate_mapping))')
		cur.execute('CREATE TABLE child_pref_mapping(child_pref_map_ID INTEGER PRIMARY KEY, pref_ID INTEGER, child_ID INTEGER, FOREIGN KEY(pref_ID) REFERENCES pref_ID(preferences), FOREIGN KEY(child_ID) REFERENCES ID(children))')
		cur.execute('CREATE TABLE pref_enabled(ID INTEGER PRIMARY KEY, pref_enabled INTEGER)')

def db_insert_default_values():
	con = lite.connect('caretakercalc.db')
	cur = con.cursor()
	with con:
		cur.execute('INSERT INTO pref_enabled(pref_enabled) VALUES(0)')
		con.commit()


class CalcSetup(object): #processes and info store for setting initial defaults
	def __init__(self, nanny_dict = {}, child_dict = {}, rate_dict = {}):
		self.nanny_dict = {}
		self.child_dict = {}
		self.rate_dict = {
			1: ['Standard', 0],
			2: ['Overtime', 0],
			3: ['Share', 0]
			}
	
	def nanny_info(self):
		clear()
		print 'please enter nanny information'
		nanny_id = 1
		entering = True
		while entering:
			nanny_first_name = raw_input('please enter nanny first name: ')
			nanny_last_name = raw_input('please enter nanny last name: ')
			nanny_phone = raw_input('please enter nanny phone: ')
			nanny_address = raw_input('please enter nanny address: ')
			nanny_email = raw_input('please enter nanny email: ')
			temp_rate_dict = self.get_rate()
			self.nanny_dict[nanny_id] = [nanny_first_name, nanny_last_name, nanny_phone, nanny_address, nanny_email, temp_rate_dict]
			more = True
			another = raw_input('do you want to enter another nanny? Y/N ')
			if another.upper() == 'Y':
				nanny_id += 1
				entering = True
				more = False
			elif another.upper() == 'N':
				entering = False
				more = False
			else:
				print 'please only enter Y or N'
				entering = True
				more = True
	
	def child_info(self):
		clear()
		print 'do you want to enter child information now?'
		choosing = True
		child_list = []
		y = 0
		while choosing:
			choice = raw_input('Y/N? ')
			if choice.upper() == 'Y':
				more = True
				while more:
					print 'please enter child information'
					first = raw_input('first name: ')
					last = raw_input('last name: ')
					birthday_input = True
					while birthday_input:
						birthday = raw_input('birthday YYYY-MM-DD format with dashes: ')
						try:
							dt.datetime.strptime(birthday, '%Y-%m-%d')
							birthday_input = False
						except ValueError:
							 print 'Incorrect data format, should be YYYY-MM-DD'
					child = (first, last, birthday)
					child_list.append(child)
					answering = True
					while answering:
						another = raw_input('do you have another child to enter? ')
						if another.upper() == 'Y':
							answering = False
						elif another.upper() == 'N':
							more = False
							answering = False
						else:
							print 'please only enter Y or N'
				for x in child_list:
					self.child_dict[y] = [child_list[y][0], child_list[y][1], child_list[y][2]]
					y += 1		
				choosing = False
			elif choice.upper() == 'N':
				choosing = False
			else:
				print 'please only enter Y or N'
		
	def get_rate(self):
		clear()
		temp_rate_dict = {}
		print 'please enter a dollar amount for each rate type below:'
		for rate in self.rate_dict:
			print rate, self.rate_dict[rate][0]
		print 'please enter new rate information'
		for new in self.rate_dict:
			pnew = self.rate_dict[new][0]
			temp_rate_dict[new] = []
			temp_rate_dict[new].append(pnew)
			inputting = True
			while inputting:
				try:
					new_rate = float(raw_input(pnew + ': '))
					inputting = False
				except ValueError:
					print 'please only enter a numeric value'
			temp_rate_dict[new].append(new_rate)
		return temp_rate_dict
		
	def get_all_info(self):
		self.child_info()
		self.nanny_info()
		
	def db_insert(self):
		con = lite.connect('caretakercalc.db')
		child_data = []
		for x in self.child_dict:
			child_data.append((self.child_dict[x][0], self.child_dict[x][1], self.child_dict[x][2]))
		caretaker_data = []
		rate_map_data = []
		for n in self.nanny_dict:
			caretaker_data.append((self.nanny_dict[n][0], self.nanny_dict[n][1], self.nanny_dict[n][2], self.nanny_dict[n][3], self.nanny_dict[n][4]))  
			temp_rate_dict = self.nanny_dict[n][5]
			for rate in temp_rate_dict:
				rate_map_data.append((rate, n, temp_rate_dict[rate][1]))
		rate_name_data = []
		for rate in self.rate_dict:
			rate_name_data.append(self.rate_dict[rate][0])
		pref_data = self.pref_load()
		with con:
			cur = con.cursor()
			cur.executemany('INSERT INTO children(First_Name, Last_Name, Birthday) VALUES(?, ?, ?)', child_data)
			cur.executemany('INSERT INTO caretaker(first_name, last_name, phone, address, email, is_deleted) VALUES(?, ?, ?, ?, ?, 0)', caretaker_data)
			cur.executemany('INSERT INTO rate_mapping(rate_id, caretaker_id, rate_amt) VALUES(?, ?, ?)', rate_map_data)
			for rate in rate_name_data:
				cur.execute('INSERT INTO rates(rate_name) VALUES(?)', (rate,))
				con.commit()
			for id in range(len(pref_data)):
				cur.execute('INSERT INTO preferences(week_day_ID) VALUES(?)', (pref_data[id],))
				con.commit()
		
	def pref_load(self):
		default_day_ID_list = [1,2,3,4,5,6,7]
		return default_day_ID_list
		#could change this to ask for pref setup; 
		#for now just populating preferences table with an entry for each day of the week
	
	def db_verify(self):
		con = lite.connect('caretakercalc.db')
		with con:
			cur = con.cursor()
			cur.execute('SELECT * FROM children')
			rows = cur.fetchall()
			for row in rows:
				print row

calc_setup = CalcSetup({}, {}, {})

def main():
	proceeding = launch_alert()
	if proceeding:
		db_setup()
		#run basic input processes
		db_insert_default_values()
		#insert default values
		calc_setup.get_all_info()
		calc_setup.db_insert()
		#calc_setup.db_verify() #for testing
		print 'Installation successful'
		print 'You may now run Caretaker Calculator'
	else:
		print 'Install will not proceed. No data has been erased'
		print 'Goodbye'

main()


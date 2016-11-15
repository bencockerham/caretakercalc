'''
Caretaker Calculator
This command line program manages daily input of caretakers' hours, calculates weekly totals,
and stores the data in a sqlite3 database.

Before running this program, 'Caretaker_Calculator_Install' must be run.  The install program
creates the databases and prompts the user to set up initial children and caretakers.  
This program contains a function to check that the install program has been run.


'''
import sqlite3 as lite 
import sys
import datetime as dt
from datetime import datetime 
from datetime import date
from datetime import timedelta
import calendar 
import csv

def install_check():
	con = lite.connect('caretakercalc.db')
	with con:
		cur = con.cursor()
		cur.execute('select name from sqlite_master where type = "'"table"'"')
		tables = cur.fetchall()
	existing_tables_list = []
	for x in tables:
		existing_tables_list.append(x[0])
	install_tables = ['caretaker', 'children', 'rates', 'rate_mapping', 'day_entry', 'day_entry_child_mapping', 'preferences', 'child_pref_mapping', 'pref_enabled']
	missing_tables = []
	for table in install_tables:
		if table in existing_tables_list:
			pass
		else:
			missing_tables.append(table)
	return missing_tables

'''
The Children class manages data on the children for the program flow.  It manages loading
child data from the sqlite table into its child_dict as well as all of the mechanics of
adding, updating, and removing children from the database. 
'''

class Children(object): 
	def __init__(self, name, child_dict = {}):
		self.name = name
		self.child_dict = {}
		
	def load_child_dict(self):
		self.child_dict = {}
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		with con:
			cur.execute('SELECT * FROM children')
			child_data = cur.fetchall()
			x = 0
			y = 1
			for child in child_data:
				child_list = []
				for ch in range(len(child_data[x])):
					child_list.append(child_data[x][ch])
				self.child_dict[y] = child_list
				x +=1
				y +=1
		#self.child_dict[child_id] = [child_id, first_name, last_name, birthday]
		
	def view_children(self):
		self.load_child_dict()
		for child in self.child_dict:
			print child, 'NAME', self.child_dict[child][1], self.child_dict[child][2], 'BIRTHDAY', self.child_dict[child][3]
		
	def update_child_menu(self):
		flow.clear()
		self.view_children()
		child_menu = {
			1: ['Edit Child', self.update_child],
			2: ['Add Child', self.add_child],
			3: ['Remove Child', self.remove_child],
			4: ['Return To The Menu', self.backmenu]
			}
		flow.header()
		for item in child_menu:
			print item, child_menu[item][0]
		print 'Please enter option number'
		choosing = True
		while choosing:
			try:
				choice = int(raw_input('? '))
				if choice in child_menu:
					child_menu[choice][1]()
					print 'finished menu choice'
					choosing = False
				else:
					print 'please only enter an integer from the list above'
			except ValueError:
					print 'please only enter an integer from the list above'
	
	def backmenu(self):
		#return to the main menu
		pass		
		
	def add_child(self):
		adding = True
		while adding:
			print 'first name'
			first_name = raw_input('? ')
			print 'last name'
			last_name = raw_input('? ')
			birthday_input = True
			while birthday_input:
				birthday = raw_input('birthday YYYY-MM-DD format with dashes: ')
				try:
					dt.datetime.strptime(birthday, '%Y-%m-%d')
					birthday_input = False
				except ValueError:
					 print 'Incorrect data format, should be YYYY-MM-DD'
			id_list = []
			for id in self.child_dict:
				id_list.append(id)
			id_list.sort()
			highest = id_list.pop()
			self.child_dict[highest] = [highest, first_name, last_name, birthday]
			print 'confirm add child:'
			print first_name, last_name, birthday
			answering = True
			while answering:
				print 'is this correct (Y/N)'
				answer = raw_input('? ')
				if answer.upper() == 'Y':
					answering = False
					adding = False
				elif answer.upper() == 'N':
					answering = False
					adding = True
				else:
					print 'please only enter Y or N'
		update_data = [first_name, last_name, birthday]
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		with con:
			cur.execute('INSERT INTO children(first_name, last_name, birthday) values(?, ?, ?)', update_data)
		
	def update_child(self):
		self.view_children()
		print 'please enter the number of the child you want to edit or type M to return to the main menu'
		choosing = True
		while choosing:
			child_id = raw_input('? ')
			if child_id.upper() == 'M':
				choosing = False
			elif int(child_id) in self.child_dict:
				self.update_child_info_process(int(child_id))
				choosing = False
			else:
				print 'please only enter an integer from the list above or M to return to the main menu'
		
	def update_child_info_process(self, child_id):
		print self.child_dict[child_id][1], self.child_dict[child_id][2], self.child_dict[child_id][3]
		updating = True
		while updating:
			print 'first name'
			first_name = raw_input('? ')
			print 'last name'
			last_name = raw_input('? ')
			print 'birthday'
			birthday_input = True
			while birthday_input:
				birthday = raw_input('birthday YYYY-MM-DD format with dashes: ')
				try:
					dt.datetime.strptime(birthday, '%Y-%m-%d')
					birthday_input = False
				except ValueError:
					 print 'Incorrect data format, should be YYYY-MM-DD'
			print 'confirm updated info:'
			print first_name, last_name, birthday
			answering = True
			while answering:
				print 'is this correct (Y/N)'
				answer = raw_input('? ')
				if answer.upper() == 'Y':
					self.child_dict[child_id][1] = first_name
					self.child_dict[child_id][2] = last_name
					self.child_dict[child_id][3] = birthday 
					self.write_child_data()
					answering = False
					updating = False
				elif answer.upper() == 'N':
					print 'info NOT updated'
					answering = False
					updating = False
				else:
					print 'please only enter Y or N'

#unlike caretakers, which are never truly deleted, children can be deleted.
#their existence has no effect on the dollar calculations

	def remove_child(self):  
		self.view_children()
		print 'please enter the number of the child you want to remove or type M to return to the main menu'
		removing = True
		while removing:
			child_id = raw_input('? ')
			if child_id.upper() == 'M':
				removing = False
			elif int(child_id) in self.child_dict:
				child_id = int(child_id)
				print 'Are you sure you want to REMOVE'
				print self.child_dict[child_id][0], self.child_dict[child_id][1], self.child_dict[child_id][2]
				answer = raw_input('Y/N ')
				if answer.upper() == 'Y':
					con = lite.connect('caretakercalc.db')
					cur = con.cursor()
					with con:
						cur.execute('DELETE FROM children WHERE id=?', (child_id,))
						con.commit()
					removing = False
				else:
					removing = False
			else:
				print 'please only enter an integer from the list above or M to return to the main menu'
		
	def write_child_data(self):
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		with con:
			for data in self.child_dict:
				update_data = []
				update_data.append(self.child_dict[data][1]) #first name
				update_data.append(self.child_dict[data][2]) #last name
				update_data.append(self.child_dict[data][3]) #birthday
				update_data.append(data) #child id
				cur.execute('UPDATE children set first_name=?, last_name=?, birthday=? WHERE ID=?', update_data)
				con.commit()
				
'''
The Caretaker class manages loading data from caretaker and rate tables into the program.
It also manages adding, updating, removing, and setting rates for each caretaker.

Each caretaker can have a maximum of 3 different rates: standard, overtime, and share.
Although this program has the 3 rate limitation hard coded in, the database is structured
to be able to support a dynamic rate process, and the code may be updated to implement that in the future.

There are intentionally no restrictions on what dollar amounts can be used as rates.  Even rates
of zero or negative are allowed.  

Connecting caretakers and rates is a 3 table process:
 - the 'caretaker' table stores data on the caretaker individual, and establishes a caretaker_id
 - the 'rates' table defines the 3 rate types and establishes a rate_id
 - the 'rate_mapping' table connects caretaker_id with rate_id and rate_amount and establishes a rate_map_id
 
The rate_map_id is the identifier used to connect a set of hours worked with a caretaker and a rate amount simultaneously

'''

class Caretaker(object):
	def __init__(self, name, caretaker_dict = {}, caretaker_rate_dict = {}):
		self.name = name
		self.caretaker_dict = {} #holds all caretaker info {ID = [first name, last name, phone, address, email]}
		self.caretaker_rate_dict = {} #holds rate-specific info for one caretaker at a time {rateID: [rate_name, rate_amt], etc}
									#used for temporary data mobility between functions
		
	def load_caretaker(self):
		self.caretaker_dict = {}
		con = lite.connect('caretakercalc.db')
		with con:
			cur = con.cursor()
			cur.execute('select * from caretaker')
			data = cur.fetchall()
		caretaker_count = len(data)
		for x in range(caretaker_count):
			if data[x][6] == 1: #this is the is_deleted flag in the caretaker table. 1=True, 0=False
				pass
			else:
				self.caretaker_dict[x+1] = [data[x][1], data[x][2], data[x][3], data[x][4], data[x][5]]
			# ID = [first name, last name, phone, address, email]
			
	def load_caretaker_rates(self, choice): #loads rate data into self dict
		rate_map_data = []
		con = lite.connect('caretakercalc.db')
		with con:
			cur = con.cursor()
			cur.execute('select * from rate_mapping INNER JOIN rates on rate_mapping.rate_id = rates.id WHERE caretaker_id=?', [choice])
			rate_map_data = cur.fetchall()
			#creates list of [(rate map ID, rate ID, caretaker ID, rate amount, ID from rates table, rate name), (etc)]
		for rate in range(len(rate_map_data)):
			self.caretaker_rate_dict[rate_map_data[rate][1]] = [rate_map_data[rate][5], rate_map_data[rate][3]]
			#{rate ID: [rate name, rate amount]}
		
	def display_caretaker(self):
		self.load_caretaker()
		flow.clear()
		print 'ID,  First Name,  Last Name'
		for x in self.caretaker_dict:
			print x, self.caretaker_dict[x][0], self.caretaker_dict[x][1], self.caretaker_dict[x][2]
	
	def select_caretaker(self):
		choice_ID = 0
		choosing = True
		self.display_caretaker()
		while choosing:
			print 'please enter caretaker ID'
			try:
				choice = int(raw_input('? '))
				if choice in self.caretaker_dict:
					choice_ID = choice
					choosing = False
				else:
					print 'please only enter a caretaker ID'
			except ValueError:
				print 'please only enter a caretaker ID'
		return choice_ID
		
	def caretaker_menu(self):
		flow.clear()
		flow.header()
		caretaker_menu_dict = {
			1: ['Update existing caretaker info', self.update_caretaker_info],
			2: ['Add new caretaker', self.add_caretaker],
			3: ['Delete caretaker', self.delete_caretaker],
			4: ['Return to the main menu', self.backmenu]
			}
		for option in caretaker_menu_dict:
			print option, caretaker_menu_dict[option][0]
		update_choice = 0
		choosing = True
		while choosing:
			try:
				update_choice = int(raw_input('? '))
				if update_choice in caretaker_menu_dict:
					caretaker_menu_dict[update_choice][1]()
					choosing = False
				else:
					print 'Please only enter a menu item number above'
			except ValueError:
				print 'Please only enter an integer from the menu items above'
	
	def backmenu(self):
		pass
	
	def delete_caretaker(self): 
	#caretakers are not actually deleted because this could cause downstream issues when calculating prior day totals
	#rather, the is_deleted column is used to note that the caretaker should not be involved in any future transactions
		flow.clear()
		print 'press any key and then select a caretaker to delete.'
		print 'you will be prompted to confirm or cancel the deletion process after you make your selection.'
		raw_input()
		id = self.select_caretaker()
		caretaker_str = self.caretaker_dict[id][0] + ' ' + self.caretaker_dict[id][1]
		print 'are you sure you want to delete', caretaker_str, '?'
		answering = True
		while answering:
			confirm = raw_input('Y/N ')
			if confirm.upper() == 'Y':
				con = lite.connect('caretakercalc.db')
				cur = con.cursor()
				with con:
					cur.execute('UPDATE caretaker SET is_deleted=1 WHERE ID=?', (id,)) 
					con.commit()
					cur.execute('SELECT pref_ID FROM preferences '
					'WHERE rate_map_ID IN '
					'(SELECT rate_map_ID FROM rate_mapping WHERE caretaker_id=?)', (id,))
					pref_IDs = cur.fetchall()
					if pref_IDs: #there are preferences using the deleted caretaker
						print 'there are preferences using the deleted caretaker'
						print 'those preferences have been reset; please return to the preferences menu to select a replacement caretaker'
						for r in range(len(pref_IDs)):
							pid = pref_IDs[r][0]
							cur.execute('UPDATE preferences SET rate_map_id=0 WHERE pref_ID=?', (pid,))
							con.commit()
					else:
						pass
				answering = False
			elif confirm.upper() == 'N':
				print 'caretaker not deleted, press any key to continue'
				raw_input()
				answering = False
			else:
				print 'please only enter Y or N'
	
	def add_caretaker(self):
		print 'please enter name'
		new_first = raw_input('first name: ')
		new_last = raw_input('last name: ')
		new_phone = self.process_phone()
		print 'please enter address'
		new_address = raw_input('address: ')
		print 'please enter email'
		new_email = raw_input('email: ')
		update_data = [new_first, new_last, new_phone, new_address, new_email]
		con = lite.connect('caretakercalc.db')
		choice = 0
		rate_data = []
		with con:
			cur = con.cursor()
			cur.execute('INSERT INTO caretaker(first_name, last_name, phone, address, email, is_deleted) values(?, ?, ?, ?, ?, 0)', update_data)
			cur.execute('SELECT id FROM caretaker WHERE id = (SELECT MAX(id) FROM caretaker)')
			choice = cur.fetchall()
			cur.execute('SELECT * FROM rates')
			rate_data = cur.fetchall()
			choice = choice[0][0]
			self.caretaker_dict[choice] = []
			self.caretaker_dict[choice].append(new_first)
			self.caretaker_dict[choice].append(new_last)
			self.caretaker_dict[choice].append(new_phone)
			self.caretaker_dict[choice].append(new_address)
			print 'please enter rate informtation'
			rate_dict = {}
			for rate in range(len(rate_data)):
				rate_id = rate_data[rate][0]
				rate_name = rate_data[rate][1]
				print rate_id, rate_name
				rating = True
				while rating:
					try:
						update_data = []
						rate_amt = float(raw_input('please enter rate '))
						rate_dict[rate_data[rate][0]] = rate_amt
						update_data = [rate_id, choice, rate_amt]
						cur.execute('INSERT INTO rate_mapping(rate_id, caretaker_id, rate_amt) VALUES(?, ?, ?)', update_data)
						con.commit()
						rating = False
					except ValueError:
						print 'please only enter a numeric value'
		print 'caretaker add completed'
		raw_input('press any key to continue')
	
	def update_caretaker_info(self):
		choice = self.select_caretaker()
		if choice == 0:
			print 'selection error'
			return
		else:
			pass
		name_to_update = (self.caretaker_dict[choice][1], self.caretaker_dict[choice][0])
		#makes a tuple of name (last, first)
		updating = True
		while updating:
			flow.clear()
			flow.header()
			#caretaker_dict {ID = [first name, last name, phone, address, email, is_deleted]}
			print '1 - Update Name', self.caretaker_dict[choice][0], self.caretaker_dict[choice][1]
			print '2 - Update Phone', self.caretaker_dict[choice][2]
			print '3 - Update Address', self.caretaker_dict[choice][3]
			print '4 - Update Email', self.caretaker_dict[choice][4]
			print '5 - Update Rates'
			print '6 - Return To The Main Menu'
			update_choice = 0
			choosing = True
			while choosing:
				try:
					update_choice = int(raw_input('? '))
					if update_choice in [1, 2, 3, 4, 5, 6]:
						choosing = False
					else:
						print 'Please only enter a menu item number above'
				except ValueError:
					print 'Please only enter an integer from the menu items above'
			if update_choice == 1:
				print 'please enter new name'
				new_first = raw_input('first name: ')
				new_last = raw_input('last name: ')
				self.caretaker_dict[choice][0] = new_first
				self.caretaker_dict[choice][1] = new_last
			elif update_choice == 2:
				new_phone = self.process_phone()
				self.caretaker_dict[choice][2] = new_phone
			elif update_choice == 3:
				print 'please enter new address'
				new_address = raw_input('address: ')
				self.caretaker_dict[choice][3] = new_address
			elif update_choice == 4:
				print 'please enter new email'
				new_email = raw_input('email: ')
				self.caretaker_dict[choice][4] = new_email
			elif update_choice == 5:
				self.update_caretaker_rates(choice)
			elif update_choice == 6:
				return
			else:
				print 'invalid menu choice'
			another = raw_input('would you like to modify another attribute of this caretaker? Y/N ')
			if another.upper() == 'Y':
				updating = True
			elif another.upper() == 'N':
				self.write_caretaker_info(choice)
				self.write_caretaker_rates(choice)
				updating = False
			else:
				print 'please only enter Y or N'
				updating = True  
		
	def write_caretaker_info(self, choice_ID): #for updating caretaker records
		update_data = self.caretaker_dict[choice_ID]
		update_data.append(choice_ID)
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		with con:
			cur.execute('UPDATE caretaker SET first_name=?, last_name=?, phone=?, address=?, email=? WHERE ID=?', (update_data))			
			con.commit()
			
	def insert_caretaker_info(self, choice_ID): #for creating caretaker records
		update_data = self.caretaker_dict[choice_ID] 
#this choice_ID is only relevant as the key in this caretaker_dict. Once the record is created it will get a unique ID which is used going forward
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		with con:
			cur.execute('INSERT INTO caretaker(first_name, last_name, phone, address, email, is_deleted) VALUES(?, ?, ?, ?, ?, 0)', update_data)
			con.commit()
	
	def display_caretaker_rates(self, choice):
		self.load_caretaker_rates(choice) #load choice's rate info into self.caretaker_rate_dict
		# choice = [rate info]
		name_to_update = (self.caretaker_dict[choice][1], self.caretaker_dict[choice][0])
		update_ID = 0
		flow.clear()
		print '***************************************'
		print 'current caretaker rates for', name_to_update
		print '***************************************'
		for rate in self.caretaker_rate_dict:
			print rate, self.caretaker_rate_dict[rate][0], '$', self.caretaker_rate_dict[rate][1]
			
	def update_caretaker_rates(self, choice):
		self.display_caretaker_rates(choice)
		updating = True
		while updating:
			print '***************************************'
			print 'please enter the number of the rate you wish to update'
			print '***************************************'
			try:
				change = int(raw_input('? '))
				if change in self.caretaker_rate_dict:
					changing = True
					rate_name = self.caretaker_rate_dict[change][0]
					print 'please enter new rate for', rate_name
					while changing:
						try:
							new_rate = float(raw_input('? '))
							if new_rate >0:
								self.caretaker_rate_dict[change] = [rate_name, new_rate]
								print 'the new rate for', rate_name, 'is', new_rate
								changing = False
							else:
								print 'please only enter a number greater than zero'
						except ValueError:
							print 'please only enter a number greater than zero'
				else:
					print 'please only enter an integer from the list above'
			except ValueError:
				print 'please only enter an integer from the list above'
			print 'do you want to update another rate?'
			answering = True
			while answering:
				another = raw_input('Y/N ')
				if another.upper() == 'Y':
					answering = False
				elif another.upper() == 'N':
					answering = False
					updating = False
				else:
					print 'please only enter Y or N'
		self.write_caretaker_rates(choice)
		return choice
		
	def write_caretaker_rates(self, caretakerID): #this function updates existing rate_mapping records
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		with con:
			for rate in self.caretaker_rate_dict:
				rate_amt = self.caretaker_rate_dict[rate][1]
				update_data = [rate_amt, rate, caretakerID]
				cur.execute('UPDATE rate_mapping SET rate_amt=? WHERE rate_id=? AND caretaker_id=?', update_data)
				con.commit()
				
	def insert_caretaker_rates(self, caretakerID): #this function creates rate_mapping records
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		with con:
			for rate in self.caretaker_rate_dict:
				rate_amt = self.caretaker_rate_dict[rate][1]
				update_data = [rate, caretakerID, rate_amt]
				cur.execute('INSERT INTO rate_mapping(rate_id, caretaker_id, rate_amt) VALUES(?, ?, ?)', update_data)
				con.commit()

	def process_phone(self):
		processing = True
		international = False
		while processing:
			print 'please enter phone number'
			phone_no = raw_input('? ')
			phone_no = phone_no.strip()
			if phone_no[0] == '+' or phone_no[0] == '0':
				international = True
				processing = False
			else:
				international = False
			if international:
				pass
			else:
				phone_len = len(phone_no)
				try:
					phone_no = int(phone_no)
					if phone_len == 10:
						processing = False
					else:
						print 'please enter a 10 digit phone number without dashes or spaces'
				except ValueError:
					print 'please only enter a 10 digit phone number without dashes or spaces'
		return phone_no

'''
The Flow class manages the overall process of the program.  Principally this is establishing the main menu
and the continual run loop that looks to see when the program is over.
'''

class Flow(object):
	def __init__(self, name, menu_dict = {}):
		self.name = name
		self.menu_dict = {}

	def header(self):
		print '***************************************'
		print 'please enter the number of your choice'
		print '***************************************'

	def clear(self):
		print(' \n' *25)
	
	def menu(self):
		self.menu_dict = {
			1: ['update caretaker information', caretaker.caretaker_menu],
			2: ['update child information', children.update_child_menu],
			3: ['quick edit: view and edit this week''s hours', processing.edit_current_week],
			4: ['edit previous weeks', processing.edit_previous_week],
			5: ['run reports', reporting.reporting_menu],
			6: ['advanced options', advopt.menu],
			7: ['exit', self.end]
			}
		self.clear()
		self.header()
		for item in self.menu_dict:
			print item, self.menu_dict[item][0]
		choosing = True
		while choosing:
			try:
				choice = int(raw_input('? '))
				if choice in self.menu_dict:
					if choice == 7:
						choosing = False
						return 'X' 
					else: 
						self.menu_dict[choice][1]()
						choosing = False
				else:
					print 'choice not in menu'
			except ValueError:
				print 'please only enter an integer from the list above'	
		
	def end(self):
		end = 'X'
		return end
		
	def startup_load(self):
		current = True
		advopt.check_pref_enabled()
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		with con:
			cur.execute('SELECT * FROM caretaker')
			data = cur.fetchall()
			if data:
				pass
			else: #this should not happen as caretakers are a required part of the install program
				print 'No caretakers in database!'
				print 'Please input caretaker information to continue'
				caretaker.add_caretaker()
		processing.load_today(current)
		processing.load_day_dict()
		processing.load_week()
		processing.view_week()
	
	def flow(self):
		advopt.check_pref_enabled()
		self.clear()
		run_check = self.menu()
		return run_check

'''
Advanced Options Class manages bulk edit and export tools that are outside the day to day operations
of editing a week's data

Advanced Options also manages preferences, a concept which is likely to be central many users' regular
usage.  Preferences sets defaults for each week day's data so each time a new week is loaded those
defaults are present.  For users who have recurring schedules this speeds up the entry process.

In order for preferences to be used, they first have to be enabled via the preferences menu.  A flag in the
pref_enabled table tells advopt.pref_enabled if the preferences function are enabled; and if so, preferences
are applied to each new day_entry.  Preferences can always be overriden and do not overwrite days that already exist.
'''

class AdvOpt(object):
	def __init__(self, name, menu_dict, pref_enabled, pref_dict, bulk_update_data):
		self.name = name
		self.menu_dict = {} 
		self.pref_enabled = False
		self.pref_dict = {}
		self.bulk_update_data = {}
		
	def menu(self):
		self.check_pref_enabled()
		self.menu_dict = {
			1: ['set preferences', self.set_preferences],
			2: ['bulk update', self.bulk_update],
			3: ['export data', self.export_data],
			4: ['quick populate testing data', self.testing_data],
			5: ['return to the main menu', processing.backmenu]
			}
		flow.clear()
		flow.header()
		for item in self.menu_dict:
			print item, self.menu_dict[item][0]
		choosing = True
		while choosing:
			try:
				choice = int(raw_input('? '))
				if choice in self.menu_dict:
					if choice == 5:
						choosing = False
						return 'X' 
					else: 
						self.menu_dict[choice][1]()
						choosing = False
				else:
					print 'choice not in menu'
			except ValueError:
				print 'please only enter an integer from the list above'
				
	def check_pref_enabled(self):
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		is_enabled = 0
		with con:
			cur.execute('SELECT pref_enabled FROM pref_enabled')
			is_enabled = cur.fetchone()
		is_enabled = is_enabled[0]
		if is_enabled == 0:
			self.pref_enabled = False
		elif is_enabled == 1:
			self.pref_enabled = True
		else: #this should never happen but just in case
			print 'boolean error in pref_enabled table. this should not happen.  resetting table now, value to False.'
			raw_input('press enter to continue')
			cur.execute('DELETE FROM pref_enabled')
			con.commit()
			cur.execute('INSERT INTO pref_enabled(pref_enabled) values(0)')
			con.commit()
			self.pref_enabled = False
		
	def write_pref_enabled(self):
		is_enabled = 0
		if self.pref_enabled == True:
			is_enabled = 1
		else:
			pass
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		with con:
			cur.execute('UPDATE pref_enabled SET pref_enabled=? WHERE ID=1', (is_enabled,))
	
	def set_preferences(self):
		pref_dict = {
			1: ['view and update preferences', self.view_preferences],
			2: ['toggle preferences', self.toggle_pref],
			3: ['return to the main menu', processing.backmenu]
			}
		flow.clear()
		flow.header()
		for item in pref_dict:
			print item, pref_dict[item][0]
		choosing = True
		while choosing:
			try:
				choice = int(raw_input('? '))
				if choice in pref_dict:
					if choice == 3:
						choosing = False
						return 'X' 
					else: 
						pref_dict[choice][1]()
						choosing = False
				else:
					print 'choice not in menu'
			except ValueError:
				print 'please only enter an integer from the list above'
				
	def toggle_pref(self):
		flow.clear()
		if self.pref_enabled:
			print 'preferences are currently enabled'
		else:
			print 'preferences are NOT currently enabled'
		toggling = True
		while toggling:
			print 'enter 1 to enable preferences or 2 to disable preferences'
			try:
				enable = int(raw_input('? '))
				if enable == 1:
					self.pref_enabled = True
					toggling = False
				elif enable == 2:
					self.pref_enabled = False
					toggling = False
				else:
					print 'please only enter 1 or 2'
			except ValueError:
				print 'please only enter 1 or 2'
		self.write_pref_enabled()

				
	def view_preferences(self):
		flow.clear()
		if self.pref_enabled:
			print 'preferences are currently enabled'
		else:
			print 'preferences are NOT currently enabled'
		print '********************************'
		print 'preferences are daily standard settings. You can specify children, caretaker, rate, hours, and misc for any day of the week.'
		print 'once a preference has been set for a day it will become the default entry for that day, thus saving you time for standard schedules.'
		print 'however, you can always override or modify any days preference through the regular editing process'
		self.retrieve_pref_data()
		for day in self.pref_dict:
			child_name_string = ''
			for child in self.pref_dict[day]['children']:
				if child:
					child_name_string += self.pref_dict[day]['children'][child][0]
					child_name_string += ' '
					child_name_string += self.pref_dict[day]['children'][child][1]
					child_name_string += ', '
				else:
					pass
			day_name = processing.date_trans[day-1]
			print day_name
			print 'children', ":", child_name_string
			if self.pref_dict[day]['rate']:
				print 'caretaker', ":", self.pref_dict[day]['rate'][1]
			else:
				pass
			if self.pref_dict[day]['rate']:
				print 'rate', ':', self.pref_dict[day]['rate'][2], '$', self.pref_dict[day]['rate'][3]
			else:
				pass
			if self.pref_dict[day]['misc']:
				print 'hours', self.pref_dict[day]['hours'], 'misc', self.pref_dict[day]['misc'][0], self.pref_dict[day]['misc'][1]
			else:
				pass
			print '-------------------'
		print 'do you want to update preferences?'
		choosing = True
		while choosing:
			choice = raw_input('Y/N? ')
			if choice.upper() == 'Y':
				self.update_pref()
				choosing = False
			elif choice.upper() == 'N':
				choosing = False
			else:
				print 'please only enter Y or N'
				
	def update_pref(self):
		flow.clear()
		updating = True
		while updating:
			day_list = []
			day_name_list = []
			day_name_dict = {
				'MON': ['Monday', 1],
				'TUE': ['Tuesday', 2],
				'WED': ['Wednesday', 3],
				'THU': ['Thursday', 4],
				'FRI': ['Friday', 5],
				'SAT': ['Saturday', 6],
				'SUN': ['Sunday', 7]
				}
			print 'select the days you want to create a standard set of preferences for'
			print 'if your preferences vary day by day, repeat this process for each day'
			choosing = True
			while choosing:
				flow.clear()
				print 'please enter the first 3 letters of the day you want to edit'
				print 'or press M to return to the main menu'
				day = raw_input('? ')
				short_day = day[0:3]
				if short_day.upper() == 'M':
					choosing = False
					updating = False
					return 'M'
				elif short_day.upper() in day_name_dict:
					short_day = short_day.upper()
					if short_day in day_list:
						print 'this day is already chosen'
						adding = True
						while adding:
							print 'do you want to add another day to the update preferences list?'
							add = raw_input('Y/N ')
							if add.upper() == 'Y':
								adding = False
							elif add.upper() == 'N':
								adding = False
								choosing = False
							else:
								print 'please only enter Y or N'
					else:
						day_list.append(day_name_dict[short_day][1])
						day_name_list.append(day_name_dict[short_day][0])
						print 'chosen days are', day_name_list
						adding = True
						while adding:
							print 'do you want to add another day to the update preferences list?'
							add = raw_input('Y/N ')
							if add.upper() == 'Y':
								adding = False
							elif add.upper() == 'N':
								adding = False
								choosing = False
							else:
								print 'please only enter Y or N'
			if day_list:
				updated_pref_data = self.get_updated_pref_data()
				for day in day_list:
					self.pref_dict[day]['children'] = updated_pref_data['children']
					self.pref_dict[day]['rate'] = updated_pref_data['rate']
					self.pref_dict[day]['hours'] = updated_pref_data['hours']
					self.pref_dict[day]['misc'] = updated_pref_data['misc']
			self.write_pref_data()
			
	def write_pref_data(self):
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		with con:
			for day in self.pref_dict:
				pref_id = self.pref_dict[day]['pref_data'][0]
				week_day_id = day
				if self.pref_dict[day]['rate']:
					rate_map_id = self.pref_dict[day]['rate'][0]
					hours = self.pref_dict[day]['hours'][0]
					misc = self.pref_dict[day]['misc'][0]
					misc_note = self.pref_dict[day]['misc'][1]
				else:
					rate_map_id = 0
					hours = 0
					misc = 0
					misc_note = ''
				pref_update_data = [week_day_id, rate_map_id, hours, misc, misc_note, pref_id]
				cur.execute('UPDATE preferences SET week_day_ID=?, rate_map_ID=?, hours=?, misc=?, misc_note=? WHERE pref_ID=?', pref_update_data)
				con.commit()
				child_id_list = self.pref_dict[day]['children']
				cur.execute('DELETE FROM child_pref_mapping WHERE pref_ID=?', (pref_id,))
				con.commit()
				for child in child_id_list:
					child_mapping_data = [pref_id, child]
					cur.execute('INSERT INTO child_pref_mapping(pref_ID, child_ID) VALUES(?, ?)', child_mapping_data)
					con.commit()
					
			
	def get_updated_pref_data(self):
		updated_pref_data = {}
		child_pref_list = self.get_children_pref_data()
		caretaker_and_rate = self.get_caretaker_pref_data()
		#get child data from child_pref list
		#get caretaker data from caretaker
		hours = 0
		houring = True
		while houring:
			try:
				hours = float(raw_input('hours: '))
				if hours <=24.0:
					houring = False
				elif hours <0:
					print 'please enter a number 0 or higher'
				else:
					print 'please enter an number <= 24'
			except ValueError:
				print 'please only enter a numeric value'
		misc = 0
		misc_note = ''
		miscing = True
		while miscing:
			try:
				misc = float(raw_input('misc amount: '))
				if misc <0:
					print 'please only enter a positive numeric value'
				elif misc == 0:
					miscing = False
				else:
					misc_note = raw_input('misc note: ')
					miscing = False
			except ValueError:
				print 'please only enter a numeric value'
		updated_pref_data['children'] = child_pref_list #need to make sure all of these are in the same order as self.pref_dict
		updated_pref_data['rate'] = caretaker_and_rate
		updated_pref_data['hours'] = [hours]
		updated_pref_data['misc'] = [misc, misc_note]
		return updated_pref_data
		
	def get_children_pref_data(self):
		child_pref_list = []
		choosing = True
		while choosing:
			flow.clear()
			children.view_children()
			print 'please enter child ID or 0 to exit and not set child preferences for this list of days'
			print 'chosen child IDs', child_pref_list
			try:
				choice = int(raw_input('? '))
				if choice == 0:
					choosing = False
				elif choice in children.child_dict:
					if choice in child_pref_list:
						pass
					else:
						child_pref_list.append(choice)
						adding = True
						while adding:
							print 'do you want to add another child to the update preferences list?'
							add = raw_input('Y/N ')
							if add.upper() == 'Y':
								adding = False
							elif add.upper() == 'N':
								adding = False
								choosing = False
							else:
								print 'please only enter Y or N'
				else:
					print 'please only enter a child ID from the list or 0 to exit'
			except ValueError:
					print 'please only enter a child ID from the list or 0 to exit'
		return child_pref_list

	def get_caretaker_pref_data(self):
		caretaker_id = caretaker.select_caretaker()
		caretaker_name_str = caretaker.caretaker_dict[caretaker_id][0] + ' ' + caretaker.caretaker_dict[caretaker_id][0]
		caretaker.display_caretaker_rates(caretaker_id)
		rate_id = 0
		rate_map_id = 0
		rating = True
		while rating:
			try:
				rate_id = int(raw_input('please input rate ID above '))
				if rate_id in caretaker.caretaker_rate_dict:
					rate_name = caretaker.caretaker_rate_dict[rate_id][0]
					rate_amt = caretaker.caretaker_rate_dict[rate_id][1]
					rating = False
				else:
					print 'please only enter an integer from the list above'
			except ValueError:
					print 'please only enter an integer from the list above'
		#get rate_map_id from caretaker and rate id
		rate_map_data = [caretaker_id, rate_id]
		con = lite.connect('caretakercalc.db')
		with con:
			cur = con.cursor()
			cur.execute('SELECT rate_map_ID FROM rate_mapping WHERE caretaker_id=? AND rate_ID=?', rate_map_data)
			data = cur.fetchone()
			rate_map_id = data[0]
		caretaker_and_rate = [rate_map_id, caretaker_name_str, rate_name, rate_amt]
		return caretaker_and_rate
						
	def retrieve_pref_data(self):
		con = lite.connect('caretakercalc.db')
		pref_data = []
		with con:
			cur = con.cursor()
			cur.execute('SELECT * FROM preferences')
			pref_data = cur.fetchall()
		x = 1
		while x <=7:
			for entry in pref_data:
				y = x-1
				self.pref_dict[x] = {'pref_data': pref_data[y]}
				x +=1
		for day in self.pref_dict:
			pref_id = self.pref_dict[day]['pref_data'][0]
			children = self.get_child_pref(day, pref_id)
			rate_map_id = self.pref_dict[day]['pref_data'][2]
			rate = self.get_rate_pref(day, pref_id, rate_map_id)
			hours = [self.pref_dict[day]['pref_data'][3]]
			misc_data = [self.pref_dict[day]['pref_data'][4], self.pref_dict[day]['pref_data'][5]]
			self.pref_dict[day]['children'] = children
			self.pref_dict[day]['rate'] = rate
			self.pref_dict[day]['hours'] = hours
			self.pref_dict[day]['misc'] = misc_data


#pref_dict = {
#	1: {'children': {id: [firstname, lastname]}, 'rate': [rate_map_id, caretaker_name_string, ratename, rateamt], 'hours': [hours], 'misc': [miscamt, miscnote]},
#	key is week day id, 1 for monday through 7 for sunday
			
	def get_child_pref(self, day, pref_id):
		child_pref_dict = {}
		child_pref_data = []
		child_id_list = []
		con = lite.connect('caretakercalc.db')
		with con:
			cur = con.cursor()
			cur.execute('SELECT * FROM child_pref_mapping WHERE pref_id=?', (pref_id,))
			child_pref_data = cur.fetchall()
			if child_pref_data:
				for child in range(len(child_pref_data)):
					child_id = child_pref_data[child][2]
					cur.execute('SELECT First_Name, Last_Name FROM children WHERE ID=?', (child_id,))
					this_child_data = cur.fetchall()
					child_pref_dict[child_id] = this_child_data[0]
			else:
				pass
		return child_pref_dict
		
	def get_rate_pref(self, day, pref_id, rate_map_id):
		all_rate_data = []
		rate_pref_data = []
		con = lite.connect('caretakercalc.db')
		with con:
			cur = con.cursor()
			cur.execute('SElECT rate_id, caretaker_id, rate_amt FROM rate_mapping WHERE rate_map_ID=?', (rate_map_id,))
			rate_pref_data = cur.fetchall()
			if rate_pref_data:
				#get caretaker info, rate name, and assign to dictionary
				caretaker_ID = rate_pref_data[0][1]
				rate_ID = rate_pref_data[0][0]
				rate_amt = rate_pref_data[0][2]
				cur.execute('SELECT ID, first_name, last_name FROM caretaker WHERE ID=?', (caretaker_ID,))
				caretaker_data = cur.fetchall()
				caretaker_string = caretaker_data[0][1] + ' ' + caretaker_data[0][2]
				cur.execute('SELECT rate_name FROM rates WHERE ID=?', (rate_ID,))
				rate_name_data = cur.fetchall()
				rate_name = rate_name_data[0][0]
				all_rate_data = [rate_map_id, caretaker_string, rate_name, rate_amt]
			else:
				pass
		return all_rate_data

	def backmenu(self, bulk_update_date_range):
		pass

	def bulk_update(self):
		bulk_update_menu = {
			1: ['update all weekdays (monday-friday) in the date range', self.get_all_weekdays],
			2: ['update ALL days (monday-sunday) in the date range', self.get_all_days],
			3: ['choose weekdays in the date range to apply updates to', self.get_custom_days],
			4: ['cancel and return to the main menu', self.backmenu]
			}
		flow.clear()
		print 'please select a date range to update'
		print 'please select the BEGINNING of the date range'
		start_date = reporting.get_date_from_cal()
		flow.clear()
		print 'please select the END of the date range'
		end_date = reporting.get_date_from_cal()
		bulk_update_date_range = [start_date, end_date]
		flow.clear()
		print 'how do you want to process the update?'
		for option in bulk_update_menu:
			print option, bulk_update_menu[option][0]
		print 'please enter the number of your choice'
		answering = True
		while answering:
			try:
				answer = int(raw_input('? '))
				if answer in bulk_update_menu:
					bulk_update_menu[answer][1](bulk_update_date_range)
					#go from here to calculating the days, then getting data, then writing it
					answering = False
				else:
					print 'please only enter an integer from the list above'
			except ValueError:
				print 'please only enter an integer from the list above'

	def get_all_weekdays(self, bulk_update_date_range): #gets a list of only weekdays M-F between two dates
		update_date_list = []
		start_date_str = bulk_update_date_range[0]
		end_date_str = bulk_update_date_range[1]
		start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
		end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
		d = start_date
		weekend = [5,6]
		delta = timedelta(days=1)
		while d<= end_date:
			if d.weekday() not in weekend:
				update_date_list.append(d.strftime('%Y-%m-%d'))
			else:
				pass
			d += delta
		bulk_update_data = self.get_bulk_update_data()
		print 'are you sure you want to execute this bulk update?'
		answering = True
		while answering:
			answer = raw_input('Y/N ')
			if answer.upper() == 'Y':
				self.write_bulk_data(bulk_update_date_range, update_date_list, bulk_update_data)
				answering = False
			elif answer.upper() == 'N':
				print 'bulk update not executed'
				raw_input()
				answering = False
			else:
				print 'please only enter Y or N' 

	def get_custom_days(self, bulk_update_date_range): #gets a list dates using only specified days of the week with in a date range
		weekday_int_dict = {
			'MON': ['Monday', 0],
			'TUE': ['Tuesday', 1],
			'WED': ['Wednesday', 2],
			'THU': ['Thursday', 3],
			'FRI': ['Friday', 4],
			'SAT': ['Saturday', 5],
			'SUN': ['Sunday', 6]
			}
		update_date_list = []
		weekday_list = []
		weekday_int_list = []
		start_date_str = bulk_update_date_range[0]
		end_date_str = bulk_update_date_range[1]
		start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
		end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
		adding = True
		while adding:
			flow.clear()
			'''for day in weekday_int_dict: #no need for this
				print weekday_int_dict[day][0]'''
			print 'please select the weekdays you would like to apply the bulk updates to within the selected date range'
			#print 'current weekdays selected ', weekday_list
			print 'please enter the first 3 letters of the weekday'
			answer = raw_input('? ')
			short_ans = answer[0:3]
			short_ans = short_ans.upper()
			if short_ans in weekday_int_dict:
				weekday_list.append(weekday_int_dict[short_ans][0])
				weekday_int_list.append(weekday_int_dict[short_ans][1])
				print 'current weekdays selected ', weekday_list
				print 'would you like to add another weekday?'
				another = raw_input('Y/N ? ')
				if another.upper() == 'N':
					adding = False
				elif another.upper() == 'Y':
					pass
				else:
					print 'please only enter Y or N'
			else:
				print 'please only enter the name of the weekday'
		d = start_date
		delta = timedelta(days=1)
		while d<= end_date:
			if d.weekday() in weekday_int_list:
				update_date_list.append(d.strftime('%Y-%m-%d'))
			else:
				pass
			d += delta
		bulk_update_data = self.get_bulk_update_data()
		print 'are you sure you want to execute this bulk update?'
		answering = True
		while answering:
			answer = raw_input('Y/N ')
			if answer.upper() == 'Y':
				self.write_bulk_data(bulk_update_date_range, update_date_list, bulk_update_data)
				answering = False
			elif answer.upper() == 'N':
				print 'bulk update not executed'
				answering = False
			else:
				print 'please only enter Y or N' 
		
	def get_all_days(self, bulk_update_date_range): #gets a list of all dates between a date range
		update_date_list = []
		start_date_str = bulk_update_date_range[0]
		end_date_str = bulk_update_date_range[1]
		start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
		end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
		d = start_date
		delta = timedelta(days=1)
		while d<= end_date:
			update_date_list.append(d.strftime('%Y-%m-%d'))
			d += delta
		bulk_update_data = self.get_bulk_update_data()
		print 'are you sure you want to execute this bulk update?'
		answering = True
		while answering:
			answer = raw_input('Y/N ')
			if answer.upper() == 'Y':
				self.write_bulk_data(bulk_update_date_range, update_date_list, bulk_update_data)
				answering = False
			elif answer.upper() == 'N':
				print 'bulk update not executed'
				answering = False
			else:
				print 'please only enter Y or N' 

#executes bulk write
	def write_bulk_data(self, bulk_update_date_range, update_date_list, bulk_update_data):
		start_date = bulk_update_date_range[0]
		end_date = bulk_update_date_range[1]
		#update_data = [rate_map_ID, hours, misc_expense, misc_note]
		update_data = [bulk_update_data['rate'][0], bulk_update_data['hours'][0], bulk_update_data['misc'][0], bulk_update_data['misc'][1]]
		child_id_list = bulk_update_data['children']
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		with con:
			for date in update_date_list:
				cur.execute('SELECT entry_ID FROM day_entry WHERE date=?', (date,))
				entry_ID = cur.fetchone()
				if not entry_ID:
					entry_ID = 0
				else:
					entry_ID = entry_ID[0]
				cur.execute('DELETE FROM day_entry_child_mapping WHERE day_entry_id=?', (entry_ID,))
				con.commit()
				cur.execute('DELETE FROM day_entry WHERE date=?', (date,))
				con.commit()
				update_data.insert(0, date)
				cur.execute('INSERT INTO day_entry(date, rate_map_ID, hours, misc_expense_amt, misc_expense_note) VALUES(?, ?, ?, ?, ?)', update_data)
				con.commit()
				update_data.pop(0)
				cur.execute('SELECT MAX(entry_id) FROM day_entry')
				latest_entry_id = cur.fetchall()
				latest_entry_id = latest_entry_id[0][0]
				for child_id in child_id_list:
					cur.execute('INSERT INTO day_entry_child_mapping(day_entry_id, child_ID) VALUES(?, ?)', (latest_entry_id, child_id))
					con.commit()
				rate_map_ID = update_data[0]
				hours = update_data[1]
				misc_expense = update_data[2]
				total = processing.day_total_calc(hours, rate_map_ID, misc_expense)
				day_total_data = [total, latest_entry_id]
				cur.execute('UPDATE day_entry SET entry_total=? WHERE entry_ID=?', day_total_data)


#gets all data to use in the bulk update
	def get_bulk_update_data(self):
		bulk_update_data = {
			'children': [],
			'rate': [],
			'hours': [],
			'misc': []
			}
		children.view_children()
		print 'please enter the child ID to add to the bulk update days'
		answering = True
		while answering:
			try:
				choice = int(raw_input('? '))
				if choice in children.child_dict:
					bulk_update_data['children'].append(choice)
				else:
					print 'please only enter a child ID from the list above'
				print 'do you want to add another child?'
				another = raw_input('Y/N ')
				if another.upper() == 'N':
					answering = False
				else:
					answering = True
			except ValueError:
				print 'please only enter a child ID from the list above'
		caretaker_and_rate = self.get_caretaker_pref_data()
		bulk_update_data['rate'].append(caretaker_and_rate[0]) #only appending the rate map ID because that's all we need to write	
		houring = True
		while houring:
			try:
				hours = float(raw_input('please enter hours: '))
				if hours <=24:
					bulk_update_data['hours'].append(hours)
					houring = False
				else:
					print 'please enter a value less than or equal to 24'
			except ValueError:
				print 'please only enter a numeric value'
		miscing = True
		while miscing:
			try:
				misc = float(raw_input('please enter any misc amount '))
				if misc >= 0:
					misc_note = raw_input('please enter a note if desired: ')
					bulk_update_data['misc'].append(misc)
					bulk_update_data['misc'].append(misc_note)
					miscing = False
				else:
					print 'please only enter a vaule greater than or equal to zero'
			except ValueError:
				print 'please only enter a number greater than or equal to zero'
		return bulk_update_data

	def export_data(self): #export data main menu
		export_dict = {
			1: ['export all day data', self.export_days],
			2: ['export all child data', self.export_children],
			3: ['export all caretaker and rate data', self.export_caretaker],
			4: ['return to the main menu', self.backmenu]
			}
		flow.clear()
		for option in export_dict:
			print option, export_dict[option][0]
		print 'please enter the number of your choice'
		answering = True
		while answering:
			try:
				answer = int(raw_input('? '))
				if answer in export_dict:
					export_dict[answer][1]()
					answering = False
				else:
					print 'please only enter an integer from the list above'
			except ValueError:
				print 'please only enter an integer from the list above'
				
	def export_days(self): #export all day_entry data, joining in names and rates via ids
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		data = []
		with con:
			cur.execute('SELECT '
				'day_entry.entry_ID as day_entry_ID,'
				'day_entry.date as date,'
				'day_entry.hours as hours,'
				'day_entry.misc_expense_amt as misc_amt,'
				'day_entry.misc_expense_note as misc_note,'
				'day_entry.rate_map_ID as rate_map_id,'
				'rate_mapping.rate_amt as rate,'
				'rate_mapping.caretaker_id as caretaker_id,'
				'caretaker.first_name as caretaker_first_name,'
				'caretaker.last_name as caretaker_last_name,'
				'day_entry.entry_total as day_total,'
				'day_entry_child_mapping.child_ID as child_ID,'
				'children.first_name as child_first_name,'
				'children.last_name as child_last_name '
			'FROM '
				'day_entry '
				'LEFT JOIN day_entry_child_mapping ON day_entry.entry_ID = day_entry_child_mapping.day_entry_id '
				'LEFT JOIN rate_mapping ON day_entry.rate_map_ID = rate_mapping.rate_map_ID '
				'LEFT JOIN caretaker ON rate_mapping.caretaker_id = caretaker.ID '
				'LEFT JOIN children ON day_entry_child_mapping.child_ID = children.ID ')
			data = cur.fetchall()
		print 'exporting data to day_data_export.csv'
		raw_input('press any key to continue')
		with open('day_data_export.csv', 'wb') as f:
			writer = csv.writer(f)
			writer.writerow(['entry_ID', 'date', 'hours', 'misc_amt', 'misc_note', 'rate_map_id', 'rate', 
			'caretaker_id', 'caretaker_first_name', 'caretaker_last_name', 
			'day_total', 'child_ID,', 'child_first_name', 'child_last_name', 'week_close_ID'])
			writer.writerows(data)
		
	def export_children(self): #exporting children table
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		data = []
		with con:
			cur.execute('SELECT * from children')
			data = cur.fetchall()
		print 'exporting child data to child_data_export.csv'
		raw_input('press any key to continue')
		with open('child_data_export.csv', 'wb') as f:
			writer = csv.writer(f)
			writer.writerow(['child_ID,', 'first_name', 'last_name', 'birthday'])
			writer.writerows(data)
		
	def export_caretaker(self): #exporting caretaker table and rate_mapping table
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		data = []
		with con:		
			cur.execute('SELECT '
				'caretaker.id as caretaker_id, '
				'caretaker.first_name as first_name, '
				'caretaker.last_name as last_name, '
				'rate_mapping.rate_map_ID as rate_map_ID, '
				'rate_mapping.rate_id as rate_id, '
				'rates.rate_name as rate_name, '
				'rate_mapping.rate_amt as rate_amt '
			'FROM '
				'caretaker '
				'LEFT JOIN rate_mapping ON caretaker.ID=rate_mapping.caretaker_id '
				'LEFT JOIN rates ON rate_mapping.rate_id=rates.ID')
			data = cur.fetchall()
		print 'exporting caretaker data to caretaker_data_export.csv'
		raw_input('press any key to continue')
		with open('caretaker_data_export.csv', 'wb') as f:
			writer = csv.writer(f)
			writer.writerow(['caretaker_id', 'first_name', 'last_name', 'rate_map-ID', 'rate_id', 'rate_name', 'rate_amt'])
			writer.writerows(data)

	def testing_data(self): #quick populate data for testing
		children.child_dict = {
			1: [1, 'elle', 'bzze', '2016-05-05'],
			2: [2, 'jack', 'abbey', '2015-01-01']
			} 
		children.write_child_data()
		caretaker.caretaker_dict = {
			1: ['glonk', 'gloop', 2123334455, '335 madison', 'tse@go.co'],
			2: ['frank', 'blank', 9998887766, '79 madison', 'frank@er.co']
			}
		new_cids = [] #starting a list for new caretakerIDs created by the insert_caretaker_info process below
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		for cid in caretaker.caretaker_dict:
			caretaker.insert_caretaker_info(cid)
			with con:
				cur.execute('SELECT MAX(ID) FROM caretaker')
				cid = cur.fetchone()
				cid = cid[0]
				new_cids.append(cid)
		caretaker.caretaker_rate_dict = {
			1: ['Standard', 14.35],
			2: ['Overtime', 21.02],
			3: ['Share', 13.31]
			}
		cid_pos = 0
		for c in caretaker.caretaker_dict:
			caretakerID = c
			new_cid = new_cids[cid_pos]
			caretaker.insert_caretaker_rates(new_cid)
			cid_pos += 1
		children.child_dict = {}
		children.caretaker_dict = {}
		children.caretaker_rate_dict = {}
		#resetting the dicts


'''
The Processing Class manages the operations around the week to week data entry.  The primary mode of operations
is editing the current week.  All weeks are displayed Monday-Sunday.  When editing current week, the program
determines which dates to display based on datetime.today().  It then calls up the appropriate day_entry records.
If no records exist with that date, a new record is created.  If preferences are enabled, the preferences data is 
used to populate the new records.  

Users select the day to edit by typing the weekday name.  They then have a menu to edit all that day's data.

Users can also select to edit a previous week.  Users select a day in the past and the program determines the
Monday-Sunday week which includes that date.  The entire week is displayed.  As above, if no day_entry records
exist with those dates, new records are created.  If preferences are enabled, the preferences data is used 
to populate the new records.
'''

class Processing(object):
	def __init__(self, name, today, day_dict, date_trans, week_hours):
		self.name = name
		self.today = [] #list of [datetime.date(yyyy, mm, dd), day-int, day-name] day-int is based on datetime.weekday() 0-6, mon-sun
		self.day_dict = {} #dict of week's days and info
		self.date_trans = 	{
			0: 'Monday',
			1: 'Tuesday',
			2: 'Wednesday',
			3: 'Thursday',
			4: 'Friday',
			5: 'Saturday',
			6: 'Sunday'
			}
		self.week_hours = {}
		self.child_list = {} # day_id = [child_list]
	
	def load_today(self, current): #this runs based on edit current week or edit previous week choices in flow.menu
		self.today = []
		if current: #load based on current date
			today = date.today()
			weekday_int = today.weekday()
			weekday_str = self.date_trans[weekday_int]
			self.today.append(today)
			self.today.append(weekday_int)
			self.today.append(weekday_str)
		else: #load self.today based on the input of another date
			print 'enter a date in a week you want to edit'
			date_str = reporting.get_date_from_cal()
			otherdate = date(*map(int, date_str.split('-')))
			weekday_int = otherdate.weekday()
			weekday_str = self.date_trans[weekday_int]
			self.today.append(otherdate)
			self.today.append(weekday_int)
			self.today.append(weekday_str)
	
	def load_day_dict(self): #creates a dict based on the week being edited
		x = self.today[1] #self.today is populated based on flow.menu choice of current vs previous weeks
		key = 0
		while x >= 0:
			temp_day = self.today[0] - timedelta(x)
			temp_day_int = temp_day.weekday()
			temp_day_str = self.date_trans[temp_day_int]
			self.day_dict[key] = [temp_day, temp_day_int, temp_day_str]
			x -= 1
			key +=1
		y = self.today[1] + 1
		ahead = 1
		while y <= 6:
			temp_day = self.today[0] + timedelta(ahead)
			temp_day_int = temp_day.weekday()
			temp_day_str = self.date_trans[temp_day_int]
			self.day_dict[y] = [temp_day, temp_day_int, temp_day_str]
			y +=1
			ahead +=1
		for r in self.day_dict:
			format_date = str(self.day_dict[r][0])
			self.day_dict[r].append(format_date)
		#self.day_dict[weekday_int]: [datetime object, weekday_int, weekday_string, formatted_date_string]

	
	def load_week(self): #the backend process to calculate which date records will be worked on in the current process
	#the end goal of this process is to populate self.week_hours which holds all the day_entry data for the monday-sunday date records being edited  
		week_date_list = []
		week_data = []
		for date in self.day_dict:
			week_date_list.append(self.day_dict[date][3])
		con = lite.connect('caretakercalc.db')
		x = 1
		with con:
			cur = con.cursor()
			for date in week_date_list:
				cur.execute('SELECT * FROM day_entry WHERE date=?', [date]) 
				data = cur.fetchone() #there shouldn't be more than one entry per day but if there is, this just takes the first one
				if data:
					for item in data:
						week_data.append(item)
					self.week_hours[x] = week_data
					day_entry_ID = self.week_hours[x][0]
					cur.execute('SELECT * FROM day_entry_child_mapping WHERE day_entry_ID=?', (day_entry_ID,))
					does_exist = cur.fetchall() #checks to see if a day_entry_child_mapping record exists for the day_entry
					if does_exist:
						pass
					else: #if no mapping record, it creates one 
						cur.execute('INSERT INTO day_entry_child_mapping (day_entry_ID) values(?)', (day_entry_ID,)) 
						con.commit()
					x +=1
					week_data = []
				else: #if there is no entry for that date, create an empty record USE ADVOPT.PREF_ENABLED here
					if advopt.pref_enabled:
						week_day_ID = x
						cur.execute('SELECT * FROM preferences WHERE week_day_ID=?', (week_day_ID,))
						pref_data = cur.fetchall()
						pref_data = pref_data[0]
						pref_id = pref_data[0]
						rate_map_ID = pref_data[2]
						hours = pref_data[3]
						misc = pref_data[4]
						misc_note = pref_data[5]
						update_data = [date, rate_map_ID, hours, misc, misc_note]
						cur.execute('INSERT INTO day_entry(date, rate_map_ID, hours, misc_expense_amt, misc_expense_note) VALUES(?, ?, ?, ?, ?)', update_data)
						con.commit()
						cur.execute('SELECT MAX(entry_ID) from day_entry')
						day_entry_ID = cur.fetchone()
						day_entry_ID = day_entry_ID[0]
						cur.execute('SELECT child_id FROM child_pref_mapping WHERE pref_ID=?', (pref_id,))
						child_id_list = cur.fetchall()
						if child_id_list:
							for child in child_id_list:
								child_map_data = [day_entry_ID, child[0]]
								cur.execute('INSERT INTO day_entry_child_mapping(day_entry_ID, child_ID) values(?, ?)', child_map_data)
								con.commit()
						cur.execute('SELECT * FROM day_entry WHERE date=?', (date,))
						data = cur.fetchone()
						for item in data:
							week_data.append(item)
						self.week_hours[x] = week_data
						x +=1
						week_data = []
					else:
						base_values = [date, 1] #adding the date and setting an arbitrary 1 for rate_map_id to link in caretaker (need to fix this later)
						cur.execute('INSERT INTO day_entry (date, rate_map_ID) values(?, ?)', base_values)
						con.commit()
						cur.execute('SELECT MAX(entry_ID) from day_entry')
						day_entry_ID = cur.fetchone()
						day_entry_ID = day_entry_ID[0]
						cur.execute('INSERT INTO day_entry_child_mapping (day_entry_ID) values(?)', (day_entry_ID,)) 
						con.commit()
						cur.execute('SELECT * FROM day_entry WHERE date=?', [date]) 
						data = cur.fetchone()
						for item in data:
							week_data.append(item)
						self.week_hours[x] = week_data
						x +=1
						week_data = []
			for day in self.week_hours:
				self.child_list[day] = []
				entry_id = self.week_hours[day][0]
				cur.execute('SELECT child_id FROM day_entry_child_mapping WHERE day_entry_id=?', (entry_id,))
				day_child_id_list = cur.fetchall()
				for id in range(len(day_child_id_list)):
					child_id = day_child_id_list[id][0]
					if child_id:
						cur.execute('SELECT first_name, last_name FROM children WHERE ID=?', (child_id,))
						child_data = cur.fetchall()
						if child_data:
							self.child_list[day].append([child_data[0][0], child_data[0][1], child_id])
						else:
							pass
					else:
						pass
			for day in self.week_hours:
				entry_id = self.week_hours[day][0]
				cur.execute('SELECT * FROM day_entry WHERE entry_ID=?', (entry_id,))
				data = cur.fetchall()
				day_total = data[0][6]
				if day_total: #should this check that the math is right vs just passing?
					pass
				else:
					hours = data[0][3]
					rate_map_id = data[0][2]
					misc = data[0][4]
					new_total = self.day_total_calc(hours, rate_map_id, misc)
					update_data = [new_total, entry_id]
					cur.execute('UPDATE day_entry SET entry_total=? WHERE entry_id=?', update_data)
					con.commit()
					
				
# 1: [1, u'2016-09-19', 1, 8.0, 5.0, u'travel expense', None, None],
# self.week_hours[day_id] = [entry_id, date, rate_map_id, hours, misc_expense_amt, misc_expense_note, total]
			
	def day_total_calc(self, hours, rate_map_id, misc_expense): #calculates the total for the day_entry record
		rate = 0
		con = lite.connect('caretakercalc.db')
		with con:
			cur = con.cursor()
			cur.execute('SELECT rate_amt FROM rate_mapping where rate_map_id=?', [rate_map_id])
			rate = cur.fetchall()
			if rate:
				rate = rate[0][0]
			else:
				rate = 0
		if hours == None:
			hours = 0
		if misc_expense == None:
			misc_expense = 0
		total = (hours * rate) + misc_expense
		return total
	
	def get_caretaker_name(self, rate_map_id):
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		caretaker_name_list = []
		if rate_map_id == 0: #zero is the value inserted if there is no caretaker that day
			caretaker_name_list = ['no', 'caretaker', 0]
		else:
			with con:
				cur.execute('SELECT caretaker_id FROM rate_mapping WHERE rate_map_ID=?', (rate_map_id,))
				caretaker_id = cur.fetchall()
				caretaker_id = caretaker_id[0][0]
				cur.execute('SELECT first_name, last_name FROM caretaker WHERE ID=?', (caretaker_id,))
				data = cur.fetchall()
				caretaker_name_tup = data[0]
				caretaker_name_list = list(caretaker_name_tup)
				caretaker_name_list.append(caretaker_id)
		return caretaker_name_list #returns [first_name, last_name, caretaker_id]
				
	def get_child_data(self, child_id):
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		child_name_list = []
		with con:		
			cur.execute('SELECT first_name, last_name FROM children WHERE ID=?', (child_id,))
			names = cur.fetchall()
			child_name_list.append(names[0][0])
			child_name_list.append(names[0][1])
		return child_name_list
			
	def view_week(self): #the process to display the monday-sunday data for user editing using self.week_hours
		caretaker_total_dict = {}
		for day in self.day_dict: #day dict key is the same as week hours key - 1
			next_day = day + 1
			rate_map_id = self.week_hours[next_day][2]
			entry_id = self.week_hours[next_day][0]
			child_string = ''
			caretaker = self.get_caretaker_name(rate_map_id) #returns list of [first_name, last_name, caretaker_id]
			caretaker_id = caretaker[2]
			caretaker_str = caretaker[0] + ' ' + caretaker[1]
			rate_name = self.get_rate_name(rate_map_id) 
			rate_amt = self.get_rate(rate_map_id)
			hours = self.week_hours[next_day][3]
			misc_expense = self.week_hours[next_day][4]
			day_total = self.day_total_calc(hours, rate_map_id, misc_expense)
			if caretaker_id in caretaker_total_dict:
				earlier_total = caretaker_total_dict[caretaker_id][1]
				new_total = day_total + earlier_total
				caretaker_total_dict[caretaker_id] = [caretaker_str, new_total]
			else:
				caretaker_total_dict[caretaker_id] = [caretaker_str, day_total]
			for name in range(len(self.child_list[next_day])):
				child_string += self.child_list[next_day][name][0]
				child_string += ' '
				child_string += self.child_list[next_day][name][1]
				if name != len(self.child_list[next_day]) - 1:
					child_string += ' | '
				else:
					pass
			print '***********************'
			print '====>', self.day_dict[day][0].strftime('%x'), self.day_dict[day][2], 'HOURS', self.week_hours[next_day][3], 'MISC', self.week_hours[next_day][4]
			print 'CARETAKER', caretaker[0], caretaker[1], 'RATE TYPE', rate_name, rate_amt, 'DAY TOTAL', day_total
			print 'CHILDREN', child_string
		print '***********************'
		print 'WEEK TOTALS'
		print '***********************'
		week_total = 0
		for cid in caretaker_total_dict:
			if cid == 0:
				pass
			else:
				print caretaker_total_dict[cid][0], caretaker_total_dict[cid][1]
				week_total += caretaker_total_dict[cid][1]
		print 'WEEK TOTAL FOR ALL CARETAKERS', week_total
			
		
# self.week_hours[day_id] = [entry_id, date, rate_map_id, hours, misc_expense_amt, misc_expense_note, total, week_close_id] 
			

	def input(self): #function to select weekday
		day_name_dict = {
			'MON': ['Monday', 1],
			'TUE': ['Tuesday', 2],
			'WED': ['Wednesday', 3],
			'THU': ['Thursday', 4],
			'FRI': ['Friday', 5],
			'SAT': ['Saturday', 6],
			'SUN': ['Sunday', 7]
			}
		self.view_week()
		chosen_day = 0
		choosing = True
		while choosing:
			print 'please enter the name of the day you want to edit'
			print 'or type ''M'' for the main menu'
			choice = raw_input('? ')
			short_choice = choice[0:3]
			if short_choice.upper() == 'M':
				return short_choice
				choosing = False
			elif short_choice.upper() in day_name_dict:
				chosen_day = day_name_dict[short_choice.upper()][1] #this is the key for self.week_hours
				choosing = False
			else:
				choosing = True
				print 'please only enter the name of a day'
		return chosen_day

	def update_day(self): #master function to guide the updating of a day record via self.week_hours
		day = self.input()
		if str(day).upper() == 'M':
			return day
		elif day in self.week_hours:
			update_menu = {
			1: ['Update Hours', self.update_hours],
			2: ['Update Misc', self.update_misc],
			3: ['Update Caretaker and Rate', self.update_caretaker],
			4: ['Update Children', self.update_children],
			5: ['Done Editing Day', self.backmenu]
			}
			choosing = True
			while choosing:
				for option in update_menu:
					print option, update_menu[option][0]
				print 'please enter the number of your choice'
				try:
					choice = int(raw_input('? '))
					if choice == 5:
						update_menu[choice][1](day)
						choosing = False
					elif choice in update_menu:
						update_menu[choice][1](day)
					else:
						choosing = True
				except ValueError:
					print 'please only enter an integer from the list above'
					choosing = True
		else:
			return 'ERROR this should not happen because processing.input should weed out any exceptions'
	
	def update_caretaker(self, day):
		print 'select caretaker IDs from the list below'
		choice = caretaker.select_caretaker()
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		rate_map_id = 0
		with con:
			cur.execute('SELECT rate_map_id FROM rate_mapping WHERE caretaker_id=? LIMIT 1', (choice,))
			rate_map_id = cur.fetchall()
			rate_map_id = rate_map_id[0][0]
		self.week_hours[day][2] = rate_map_id #assigns the standard rate of the new caretaker to self.week_hours. Doing this to prime the change_rate function
		self.change_rate(day)
		
		
	def update_children(self, day):
		print 'select child IDs from the list below'
		children.view_children()
		add_child_list = []
		adding = True
		while adding:
			print 'please enter child ID or M to return to the menu'
			new_child = raw_input('? ')
			if new_child.upper() == 'M':
				adding = False
				return
			elif int(new_child) in children.child_dict:
				child_id = int(new_child)
				add_child_list.append(child_id) 
				print 'add another child?'
				another = True
				keep_going = raw_input('Y/N ')
				if keep_going.upper() == 'Y':
					adding = True
				elif keep_going.upper() == 'N':
					another = False
					adding = False
				else:
					print 'please only enter Y or N'
			else:
				print 'please only enter Y, N or M'
		self.child_list[day] = []
		for id in add_child_list:
			name_data = self.get_child_data(id)
			name_data.append(id)
			self.child_list[day].append(name_data)
	
	def update_hours(self, day):
		print 'enter hours'
		editing_hours = True
		while editing_hours:
			try:
				hours = float(raw_input('? '))
				self.week_hours[day][3] = hours 
				editing_hours = False
			except ValueError:
				print 'please only enter numbers'
				
	def update_misc(self, day):
		print 'enter any misc expense'
		editing_misc = True
		while editing_misc:
			try:
				misc = float(raw_input('? '))
				misc_note = 'None'
				if misc != 0:
					print 'enter a misc expense note if you want'
					misc_note = raw_input('? ')
				else:
					pass
				self.week_hours[day][4] = misc
				self.week_hours[day][5] = misc_note
				editing_misc = False
			except ValueError:
				print 'please only enter numbers; if no misc expense enter 0'
	
	def get_rate_name(self, rate_map_id):
		con = lite.connect('caretakercalc.db')
		rdata = []
		rate_name = ''
		with con:
			cur = con.cursor()
			cur.execute('SELECT rate_name FROM rates WHERE id=(SELECT rate_id FROM rate_mapping WHERE rate_map_ID=?)', (rate_map_id,))
			rdata = cur.fetchall() 
			if rdata:
				rate_name = rdata[0][0]
			else:
				rate_name = ('no rate')
		return rate_name
		
	def get_rate(self, rate_map_id):
		con = lite.connect('caretakercalc.db')
		rdata = []
		with con:
			cur = con.cursor()
			cur.execute('SELECT rate_amt FROM rate_mapping WHERE rate_map_id=?', (rate_map_id,))
			rdata = cur.fetchall()
			if rdata:
				rate = rdata[0][0]
			else:
				rate = 0
		return rate
	
	def display_rate(self, day_id):
		rate_name = self.get_rate_name(self.week_hours[day_id][2]) #rate_map_id
		rate = self.get_rate(self.week_hours[day_id][2])
		print 'Current Rate: ', rate_name, rate, '/hr'
		
	def view_all_caretaker_rates(self, rate_map_id): #function to display all caretaker rates for user selection
		con = lite.connect('caretakercalc.db')
		rdata = []
		caretaker_data_from_rate_mapping = []
		rate_id_list = []
		caretaker_data = []
		caretaker_id = 0
		with con:
			cur = con.cursor()
			cur.execute('SELECT caretaker_id FROM rate_mapping WHERE rate_map_id=?', (rate_map_id,))
			rdata = cur.fetchall()
			caretaker_id = rdata[0][0]
			cur.execute('SELECT rate_map_id, rate_id, rate_amt FROM rate_mapping WHERE caretaker_id=?', (caretaker_id,))
			caretaker_data_from_rate_mapping = cur.fetchall() #results are [(rate_map_id, rate_id, rate_amt), (etc)]			
		x = 0
		for item in caretaker_data_from_rate_mapping:
			y = 0
			entry_data = []
			rate_map_id = caretaker_data_from_rate_mapping[x][y]
			rate_name = self.get_rate_name(rate_map_id)
			entry_data.append(rate_name)
			for g in caretaker_data_from_rate_mapping[x]:
				entry_data.append(caretaker_data_from_rate_mapping[x][y])
				y +=1
			caretaker_data.append(entry_data)
			#entry_data = [rate_name, rate_map_id, rate_id, rate_amt]
			x +=1
		caretaker_rate_ids = []
		w = 0
		for e in caretaker_data:
			print caretaker_data[w][2], caretaker_data[w][0], caretaker_data[w][3]
			caretaker_rate_ids.append(caretaker_data[w][2])
			w +=1
		caretaker_rate_ids_and_caretaker_id = [caretaker_rate_ids]
		caretaker_rate_ids_and_caretaker_id.append(caretaker_id)
		return caretaker_rate_ids_and_caretaker_id
		
	def change_rate(self, day_id): #function to select a new caretaker rate
		print 'Please select the rate for this caretaker for this day'
		caretaker_rate_ids = self.view_all_caretaker_rates(self.week_hours[day_id][2]) #displays all rates for the caretaker
		rating = True 
		while rating:
			try:
				new_rate = int(raw_input('? '))
				if new_rate in caretaker_rate_ids[0]:
					caretaker_id = caretaker_rate_ids[1]
					new_rate_map_id = []
					con = lite.connect('caretakercalc.db')
					with con:
						cur = con.cursor()
						cur.execute('SELECT rate_map_id FROM rate_mapping WHERE caretaker_id=?', (caretaker_id,))
						new_rate_map_id = cur.fetchall()
						if new_rate_map_id:
							self.week_hours[day_id][2] = new_rate_map_id[0][0] 
							#there should only be one ID in this list. However if there are more, it simply takes the first one
						else:
							print 'Error, no rate mapping found'
					rating = False
				else:
					print 'Please only enter an integer from the list above'
					rating = True
			except ValueError:
				print 'please only enter an integer from the list above'
		
	def keep_editing(self):
		print 'do you want to edit another day?'
		answering = True
		keep = True
		while answering:
			another = raw_input('Y/N ')
			if another.upper() == 'Y':
				keep = True
				answering = False
			elif another.upper() == 'N':
				keep = False
				answering = False
			else:
				print 'please only enter Y or N'
		return keep
	
	def write_day(self): #function to write changes back to the database using self.week_hours. 
	#this is set to run after each day is done being updated so that each time view_week is reloaded
	#the updated changes will show
		for day in self.week_hours:
			hours = self.week_hours[day][3]
			rate_map_id = self.week_hours[day][2]
			misc_expense = self.week_hours[day][4]
			day_total = self.day_total_calc(hours, rate_map_id, misc_expense)
			self.week_hours[day][6] = day_total
		con = lite.connect('caretakercalc.db')
		with con:
			cur = con.cursor()
			for x in self.week_hours: #
				update_data = self.week_hours[x][0:7]
				id = update_data.pop(0)
				update_data.append(id)
				cur.execute('UPDATE day_entry SET date=?, rate_map_id=?, hours=?, misc_expense_amt=?, misc_expense_note=?, entry_total=? WHERE entry_id=?', update_data)
				con.commit()
				cur.execute('DELETE FROM day_entry_child_mapping WHERE day_entry_id=?', (id,))
				con.commit()
				for child in range(len(self.child_list[x])):
					update_child_data = [self.week_hours[x][0], self.child_list[x][child][2]] #[day_entry_id, child_id]
					cur.execute('INSERT INTO day_entry_child_mapping(day_entry_id, child_ID) VALUES(?,?)', update_child_data)
					con.commit()
	
	def edit_previous_week(self): #gets dates for editing a previous week
		current = False
		self.load_today(current)
		self.load_day_dict() 
		self.load_week()
		keep = True
		while keep:
			option = self.update_day()
			if str(option).upper() == 'M':
				keep = False
			else:
				keep = self.keep_editing()
		self.write_day()
	
	def backmenu(self, day):
		pass
	
	def edit_current_week(self): #establishes that the processing of load and view_week will run on the current week
		current = True
		self.load_today(current)
		self.load_day_dict()
		self.load_week()
		keep = True
		while keep:
			option = self.update_day()
			if str(option).upper() == 'M':
				keep = False
			else:
				keep = self.keep_editing()
		self.write_day()

'''
The reporting class holds processes for selecting and executing custom reports.
'''

class Reporting(object):
	def __init__(self, name):
		self.name = name
		
	def reporting_menu(self):
		flow.clear()
		reporting_menu = {
			1: ['Totals By Week', self.totals_by_week], #by selecting a week end date, user gets a dollar total for that week
			2: ['Totals By Child', self.totals_by_child], #totals by child for all dates
			3: ['Totals By Caretaker', self.totals_by_caretaker], #totals by caretaker for all dates
			4: ['Total From Custom Date Range', self.totals_by_custom_date_range], #total dollar amount based on custom date range
			5: ['Return to Menu', self.backmenu]
			}
		for option in reporting_menu:
			print option, reporting_menu[option][0]
		choosing = True
		while choosing:
			print 'please enter the number of your choice'
			print 'or type ''m'' for the main menu or ''x'' to exit'
			try:
				choice = int(raw_input('? '))
				if choice in reporting_menu:
					reporting_menu[choice][1]()
					choosing = False
				else:
					choosing = True
			except ValueError:
				print 'please only enter an integer from the list above'
				choosing = True
	
	def get_week_end(self): #for use in totals by week
		right_length = True
		while right_length:
			print 'please enter week end (SUNDAY) date in YYYY-MM-DD format'
			week_end_date = raw_input('? ')
			if len(week_end_date) == 10:
				return week_end_date
				right_length = False
			else:
				print 'please only enter YYYY-MM-DD format WITH dashes'
				
	def get_date(self): #simplified get_date function; this has been superseded in almost all cases by get_date_from_cal
		right_length = True
		while right_length:
			print 'please enter a date in YYYY-MM-DD format'
			date_response = raw_input('? ')
			if len(date_response) == 10:
				return date_response
				right_length = False
			else:
				print 'please only enter YYYY-MM-DD format WITH dashes'
				
	def get_date_from_cal(self): #function to get date string based on a command line cal display, for ease of user entry
		current_date = dt.date.today()
		current_month = current_date.month
		current_year = current_date.year
		last_day_of_month = calendar.monthrange(current_year, current_month)
		last_day_of_month = last_day_of_month[1]
		inputting = True
		while inputting:
			cal.prmonth(current_year, current_month)
			input_date = raw_input('please enter day of month or press C to change month ')
			if input_date.upper() == 'C':
				yearing = True
				while yearing:
					try:
						current_year = int(raw_input('please enter year (YYYY) '))
						if len(str(current_year)) == 4:
							yearing = False
						else:
							print 'please only enter an integer YYYY'
					except ValueError:
						print 'please only enter an integer YYYY'
				monthing = True
				while monthing:
					try:
						current_month = int(raw_input('please enter a month integer (MM) '))
						if current_month >= 1 and current_month <= 12:
							monthing = False
						else:
							print 'please only enter an integer from 1-12'
					except ValueError:
						print 'please only enter an integer MM'
				last_day_of_month = calendar.monthrange(current_year, current_month)
				last_day_of_month = last_day_of_month[1]
			elif (int(input_date)-1) in range(last_day_of_month):
				date_string = str(current_year)
				date_string += '-'
				date_string += str(current_month)
				date_string += '-'
				if len(input_date) == 1:
					date_string += '0'
				else:
					pass
				date_string += input_date
				return date_string
				inputting = False
			else:
				print 'please only enter an integer day of the month above or press C to change month'
		
	def totals_by_week(self):
		flow.clear()
		week_end_date = ''
		week_end = ''
		print 'please enter a SUNDAY representing the END of the week you want to total'
		not_sunday = True
		while not_sunday:
			week_end_date = self.get_date_from_cal()
			week_end_date_parsed = week_end_date.split('-')
			year = int(week_end_date_parsed[0])
			month = int(week_end_date_parsed[1])
			day = int(week_end_date_parsed[2])
			week_end = dt.date(year, month, day)
			print 'week_end.weekday() is', week_end.weekday()
			if week_end.weekday() == 6:
				not_sunday = False
			else:
				print 'please make sure you select a SUNDAY representing the END of the week you want to total'
		week_start = week_end - timedelta(6)
		week_start_str = str(week_start)
		week_start_end_list = [week_start_str, week_end_date]
		latest_total = 0
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		with con:
			cur.execute('SELECT sum(entry_total) FROM day_entry WHERE date BETWEEN ? AND ?', week_start_end_list)
			data = cur.fetchall()
			latest_total = data[0][0]
		print '*************************'
		print 'TOTAL FOR WEEK ENDING', week_end_date
		print '*************************'
		print latest_total
		raw_input('press any key to return to the menu')
		
	def totals_by_child(self):
		flow.clear()
		children.view_children()
		choosing = True
		while choosing:
			print 'please enter child ID'
			try:
				child = int(raw_input('? '))
				if child in children.child_dict:
					child_total = self.totals_by_child_processing(child)
					print '*************************'
					print 'TOTAL FOR CHILD', child, ':', children.child_dict[child][1], children.child_dict[child][2]
					print '*************************'
					print child_total
					raw_input('press any key to return to the menu')
					choosing = False
				else:
					print 'please only enter a child ID'
			except ValueError:
				print 'please only enter a child ID'
		
	def totals_by_child_processing(self, child):
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		with con:
			cur.execute('SELECT SUM(entry_total) FROM day_entry JOIN day_entry_child_mapping ON day_entry.entry_ID=day_entry_child_mapping.day_entry_ID WHERE child_ID=?', (child,))
			child_total = cur.fetchall()
			child_total = child_total[0][0]
			return child_total
		
	def totals_by_caretaker(self):
		flow.clear()
		caretaker.display_caretaker()
		choosing = True
		while choosing:
			print 'please enter caretaker ID'
			try:
				caretaker_id = int(raw_input('? '))
				if caretaker_id in caretaker.caretaker_dict:
					caretaker_total = self.totals_by_caretaker_processing(caretaker_id)
					print '*************************'
					print 'TOTAL FOR CARETAKER', caretaker_id, ":", caretaker.caretaker_dict[caretaker_id][0], caretaker.caretaker_dict[caretaker_id][1]
					print '*************************'
					print caretaker_total
					raw_input('press any key to return to the menu')
					choosing = False
				else:
					print 'please only enter a caretaker ID'
			except ValueError:
				print 'please only enter a caretaker ID'
				
	def totals_by_caretaker_processing(self, caretaker_id):
		caretaker_total = 0
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		with con:
			cur.execute('SELECT rate_map_ID FROM rate_mapping WHERE caretaker_ID=?', (caretaker_id,))
			all_rate_map_ID = cur.fetchall()
			for id in all_rate_map_ID:
				rate_map_ID=id[0]			
				cur.execute('SELECT SUM(entry_total) FROM day_entry WHERE rate_map_ID=?', (rate_map_ID,))
				rate_ID_total = cur.fetchall()
				if rate_ID_total[0][0]:
					caretaker_total += rate_ID_total[0][0]
				else:
					pass
			return caretaker_total
			
	def get_date_range(self): #function to return list of date strings - does not have to be sequential as this drives a BETWEEN function
		print 'please select the start date'
		start_date_string = self.get_date_from_cal()
		print 'please select the end date'
		end_date_string = self.get_date_from_cal()
		date_range = [start_date_string, end_date_string]
		return date_range
		
	def totals_by_custom_date_range(self):
		date_range = self.get_date_range()
		date_range.sort() #making sure the earliest date is first
		#date range strings need to have leading 0s on single digits
		custom_range_total = 0
		con = lite.connect('caretakercalc.db')
		cur = con.cursor()
		with con:
			cur.execute('SELECT SUM(entry_total) FROM day_entry WHERE date BETWEEN ? AND ?', date_range)
			sum = cur.fetchall()
			custom_range_total = sum[0][0]
			print '*************************'
			print 'TOTAL FOR CUSTOM DATE RANGE BETWEEN', date_range[0], 'AND', date_range[1]
			print '*************************'
			print custom_range_total
			raw_input('press any key to return to the menu')
	
	def backmenu(self):
		pass

processing = Processing('processing', [], {}, {}, {})
flow = Flow('flow', {})
caretaker = Caretaker('caretaker', {}, {})
children = Children('children', {})
reporting = Reporting('reporting')
cal = calendar.TextCalendar(0)
advopt = AdvOpt('advanced options', {}, False, {}, {})

'''
Main function to manage basic running loop
'''

def main():
	flow.startup_load()
	missing_tables = install_check()
	if missing_tables:
		return 'database not installed; please run the setup program'
	else:
		pass
	running = True
	while running:
		run_check = flow.flow()	
		if run_check == 'X':
			running = False
		else:
			pass
	print 'goodbye'
	
main()
####Caretaker Calc README — by bencockerham — November 14, 2016

###Overview: this is a command line program written in Python 2.7 and using a SQLite3 database to track and manage hours worked for a child's caretaker. The program allows you to:

-add and manage multiple caretakers' information including contact information and rates

-add and manage child information

-create a record for each day recording hours worked, the caretaker and his or her rate, the children being cared for, and misc expense and notes

-easily view day and week totals due to caretakers

-set default hours and data for each day of the week to speed entry

-retroactively modify prior dates 

-execute bulk data updates

-run reports by date range, caretaker, and child

-export data to csv

###Installation 
Before CaretakerCalc can be run, you must first run the installation program. The installation program creates the database and prompts for child and caretaker entry. That entry is optional and can also be run from the main program. However it may save you time in the setup process. Note: running the install program ERASES any pre-existing data from CaretakerCalc.  

#Quick Start — 5 easy steps to get up and running
  1. INSTALL AND SET UP: Run caretaker_calc_install and input child and caretaker data, including caretaker’s rates
  2. DAILY OPERATIONS: Run caretaker_calc.  Choose menu option 3 to see the current week (Monday-Sunday) based on today’s date.  By typing the week day name (i.e. ‘Monday’) you can edit attributes of the day including caretaker, rate, and hours worked.  A total appears for each day and for the week as a whole, broken down by caretaker.  Every Monday, a blank slate (or default data, if you have preferences enabled, see below) is created for the dates Monday-Sunday of that week.
  3. PREVIOUS WEEKS: Choose option 4 to view or edit previous weeks.  Choose a date and the program will bring up the Monday-Sunday days around that date.  From there you can edit prior days using the same operations as in option 2 above.
  4.  ADVANCED OPTIONS: Among other things, the advanced options menu allows you to set preferences for each weekday.  This is helpful if you have a recurring schedule — say every Monday and Wednesday you have the same caretaker, rate, hours, and children, but Tuesday and Thursday are different.  Preferences allows you to establish these defaults.  Every time a new week is created, the days will load with those preferences as defaults.  It will not override existing data, and once created, preferences data can be manually adjusted as part of the regular weekly operations.  Note that preferences must be ENABLED via the Toggle Preferences menu before it is active.  Further note that preferences will be applied when creating new date records for prior days.  For example, if you wanted to edit a week from many months ago where no date records already exist, when you call up those dates the preferences you selected would be pre-loaded (from there you can edit further).  Advanced Options also allows you to bulk update and export data.
  5.  MANAGE CARETAKERS AND CHILDREN: You can create, manage, and delete caretakers in option 1 in the main menu and children in option 2 in the main menu.  Each caretaker is limited to 3 rates: standard, overtime, and share but you can create an unlimited number of caretakers.  Children have no operational effect on the calculations, but you may find them organizationally useful for your own purposes — you can choose to include children or not at your discretion.


###Full user manual

#Managing Caretakers (Menu Option 1)
In order to use CaretakerCalc you need to add at least one caretaker and set that caretaker's rates. Option 2 from the main menu gives you access to the caretaker menu. From here you can add, manage, and delete caretaker data. 

When adding a caretaker you will be prompted for first and last name, email, address, and phone. Make sure to enter the phone as only integers without parenthesis, dashes, or dots. IE 1-(212) 555-5555 should be entered as 2125555555. Note that if you are entering an international number, preface it with a + and you will bypass the phone number verification, allowing the entry of any style of international number. 

When editing a caretaker you are forced to enter dollar amounts for 3 different rate types: Standard, Overtime, Share.  These rate types are not editable in concept (i.e. there are always only 3 of them and are always named as such).  However they may be set to any non-negative dollar amount.  The purpose of each rate is 
  1. Standard - the default daily rate
  2. Overtime - a rate for after hours or other increased rate times
  3. Share - a rate for sharing hours with another family, and therefore expected to be a reduced rate
However, you may assign whatever dollar amounts you feel useful to these 3 buckets.  If you feel like you need more than 3 buckets, you may create a new caretaker entity.

#Adding Children (Menu Option 2)
Adding and editing child information.  NOTE: A child entity is purely a convenience for your internal organization.  It has no bearing on dollar calculations.  However it may help you better organize who is being cared for and at which times.

#Quick Edit: View and Edit This Week’s Hours (Menu Option 3)
This, and the subsequent ‘Edit Previous Weeks’ function represent the primary daily operations of this program.  Quick edit loads a week’s data based on the current day, Monday through Sunday.  By typing the name of the day you want to edit, you will access a menu of options to edit properties for the day:
  1. hours: the number of hours the caretaker worked for the day
  2. misc: and misc expense (and corresponding note) for the day. Often used for travel expense or other reimbursements.  Note: misc amounts can be negative if you need to make a downward adjustment.
  3. caretaker and rate: selecting the caretaker and choosing the rate.  Only one caretaker and one rate is allowed for each day.
  4. children: assigning children to the day.  This has no computational effect, it is purely for record keeping

#Edit Previous Weeks (Menu Option 4)
This functions the same as “edit this week’s hours” but with the ability to specify any week.  The initial prompt brings up a current month calendar.  Choosing any day in the calendar brings up the Monday-Sunday records that contains that date.  

Typing ‘C’ allows you to change months.  When typing C, first enter YYYY date, then MM month and then pick a day of the month.

#Run Reports (Menu Option 5)
Four different reports are provided:
  1. Totals by week: Enter a SUNDAY representing the end of the week you want to total and receive a dollar amount for all days in that week
  2. Totals by child: Enter a child ID from the menu and receive a dollar amount for all days with that child
  3. Totals by caretaker: Enter a caretaker ID from the menu and receive a dollar amount for all days with that caretaker
  4. Totals from custom date range: Select a start and end date and receive a dollar amount for all days in that range 

#Advanced Options (Menu Option 6)
This menu offers a range of (you guessed it) advanced options.
  1. Preferences: The preferences function pre-populates any day, or any series of days, with pre-decided caretakers, hours, children, and misc.  This is useful for users with regular schedules (i.e. caretaker works X Y Z days with N hours and C kids with R rate).
    1. Set preferences: This menu sets preferences for each Monday-Sunday.
    2. Toggle preferences: In order for preferences to be effective you must turn preferences on.  The default is preferences turned off.  If you wish to use preferences please make sure and ENABLE preferences via this menu.
  2. Bulk update: This  allows you to update data in bulk between two date ranges.  Three options are provided:
    1. Update all WEEKDAYS (Monday-Friday) in the date range
    2. Update ALL days (Monday-Sunday) in the date range
    3. Choose specific days of the week to update
    4. Export data: This option exports your data to a csv.  Each time you run each export it exports ALL data for the chosen option and overwrites the existing file. 3 data export options are provided:
      1. Export all day data: this exports all of the data attached to all dates, including hours, rate, caretaker, children, and misc expense/notes.  The export file is will be named day_data_export.csv
      2. Export all child data: This exports all information about the children (names, birthdays, IDs).  Export will be named child_data_export.csv
      3. Export all caretaker and rate data: This exports all information about each caretaker (name, contact info, IDs, and rates).  Export will be named caretaker_data_export.csv
      4. Quick populate for testing: This is a testing feature which auto populates child, caretaker, and rate data
		






'''
This file is to draft prototype code and functions before intergrating them into their
main files.

'''

sentence_1 = "i want to travel to london at 5pm"
sentence_2 = "i want to travel to london at 12:00"
sentence_3 = "i want to travel to london tomorrow"
sentence_4 = "i want to travel to london on the 5th of may"
sentence_5 = "i want to travel to london on the 10th of may at 5pm"
sentence_6 = "i want to travel to london on the 19th"
sentence_7 = "i want to travel to london on 22/5"
sentence_8 = "i want to travel to london on 22/5/23"
sentence_9 = "i want to travel to london on 20th of may and return on the 23rd"
sentence_10 = "i want to travel to london at 7am and return at 9pm"

import re
from datetime import datetime
import datetime as d



def infer_time(user_input):
    '''
        Function to infer time from a user input, returns the time as a datetime object
    '''
    def convert_matches(regex, matches):
        '''
            Function to convert matches into datetime objects and return them all in a list
        '''
        return_list = []
        for match in matches:
            time = match
            time_obj = datetime.strptime(time, regex)
            return_list.append(time_obj.time())
        return return_list

    time_and_date = []

    #am/pm
    regex_12_hour = re.compile(r'\d{1,2}(?::\d{2})?\s*(?:a|p)m', re.IGNORECASE)
    matches = re.findall(regex_12_hour, user_input)
    time_and_date.extend(convert_matches("%I%p", matches))

    #24 hour clock
    regex_24_hour = re.compile(r"\b\d\d:\d\d\b", re.IGNORECASE)
    matches = re.findall(regex_24_hour, user_input)

    if matches:
        time_and_date.extend(convert_matches("%H:%M",matches))

    if time_and_date:
        return time_and_date
    return None



def infer_date(user_input):
    '''
        Function to infer a date that may be in a user input, returns the date as a datetime object
    '''
    def create_date_object(year, month, day):
        '''
            Function to take year, month and day parameters to create a datetime object. If the date is in the
            past, the next instance of the date is returned (365 days after the previous instance)
        '''
        date_object = d.datetime(year, month, day).date()
        if datetime.today().month > date_object.month:
            date_object = date_object + d.timedelta(days=365)
        elif datetime.today().month == date_object.month and datetime.today().day > date_object.day:
            date_object = date_object + d.timedelta(days=365)

        return date_object

    # dates
    time_and_date = []
    matches = []

    #all regex patterns
    regex_date_and_month = re.compile(r"\b(\d+)(st|nd|rd|th) of (\w+)\b")
    regex_date = re.compile(r"\b(\d+)(st|nd|rd|th)")
    regex_numeric_day_month = re.compile(r"(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|[1][0-2])")
    regex_numeric_day_month_year = re.compile(r"(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|[1][0-2])/[0-9]+")

    #find regex with date and month in format [num][st/nd/rd/th] of [month]
    if (re.findall(regex_date_and_month, user_input)):
        matches = re.findall(regex_date_and_month, user_input)
        for match in matches:
            #set day and month in user input
            day = match[0]
            month = match[2]

            #create date object, store days and month in individual elements
            date_object = datetime.strptime(day + " " + month, "%d %B").date()
            date_object_month = date_object.month
            date_object_day = date_object.day

            #set year to current year
            date_object = date_object.replace(year=datetime.today().year)

            #if the date is in the past, set the year to when the date next occurs
            if datetime.today().month>date_object_month:
                date_object = date_object+d.timedelta(days=365)
            elif datetime.today().month==date_object_month and datetime.today().day>date_object_day:
                date_object = date_object + d.timedelta(days=365)

            time_and_date.extend([date_object])
    else:
        #find all instances of just [num][st/nd/rd/th]
        matches = re.findall(regex_date, user_input)
        for match in matches:
            day = int(match[0])
            month = datetime.today().month
            year = datetime.today().year
            date_object = create_date_object(year,month,day)
            time_and_date.extend([date_object])

    #finding all instances of numerical day and months ie [num]/[num]
    if(re.findall(regex_numeric_day_month,user_input)):
        matches = re.findall(regex_numeric_day_month, user_input)
        for match in matches:
            day = int(match[0])
            month = int(match[1])
            year = datetime.today().year

            date_object = create_date_object(year, month, day)
            time_and_date.extend([date_object])

    #finding all instances of numerical days with month and year eg [num]/[num]/[num]
    elif (re.findall(regex_numeric_day_month_year, user_input)):
        matches = re.findall(regex_numeric_day_month_year, user_input)
        for match in matches:
            day = int(match[0])
            month = int(match[1])
            year = int(match[3])

            date_object = create_date_object(year, month, day)
            time_and_date.extend([date_object])

    # generic time expressions, i.e. 'tomorrow'
    regex_tomorrow = re.compile(r"\btomorrow\b", re.IGNORECASE)
    matches = re.findall(regex_tomorrow, user_input)
    if matches:
        tomorrow_dt = datetime.today() + d.timedelta(days=1)
        time_and_date.extend([tomorrow_dt.date()])

    if time_and_date:
        return time_and_date
    return None



def infer_time_and_date(user_input):
    '''
    Function to call infer time and infer date and combine the return values
    '''
    time = infer_time(user_input)
    date = infer_date(user_input)

    if time and date:
        if len(time)==1 and len(date)==1:
            return {'date': date[0], 'time': time[0]}
        return {'date': date, 'time': time}
    elif date:
        if(len(date)==1):
            return {'date': date[0], 'time': None}
        return {'date': date, 'time': None}
    elif time:
        if (len(time) == 1):
            return {'date': None, 'time': time[0]}
        return {'date': None, 'time': time}

    return None

'''
########################################################################
############################ TEST SENTENCES ############################
########################################################################
'''
print(infer_time_and_date(sentence_1)) # sentence_1 = "i want to travel to london at 5pm"
print(infer_time_and_date(sentence_2)) # sentence_2 = "i want to travel to london at 12:00"
print(infer_time_and_date(sentence_3)) # sentence_3 = "i want to travel to london tomorrow"
print(infer_time_and_date(sentence_4)) # sentence_4 = "i want to travel to london on the 5th of may"
print(infer_time_and_date(sentence_5)) # sentence_5 = "i want to travel to london on the 10th of may at 5pm"
print(infer_time_and_date(sentence_6)) # sentence_6 = "i want to travel to london on the 15th"
print(infer_time_and_date(sentence_7)) # sentence_7 = "i want to travel to london on 22/5"
print(infer_time_and_date(sentence_8)) # sentence_8 = "i want to travel to london on 22/5/23"
#print(infer_time_and_date(sentence_9)) # sentence_9 = "i want to travel to london on 20th of may and return on the 23rd"
#print(infer_time_and_date(sentence_10)) # sentence_10 = "i want to travel to london at 7am and return at 9pm"


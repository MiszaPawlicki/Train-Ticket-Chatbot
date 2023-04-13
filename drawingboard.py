'''
This file is to draft prototype code and functions before intergrating them into their
main files.

'''

sentence_1 = "i want to travel to london at 5pm"
sentence_2 = "i want to travel to london at 17:00"
sentence_3 = "i want to travel to london tomorrow"
sentence_4 = "i want to travel to london on the 5th of may"
sentence_5 = "i want to travel to london on the 10th of may at 5pm"
sentence_6 = "i want to travel to london on the 15th"

from chronyk import Chronyk
from dateutil.parser import parse
import re

def infer_time(user_input):

    matches = []
    #am/pm
    regex_12_hour = re.compile(r'\d{1,2}(?::\d{2})?\s*(?:a|p)m', re.IGNORECASE)
    matches.extend(re.findall(regex_12_hour, user_input))
    #24 hour clock
    regex_24_hour = re.compile(r"\b(([01]?[0-9]|2[0-3]):([0-5][0-9]))\b", re.IGNORECASE)
    matches.extend(re.findall(regex_24_hour, user_input))
    #dates
    regex_date_and_month = re.compile(r"\b(\d+)(st|nd|rd|th) of (\w+)\b")
    regex_date = re.compile(r"\b(\d+)(st|nd|rd|th)")
    if(re.findall(regex_date_and_month, user_input)):
        matches.extend(re.findall(regex_date_and_month, user_input))
    else:
        matches.extend(re.findall(regex_date, user_input))
    #generic time expressions, i.e. 'tomorrow'
    regex_tomorrow = re.compile(r"\btomorrow\b",re.IGNORECASE)
    matches.extend(re.findall(regex_tomorrow, user_input))

    print(matches)

infer_time(sentence_1)
infer_time(sentence_2)
infer_time(sentence_3)
infer_time(sentence_4)
infer_time(sentence_5)
infer_time(sentence_6)


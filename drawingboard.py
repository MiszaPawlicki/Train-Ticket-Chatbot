'''
This file is to draft prototype code and functions before intergrating them into their
main files.

'''

sentence_1 = "i want to travel to london at 5pm"
sentence_2 = "i want to travel to london at 17:00"
sentence_3 = "i want to travel to london tomorrow"
sentence_4 = "i want to travel to london on the 5th of may"
sentence_5 = "i want to travel to london on the 10th of may at 5pm"

from chronyk import Chronyk
from dateutil.parser import parse
import re

def infer_time(user_input):
    #am/pm
    time_pattern_1 = re.compile(r'\d{1,2}(?::\d{2})?\s*(?:a|p)m', re.IGNORECASE)
    matches = time_pattern_1.findall(user_input)
    #24 hour clock
    time_pattern_2 = re.compile(r'\d{1,2}:\d{2}', re.IGNORECASE)
    matches.extend(time_pattern_2.findall(user_input))
    #dates

    #generic words such as 'tomorrow'


    print(matches)

infer_time(sentence_1)
infer_time(sentence_2)
infer_time(sentence_3)
infer_time(sentence_4)
infer_time(sentence_5)
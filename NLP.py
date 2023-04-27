
import random
import nltk
import spacy
import json
from fuzzywuzzy import fuzz
from nltk.util import ngrams
import re
from datetime import datetime
import datetime as dtime
import scraper

nlp = spacy.load('en_core_web_sm')
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()

#loading station data
f = open('stations.json')
stations = json.load(f)
station_names = [i['stationName'].lower() for i in stations]

#loading intent
f = open('KB.json')
intents = json.load(f)

def clean_input(user_input):
    '''
    Function to lower and remove punctuation from a string
    '''

    punctuation = [',', '.', '?', '!']
    for p in punctuation:
        user_input = user_input.replace(p, "")
    user_input = user_input.lower()

    return user_input

def find_station_in_sentence(sentence):
    '''
        This function takes a string and checks through ngrams of varying lengths. If the similarity score
        of an n-gram is above a threshold it can be assumed the ngram is a station name
    '''
    #use ngrams to find nearest station

    sentence = clean_input(sentence)

    threshold = 90

    destination_list = []
    origin_list = []
    unspecified_list = []
    # Loop through the list of train station names and compare each name to the input text
    for station in station_names:
        n = len(station.split())
        sentence_ngrams = ngrams(sentence.split(), n)

        for ngram in sentence_ngrams:
            similarity_score = fuzz.token_sort_ratio(' '.join(ngram).lower(), station.lower())
            if similarity_score >= threshold:
                station_index = nltk.word_tokenize(sentence).index(ngram[0])
                preceding_word = nltk.word_tokenize(sentence)[station_index-1]

                if(preceding_word=="to"):
                    destination_list.extend([s for s in stations if s['stationName'].lower()==station.lower()])
                elif(preceding_word=="from"):
                    origin_list.extend([s for s in stations if s['stationName'].lower()==station.lower()])
                else:
                    unspecified_list.extend([s for s in stations if s['stationName'].lower()==station.lower()])

                #print(f"Match found: {station} - {similarity_score}")


    return_dict = {}
    return_dict['destinations'] = destination_list
    return_dict['origins'] = origin_list
    return_dict['unspecified'] = unspecified_list
    return return_dict


def get_crs_and_station_name(journey_details, origin_or_destination):
    '''
        journey details is a dict, place is either a string 'origins' or 'destinations'
    '''
    place = journey_details[origin_or_destination][0]['stationName']
    # if station has mulltiple locations
    crs_code = journey_details[origin_or_destination][0]['crsCode']
    if crs_code.isdigit():
        crs_code = place
    return crs_code,place

def ask_if_return():
    '''
    This function checks whether the user wanted a return journey or not, if yes returns true, if no returns false
    '''
    #ask the question and get user input
    user_input = clean_input(input("Is this a return journey?\n"))

    yes_synonyms = ['yes', 'y']
    no_synonyms = ['no', 'n']

    while True:
        words = user_input.split()
        for y in yes_synonyms:
            if y in words:
                return True
        for n in no_synonyms:
            if n in words:
                return False
        user_input = clean_input(input("I'm sorry, I didn't understand. Is this a return journey?\n"))


def get_return_details():
    '''
    Function to get time and date of return from user
    '''
    user_input = clean_input(input("When would you like to return?\n"))
    time_and_date = infer_time_and_date(user_input)

    #get date
    while not time_and_date['date']:
        user_input = clean_input(input("What date did you want to travel?\n"))
        temp_time_and_date = infer_time_and_date(user_input)
        if temp_time_and_date['date']:
            time_and_date['date'] = temp_time_and_date['date']
    # get time
    while not time_and_date['time']:
        user_input = clean_input(input("What time did you want to travel?\n"))
        temp_time_and_date = infer_time_and_date(user_input)
        if temp_time_and_date['time']:
            time_and_date['time'] = temp_time_and_date['time']

    return time_and_date

def get_response(intent):
    '''
        Function that takes an intent and returns a random response for the intent as specified in the KB
    '''
    responses = intents[intent]['responses']
    response = random.choice(responses)

    return response

#### TIME AND DATE FUNCTIONS ###

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
        date_object = dtime.datetime(year, month, day).date()
        if datetime.today().month > date_object.month:
            date_object = date_object + dtime.timedelta(days=365)
        elif datetime.today().month == date_object.month and datetime.today().day > date_object.day:
            date_object = date_object + dtime.timedelta(days=365)

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
                date_object = date_object + dtime.timedelta(days=365)
            elif datetime.today().month==date_object_month and datetime.today().day>date_object_day:
                date_object = date_object + dtime.timedelta(days=365)

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
        tomorrow_dt = datetime.today() + dtime.timedelta(days=1)
        time_and_date.extend([tomorrow_dt.date()])

    if time_and_date:
        return time_and_date
    return None



def infer_time_and_date(user_input):
    '''
    Function to call infer time and infer date and combine the return values. The code is looped until a time/date
    is obtained from the user
    '''
    while True:
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

        #if both time and date are none, it can be assumed they were not included
        user_input = input("What was the time and date of your journey?\n")

## MAIN FUNCTION ##

def full_details_response(journey_details, intent):
    '''
        for use in the process request function. When all details have been obtained, this
        can be called to generate the final response
    '''
    #ask if return
    return_times = None
    return_time = None
    return_date = None
    if ask_if_return():
        #get the details of the return
        return_details = get_return_details()

        #format details if they are present
        if return_details['date']:
            return_time = return_details['date'].strftime("%d%m%y")
        if return_details['time']:
            return_date = return_details['time'].strftime("%H%M")



    #intent may have changed since new details have been gathered, so appropriate response is generated
    response = get_response(intent)

    #replace origin and destination in response
    if len(journey_details['origins']) == 1:
        origin_crs_code, origin = get_crs_and_station_name(journey_details,'origins')
        response = response.replace("#origin", origin)
    if len(journey_details['destinations']) == 1:
        destination_crs_code, destination = get_crs_and_station_name(journey_details,'destinations')
        response = response.replace("#destination", destination)

    #date and time info
    date = "today"
    time = datetime.now().strftime("%H%M")

    if 'departureDate' in journey_details:
        if journey_details['departureDate']:
            date = journey_details['departureDate'].strftime("%d%m%y")
    if 'departureTime' in journey_details:
        if journey_details['departureTime']:
            time = journey_details['departureTime'].strftime("%H%M")

    #get the train details using web scraping
    scraper_info = scraper.cheapest_ticket(origin_crs_code, destination_crs_code,date,time, return_date, return_time)
    #append new details to response
    response = response.replace("#leave_time", scraper_info['departure'])
    response = response.replace("#price", scraper_info['price'])
    response += "\n" + scraper_info['url']

    return response

def process_request(user_input,intent):
    '''
        Function to take a user_input and determine what details are in the sentence
    '''
    if(intent=='requests'):
        return generate_response(intent)
    elif(intent=='requests_no_time_single'):
        journey_details = find_station_in_sentence(user_input)
        response = full_details_response(journey_details, intent)
        return response

    elif(intent=='requests_no_time_no_origin_single'):

        #find destination station
        journey_details_destination = find_station_in_sentence(user_input)

        #ask for origin station
        user_input = input(get_response(intent) + '\n')

        #get journey time and/or date
        datetime_obj = infer_time_and_date(user_input)

        #append destination and origin
        journey_details_origin = find_station_in_sentence(user_input)

        #for now assume no time specified
        journey_details = {}
        journey_details['origins'] = journey_details_origin['unspecified']+journey_details_origin['origins']
        journey_details['destinations'] = journey_details_destination['destinations']
        journey_details['departureDate'] = datetime_obj['date']
        journey_details['departureTime'] = datetime_obj['time']
        #call full_details function and get ticket info response
        return full_details_response(journey_details,'requests_with_time_with_location_single')

    elif intent == 'requests_with_time_with_location_single':

        #get journey information
        journey_details = find_station_in_sentence(user_input)

        # get journey time and/or date
        datetime_obj = infer_time_and_date(user_input)

        #set time details
        journey_details['departureDate'] = datetime_obj['date']
        journey_details['departureTime'] = datetime_obj['time']

        # switching the intent, if this function has been called a certain criteria has been met and therefore the intent switch is needed
        return full_details_response(journey_details, intent)



    return "no response implemented for: "+intent
def generate_response(user_input):
    '''
        Function that takes user_input and prints what it determines to be a suitable response based on the
        input intent
    '''
    user_input = clean_input(user_input)

    #inferring intent using the NN
    intent = predict_intent(user_input) #check_intent(user_input)

    if(not intent):
        return "I'm sorry, I don't understand."
    else:
        if(intent=="goodbye" or intent=="greeting" or intent=="thanks" or intent=="requests"):
            response = str(get_response(intent))
            return response
        else:
            response = process_request(user_input, intent)
            return response



####NEURAL NETWORK####
#load model data
import pickle
from keras.models import load_model
import numpy as np
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('model.h5')
def predict_intent(user_input):

    sent_words = nltk.word_tokenize(user_input)
    sent_words = [lemmatizer.lemmatize(word) for word in sent_words]
    bag = [0]*len(words)
    for w in sent_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    bow = np.array(bag)
    res = model.predict(np.array([bow]))[0]
    threshold = 0.2
    results = [[i, r] for i, r in enumerate(res) if r>threshold]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    intent = None
    probability = 0.75
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
        #print(classes[r[0]])
        if r[1] > probability:
            probability = r[1]
            intent = classes[r[0]]
    #print(intent)
    #print(return_list)
    return intent
######################

while True:
    user_input = input("enter a command:\n")
    print(generate_response(user_input))

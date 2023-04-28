
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


#active questions

active_question = {'time': False, 'date': False, 'return-time': False, 'return-date': False, 'origin': False, 'return': False, 'active': False}

#journey details
journey = {'origin': None, 'destination': None, 'time': None, 'date': None, 'return-time': None, 'return-date': None, 'return': None}
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
    Function to call infer time and infer date and combine the return values.
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


def check_questions(user_input, intent):
    '''
    Function that checks if any questions are active, returns appriproate response. If no questions are active, returns
    None
    '''
    #origin station
    if(active_question['origin']):
        #check if info in userinput
        journey_details = find_station_in_sentence(user_input)

        if journey_details['origins']:
            active_question['origin'] = False
            journey['origin'] = journey_details['origins']
            print(journey)
        elif journey_details['unspecified']:
            active_question['origin'] = False
            journey['origin'] = journey_details['unspecified']

        #if not return the question
        else:
            return "When and where will you be departing from?"

    #time
    if (active_question['time'] or active_question['date']):
        # check if info in userinput
        time_details = infer_time_and_date(user_input)
        print(time_details)

        if(time_details):
            #check if time obtained
            if(time_details['time'] and not journey['time']):
                journey['time'] = time_details['time']
                active_question['time'] = False

            #check if date obtained
            if(time_details['date'] and not journey['date']):
                journey['date'] = time_details['date']
                active_question['date'] = False

            #return appropriate response
            if not journey['time'] and not journey['date']:
                return "What time and date are you traveling?"
            elif not journey['date']:
                return "What date are you traveling?"
            elif not journey['time']:
                return "What time are you traveling?"


        else:
            return "When will you be traveling?"

    # returns

    if active_question['return'] and not (active_question['time'] or active_question['date']):
        #ask if return
        yes_synonyms = ['yes', 'y']
        no_synonyms = ['no', 'n']

        words = user_input.split()
        for y in yes_synonyms:
            if y in words:
                active_question['return-time'] = True
                active_question['return-date'] = True
        for n in no_synonyms:
            if n in words:
                active_question['return'] = False

        #if unknown ask if return
        if active_question['return'] and not (active_question['return-time'] and active_question['return-date']):
            return "Is this a return journey?"

        #if return gather details
        if active_question['return'] and (active_question['return-time'] or active_question['return-date']):
            time_details = infer_time_and_date(user_input)

            #if time info in user input
            if (time_details):
                # check if time obtained
                if (time_details['time'] and not journey['return-time']):
                    journey['return-time'] = time_details['time']
                    active_question['return-time'] = False

                # check if date obtained
                if (time_details['date'] and not journey['return-date']):
                    journey['return-date'] = time_details['date']
                    active_question['return-date'] = False

                #if questions have been answered skip further questions
                if not journey['return-date'] or not journey['return-time']:
                    # return appropriate response
                    if not journey['time'] and not journey['return-date']:
                        return "What time and date are you returning?"
                    elif not journey['return-date']:
                        return "What date are you returning?"
                    elif not journey['return-time']:
                        return "What time are you returning?"
                else:
                    active_question['return'] = False

            else:
                return "When will you be returning?"




    #if only active is true, get url
    if active_question['active'] and all(value == False for key, value in active_question.items() if key != 'active'):
        print("trigger")
        journey_details = {'origins': journey['origin'],
                           'destinations': journey['destination'],
                           'departureDate': journey['date'],
                           'departureTime': journey['time'],
                           'returnDate': journey['return-date'],
                           'returnTime': journey['return-time']
                           }
        active_question['active'] = False
        
        return full_details_response(journey_details)

    print(journey)
    return None

## MAIN FUNCTION ##

def full_details_response(journey_details):
    '''
        for use in the process request function. When all details have been obtained, this
        can be called to generate the final response
    '''


    #intent may have changed since new details have been gathered, so appropriate response is generated
    response = "the cheapest available journey from #origin to #destination is at #leave_time and costs #price purchase can be made here: "

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


    return_date = None
    return_time = None

    if 'returnDate' in journey_details:
        if journey_details['returnDate']:
            return_date = journey_details['returnDate'].strftime("%d%m%y")
    if 'returnTime' in journey_details:
        if journey_details['returnTime']:
            return_time = journey_details['returnTime'].strftime("%H%M")
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
        response = full_details_response(journey_details)
        return response

    elif(intent=='requests_no_time_no_origin_single'):

        #find destination station

        journey_details_destination = find_station_in_sentence(user_input)
        journey['destination'] = journey_details_destination['destinations']

        #set active questions

        active_question['origin'] = True
        active_question['time'] = True
        active_question['date'] = True
        active_question['return'] = True
        active_question['active'] = True

        return get_response(intent)

    elif intent == 'requests_with_time_with_location_single':

        #get journey information
        journey_details = find_station_in_sentence(user_input)

        # get journey time and/or date
        datetime_obj = infer_time_and_date(user_input)

        #set time details
        journey_details['departureDate'] = datetime_obj['date']
        journey_details['departureTime'] = datetime_obj['time']

        # switching the intent, if this function has been called a certain criteria has been met and therefore the intent switch is needed
        return full_details_response(journey_details)



    return "no response implemented for: "+intent
def generate_response(user_input):
    '''
        Function that takes user_input and prints what it determines to be a suitable response based on the
        input intent
    '''
    user_input = clean_input(user_input)

    intent = None

    #check if any questions are being asked
    questions = check_questions(user_input, intent)
    # inferring intent using the NN
    intent = predict_intent(user_input)  # check_intent(user_input)
    if(questions):
        return questions

    #else check intent
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



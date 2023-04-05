
import random
import re
from datetime import datetime
import nltk
import spacy
import json
from fuzzywuzzy import fuzz
from nltk.util import ngrams

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

def check_intent(user_sentence):

    '''
        A function to take a user sentence and infer the intention of the user using info in KB.json
    '''

    #all_sents = [sent for intention_type in intents for sent in intents[intention_type]['patterns']]

    max_similarity = -1
    most_similar_sentence = ""
    intent = ""
    user_sentence = lemmatizer.lemmatize(user_sentence)
    doc1 = nlp(user_sentence)
    for intention_type in intents:
        for kb_sent in intents[intention_type]['patterns']:
            kb_sent = re.sub(r'\#\w+', '', kb_sent)
            kb_sent = lemmatizer.lemmatize(kb_sent)
            #clean_sent = re.sub(r'\#\w+', '', kb_sent)
            doc2 = nlp(kb_sent)
            similarity = doc1.similarity(doc2)
            if similarity>max_similarity:
                max_similarity = similarity
                most_similar_sentence = kb_sent
                intent = intention_type
    #print(most_similar_sentence)
    #print(max_similarity)
    #if not sure of intent
    if(max_similarity<0.65):
        return None

    return intent




def find_station_in_sentence(sentence):
    #use ngrams to find nearest station

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


def infer_journey_times(user_input):
    '''
        A function to take a user input and return the times specified
    '''

    return None



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

        #ask for origin station
        user_input = input(get_response(intent) + '\n')

        #append destination and origin
        journey_details_origin = find_station_in_sentence(user_input)

        #for now assume no time specified
        journey_details = {}
        journey_details['origins'] = journey_details_origin['unspecified']+journey_details_origin['origins']
        journey_details['destinations'] = journey_details_destination['destinations']
        #call full_details function and get ticket info response
        return full_details_response(journey_details)



    return "no response implemented for: "+intent

def full_details_response(journey_details):
    '''
        for use in the process request function. When all details have been obtained, this
        can be called to generate the final response
    '''
    response = "the cheapest next available journey from #origin to #destination is at #leave_time and costs #price purchase can be made here: "

    #replace origin and destination in response
    if len(journey_details['origins']) == 1:
        origin = journey_details['origins'][0]['stationName']
        origin_crs_code = journey_details['origins'][0]['crsCode']
        response = response.replace("#origin", origin)
    if len(journey_details['destinations']) == 1:
        destination = journey_details['destinations'][0]['stationName']
        destination_crs_code = journey_details['destinations'][0]['crsCode']
        response = response.replace("#destination", destination)

    #get the train details using web scraping
    scraper_info = scraper.scrape_ticket(origin_crs_code, destination_crs_code, datetime.now().strftime("%H%M"),
                                         "today")
    #append new details to response
    response = response.replace("#leave_time", scraper_info['departure'])
    response = response.replace("#price", scraper_info['price'])
    response += "\n" + scraper_info['url']

    return response
def get_response(intent):
    '''
        Function that takes an intent and returns a random response for the intent as specified in the KB
    '''
    responses = intents[intent]['responses']
    response = random.choice(responses)

    return response

def generate_response(user_input):
    '''
        Function that takes user_input and prints what it determines to be a suitable response based on the
        input intent
    '''

    intent = predict_intent(user_input)#check_intent(user_input)

    if(not intent):
        return "I'm sorry, I don't understand."
    else:
        if(intent=="goodbye"):
            # if the intent is to end the conversation, the loop is exited using break
            response = str(get_response(intent))
            return response
        elif(intent=="greeting"):
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
        if r[1]>probability:
            probability = r[1]
            intent = classes[r[0]]
    #print(intent)
    #print(return_list)
    return intent
######################

while True:
    user_input = input("enter a command:\n")
    print(generate_response(user_input))
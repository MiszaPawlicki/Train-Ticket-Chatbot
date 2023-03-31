import pickle
import random
import re

import nltk
import spacy
import json
import difflib
from fuzzywuzzy import fuzz
from nltk.util import ngrams
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
#

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
                    print("error in find_station")
                    return None

                #print(f"Match found: {station} - {similarity_score}")


    return_dict = {}
    return_dict['destinations'] = destination_list
    return_dict['origins'] = origin_list
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
        origin = ""
        destination = ""
        response = get_response(intent)
        #print(response)
        #print(journey_details)
        if len(journey_details['origins'])==1:
            origin = journey_details['origins'][0]['stationName']
            response = response.replace("#origin", origin)
        if len(journey_details['destinations'])==1:
            destination = journey_details['destinations'][0]['stationName']
            response = response.replace("#destination", destination)

        return response


    return None


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

    intent = check_intent(user_input)

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



#user_input = input("enter a command:\n")
print(generate_response("I need to go from brighton to norwich"))


import random
import nltk
import spacy
import json
import difflib
from fuzzywuzzy import fuzz
from nltk.util import ngrams
nlp = spacy.load('en_core_web_sm')

#loading station data
f = open('stations.json')
stations = json.load(f)
station_names = [i['stationName'].lower() for i in stations]

#loading intent
f = open('KB.json')
intents = json.load(f)
#
def lemmatize_and_clean(text):
    doc = nlp(text.lower())
    out = ""
    for token in doc:
        if not token.is_stop and not token.is_punct:
            out = out + token.lemma_ + " "
    return out.strip()


def get_closest_station_match(station):
    '''
        This function takes a string, 'station', and finds the closest match. If the match has a similarity
        score of 0.9 or above, only the closest station is returned. Otherwise, the three closest stations are returned
    '''
    closest_matches = difflib.get_close_matches(station,station_names)
    score = difflib.SequenceMatcher(None, station, closest_matches[0]).ratio()
    return_stations = []
    print(closest_matches)
    print(score)
    if score>0.9:
        for i in stations:
            if i['stationName'].lower() == closest_matches[0]:
                print(i)
                return_stations.append(i)
                break
        return return_stations
    else:
        for m in closest_matches:
            for i in stations:
                if i['stationName'].lower() == m:
                    print(i)
                    return_stations.append(i)
                    break
        return return_stations

def check_intent(user_sentence):

    '''
        A function to take a user sentence and infer the intention of the user using info in KB.json
    '''

    #all_sents = [sent for intention_type in intents for sent in intents[intention_type]['patterns']]

    max_similarity = -1
    most_similar_sentence = ""
    intent = ""
    doc1 = nlp(user_sentence)
    for intention_type in intents:
        for kb_sent in intents[intention_type]['patterns']:
            doc2 = nlp(kb_sent)
            similarity = doc1.similarity(doc2)
            if similarity>max_similarity:
                max_similarity = similarity
                most_similar_sentence = kb_sent
                intent = intention_type
    print(max_similarity)
    #if not sure of intent
    if(max_similarity<0.65):
        return None

    return intent

def find_station_in_sentence(sentence):
    #use ngrams to find nearest station

    threshold = 90
    matching_stations = []
    # Loop through the list of train station names and compare each name to the input text
    for station in station_names:
        n = len(station.split())
        sentence_ngrams = ngrams(sentence.split(), n)
        for ngram in sentence_ngrams:
            similarity_score = fuzz.token_sort_ratio(' '.join(ngram).lower(), station.lower())
            if similarity_score >= threshold:
                print(f"Match found: {station} - {similarity_score}")
                matching_stations.append(station)

    return [station for station in stations if station['stationName'].lower() in matching_stations]




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
            # else the most suitable response is printed
            return str(find_station_in_sentence(user_input))



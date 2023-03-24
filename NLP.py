import spacy
import json
import difflib
nlp = spacy.load('en_core_web_sm')

#loading place data
f = open('places.json')
places = json.load(f)

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

def check_intent(sentence):
    for intention_type in intents:
        for sent in intents[intention_type]['patterns']:
            print(sent)

check_intent("hello how are you")


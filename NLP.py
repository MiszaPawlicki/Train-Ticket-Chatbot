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
station_names = [i['stationName'] for i in stations]

#
def lemmatize_and_clean(text):
    doc = nlp(text.lower())
    out = ""
    for token in doc:
        if not token.is_stop and not token.is_punct:
            out = out + token.lemma_ + " "
    return out.strip()

#find closest match


def get_closest_station_matches(station):
    print(difflib.get_close_matches(station,station_names))

while True:
    s = input("enter a station name: ")
    get_closest_station_matches(s)


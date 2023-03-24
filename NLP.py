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

#
def lemmatize_and_clean(text):
    doc = nlp(text.lower())
    out = ""
    for token in doc:
        if not token.is_stop and not token.is_punct:
            out = out + token.lemma_ + " "
    return out.strip()

#find closest match
def get_closest_station_match(station):
    closest_matches = difflib.get_close_matches(station,station_names)
    score = difflib.SequenceMatcher(None, station, closest_matches[0]).ratio()
    print(closest_matches)
    print(score)
    if score>0.9:
        for i in stations:
            if i['stationName'].lower() == closest_matches[0]:
                print(i)
                break
    else:
        for m in closest_matches:
            for i in stations:
                if i['stationName'].lower() == m:
                    print(i)
                    break

while True:
    s = input("enter a station name: ")
    get_closest_station_match(s)


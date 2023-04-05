'''
This file will contain code to train a model based on data in the KB
'''
import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.optimizers import SGD
import re

lemmatizer = WordNetLemmatizer()
intents = json.loads(open('KB.json').read())
words = []
classes = []
docs = []
stop_letters = ['?','!','.',',']

'''
loop through each word of each pattern. lemmatize the word
and store in word_list. in docs list store the word and its
associated intent. store the intent in classes
'''
for intent in intents:
    for pattern in intents[intent]['patterns']:
        pattern = re.sub(r'\#\w+', '', pattern)
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list)
        docs.append((word_list,intent))
        if intent not in classes:
            classes.append(intent)

#lemmatize all words
words = [lemmatizer.lemmatize(word) for word in words if word not in stop_letters]
#remove all duplicates
words = sorted(set(words))
#remove all words starting with '
words = [word for word in words if word[0]!="'"]

#remove all class duplicates
classes = sorted(set(classes))
print(words)
#save words and classes list in .pkl file
pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

training = []
output_empty = [0] * len(classes)

for doc in docs:
    bag = []
    word_patterns = doc[0]
    word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]
    for word in words:
        bag.append(1) if word in word_patterns else bag.append(0)

    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1
    training.append([bag, output_row])

random.shuffle(training)
training = np.array(training)
train_x = list(training[:, 0])
train_y = list(training[:, 1])

model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0],),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]),activation='softmax'))

sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
hist = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)
model.save('model.h5', hist)
print("model saved")


#####
#code to predict
###
#load model data
from keras.models import load_model
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
        print(classes[r[0]])
        if r[1]>probability:
            probability = r[1]
            intent = classes[r[0]]
    print(intent)
    print(return_list)
    return intent

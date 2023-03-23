import spacy

nlp = spacy.load('en_core_web_sm')

user_input = input("Enter a command: \n")

def lemmatize_and_clean(text):
    doc = nlp(text.lower())
    out = ""
    for token in doc:
        if not token.is_stop and not token.is_punct:
            out = out + token.lemma_ + " "
    return out.strip()

print(lemmatize_and_clean(user_input))
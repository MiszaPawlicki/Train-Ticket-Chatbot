from flask import Flask, render_template, request
import NLP
import pyttsx3

app = Flask(__name__)
app.static_folder = 'static'

def speak(text):
    text_speech = pyttsx3.init()
    text_speech.say(text)
    text_speech.runAndWait()


@app.route("/")
def home():
    #Speaks before loading and delays the system, not sure if we should just skip the intro message or not.
    #speak("Hi, I am your personal ticket assistant! How can I help you today?")
    #testing
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    response = NLP.generate_response(userText)
    speak(response)
    return response

if __name__ == "__main__":
    app.run()
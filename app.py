from flask import Flask, render_template, request
import NLP
import pyttsx3
import threading

app = Flask(__name__)
app.static_folder = 'static'

def speak(text):
    text_speech = pyttsx3.init()
    text_speech.say(text)
    text_speech.runAndWait()


@app.route("/")
def home():
    speach_thread = threading.Thread(target=speak, args=("Hi, I am your personal ticket assistant! How can I help you today?",))
    speach_thread.start()
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    response = NLP.generate_response(userText)
    if ("<" in response):
        stop = response.find("<")
        final_msg = response[0:stop]
        talk_after = threading.Thread(target=speak, args=(final_msg,))
        talk_after.start()
    else:
        talk_after = threading.Thread(target=speak, args=(response,))
        talk_after.start()
    return response

if __name__ == "__main__":
    app.run()
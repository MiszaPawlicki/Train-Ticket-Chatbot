from flask import Flask, render_template, request
import NLP
import pyttsx3
import threading

# Start by initialising flask and linkning the static folder
app = Flask(__name__)
app.static_folder = 'static'

# Function for operating the text-to-speech functionality
def speak(text):
    text_speech = pyttsx3.init()
    text_speech.say(text)
    text_speech.runAndWait()


# Initialise the index page use threading so that messages can appear and be read at the same time
@app.route("/")
def home():
    speach_thread = threading.Thread(target=speak, args=("Hi, I am your personal ticket assistant! How can I help you today?",))
    speach_thread.start()
    return render_template("index.html")


# Retrieve responses from the bot and check for hyperlink, if found do not read that part
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
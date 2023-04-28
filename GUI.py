import tkinter as tk
import random

import NLP

# Create the main window
root = tk.Tk()
root.title("Chatbot GUI")

# Create the chat history window
history_window = tk.Text(root, height=20, width=50)
history_window.pack()

# Create the chat input field
input_field = tk.Entry(root, width=50)
input_field.pack()

# Function to handle sending a message
# Function to handle sending a message
def send_message():
    message = input_field.get()
    history_window.insert(tk.END, "You: " + message + "\n")
    input_field.delete(0, tk.END)
    response = NLP.generate_response(message)
    history_window.insert(tk.END, "Bot: " + response + "\n")


def func(event):
    send_message()

def onclick(event):
    send_message()

root.bind('<Return>', onclick)

button = tk.Button(root, text="Send")
button.bind('<Button-1>', onclick)
button.pack()

# Start the main loop
root.mainloop()

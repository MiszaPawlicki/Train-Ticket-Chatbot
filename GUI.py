import tkinter as tk

import NLP



def send_message():
    '''
        This function takes a user input and generates a response using the generate respose function
        in NLP.py, generate_response returns a string
    '''
    message = user_input.get()
    response = NLP.generate_response(message)
    chat_log.insert(tk.END, 'You: ' + message + '\n')
    chat_log.insert(tk.END, 'Chatbot: ' + response + '\n')
    user_input.delete(0, tk.END)


# Code to set up the basic window
root = tk.Tk()
root.title('Train Chatbot')

# Size params
chat_log = tk.Text(root, height=40, width=100)
chat_log.pack()

# Text input params
user_input = tk.Entry(root, width=50)
user_input.pack()

# Send button params
send_button = tk.Button(root, text='Send', command=send_message)
send_button.pack()

# Inserting initial hello message
chat_log.insert(tk.END, 'Chatbot: Hello, how may I help?' + '\n')

root.mainloop()

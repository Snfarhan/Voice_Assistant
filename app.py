from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
import pyttsx3
import ollama

app = Flask(__name__)
CORS(app)

# Initialize speech recognition object
r = sr.Recognizer()

def record_text():
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source)
            text = r.recognize_google(audio)
            return text
    except sr.RequestError as e:
        return f'Could not request results: {e}'
    except sr.UnknownValueError:
        return 'Unknown error occurred.'

def text2speech(message):
    engine = pyttsx3.init()
    engine.setProperty('rate', 175)
    engine.say(message)
    engine.runAndWait()

def call_llm(message):
    if message.lower() == 'stop':
        return 'stop'
    
    system_prompt = (
        "You are a helpful assistant that answers questions in a very concise way."
    )

    response = ollama.chat(model='mistral', messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': message},
    ])

    return response['message']['content']

@app.route('/text', methods=['POST'])
def handle_text():
    data = request.json
    message = data.get('message')
    response = call_llm(message)
    return jsonify({'response': response})

@app.route('/voice', methods=['GET'])
def handle_voice():
    message = record_text()
    if "error" in message.lower():
        return jsonify({'user_message': message, 'response': message})
    response = call_llm(message)
    return jsonify({'user_message': message, 'response': response})

@app.route('/tts', methods=['POST'])
def handle_tts():
    data = request.json
    message = data.get('message')
    text2speech(message)
    return jsonify({'status': 'done'})

if __name__ == '__main__':
    app.run(debug=True)

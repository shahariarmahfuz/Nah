import os
from flask import Flask, request, jsonify
import google.generativeai as genai
import threading
import time
import requests
import logging

app = Flask(__name__)

# Get API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

chat_sessions = {}  # Dictionary to store chat sessions per user

# Set up logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/ask', methods=['GET'])
def ask():
    query = request.args.get('q')
    user_id = request.args.get('id')

    if not query or not user_id:
        logging.error("Query or User ID not provided")
        return jsonify({"error": "Please provide both query and id parameters."}), 400

    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])

    try:
        chat_session = chat_sessions[user_id]
        response = chat_session.send_message(query)
        return jsonify({"response": response.text})
    except genai.exceptions.ApiError as e:
        logging.error(f"API error: {e}")
        return jsonify({"error": "API error occurred"}), 500
    except genai.exceptions.RateLimitExceeded as e:
        logging.error(f"Rate limit exceeded: {e}")
        return jsonify({"error": "Rate limit exceeded"}), 429
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "alive"})

def keep_alive():
    url = "https://nah-x3n3.onrender.com/ping"  # আপনার রেন্ডার URL এখানে বসান
    while True:
        time.sleep(300)  # Ping every 5 minutes
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("Ping successful")
            else:
                print("Ping failed with status code", response.status_code)
        except Exception as e:
            print("Ping failed with exception", e)

if __name__ == '__main__':
    # Start keep-alive thread
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)

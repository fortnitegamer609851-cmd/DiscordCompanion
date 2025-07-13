from flask import Flask
import threading
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return "Pennsylvania State Roleplay Bot is running!"

@app.route('/health')
def health():
    return {"status": "healthy", "message": "Bot is operational"}

@app.route('/status')
def status():
    return {
        "bot_name": "Pennsylvania State Roleplay Bot",
        "version": "2.0",
        "status": "online"
    }

def run():
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        logger.error(f'Error running Flask app: {e}')

def keep_alive():
    try:
        server = threading.Thread(target=run)
        server.daemon = True
        server.start()
        logger.info('Keep alive server started on port 5000')
    except Exception as e:
        logger.error(f'Error starting keep alive server: {e}')

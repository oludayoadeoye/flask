import eventlet

eventlet.monkey_patch()

# Updated `server.py`
from flask import Flask, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pickle  # For loading the ML model
import numpy as np  # For data manipulation
import time


# Initialize Flask and SocketIO
app = Flask(__name__, static_folder='static', template_folder='static')
socketio = SocketIO(app, 
                    cors_allowed_origins="*", 
                    async_mode='eventlet',
                    logger=True,  # Enable logging
                   engineio_logger=True
                    
                    )
CORS(app, resources={r"/*": {"origins": "*"}})

# Serve the index.html file
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# Serve static files (e.g., app.js, styles.css)
@app.route('/<path:path>')
def serve_static_file(path):
    return send_from_directory('static', path)

# Load the LightGBM model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# Configure Selenium headless Chrome
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# service = Service(ChromeDriverManager().install())

# Configure Selenium headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")

# Use a specific ChromeDriver version instead of automatic manager
# service = Service('chromedriver')  # Make sure chromedriver is in your PATH
# Or specify the full path:
service = Service('/usr/local/bin/chromedriver')

# Store the latest numbers
latest_numbers = []

# Function to fetch live roulette numbers
def fetch_live_numbers():
    url = 'https://gamblingcounting.com/immersive-roulette'
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'roulette-number'))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        number_elements = soup.find_all('div', class_='roulette-number')

        numbers = []
        for element in number_elements:
            raw_text = element.text.strip()
            if raw_text.isdigit():
                numbers.append(int(raw_text))

        driver.quit()
        return numbers[30:42]
    except Exception as e:
        print(f"Error fetching live numbers: {e}")
        return []

# Function to make predictions
def make_prediction(last_12_numbers):
    if len(last_12_numbers) < 2:
        return []

    try:
        # Prepare input features for prediction
        input_data = np.array([last_12_numbers])  # Convert to a 2D array

        # Make predictions
        probabilities = model.predict_proba(input_data)
        top_3_indices = np.argsort(probabilities[0])[::-1][:3]  # Top 3 predictions
        top_3_numbers = [int(i) for i in top_3_indices]  # Ensure Python int type

        return top_3_numbers
    except Exception as e:
        print(f"Error making predictions: {e}")
        return []

# Background task to fetch numbers and emit updates
def update_numbers():
    global latest_numbers
    while True:
        new_numbers = fetch_live_numbers()
        if new_numbers != latest_numbers:
            latest_numbers = [int(num) for num in new_numbers]  # Ensure Python int type
            predictions = make_prediction(latest_numbers)
            socketio.emit('rouletteUpdate', {
                'numbers': latest_numbers,
                'predictions': predictions
            })
            print(f"Emitted data: {{'numbers': {latest_numbers}, 'predictions': {predictions}}}")
        socketio.sleep(2)

# Handle client connection
@socketio.on('connect')
def handle_connect(auth=None):  # Accept the 'auth' argument
    print("A client connected.")
    predictions = make_prediction(latest_numbers)

    socketio.emit('rouletteUpdate', {
        'numbers': [int(num) for num in latest_numbers],  # Convert numbers to Python ints
        'predictions': predictions
    })

# Handle client disconnection
@socketio.on('disconnect')
def handle_disconnect():
    print("A client disconnected.")

# Main entry point
if __name__ == '__main__':
    socketio.start_background_task(target=update_numbers)
    socketio.run(app, host='0.0.0.0', port=3000)

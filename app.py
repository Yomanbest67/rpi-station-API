from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from tinydb import TinyDB, Query
import datetime
import dht22
import ltr390

app = Flask(__name__)
db = TinyDB('weather_data.json')

with app.app_context():
    dht22.init_sensor()

def scheduled_task():
    def getData():
        weatherData = dht22.getAll()
        lux = ltr390.getLux()
        uvi = ltr390.getUvi()
        timestamp = datetime.datetime.now().isoformat()
        return timestamp, weatherData, lux, uvi
    
    attempts = 0
    recordSuccess = False
    
    while not recordSuccess and attempts < 10:
        try:
            timestamp, weatherData, lux, uvi = getData()

            db.insert({ 'timestamp': timestamp, 'weatherData': weatherData, 'lux': lux, 'uvi': uvi })

            recordSuccess = True
            print(f"Data recorded at {timestamp}")
        except Exception as e:
            print(f"Error during scheduled task: {e}")
            attempts += 1


scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduled_task, trigger="interval", hours=1)
scheduler.start()

@app.route('/')
def index():
    return jsonify({'message': 'Hello, World!'}), 200

@app.route('/data')
def data():
    try:
        weatherData = dht22.getAll()
        lux = ltr390.getLux()
        uvi = ltr390.getUvi()

        return jsonify({
            'weatherData': weatherData,
            'lux': lux, 
            'uvi': uvi
        }), 200

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500
    
@app.route('/data/history')
def history():
    try:
        all_data = db.all()
        return jsonify(all_data), 200

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
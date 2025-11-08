from flask import Flask, request, jsonify
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
    weatherData = dht22.getAll()
    lux = ltr390.getLux()
    uvi = ltr390.getUvi()
    timestamp = datetime.datetime.now().isoformat()

    if weatherData is not None:
        db.insert({'timestamp': timestamp, 'weatherData': weatherData, 'lux': lux, 'uvi': uvi})
        print(f"Data logged at {timestamp}")
    else:
        weatherData = dht22.getAll()
 

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
    queryParams = request.args
    query = Query()

    filters = {}
    sortOrder = queryParams.get('sort', 'asc').lower()

    for key, value in queryParams.items():
        if key == 'date':
            try:
                parsedDate = datetime.datetime.fromisoformat(value)
                filters['timestamp'] = lambda t: t.startswith(parsedDate.date().isoformat())
            except ValueError:
                try:
                    parsedDate = datetime.datetime.strptime(value, '%d-%m-%Y')
                    parsedDate = parsedDate.strftime('%Y-%m-%d')
                    filters['timestamp'] = lambda t: t.startswith(parsedDate)
                except ValueError:
                    return jsonify({'error': 'Invalid date format. Use ISO 8601 or DD-MM-YYYY.'}), 400
        else:
            filters[key] = value

    if sortOrder == 'desc':
        db = db.search(query(**filters).order_by('-timestamp'))
    else:
        db = db.search(query(**filters).order_by('timestamp'))

    return jsonify(db), 200

if __name__ == '__main__':
    app.json.compact = False
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
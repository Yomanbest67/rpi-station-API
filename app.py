from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from functools import reduce
import operator
import logging
from logging.handlers import TimedRotatingFileHandler
import time
from tinydb import TinyDB, Query
import datetime
import dht22
import ltr390

app = Flask(__name__)
db = TinyDB('weather_data.json')

################# Set up app logging #################
logger = logging.getLogger('RpiStationLogger')
logger.setLevel(logging.INFO)

handler = TimedRotatingFileHandler('rpi_station.log', when='D', interval=1, backupCount=7)
handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
######################################################

with app.app_context():
    dht22.init_sensor()

def scheduled_task(retries = 15, delay = 2):
    
    for attempt in range(retries):
        try:
            weatherData = dht22.getAll()
            lux = ltr390.getLux()
            uvi = ltr390.getUvi()

            if weatherData is not None:
                record = {
                    'lux': lux,
                    'uvi': uvi,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'weatherData': weatherData
                }

                currentHour = datetime.datetime.now().strftime('%Y-%m-%dT%H')
                existingEntry = db.search(Query().timestamp.matches(currentHour))

                if existingEntry:
                    db.update(record, Query().timestamp.matches(currentHour))
                    print(f"Data updated at {record['timestamp']}")
                else:
                    db.insert(record)
                    print(f"Data recorded at {record['timestamp']}")

                return
        except Exception as e:
            print(f"[{time.ctime()}] Attempt {attempt + 1} failed: {e}")
            logger.error(f"Scheduled task error on attempt {attempt + 1}: {e}")
            time.sleep(delay)
 

scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduled_task, trigger="cron", minute='0, 25, 50', max_instances=1)
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
    global db
    queryParams = request.args
    query = Query()

    if not queryParams:
        queryResult = db.all()
        sortedQueryResult = sorted(queryResult, key=lambda x: datetime.datetime.fromisoformat(x['timestamp']), reverse=True)

        return jsonify(sortedQueryResult), 200

    filters = {}
    sortOrder = queryParams.get('sort').lower()

    for key, value in queryParams.items():
        if key == 'date':
            try:
                parsedDate = datetime.datetime.fromisoformat(value)
                filters['timestamp'] = parsedDate.strftime('%Y-%m-%d')
            except ValueError:
                try:
                    parsedDate = datetime.datetime.strptime(value, '%d-%m-%Y')
                    parsedDate = parsedDate.strftime('%Y-%m-%d')
                    filters['timestamp'] = parsedDate
                except ValueError:
                    return jsonify({'error': 'Invalid date format. Use ISO 8601 or DD-MM-YYYY.'}), 400
        elif key == 'sort':
            continue
        else:
            filters[key] = value

    conditions = [
        query[key].matches(value) for key, value in filters.items()
    ]

    if conditions:
        combinedConditions = reduce(operator.and_, conditions)

    results = db.search(combinedConditions) if conditions else db.all()

    if sortOrder == 'desc':
        queryResult = sorted(results, key=lambda x: datetime.datetime.fromisoformat(x['timestamp']), reverse=True)
    else:
        queryResult = sorted(results, key=lambda x: datetime.datetime.fromisoformat(x['timestamp']))

    return jsonify(queryResult), 200

@app.route('/data/logs')
def logs():
    baseFile = 'rpi_station.log'
    logDate = request.args.get('date')

    if logDate:
        try:
            parsedDate = datetime.datetime.fromisoformat(logDate)
            logFile = f"{baseFile}.{parsedDate.strftime('%Y-%m-%d')}"
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use ISO 8601.'}), 400
    else:
        logFile = baseFile

    try:
        with open(logFile, 'r') as f:
            logData = f.read()

        return jsonify({
            'file': logFile,
            'log': logData.splitlines()
        }), 200

    except FileNotFoundError:
        return jsonify({'error': 'Log file not found.'}), 404

if __name__ == '__main__':
    app.json.compact = False
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
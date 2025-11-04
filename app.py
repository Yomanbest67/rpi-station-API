from flask import Flask, jsonify
import dht22
import ltr390

app = Flask(__name__)

with app.app_context():
    dht22.init_sensor()

@app.route('/')
def index():
    return jsonify({'message': 'Hello, World!'}), 200

@app.route('/data')
def data():
    try:
        temperature = dht22.getTemperature()
        humidity = dht22.getHumidity()
        lux = ltr390.getLux()
        uvi = ltr390.getUvi()

        return jsonify({
            'temperature': temperature,
            'humidity': humidity, 
            'lux': lux, 
            'uvi': uvi
        }), 200

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
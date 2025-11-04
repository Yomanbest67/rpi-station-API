from flask import Flask, jsonify
import dht22
import ltr390

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({'message': 'Hello, World!'}), 200

@app.route('/data')
def data():
    return jsonify({'temperature': dht22.getTemperature(), 'humidity': dht22.getHumidity(), 'lux': ltr390.getLux(), 'uvi': ltr390.getUvi()}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/api/log', methods=['PUT'])
def put():
    if request.method == 'PUT':
        print(request.form['what'])
        print(request.form['tags'])
        print(request.form['datetime'])
        return 'PUT came'

@app.route('/api/event/create', methods=['POST'])
def post():
    if request.method == 'POST':
        print(request.data)
        return 'POST came'


from flask import Flask, request

app = Flask(__name__)

@app.route('/school/<id>')
def query_example(id):
    return 'id: '+id

app.run(debug=True, port=5000)
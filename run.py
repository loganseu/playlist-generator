from flask import Flask, request

app = Flask(__name__)

@app.route('/')

def index():
    return "test"

def post_req():
    requests.post(access_token_url)

if (__name__ == "__main__"):
    app.run()
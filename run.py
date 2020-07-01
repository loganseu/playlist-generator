from flask import Flask, request

app = Flask(__name__)

@app.route('/')

def index():
    return "<h1>Copy and paste this Spotify code into the terminal: </h1>" + request.args.get("code")

def post_req():
    pass

if (__name__ == "__main__"):
    app.run()
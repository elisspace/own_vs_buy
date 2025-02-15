from flask import Flask, render_template, request, jsonify
from calculate import simulate_own_vs_rent

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    params = request.get_json()
    results = simulate_own_vs_rent(params)
    return jsonify(results)

if __name__ == "__main__":
    app.run()


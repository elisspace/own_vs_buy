from flask import Flask, render_template, request, jsonify
from calculate import simulate_own_vs_rent

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate_endpoint():
    try:
        params = request.get_json(force=True)
        results = simulate_own_vs_rent(params)
        return jsonify(results)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Unexpected server error: " + str(e)}), 500


if __name__ == "__main__":
    app.run()


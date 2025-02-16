from flask import Flask, render_template, request, jsonify
from calculate import simulate_own_vs_rent
from monte_carlo import run_monte_carlo

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


# app.py

from flask import Flask, request, jsonify, render_template
from montecarlo import run_monte_carlo

app = Flask(__name__)

@app.route('/mc', methods=['GET', 'POST'])
def mc():
    if request.method == 'GET':
        # Simply serve the mc.html form/page
        return render_template('mc.html', results=None)

    else:  # POST: user submitted a JSON payload with all variables + distributions
        data = request.get_json(force=True)

        # Build dist_params dictionary from the full listing of distributions
        # We'll just pass them along exactly as provided, with a default empty dict if not found
        dist_params = {
            'annual_income_dist': data.get('annual_income_dist', {}),
            'home_price_dist': data.get('home_price_dist', {}),
            'down_payment_dist': data.get('down_payment_dist', {}),
            'mortgage_rate_dist': data.get('mortgage_rate_dist', {}),
            'mortgage_term_dist': data.get('mortgage_term_dist', {}),
            'property_tax_rate_dist': data.get('property_tax_rate_dist', {}),
            'homeowner_insurance_dist': data.get('homeowner_insurance_dist', {}),
            'maintenance_rate_dist': data.get('maintenance_rate_dist', {}),
            'rent_dist': data.get('rent_dist', {}),
            'rent_escalation_rate_dist': data.get('rent_escalation_rate_dist', {}),
            'home_appreciation_dist': data.get('home_appreciation_dist', {}),
            'investment_return_dist': data.get('investment_return_dist', {}),
            'marginal_tax_rate_dist': data.get('marginal_tax_rate_dist', {}),
            'inflation_rate_dist': data.get('inflation_rate_dist', {}),
            'start_age_dist': data.get('start_age_dist', {}),
            'end_age_dist': data.get('end_age_dist', {}),
            'monthly_travel_dist': data.get('monthly_travel_dist', {}),
            'monthly_groceries_dist': data.get('monthly_groceries_dist', {}),
            'monthly_bills_dist': data.get('monthly_bills_dist', {}),
            'monthly_healthcare_dist': data.get('monthly_healthcare_dist', {})
        }

        # Optionally, let the user specify the number of simulations or default to 1000
        # e.g.: num_sims = data.get('num_sims', 1000)
        num_sims = 1000

        # Run the Monte Carlo simulation
        results = run_monte_carlo(dist_params, num_sims=num_sims)

        # Return as JSON. The front-end can use these arrays/stats for Chart.js, etc.
        return jsonify(results)


if __name__ == "__main__":
    app.run()


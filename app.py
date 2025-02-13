from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = 'SUPER-SECRET-KEY'  # Replace with something more secure in production

# Demo user dictionary (store hashed credentials in a real system)
USERS = {
    "testuser": "testpass"
}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if USERS.get(username) == password:
            session['logged_in'] = True
            return redirect(url_for('calculator'))
        else:
            return render_template('login.html', error="Invalid username/password.")
    else:
        if session.get('logged_in'):
            return redirect(url_for('calculator'))
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/calculator')
def calculator():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('calculator.html')

@app.route('/compute', methods=['POST'])
def compute():
    """
    AJAX endpoint that receives user inputs (via JSON),
    then calculates renting vs. buying outcomes.
    This version dynamically updates taxes, insurance,
    and maintenance based on the house's changing value.
    """
    data = request.json

    # User inputs
    current_age = float(data.get('current_age', 30))
    age_at_death = float(data.get('age_at_death', 90))
    monthly_salary = float(data.get('monthly_salary', 5000))
    monthly_rent = float(data.get('monthly_rent', 1500))
    home_cost = float(data.get('home_cost', 400000))
    down_payment = float(data.get('down_payment', 80000))
    monthly_expenses = float(data.get('monthly_expenses', 1500))
    investment_return = float(data.get('investment_return', 6)) / 100.0

    # Time horizon
    years = age_at_death - current_age
    months = int(years * 12)

    # Simple monthly investment rate
    monthly_investment_rate = investment_return / 12

    # ------------------
    # Renter Scenario
    # ------------------
    # Start with a lump sum (down payment) in investments
    renter_investment_balance = down_payment
    current_monthly_salary = monthly_salary

    # We won't change rent monthly here in detail,
    # but you could add rent growth if desired.
    # For now, keep it fixed for simplicity.

    for _ in range(months):
        leftover_rent = current_monthly_salary - (monthly_rent + monthly_expenses)
        if leftover_rent > 0:
            renter_investment_balance += leftover_rent
        # Grow investment
        renter_investment_balance *= (1 + monthly_investment_rate)

        # We’ll skip monthly salary growth to keep it straightforward
        # but you could easily incorporate that as well.

    renter_net_worth = renter_investment_balance

    # ------------------
    # Buyer Scenario
    # ------------------
    # Mortgage logic: Very simplified example
    principal = home_cost - down_payment
    mortgage_rate_annual = 0.04        # 4% annual, for demonstration
    monthly_mortgage_rate = mortgage_rate_annual / 12
    mortgage_term_years = 30
    num_payments = mortgage_term_years * 12

    if principal > 0:
        # Standard formula
        monthly_mortgage_payment = (
            principal *
            (monthly_mortgage_rate * (1 + monthly_mortgage_rate) ** num_payments) /
            ((1 + monthly_mortgage_rate) ** num_payments - 1)
        )
    else:
        monthly_mortgage_payment = 0

    # Let's assume a 1% property tax and 0.3% insurance, 0.2% maintenance, all annual,
    # but it will scale with changing house value
    property_tax_annual_rate = 0.01
    insurance_annual_rate = 0.003
    maintenance_annual_rate = 0.002

    # House appreciation
    annual_appreciation_rate = 0.02  # 2% annual
    monthly_appreciation_rate = annual_appreciation_rate / 12

    house_value = home_cost
    buyer_investment_balance = 0
    total_upfront = down_payment  # ignoring closing costs for simplicity here

    for month_index in range(months):
        # Each month, update the house value first
        house_value *= (1 + monthly_appreciation_rate)

        # Recalc these costs based on the updated house value
        monthly_taxes = (house_value * property_tax_annual_rate) / 12
        monthly_insurance = (house_value * insurance_annual_rate) / 12
        monthly_maintenance = (house_value * maintenance_annual_rate) / 12

        # If mortgage is still active
        if month_index < num_payments:
            monthly_costs = monthly_mortgage_payment + monthly_taxes + monthly_insurance + monthly_maintenance
        else:
            monthly_costs = monthly_taxes + monthly_insurance + monthly_maintenance

        leftover_buy = monthly_salary - (monthly_expenses + monthly_costs)
        if leftover_buy > 0:
            buyer_investment_balance += leftover_buy

        # Grow leftover investment
        buyer_investment_balance *= (1 + monthly_investment_rate)

    homeowner_net_worth = buyer_investment_balance + house_value

    # Compare
    difference = homeowner_net_worth - renter_net_worth

    results = {
        "renter_investment_balance": f"${renter_investment_balance:,.2f}",
        "homeowner_investment_balance": f"${buyer_investment_balance:,.2f}",
        "final_house_value": f"${house_value:,.2f}",
        "homeowner_net_worth": f"${homeowner_net_worth:,.2f}",
        "renter_net_worth": f"${renter_net_worth:,.2f}",
        "difference": difference
    }

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


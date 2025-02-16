"""
montecarlo.py

This file provides a demonstration of how to use all the front-end variables
(annual_income, home_price, etc.) within placeholder logic for a Monte Carlo
buy-vs-rent simulation. It includes:

1) A function to sample from user-selected distributions (sample_distribution).
2) A function to run a single simulation iteration (run_single_simulation),
   which:
   a) samples each variable's value
   b) calculates final net worth for both "own" and "rent" scenarios
3) Two core placeholder scenario functions: calculate_own_scenario, calculate_rent_scenario
   that run a monthly loop from start_age to end_age to accumulate net worth.
4) A function (run_monte_carlo) that repeats these steps num_sims times and
   returns aggregated results plus summary statistics.

WARNING: This logic is for illustration only. Real-world financial modeling
         will likely be more detailed and accurate.
"""

import random
import math
import statistics


def sample_distribution(dist_type, mean, stdev, minimum, maximum, mode):
    """
    Returns a single random value from one of the supported distributions:
      'normal', 'lognormal', or 'triangular'.
    
    For each:
      - normal: random.gauss(mean, stdev)
      - lognormal: random.lognormvariate(log_mean, log_stdev) 
                   (Assumes mean, stdev are in log-space if you're truly modeling lognormal.)
      - triangular: random.triangular(minimum, maximum, mode)
    """
    if dist_type == 'normal':
        val = random.gauss(mean, stdev)
        return val
    elif dist_type == 'lognormal':
        # This placeholder approach interprets 'mean' and 'stdev' as log-space params.
        val = random.lognormvariate(mean, stdev)
        return val
    elif dist_type == 'triangular':
        val = random.triangular(minimum, maximum, mode)
        return val

    # Default fallback:
    return mean


def calculate_own_scenario(vals):
    """
    Calculates final net worth for the 'buy' scenario, using placeholder monthly logic.

    Inputs (vals) is a dictionary of all sampled variables, e.g.:
      {
        "annual_income": 55000,
        "home_price": 300000,
        "down_payment": 60000,
        "mortgage_rate": 4,
        "mortgage_term": 30,
        "property_tax_rate": 1.2,
        "homeowner_insurance": 1200,
        "maintenance_rate": 1,
        "rent": 1500,
        "rent_escalation_rate": 3,
        "home_appreciation": 3,
        "investment_return": 5,
        "marginal_tax_rate": 25,
        "inflation_rate": 2,
        "start_age": 30,
        "end_age": 65,
        "monthly_travel": 300,
        "monthly_groceries": 400,
        "monthly_bills": 250,
        "monthly_healthcare": 200,
        ...
      }

    Returns final net worth (float).
    """

    # Convert percentages where needed:
    annual_income = vals['annual_income']
    mortgage_rate_annual = vals['mortgage_rate'] / 100.0  # e.g. 4 -> 0.04
    property_tax_rate = vals['property_tax_rate'] / 100.0
    maintenance_rate = vals['maintenance_rate'] / 100.0
    home_appreciation_rate = vals['home_appreciation'] / 100.0
    investment_return_annual = vals['investment_return'] / 100.0
    marginal_tax_rate = vals['marginal_tax_rate'] / 100.0
    inflation_rate = vals['inflation_rate'] / 100.0

    # Basic derived values:
    monthly_income = (annual_income * (1 - marginal_tax_rate)) / 12.0
    months = int((vals['end_age'] - vals['start_age']) * 12)
    if months < 1:
        return 0.0

    house_value = vals['home_price']
    down_payment = vals['down_payment']
    mortgage_principal = house_value - down_payment
    if mortgage_principal < 0:
        mortgage_principal = 0

    mortgage_term_months = int(vals['mortgage_term'] * 12)
    monthly_interest_rate = mortgage_rate_annual / 12.0

    # Monthly mortgage payment (standard formula) if mortgage_principal > 0:
    if mortgage_principal > 0 and monthly_interest_rate > 0:
        mortgage_payment = (
            mortgage_principal 
            * (monthly_interest_rate * (1 + monthly_interest_rate) ** mortgage_term_months)
            / ((1 + monthly_interest_rate) ** mortgage_term_months - 1)
        )
    else:
        mortgage_payment = 0.0

    # Net worth components:
    # Let's track "liquid_investments" and "mortgage_balance" and "house_value" separately.
    # Start with net outlay for down payment:
    liquid_investments = 0.0  # buyer invests leftover monthly
    mortgage_balance = mortgage_principal

    # Subtract down payment from net worth:
    # So effectively net worth = house_value - mortgage_balance + liquid_investments
    # But if you prefer to track just the "cash" side:
    # we'll do: net_worth = -down_payment initially + 0 investments
    # For clarity, let's track them separately:
    net_worth = -down_payment

    # Monthly costs:
    monthly_insurance = vals['homeowner_insurance'] / 12.0

    # We'll track these living expenses separately and inflate them each year.
    monthly_travel = vals['monthly_travel']
    monthly_groceries = vals['monthly_groceries']
    monthly_bills = vals['monthly_bills']
    monthly_healthcare = vals['monthly_healthcare']

    # Run the monthly loop:
    for m in range(months):
        # Every 12 months, we apply annual inflation to (monthly_income, expenses, etc.)
        if m > 0 and m % 12 == 0:
            # Increase annual_income by inflation, recompute monthly:
            annual_income *= (1 + inflation_rate)
            monthly_income = (annual_income * (1 - marginal_tax_rate)) / 12.0

            # House appreciates once per year:
            house_value *= (1 + home_appreciation_rate)

            # Also inflate monthly living expenses:
            monthly_travel *= (1 + inflation_rate)
            monthly_groceries *= (1 + inflation_rate)
            monthly_bills *= (1 + inflation_rate)
            monthly_healthcare *= (1 + inflation_rate)
            monthly_insurance *= (1 + inflation_rate)

        # If we still have a mortgage, pay it:
        actual_mortgage_payment = 0.0
        if m < mortgage_term_months and mortgage_balance > 0:
            # interest portion this month:
            interest_portion = mortgage_balance * monthly_interest_rate
            principal_portion = mortgage_payment - interest_portion
            if principal_portion > mortgage_balance:
                # Final payment might be smaller if principal is near zero
                principal_portion = mortgage_balance

            mortgage_balance -= principal_portion
            actual_mortgage_payment = interest_portion + principal_portion

        # monthly property tax (on current house_value):
        monthly_property_tax = (house_value * property_tax_rate) / 12.0

        # monthly maintenance:
        monthly_maintenance = (house_value * maintenance_rate) / 12.0

        # Sum up monthly homeowner costs:
        monthly_homeowner_costs = (
            actual_mortgage_payment
            + monthly_property_tax
            + monthly_insurance
            + monthly_maintenance
        )

        # Sum up living expenses:
        monthly_living_expenses = (
            monthly_travel
            + monthly_groceries
            + monthly_bills
            + monthly_healthcare
        )

        total_monthly_spending = monthly_homeowner_costs + monthly_living_expenses

        # leftover = monthly_income - total_monthly_spending
        leftover = monthly_income - total_monthly_spending

        # If leftover is positive, invest it:
        if leftover > 0:
            liquid_investments += leftover

        # Grow all existing liquid investments by monthly investment_return:
        monthly_invest_return = (investment_return_annual / 12.0)
        liquid_investments *= (1 + monthly_invest_return)

    # After final month, let's also do one last property appreciation if you prefer,
    # but we'll skip it here. We'll say the house_value is final.

    # Final net worth = house_value (asset) - mortgage_balance (liability)
    # + any leftover in liquid_investments + the net_worth offset
    # Because we set net_worth = -down_payment initially, let's unify that:

    final_net_worth = (
        net_worth  # which started at -down_payment
        + (house_value - mortgage_balance)
        + liquid_investments
    )

    return final_net_worth


def calculate_rent_scenario(vals):
    """
    Calculates final net worth for the 'rent' scenario, using placeholder monthly logic.
    In rent scenario, the user invests leftover money instead of paying a mortgage
    or property taxes, etc. We also model rent escalation once per year and
    inflation for living expenses.
    """
    annual_income = vals['annual_income']
    rent = vals['rent']
    rent_escalation_rate = vals['rent_escalation_rate'] / 100.0
    investment_return_annual = vals['investment_return'] / 100.0
    marginal_tax_rate = vals['marginal_tax_rate'] / 100.0
    inflation_rate = vals['inflation_rate'] / 100.0

    months = int((vals['end_age'] - vals['start_age']) * 12)
    if months < 1:
        return 0.0

    # monthly income after taxes:
    monthly_income = (annual_income * (1 - marginal_tax_rate)) / 12.0
    liquid_investments = 0.0

    # monthly living expenses (besides rent):
    monthly_travel = vals['monthly_travel']
    monthly_groceries = vals['monthly_groceries']
    monthly_bills = vals['monthly_bills']
    monthly_healthcare = vals['monthly_healthcare']

    current_rent = rent

    for m in range(months):
        # each year, update:
        if m > 0 and m % 12 == 0:
            # escalate rent
            current_rent *= (1 + rent_escalation_rate)

            # inflate annual income
            annual_income *= (1 + inflation_rate)
            monthly_income = (annual_income * (1 - marginal_tax_rate)) / 12.0

            # inflate monthly expenses
            monthly_travel *= (1 + inflation_rate)
            monthly_groceries *= (1 + inflation_rate)
            monthly_bills *= (1 + inflation_rate)
            monthly_healthcare *= (1 + inflation_rate)

        # total monthly spending = rent + other living costs
        monthly_living_expenses = (
            current_rent
            + monthly_travel
            + monthly_groceries
            + monthly_bills
            + monthly_healthcare
        )

        leftover = monthly_income - monthly_living_expenses
        if leftover > 0:
            liquid_investments += leftover

        # grow investments each month
        monthly_invest_return = (investment_return_annual / 12.0)
        liquid_investments *= (1 + monthly_invest_return)

    # No house asset in rent scenario, so final net worth is just the
    # total in liquid_investments
    final_net_worth = liquid_investments
    return final_net_worth


def run_single_simulation(dist_params):
    """
    Runs a single Monte Carlo iteration:
      1) Samples a random value for each variable's distribution
      2) Calls calculate_own_scenario and calculate_rent_scenario
      3) Returns (own_value, rent_value)
    """

    # We'll map the front-end variable names to random draws:
    # For example: 'annual_income' -> sample from dist_params['annual_income_dist']
    sampled_vals = {}

    # List of (key, distribution_key) pairs. The second element is how we labeled
    # the distribution entry in dist_params, e.g. 'annual_income_dist'.
    variable_keys = [
        ('annual_income', 'annual_income_dist'),
        ('home_price', 'home_price_dist'),
        ('down_payment', 'down_payment_dist'),
        ('mortgage_rate', 'mortgage_rate_dist'),
        ('mortgage_term', 'mortgage_term_dist'),
        ('property_tax_rate', 'property_tax_rate_dist'),
        ('homeowner_insurance', 'homeowner_insurance_dist'),
        ('maintenance_rate', 'maintenance_rate_dist'),
        ('rent', 'rent_dist'),
        ('rent_escalation_rate', 'rent_escalation_rate_dist'),
        ('home_appreciation', 'home_appreciation_dist'),
        ('investment_return', 'investment_return_dist'),
        ('marginal_tax_rate', 'marginal_tax_rate_dist'),
        ('inflation_rate', 'inflation_rate_dist'),
        ('start_age', 'start_age_dist'),
        ('end_age', 'end_age_dist'),
        ('monthly_travel', 'monthly_travel_dist'),
        ('monthly_groceries', 'monthly_groceries_dist'),
        ('monthly_bills', 'monthly_bills_dist'),
        ('monthly_healthcare', 'monthly_healthcare_dist')
    ]

    # For each variable, sample from its distribution, or just use a fallback
    # if no distribution info is provided:
    for base_key, dist_key in variable_keys:
        if dist_key in dist_params:
            d = dist_params[dist_key]
            val = sample_distribution(
                d.get('dist_type', 'normal'),
                d.get('mean', 0.0),
                d.get('stdev', 0.0),
                d.get('min', 0.0),
                d.get('max', 0.0),
                d.get('mode', 0.0)
            )
            sampled_vals[base_key] = val
        else:
            # If not in dist_params, fallback to a safe default (like 0)
            sampled_vals[base_key] = 0.0

    own_final = calculate_own_scenario(sampled_vals)
    rent_final = calculate_rent_scenario(sampled_vals)

    return own_final, rent_final


def percentile(sorted_list, p):
    """
    Returns the p-th percentile from a sorted list (0 <= p <= 100).
    """
    if not sorted_list:
        return None
    index = (len(sorted_list) - 1) * (p / 100.0)
    lower = int(math.floor(index))
    upper = int(math.ceil(index))
    if lower == upper:
        return sorted_list[lower]
    fraction = index - lower
    return sorted_list[lower] + (sorted_list[upper] - sorted_list[lower]) * fraction


def run_monte_carlo(dist_params, num_sims=1000):
    """
    1) Repeats run_single_simulation num_sims times.
    2) Collects own and rent final net worth.
    3) Sorts them and computes summary stats (mean, median, 10th, 90th).
    4) Returns a results dictionary with:
       {
         'own_results': [...],
         'rent_results': [...],
         'mean_own': ...,
         'mean_rent': ...,
         'median_own': ...,
         'median_rent': ...,
         'pct_10_own': ...,
         'pct_90_own': ...,
         'pct_10_rent': ...,
         'pct_90_rent': ...
       }
    """

    own_values = []
    rent_values = []

    for _ in range(num_sims):
        own, rent = run_single_simulation(dist_params)
        own_values.append(own)
        rent_values.append(rent)

    own_values.sort()
    rent_values.sort()

    mean_own = statistics.mean(own_values) if own_values else 0.0
    mean_rent = statistics.mean(rent_values) if rent_values else 0.0
    median_own = statistics.median(own_values) if own_values else 0.0
    median_rent = statistics.median(rent_values) if rent_values else 0.0

    pct_10_own = percentile(own_values, 10)
    pct_90_own = percentile(own_values, 90)
    pct_10_rent = percentile(rent_values, 10)
    pct_90_rent = percentile(rent_values, 90)

    return {
        'own_results': own_values,
        'rent_results': rent_values,
        'mean_own': mean_own,
        'mean_rent': mean_rent,
        'median_own': median_own,
        'median_rent': median_rent,
        'pct_10_own': pct_10_own,
        'pct_90_own': pct_90_own,
        'pct_10_rent': pct_10_rent,
        'pct_90_rent': pct_90_rent
    }


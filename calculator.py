import math

def calculate_mortgage_payment(principal, annual_interest_rate, term_years):
    """Calculates the fixed monthly mortgage payment."""
    monthly_rate = annual_interest_rate / 12
    n = term_years * 12
    if monthly_rate == 0:
        return principal / n
    payment = principal * monthly_rate / (1 - (1 + monthly_rate) ** (-n))
    return payment

def simulate_own_vs_rent(params):
    # Extract parameters with defaults (as provided)
    start_age = params.get("start_age", 30)
    end_age = params.get("end_age", 65)
    total_months = (end_age - start_age) * 12

    annual_income = params.get("annual_income", 60000)
    annual_salary_growth = params.get("annual_salary_growth", 0.02)
    home_price = params.get("home_price", 300000)
    down_payment = params.get("down_payment", 60000)
    mortgage_rate = params.get("mortgage_rate", 0.04)
    mortgage_term = params.get("mortgage_term", 30)
    property_tax_rate = params.get("property_tax_rate", 0.012)
    homeowner_insurance = params.get("homeowner_insurance", 1200)
    maintenance_rate = params.get("maintenance_rate", 0.01)
    rent = params.get("rent", 1500)
    rent_escalation_rate = params.get("rent_escalation_rate", 0.03)
    renters_insurance_annual = params.get("renters_insurance_annual", 240)  # ~$20/month
    home_appreciation = params.get("home_appreciation", 0.03)
    investment_return = params.get("investment_return", 0.05)
    marginal_tax_rate = params.get("marginal_tax_rate", 0.25)
    inflation_rate = params.get("inflation_rate", 0.02)

    # Monthly conversion factors (using monthly compounding approximations)
    monthly_salary_growth = (1 + annual_salary_growth) ** (1/12) - 1
    monthly_investment_return = (1 + investment_return) ** (1/12) - 1
    monthly_home_appreciation = (1 + home_appreciation) ** (1/12) - 1
    monthly_rent_escalation = (1 + rent_escalation_rate) ** (1/12) - 1

    # Initialize simulation variables
    salary = annual_income
    current_home_value = home_price
    mortgage_balance = home_price - down_payment
    mortgage_payment = calculate_mortgage_payment(mortgage_balance, mortgage_rate, mortgage_term)
    mortgage_term_months = mortgage_term * 12

    homeowner_investment = 0.0
    renter_investment = down_payment  # down payment is invested in the renting scenario
    homeowner_debt = 0.0
    renter_debt = 0.0
    lifetime_income = 0.0

    # For rent, we will update the current monthly rent over time
    current_rent = rent

    # Simulation loop (month by month)
    for month in range(1, total_months + 1):
        # Update lifetime income (monthly)
        monthly_income = salary / 12
        lifetime_income += monthly_income

        # --- Homeowner Scenario ---
        if month <= mortgage_term_months:
            # Calculate current month's mortgage payment details
            monthly_interest = mortgage_balance * (mortgage_rate / 12)
            principal_payment = mortgage_payment - monthly_interest
            # Adjust final payment if necessary
            if principal_payment > mortgage_balance:
                principal_payment = mortgage_balance
                mortgage_payment = monthly_interest + principal_payment
            mortgage_balance -= principal_payment
        else:
            mortgage_payment = 0
            monthly_interest = 0

        monthly_property_tax = (current_home_value * property_tax_rate) / 12
        monthly_insurance = homeowner_insurance / 12
        monthly_maintenance = (current_home_value * maintenance_rate) / 12

        # Tax benefit applies only when mortgage (and its interest) is active.
        tax_benefit = 0
        if month <= mortgage_term_months:
            tax_benefit = (monthly_interest + monthly_property_tax) * marginal_tax_rate

        homeowner_cost = mortgage_payment + monthly_property_tax + monthly_insurance + monthly_maintenance - tax_benefit

        # --- Renting Scenario ---
        monthly_rent = current_rent
        renters_insurance = renters_insurance_annual / 12
        renting_cost = monthly_rent + renters_insurance

        # --- Surplus Cash Flow ---
        homeowner_surplus = monthly_income - homeowner_cost
        renter_surplus = monthly_income - renting_cost

        # Update investment balances (if surplus positive) or accumulate debt (if negative)
        if homeowner_surplus >= 0:
            homeowner_investment = homeowner_investment * (1 + monthly_investment_return) + homeowner_surplus
        else:
            # Debt grows with the effective investment rate
            homeowner_debt = homeowner_debt * (1 + monthly_investment_return) - homeowner_surplus

        if renter_surplus >= 0:
            renter_investment = renter_investment * (1 + monthly_investment_return) + renter_surplus
        else:
            renter_debt = renter_debt * (1 + monthly_investment_return) - renter_surplus

        # Update home value (appreciation)
        current_home_value *= (1 + monthly_home_appreciation)

        # Update salary for next month
        salary *= (1 + monthly_salary_growth)

        # Update rent for next month
        current_rent *= (1 + monthly_rent_escalation)

    final_house_value = current_home_value

    # Net worth calculations: include investment balance, property value, subtract remaining mortgage and any accumulated debt.
    homeowner_net_worth = final_house_value + homeowner_investment - mortgage_balance - homeowner_debt
    renter_net_worth = renter_investment - renter_debt

    results = {
        "lifetime_income": lifetime_income,
        "renter_final_investment": renter_investment,
        "homeowner_final_investment": homeowner_investment,
        "final_house_value": final_house_value,
        "homeowner_net_worth": homeowner_net_worth,
        "renter_net_worth": renter_net_worth,
        "mortgage_balance": mortgage_balance,  # for reference if needed
    }
    return results

if __name__ == "__main__":
    # Run simulation with default values for testing
    defaults = {
        "start_age": 30,
        "end_age": 65,
        "annual_income": 60000,
        "annual_salary_growth": 0.02,
        "home_price": 300000,
        "down_payment": 60000,
        "mortgage_rate": 0.04,
        "mortgage_term": 30,
        "property_tax_rate": 0.012,
        "homeowner_insurance": 1200,
        "maintenance_rate": 0.01,
        "rent": 1500,
        "rent_escalation_rate": 0.03,
        "renters_insurance_annual": 240,
        "home_appreciation": 0.03,
        "investment_return": 0.05,
        "marginal_tax_rate": 0.25,
        "inflation_rate": 0.02,
    }
    results = simulate_own_vs_rent(defaults)
    for key, value in results.items():
        print(f"{key}: {value:.2f}")


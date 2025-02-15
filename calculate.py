import math

def validate_param(value, min_val, max_val, param_name):
    """
    Validate a single parameter against specified min and max range.
    Raises ValueError if out of range or if cast fails.
    """
    try:
        val = float(value)
    except:
        raise ValueError(f"Parameter '{param_name}' must be a numeric value.")
    
    if val < min_val or val > max_val:
        raise ValueError(
            f"Parameter '{param_name}' with value {val} is out of the allowed range [{min_val}, {max_val}]."
        )
    return val


def calculate_mortgage_payment(principal, annual_interest_rate, term_years):
    """
    Calculates the fixed monthly mortgage payment for a standard amortized loan.
    
    principal:        The initial amount borrowed.
    annual_interest_rate:   The nominal annual interest rate (e.g. 0.04 for 4%).
    term_years:       The length of the mortgage in years.
    
    Returns a float that is the monthly payment required to fully amortize
    the loan over the specified term and interest rate.
    """
    monthly_rate = annual_interest_rate / 12
    n = term_years * 12
    
    # If interest rate is zero, avoid division by zero:
    if monthly_rate == 0:
        return principal / n
    
    # Standard formula for an amortizing loan payment:
    payment = principal * (monthly_rate) / (1 - (1 + monthly_rate) ** (-n))
    return payment


def simulate_own_vs_rent(params):
    """
    Runs the month-by-month simulation comparing home ownership versus renting.
    
    Inputs:
      params: A dictionary of simulation parameters, which can include:
        - start_age (int):       Starting age of the user
        - end_age (int):         Ending age of the user
        - annual_income (float): Current annual income of the user
        - annual_salary_growth (float): Annual salary growth assumption
        - home_price (float):    Purchase price of the home
        - down_payment (float):  Down payment amount on the home
        - mortgage_rate (float): Annual mortgage interest rate (0.04 = 4%)
        - mortgage_term (int):   Years of the mortgage (e.g., 30)
        - property_tax_rate (float): Yearly property tax rate (0.012 = 1.2%)
        - homeowner_insurance (float): Yearly homeowner’s insurance
        - maintenance_rate (float): Yearly maintenance as % of home value
        - rent (float):          Current monthly rent
        - rent_escalation_rate (float): Annual rent escalation rate (0.03 = 3%)
        - renters_insurance_annual (float): Yearly renters insurance
        - home_appreciation (float): Annual home appreciation rate
        - investment_return (float): Annual return of invested surplus
        - marginal_tax_rate (float): Marginal tax rate for interest deduction
        - inflation_rate (float):     General inflation rate (currently not used in detail here)
        
        - monthly_travel (float):     Monthly travel/car costs
        - monthly_groceries (float):  Monthly groceries
        - monthly_bills (float):      Monthly bills (utilities, phone, etc.)
        - monthly_healthcare (float): Monthly healthcare costs

    Returns:
      A dict containing:
        - "lifetime_income"
        - "renter_final_investment"
        - "homeowner_final_investment"
        - "final_house_value"
        - "homeowner_net_worth"
        - "renter_net_worth"
        - "mortgage_balance" (remaining mortgage after final month)
    """

    # 1. Validate and extract parameters with fallback defaults
    start_age = validate_param(params.get("start_age", 30), 17, 90, "start_age")
    end_age = validate_param(params.get("end_age", 65), 30, 120, "end_age")
    
    # If start_age >= end_age, just return empty or handle gracefully
    if start_age >= end_age:
        raise ValueError("The end_age must be greater than start_age.")

    total_months = int((end_age - start_age) * 12)

    annual_income = validate_param(params.get("annual_income", 60000), 10000, 20000000, "annual_income")
    annual_salary_growth = params.get("annual_salary_growth", 0.02)

    home_price = validate_param(params.get("home_price", 300000), 100000, 20000000, "home_price")
    down_payment = validate_param(params.get("down_payment", 60000), 0, 500000, "down_payment")
    mortgage_rate = validate_param(params.get("mortgage_rate", 0.04), 0.0, 0.10, "mortgage_rate")
    mortgage_term = validate_param(params.get("mortgage_term", 30), 10, 70, "mortgage_term")

    property_tax_rate = validate_param(params.get("property_tax_rate", 0.012), 0.0, 0.15, "property_tax_rate")
    homeowner_insurance = validate_param(params.get("homeowner_insurance", 1200), 500, 20000, "homeowner_insurance")
    maintenance_rate = validate_param(params.get("maintenance_rate", 0.01), 0.0, 0.20, "maintenance_rate")

    rent = validate_param(params.get("rent", 1500), 500, 5000, "rent")
    rent_escalation_rate = validate_param(params.get("rent_escalation_rate", 0.03), 0.0, 0.10, "rent_escalation_rate")
    renters_insurance_annual = validate_param(params.get("renters_insurance_annual", 240), 0.0, 5000, "renters_insurance_annual")

    home_appreciation = validate_param(params.get("home_appreciation", 0.03), 0.0, 0.10, "home_appreciation")
    investment_return = validate_param(params.get("investment_return", 0.05), 0.0, 0.25, "investment_return")
    marginal_tax_rate = validate_param(params.get("marginal_tax_rate", 0.25), 0.0, 1.0, "marginal_tax_rate")
    inflation_rate = validate_param(params.get("inflation_rate", 0.02), 0.0, 0.50, "inflation_rate")

    # New monthly expenses
    monthly_travel = validate_param(params.get("monthly_travel", 300), 0, 10000, "monthly_travel")
    monthly_groceries = validate_param(params.get("monthly_groceries", 400), 0, 10000, "monthly_groceries")
    monthly_bills = validate_param(params.get("monthly_bills", 250), 0, 100000, "monthly_bills")
    monthly_healthcare = validate_param(params.get("monthly_healthcare", 200), 0, 10000, "monthly_healthcare")

    # 2. Convert annual rates to monthly approximation
    monthly_salary_growth = (1 + annual_salary_growth) ** (1/12) - 1
    monthly_investment_return = (1 + investment_return) ** (1/12) - 1
    monthly_home_appreciation = (1 + home_appreciation) ** (1/12) - 1
    monthly_rent_escalation = (1 + rent_escalation_rate) ** (1/12) - 1

    # 3. Initialize financial variables
    salary = annual_income
    current_home_value = home_price
    mortgage_balance = home_price - down_payment
    mortgage_payment = calculate_mortgage_payment(mortgage_balance, mortgage_rate, mortgage_term)
    mortgage_term_months = int(mortgage_term * 12)

    homeowner_investment = 0.0
    renter_investment = down_payment  # assume we invest the down_payment if renting
    homeowner_debt = 0.0
    renter_debt = 0.0
    lifetime_income = 0.0

    current_rent = rent

    # 4. Simulation loop
    for month in range(1, total_months + 1):
        # 4a. Calculate monthly income
        monthly_income = salary / 12
        lifetime_income += monthly_income

        # Subtract monthly expenses (travel, groceries, bills, healthcare) from the income for BOTH scenarios
        # This ensures each scenario’s leftover cash flow is after these personal expenses.
        monthly_expenses = monthly_travel + monthly_groceries + monthly_bills + monthly_healthcare
        monthly_income_after_expenses = monthly_income - monthly_expenses

        # 4b. Homeowner scenario
        if month <= mortgage_term_months:
            monthly_interest = mortgage_balance * (mortgage_rate / 12)
            principal_payment = mortgage_payment - monthly_interest

            # Prevent overpaying the final month
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

        # Tax benefit only if mortgage interest is being paid
        tax_benefit = 0
        if month <= mortgage_term_months:
            tax_benefit = (monthly_interest + monthly_property_tax) * marginal_tax_rate

        homeowner_cost = mortgage_payment + monthly_property_tax + monthly_insurance + monthly_maintenance - tax_benefit

        # 4c. Renting scenario
        monthly_rent_payment = current_rent
        renters_insurance = renters_insurance_annual / 12
        renting_cost = monthly_rent_payment + renters_insurance

        # 4d. Surplus calculation
        homeowner_surplus = monthly_income_after_expenses - homeowner_cost
        renter_surplus = monthly_income_after_expenses - renting_cost

        # 4e. Investment or debt update
        if homeowner_surplus >= 0:
            # Grow existing investment by monthly_investment_return, then add surplus
            homeowner_investment = homeowner_investment * (1 + monthly_investment_return) + homeowner_surplus
        else:
            # If negative, treat it as debt that also compounds
            homeowner_debt = homeowner_debt * (1 + monthly_investment_return) - homeowner_surplus

        if renter_surplus >= 0:
            renter_investment = renter_investment * (1 + monthly_investment_return) + renter_surplus
        else:
            renter_debt = renter_debt * (1 + monthly_investment_return) - renter_surplus

        # 4f. Update home value
        current_home_value *= (1 + monthly_home_appreciation)

        # 4g. Salary growth
        salary *= (1 + monthly_salary_growth)

        # 4h. Rent escalation
        current_rent *= (1 + monthly_rent_escalation)

    # 5. Final calculations
    final_house_value = current_home_value

    homeowner_net_worth = final_house_value + homeowner_investment - mortgage_balance - homeowner_debt
    renter_net_worth = renter_investment - renter_debt

    results = {
        "lifetime_income": lifetime_income,
        "renter_final_investment": renter_investment,
        "homeowner_final_investment": homeowner_investment,
        "final_house_value": final_house_value,
        "homeowner_net_worth": homeowner_net_worth,
        "renter_net_worth": renter_net_worth,
        "mortgage_balance": mortgage_balance
    }

    return results


if __name__ == "__main__":
    # Example usage
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
        # Sample monthly expenses
        "monthly_travel": 300,
        "monthly_groceries": 400,
        "monthly_bills": 250,
        "monthly_healthcare": 200
    }
    output = simulate_own_vs_rent(defaults)
    for k, v in output.items():
        print(f"{k}: {v:.2f}")


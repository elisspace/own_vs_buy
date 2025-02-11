def main():
    """
    Compare lifetime cost of home ownership vs. renting+investing.
    Incorporates:
    - House appreciation/depreciation
    - Down payment and closing costs
    - Monthly leftover investment if renting is cheaper
    - Monthly compounding for investment returns
    """

    # 1. Define Constants
    CURRENT_AGE = 35
    AGE_AT_DEATH = 90

    # Mortgage details
    MORTGAGE_RATE = 0.04  # 4% annual
    MORTGAGE_TERM_YEARS = 30
    HOME_COST = 350_000
    DOWN_PAYMENT = 50_000
    BUYER_CLOSING_COSTS = 10_000  # e.g., typical closing fees

    # Home-related costs
    PROPERTY_TAX_RATE = 0.083      # 1% per year
    HOME_INSURANCE_PER_YEAR = 1200
    AVERAGE_YEARLY_MAINTENANCE = 5000

    # House appreciation/depreciation
    # e.g. 0.02 => +2% per year, -0.02 => -2% per year
    HOME_APPRECIATION_PERCENT = 0.05

    # Rent details
    RENT_PER_MONTH = 1500
    RENT_ANNUAL_GROWTH_RATE = 0.10  # 2.5% per year

    # Investment details
    INVESTMENT_RETURN_PERCENT = 0.07  # 10% annual

    # 2. Calculate total months for the simulation
    total_years = AGE_AT_DEATH - CURRENT_AGE
    total_months = total_years * 12

    # 3. Mortgage Payment Calculation (Monthly)
    #    Formula: M = P * (r(1+r)^n) / ((1+r)^n - 1)
    #    where:
    #      P = (HOME_COST - DOWN_PAYMENT)
    #      r = MORTGAGE_RATE / 12
    #      n = MORTGAGE_TERM_YEARS * 12
    principal = HOME_COST - DOWN_PAYMENT
    monthly_interest_rate = MORTGAGE_RATE / 12
    number_of_payments = MORTGAGE_TERM_YEARS * 12

    if principal > 0:
        monthly_mortgage_payment = (
            principal *
            (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments) /
            ((1 + monthly_interest_rate) ** number_of_payments - 1)
        )
    else:
        # If DOWN_PAYMENT >= HOME_COST, no mortgage needed
        monthly_mortgage_payment = 0

    # 4. Break down monthly home costs
    monthly_property_tax = (HOME_COST * PROPERTY_TAX_RATE) / 12
    monthly_insurance = HOME_INSURANCE_PER_YEAR / 12
    monthly_maintenance = AVERAGE_YEARLY_MAINTENANCE / 12

    # 5. Initialize tracking variables

    # For the homeowner:
    # Start with the home’s initial value; it will appreciate monthly
    house_value = HOME_COST  
    total_ownership_cost = DOWN_PAYMENT + BUYER_CLOSING_COSTS  # upfront out-of-pocket
    
    # For the renter:
    # Lump sum investment is the down payment + closing costs that aren't spent on buying.
    investment_balance = DOWN_PAYMENT + BUYER_CLOSING_COSTS
    total_renting_cost = 0.0
    
    # Convert annual appreciation to a monthly factor
    monthly_appreciation_rate = (1 + HOME_APPRECIATION_PERCENT) ** (1/12) - 1
    
    # Convert annual investment return to monthly
    monthly_investment_return_rate = INVESTMENT_RETURN_PERCENT / 12

    current_rent = RENT_PER_MONTH

    # 6. Iterate month by month
    for month in range(1, total_months + 1):
        # House appreciates each month (can be negative if it's depreciation)
        house_value *= (1 + monthly_appreciation_rate)

        # Calculate monthly ownership cost
        if month <= number_of_payments:
            # Mortgage not fully paid yet
            monthly_owner_cost = (monthly_mortgage_payment +
                                  monthly_property_tax +
                                  monthly_insurance +
                                  monthly_maintenance)
        else:
            # After the mortgage is paid off, only taxes, insurance, and maintenance remain
            monthly_owner_cost = (monthly_property_tax +
                                  monthly_insurance +
                                  monthly_maintenance)
        
        # Add to total ownership cost
        total_ownership_cost += monthly_owner_cost

        # Renter pays this month’s rent
        total_renting_cost += current_rent

        # Determine leftover that the renter invests if renting is cheaper
        # difference > 0 => owning is more expensive => that difference can be invested by the renter
        difference = monthly_owner_cost - current_rent
        
        if difference > 0:
            # This means renting is cheaper by 'difference'
            investment_balance += difference  # invest that difference immediately

        # Grow the investment balance by the monthly return
        investment_balance *= (1 + monthly_investment_return_rate)

        # Increase rent once a year
        if month % 12 == 0:
            current_rent *= (1 + RENT_ANNUAL_GROWTH_RATE)

    # 7. Final net worth calculations
    # Homeowner's final net worth (simplified):
    #   They own the house, which is now worth house_value.
    #   total_ownership_cost is how much cash was spent over the period (plus the upfront).
    #   You can show them both or compute net_worth as (house_value - total_ownership_cost)
    net_worth_owning = house_value - total_ownership_cost

    # Renter's final net worth is simply the investment balance
    net_worth_renting = investment_balance

    # 8. Results
    print("----- Results -----")
    print(f"Total Ownership Cost (cash outlay): ${total_ownership_cost:,.2f}")
    print(f"Final House Value:                  ${house_value:,.2f}")
    print(f"Net Worth (Owning) = House Value - Outlays = ${net_worth_owning:,.2f}")
    print()
    print(f"Total Rent Paid Over {total_years} Years:     ${total_renting_cost:,.2f}")
    print(f"Final Investment Balance (Renting):           ${investment_balance:,.2f}")
    print(f"Net Worth (Renting) = ${net_worth_renting:,.2f}")
    print()
    difference = net_worth_renting - net_worth_owning
    print(f"Difference (Renting Net Worth - Owning Net Worth): ${difference:,.2f}")

if __name__ == "__main__":
    main()


def main():
    """
    1. Prints assumption values.
    2. Calculates monthly living expenses (inflation-adjusted) for groceries, travel, schooling, healthcare, incidentals.
    3. Calculates renting vs buying costs each month (both in terms of cash flow and net worth).
    4. Compares the final net worth of renting vs buying, color-codes the final statement to indicate which is better.
    """

    # ANSI color codes for terminal output
    COLOR_GREEN = "\033[92m"
    COLOR_RED = "\033[91m"
    COLOR_RESET = "\033[0m"
    COLOR_YELLOW = "\033[93m"  # optional for neutral or headings

    # ================
    # Part 1: Constants
    # ================

    # Time horizon
    CURRENT_AGE = 35
    AGE_AT_DEATH = 90
    total_years = AGE_AT_DEATH - CURRENT_AGE
    total_months = total_years * 12

    # --- Income & Growth ---
    MONTHLY_SALARY = 5000.0          # Initial monthly salary
    ANNUAL_SALARY_GROWTH = 0.02      # 2% annual salary increase

    # --- Inflation for Monthly Expenses ---
    ANNUAL_INFLATION = 0.03          # 3% annual

    # --- Base Monthly Expenses (excluding accommodation) ---
    BASE_GROCERIES = 500.0
    BASE_TRAVEL = 200.0
    BASE_SCHOOLING = 300.0
    BASE_HEALTHCARE = 400.0
    BASE_INCIDENTALS = 2500  # "catch-all" category

    # --- Investment Growth ---
    ANNUAL_INVESTMENT_RETURN = 0.06  # 6% annual

    # --- Renting Details ---
    RENT_PER_MONTH = 1500.0
    ANNUAL_RENT_GROWTH = 0.025       # 2.5% annual

    # --- Buying Details ---
    HOME_COST = 350_000.0
    DOWN_PAYMENT = 80_000.0
    BUYER_CLOSING_COSTS = 5_000.0

    MORTGAGE_RATE = 0.04             # 4% annual
    MORTGAGE_TERM_YEARS = 30
    PROPERTY_TAX_RATE = 0.01         # 1% of home value per year
    HOME_INSURANCE_PER_YEAR = 1200.0
    AVERAGE_YEARLY_MAINTENANCE = 5000.0

    # Home appreciation (positive or negative)
    ANNUAL_HOME_APPRECIATION = 0.02  # 2% per year

    # ================
    # Display Assumptions
    # ================
    print(f"{COLOR_YELLOW}----- Assumptions -----{COLOR_RESET}")
    print(f"Time Span: {CURRENT_AGE} to {AGE_AT_DEATH} (Total {total_years} years)")
    print(f"Initial Monthly Salary: ${MONTHLY_SALARY:,.2f}")
    print(f"Annual Salary Growth: {ANNUAL_SALARY_GROWTH*100:.2f}%")
    print(f"Annual Inflation (non-housing expenses): {ANNUAL_INFLATION*100:.2f}%")
    print(f"Base Monthly Expenses (Groceries + Travel + Schooling + Healthcare + Incidentals): "
          f"${(BASE_GROCERIES + BASE_TRAVEL + BASE_SCHOOLING + BASE_HEALTHCARE + BASE_INCIDENTALS):,.2f}")
    print(f"Annual Investment Return: {ANNUAL_INVESTMENT_RETURN*100:.2f}%\n")

    print("Renting Assumptions:")
    print(f" - Initial Monthly Rent: ${RENT_PER_MONTH:,.2f}")
    print(f" - Annual Rent Growth: {ANNUAL_RENT_GROWTH*100:.2f}%\n")

    print("Buying Assumptions:")
    print(f" - Home Cost: ${HOME_COST:,.2f}")
    print(f" - Down Payment: ${DOWN_PAYMENT:,.2f}")
    print(f" - Buyer Closing Costs: ${BUYER_CLOSING_COSTS:,.2f}")
    print(f" - Mortgage Rate (Annual): {MORTGAGE_RATE*100:.2f}%")
    print(f" - Mortgage Term: {MORTGAGE_TERM_YEARS} years")
    print(f" - Property Tax Rate: {PROPERTY_TAX_RATE*100:.2f}% of home value/year")
    print(f" - Home Insurance/Year: ${HOME_INSURANCE_PER_YEAR:,.2f}")
    print(f" - Avg Yearly Maintenance: ${AVERAGE_YEARLY_MAINTENANCE:,.2f}")
    print(f" - Annual Home Appreciation: {ANNUAL_HOME_APPRECIATION*100:.2f}%")
    print(f"{'-'*50}\n")

    # ================
    # Part 2: Derive Monthly Rates and Setup
    # ================
    monthly_salary_growth = (1 + ANNUAL_SALARY_GROWTH) ** (1/12) - 1
    monthly_inflation = (1 + ANNUAL_INFLATION) ** (1/12) - 1
    monthly_investment_growth = ANNUAL_INVESTMENT_RETURN / 12
    monthly_rent_growth = (1 + ANNUAL_RENT_GROWTH) ** (1/12) - 1
    monthly_home_appreciation = (1 + ANNUAL_HOME_APPRECIATION) ** (1/12) - 1

    # Base standard expenses total
    base_standard_expenses = (
        BASE_GROCERIES +
        BASE_TRAVEL +
        BASE_SCHOOLING +
        BASE_HEALTHCARE +
        BASE_INCIDENTALS
    )
    current_standard_expenses = base_standard_expenses

    # Mortgage payment
    principal = HOME_COST - DOWN_PAYMENT
    monthly_mortgage_rate = MORTGAGE_RATE / 12
    number_of_payments = MORTGAGE_TERM_YEARS * 12

    if principal > 0:
        monthly_mortgage_payment = (
            principal *
            (monthly_mortgage_rate * (1 + monthly_mortgage_rate) ** number_of_payments) /
            ((1 + monthly_mortgage_rate) ** number_of_payments - 1)
        )
    else:
        monthly_mortgage_payment = 0.0

    monthly_property_tax = (HOME_COST * PROPERTY_TAX_RATE) / 12
    monthly_insurance = HOME_INSURANCE_PER_YEAR / 12
    monthly_maintenance = AVERAGE_YEARLY_MAINTENANCE / 12

    # ================
    # Part 3: Tracking & Simulation
    # ================
    total_income = 0.0
    total_standard_expenses_accum = 0.0

    # Renting scenario
    total_rent_cost = 0.0
    rent_investment_balance = DOWN_PAYMENT + BUYER_CLOSING_COSTS  # Freed up capital if you don't buy
    current_rent = RENT_PER_MONTH

    # Buying scenario
    total_buy_cost = DOWN_PAYMENT + BUYER_CLOSING_COSTS  # upfront cost
    buy_investment_balance = 0.0
    house_value = HOME_COST

    # Starting salary
    current_monthly_salary = MONTHLY_SALARY

    for month in range(1, total_months + 1):
        # --- Income
        total_income += current_monthly_salary

        # --- Standard Expenses (inflation-adjusted)
        total_standard_expenses_accum += current_standard_expenses

        # --- Renting: Pay Rent, Invest Leftover
        total_rent_cost += current_rent
        leftover_rent = current_monthly_salary - current_standard_expenses - current_rent
        if leftover_rent > 0:
            rent_investment_balance += leftover_rent
        rent_investment_balance *= (1 + monthly_investment_growth)

        # --- Buying: Pay Mortgage/Costs, Invest Leftover
        if month <= number_of_payments:
            monthly_ownership_cost = (
                monthly_mortgage_payment +
                monthly_property_tax +
                monthly_insurance +
                monthly_maintenance
            )
        else:
            monthly_ownership_cost = (
                monthly_property_tax +
                monthly_insurance +
                monthly_maintenance
            )

        total_buy_cost += monthly_ownership_cost
        leftover_buy = current_monthly_salary - current_standard_expenses - monthly_ownership_cost
        if leftover_buy > 0:
            buy_investment_balance += leftover_buy
        buy_investment_balance *= (1 + monthly_investment_growth)

        # House Appreciation
        house_value *= (1 + monthly_home_appreciation)

        # Increase Salary, Rent, Standard Expenses (monthly growth)
        current_monthly_salary *= (1 + monthly_salary_growth)
        current_rent *= (1 + monthly_rent_growth)
        current_standard_expenses *= (1 + monthly_inflation)

    # ================
    # Part 4: Final Output & Comparison
    # ================
    print(f"{COLOR_YELLOW}----- Final Results -----{COLOR_RESET}")
    print(f"Total Income (All Sources):           ${total_income:,.2f}")
    print(f"Total Standard Expenses (Excl. Accommodation): ${total_standard_expenses_accum:,.2f}")

    # Costs including renting
    total_rent_incl_expenses = total_standard_expenses_accum + total_rent_cost
    print(f"Total Costs (Incl. Rent):            ${total_rent_incl_expenses:,.2f}")

    # Costs including buying
    total_buy_incl_expenses = total_standard_expenses_accum + total_buy_cost
    print(f"Total Costs (Incl. Buy):             ${total_buy_incl_expenses:,.2f}\n")

    # Compute a simplified 'final net worth' approach
    # - Renter's net worth: final investment balance
    # - Owner's net worth: final investment balance + house value
    rent_net_worth = rent_investment_balance
    buy_net_worth = buy_investment_balance + house_value

    print(f"Renter's Final Investment Balance:    ${rent_net_worth:,.2f}")
    print(f"Homeowner's Investment Balance:       ${buy_investment_balance:,.2f}")
    print(f"Final House Value:                    ${house_value:,.2f}")

    print()
    difference = buy_net_worth - rent_net_worth
    if difference > 0:
        # Buying scenario is ahead
        print(
            f"{COLOR_GREEN}Buying is ahead by ${difference:,.2f} "
            f"({buy_net_worth:,.2f} vs. {rent_net_worth:,.2f}){COLOR_RESET}"
        )
    elif difference < 0:
        # Renting scenario is ahead
        print(
            f"{COLOR_GREEN}Renting is ahead by ${abs(difference):,.2f} "
            f"({rent_net_worth:,.2f} vs. {buy_net_worth:,.2f}){COLOR_RESET}"
        )
    else:
        # Exactly the same (unlikely in real life)
        print(f"{COLOR_YELLOW}Both scenarios come out exactly the same!{COLOR_RESET}")


if __name__ == "__main__":
    main()


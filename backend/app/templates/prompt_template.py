"""
Simplified and optimized prompt template for Gemini 2.0 Flash.
Focuses on practical extraction with clear structure.
"""

EXTRACTION_PROMPT_TEMPLATE = """You are a financial data extraction expert. Extract ALL data from this fund report PDF and return it as detailed JSON.

CRITICAL RULES:
1. You MUST return ONLY valid JSON - no explanations, no markdown, no code blocks
2. Start your response with {{ and end with }}
3. Extract EVERY number, percentage, and text value you see in the document
4. For missing data, use null (not 0, not empty string)
5. For Portfolio Summary: Find all fund metrics, performance data, regional and industry breakdowns

3. **STATEMENT OF CASHFLOWS - TABLE EXTRACTION:**
   Find the "Statement of Cashflows" table in the PDF. The table structure is:
   - ROWS: 26 line items (see list below)
   - COLUMNS: Current Period, Prior Period, Year to Date
   
   For EACH line item, find the row in the table and extract the value from each of the 3 columns:
   - row_1_current = Find "Cash flows from operating activities" row, get Current Period column value
   - row_1_prior = Find "Cash flows from operating activities" row, get Prior Period column value
   - row_1_ytd = Find "Cash flows from operating activities" row, get Year to Date column value
   - row_2_current = Find "Net increase/(decrease) in partners' capital" row, get Current Period value
   - row_2_prior = Find "Net increase/(decrease) in partners' capital" row, get Prior Period value
   - row_2_ytd = Find "Net increase/(decrease) in partners' capital" row, get Year to Date value
   
   Continue for ALL 26 rows. The line items are:
   1. Cash flows from operating activities
   2. Net increase/(decrease) in partners' capital
   3. Adjustments to reconcile net increase/(decrease)
   4. Net realized (gain)/loss on investments
   5. Net change in unrealized (gain)/loss on investments
   6. Changes in operating assets and liabilities
   7. (Increase)/decrease in due from affiliates
   8. (Increase)/decrease in due from third party
   9. (Increase)/decrease in due from investment
   10. Purchase of investments
   11. Proceeds from sale of investments
   12. Net cash provided by/(used in) operating activities
   13. Cash flows from financing activities
   14. Capital contributions
   15. Distributions
   16. Increase/(decrease) in due to limited partners
   17. Increase/(decrease) in due to affiliates
   18. (Increase)/decrease in due from limited partners
   19. Proceeds from loans
   20. Repayment of loans
   21. Net cash provided by/(used in) financing activities
   22. Net increase/(decrease) in cash and cash equivalents
   23. Cash and cash equivalents, beginning of period
   24. Cash and cash equivalents, end of period
   25. Supplemental disclosure of cash flow information
   26. Cash paid for interest
   
   **KEY**: Look for similar wording in the PDF. The exact text may vary slightly.
   Extract ACTUAL numbers - each period should have DIFFERENT values!

4. **PCAP STATEMENT - TABLE EXTRACTION:**
   Find the "PCAP Statement" or "Partners' Capital Account" or "Statement of Changes in Partners' Capital" table.
   Structure: 28 line items × 3 time periods
   
   For EACH line item, find the row and extract values from all 3 period columns:
   - row_1_current = Find "Beginning NAV" row, get Current Period value
   - row_1_prior = Find "Beginning NAV" row, get Prior Period value
   - row_1_ytd = Find "Beginning NAV" row, get Year to Date value
   
   Continue for ALL 28 rows. The line items are:
   1. Beginning NAV - Net of Incentive Allocation
   2. Contributions - Cash & Non-Cash
   3. Distributions - Cash & Non-Cash
   4. Total Cash / Non-Cash Flows
   5. (Management Fees - Gross of Offsets, Waivers & Rebates)
   6. (Management Fee Rebate)
   7. (Partnership Expenses - Total)
   8. Total Offsets to Fees & Expenses
   9. Fee Waiver
   10. Interest Income
   11. Dividend Income
   12. (Interest Expense)
   13. Other Income/(Expense)
   14. Total Net Operating Income / (Expense)
   15. (Placement Fees)
   16. Realized Gain / (Loss)
   17. Change in Unrealized Gain / (Loss)
   18. Ending NAV - Net of Incentive Allocation
   19. Incentive Allocation - Paid During the Period
   20. Accrued Incentive Allocation - Periodic Change
   21. Accrued Incentive Allocation - Ending Period Balance
   22. Ending NAV - Gross of Accrued Incentive Allocation
   23. Total Commitment
   24. Beginning Unfunded Commitment
   25. Plus Recallable Distributions
   26. Less Expired/Released Commitments
   27. +/- Other Unfunded Adjustment
   28. Ending Unfunded Commitment
   
   **KEY**: Look for similar wording. Extract ACTUAL numbers - different for each period!

5. Numbers: Remove $ and commas (e.g., "$1,000,000" becomes 1000000)
6. Percentages: Convert to decimals (e.g., "15.5%" becomes 15.5)
7. Negative numbers in parentheses: "(1000)" becomes -1000
8. Dates: Format as YYYY-MM-DD
9. Missing/blank cells: Use null (not 0)
10. Return ONLY valid JSON (no markdown code blocks, no explanations)

DOCUMENT TEXT:
{extracted_text}

Return JSON with this EXACT structure (fill with ALL data from the document):

{{
  "portfolio_summary": {{
    "general_partner": "extract GP name",
    "fund_name": "extract fund name",
    "fund_currency": "USD or other",
    "reporting_period": "extract period",
    "report_date": "YYYY-MM-DD",
    "fund_inception_date": "YYYY-MM-DD",
    "total_commitments": 0,
    "total_drawdowns": 0,
    "remaining_commitments": 0,
    "total_distributions": 0,
    "net_contributions": 0,
    "assets_under_management": 0,
    "nav": 0,
    "fair_value": 0,
    "active_funds": 0,
    "active_portfolio_companies": 0,
    "total_investments": 0,
    "realized_investments": 0,
    "unrealized_investments": 0,
    "dpi": 0,
    "rvpi": 0,
    "tvpi": 0,
    "irr": 0,
    "moic": 0,
    "north_america_percent": 0,
    "europe_percent": 0,
    "asia_percent": 0,
    "other_region_percent": 0,
    "consumer_goods_percent": 0,
    "it_percent": 0,
    "financials_percent": 0,
    "healthcare_percent": 0,
    "services_percent": 0,
    "industrials_percent": 0,
    "other_industry_percent": 0
  }},
  
  "schedule_of_investments": [
    {{
      "company": "...",
      "fund": "...",
      "reported_date": "YYYY-MM-DD",
      "investment_status": "...",
      "security_type": "...",
      "initial_investment_date": "YYYY-MM-DD",
      "total_invested": 0,
      "current_cost": 0,
      "reported_value": 0,
      "realized_proceeds": 0,
      "fund_ownership_percent": 0,
      "valuation_policy": "...",
      "investment_multiple": 0,
      "irr": 0
    }}
  ],
  
  "statement_of_operations": [
    {{
      "period": "...",
      "portfolio_interest_income": 0,
      "portfolio_dividend_income": 0,
      "total_income": 0,
      "management_fees_net": 0,
      "professional_fees": 0,
      "total_expenses": 0,
      "net_operating_income": 0,
      "net_realized_gain_loss": 0,
      "net_unrealized_gain_loss": 0,
      "net_increase_in_capital": 0
    }}
  ],
  
  "statement_of_cashflows": {{
    "row_1_current": 0, "row_1_prior": 0, "row_1_ytd": 0,
    "row_2_current": 0, "row_2_prior": 0, "row_2_ytd": 0,
    "row_3_current": 0, "row_3_prior": 0, "row_3_ytd": 0,
    "row_4_current": 0, "row_4_prior": 0, "row_4_ytd": 0,
    "row_5_current": 0, "row_5_prior": 0, "row_5_ytd": 0,
    "row_6_current": 0, "row_6_prior": 0, "row_6_ytd": 0,
    "row_7_current": 0, "row_7_prior": 0, "row_7_ytd": 0,
    "row_8_current": 0, "row_8_prior": 0, "row_8_ytd": 0,
    "row_9_current": 0, "row_9_prior": 0, "row_9_ytd": 0,
    "row_10_current": 0, "row_10_prior": 0, "row_10_ytd": 0,
    "row_11_current": 0, "row_11_prior": 0, "row_11_ytd": 0,
    "row_12_current": 0, "row_12_prior": 0, "row_12_ytd": 0,
    "row_13_current": 0, "row_13_prior": 0, "row_13_ytd": 0,
    "row_14_current": 0, "row_14_prior": 0, "row_14_ytd": 0,
    "row_15_current": 0, "row_15_prior": 0, "row_15_ytd": 0,
    "row_16_current": 0, "row_16_prior": 0, "row_16_ytd": 0,
    "row_17_current": 0, "row_17_prior": 0, "row_17_ytd": 0,
    "row_18_current": 0, "row_18_prior": 0, "row_18_ytd": 0,
    "row_19_current": 0, "row_19_prior": 0, "row_19_ytd": 0,
    "row_20_current": 0, "row_20_prior": 0, "row_20_ytd": 0,
    "row_21_current": 0, "row_21_prior": 0, "row_21_ytd": 0,
    "row_22_current": 0, "row_22_prior": 0, "row_22_ytd": 0,
    "row_23_current": 0, "row_23_prior": 0, "row_23_ytd": 0,
    "row_24_current": 0, "row_24_prior": 0, "row_24_ytd": 0,
    "row_25_current": 0, "row_25_prior": 0, "row_25_ytd": 0,
    "row_26_current": 0, "row_26_prior": 0, "row_26_ytd": 0
  }},
    "row_25_current": 0, "row_25_prior": 0, "row_25_ytd": 0,
    "row_26_current": 0, "row_26_prior": 0, "row_26_ytd": 0
  }},
  
  "pcap_statement": {{
    "row_1_current": 0, "row_1_prior": 0, "row_1_ytd": 0,
    "row_2_current": 0, "row_2_prior": 0, "row_2_ytd": 0,
    "row_3_current": 0, "row_3_prior": 0, "row_3_ytd": 0,
    "row_4_current": 0, "row_4_prior": 0, "row_4_ytd": 0,
    "row_5_current": 0, "row_5_prior": 0, "row_5_ytd": 0,
    "row_6_current": 0, "row_6_prior": 0, "row_6_ytd": 0,
    "row_7_current": 0, "row_7_prior": 0, "row_7_ytd": 0,
    "row_8_current": 0, "row_8_prior": 0, "row_8_ytd": 0,
    "row_9_current": 0, "row_9_prior": 0, "row_9_ytd": 0,
    "row_10_current": 0, "row_10_prior": 0, "row_10_ytd": 0,
    "row_11_current": 0, "row_11_prior": 0, "row_11_ytd": 0,
    "row_12_current": 0, "row_12_prior": 0, "row_12_ytd": 0,
    "row_13_current": 0, "row_13_prior": 0, "row_13_ytd": 0,
    "row_14_current": 0, "row_14_prior": 0, "row_14_ytd": 0,
    "row_15_current": 0, "row_15_prior": 0, "row_15_ytd": 0,
    "row_16_current": 0, "row_16_prior": 0, "row_16_ytd": 0,
    "row_17_current": 0, "row_17_prior": 0, "row_17_ytd": 0,
    "row_18_current": 0, "row_18_prior": 0, "row_18_ytd": 0,
    "row_19_current": 0, "row_19_prior": 0, "row_19_ytd": 0,
    "row_20_current": 0, "row_20_prior": 0, "row_20_ytd": 0,
    "row_21_current": 0, "row_21_prior": 0, "row_21_ytd": 0,
    "row_22_current": 0, "row_22_prior": 0, "row_22_ytd": 0,
    "row_23_current": 0, "row_23_prior": 0, "row_23_ytd": 0,
    "row_24_current": 0, "row_24_prior": 0, "row_24_ytd": 0,
    "row_25_current": 0, "row_25_prior": 0, "row_25_ytd": 0,
    "row_26_current": 0, "row_26_prior": 0, "row_26_ytd": 0,
    "row_27_current": 0, "row_27_prior": 0, "row_27_ytd": 0,
    "row_28_current": 0, "row_28_prior": 0, "row_28_ytd": 0
  }},
  
  "portfolio_company_profile": [
    {{
      "company_name": "...",
      "initial_investment_date": "YYYY-MM-DD",
      "industry": "...",
      "headquarters": "...",
      "company_description": "...",
      "fund_ownership_percent": 0,
      "securities_held": "...",
      "investment_commitment": 0,
      "invested_capital": 0,
      "reported_value": 0,
      "investment_multiple": 0,
      "irr": 0,
      "investment_thesis": "...",
      "exit_expectations": "...",
      "recent_events": "...",
      "valuation_methodology": "...",
      "risk_assessment": "..."
    }}
  ],
  
  "portfolio_company_financials": [
    {{
      "company": "...",
      "company_currency": "...",
      "operating_data_date": "YYYY-MM-DD",
      "ltm_revenue": 0,
      "ltm_ebitda": 0,
      "cash": 0,
      "gross_debt": 0,
      "yoy_revenue_growth": 0,
      "ebitda_margin": 0,
      "total_enterprise_value": 0,
      "tev_multiple": 0
    }}
  ],
  
  "footnotes": [
    {{
      "note_number": 0,
      "note_header": "...",
      "description": "..."
    }}
  ],
  
  "reference_values": {{
    "investment_status_types": [],
    "security_types": [],
    "industries": [],
    "currencies": [],
    "valuation_methods": []
  }}
}}

CRITICAL REQUIREMENTS - YOUR JSON MUST INCLUDE ALL THESE SECTIONS:
✓ portfolio_summary (with all 37 fields)
✓ schedule_of_investments (array of companies)
✓ statement_of_operations (array with period data)
✓ statement_of_cashflows (object with row_1_current through row_26_ytd - 78 values total)
✓ pcap_statement (object with row_1_current through row_28_ytd - 84 values total)
✓ portfolio_company_profile (array of companies)
✓ portfolio_company_financials (array of company financials)
✓ footnotes (array of notes)
✓ reference_values (object with arrays)

RESPONSE FORMAT RULES:
1. Your response MUST start with {{ and end with }}
2. Do NOT include any text before or after the JSON
3. Do NOT wrap the JSON in markdown code blocks (```json)
4. Include ALL 9 sections listed above (even if some arrays are empty [])
5. For statement_of_cashflows: MUST have all 78 keys (row_1_current/prior/ytd through row_26_current/prior/ytd)
6. For pcap_statement: MUST have all 84 keys (row_1_current/prior/ytd through row_28_current/prior/ytd)
7. If you cannot find data for a field, use null (not 0, not empty string)
8. Extract ALL tables, ALL companies, ALL financial data

Now extract the data and return ONLY the complete JSON with ALL 9 sections:"""

VALIDATION_PROMPT = """Fix and validate this JSON. Ensure all numeric fields are numbers (not strings), all dates are YYYY-MM-DD format, and structure is correct.

{extracted_data}

Return the corrected JSON only."""

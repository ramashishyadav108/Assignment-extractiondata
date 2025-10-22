"""
Optimized prompt template for extracting structured fund data from PDF reports.
This prompt is designed to work with Google Gemini 2.0 Flash API for accurate data extraction.
"""

EXTRACTION_PROMPT_TEMPLATE = """You are a financial data extraction expert. Extract ALL data from this fund report into a comprehensive JSON structure.

FORMATTING RULES:
- Numbers: no symbols (1000000 not "$1,000,000")
- Percentages: as decimals (15.5 not "15.5%")  
- Dates: YYYY-MM-DD format
- Missing values: use null
- Return ONLY JSON (no markdown, no explanations)

DOCUMENT TEXT:
{extracted_text}

Extract and return JSON with this complete structure (fill ALL fields with actual data from document):

{{
  "portfolio_summary": {{
    "general_partner": "string",
    "ilpa_gp": "string",
    "assets_under_management": "number",
    "active_funds": "number",
    "active_portfolio_companies": "number",
    "fund_summary": {{
      "fund_name": "string",
      "fund_currency": "string",
      "total_commitments": "number",
      "total_drawdowns": "number",
      "remaining_commitments": "number",
      "total_number_of_investments": "number",
      "total_distributions": "number",
      "distributions_as_percent_of_drawdowns": "number",
      "distributions_as_percent_of_commitments": "number"
    }},
    "key_fund_valuation_metrics": {{
      "dpi": "number",
      "rvpi": "number",
      "tvpi": "number"
    }},
    "portfolio_breakdown_by_region": {{
      "north_america": "number",
      "europe": "number",
      "asia": "number"
    }},
    "portfolio_breakdown_by_industry": {{
      "consumer_goods": "number",
      "it": "number",
      "financials": "number",
      "healthcare": "number",
      "services": "number",
      "other": "number"
    }}
  }},
  
  "schedule_of_investments": [
    {{
      "company": "string",
      "fund": "string",
      "reported_date": "YYYY-MM-DD",
      "investment_status": "string",
      "security_type": "string",
      "number_of_shares": "number",
      "fund_ownership_percent": "number",
      "initial_investment_date": "YYYY-MM-DD",
      "fund_commitment": "number",
      "total_invested": "number",
      "current_cost": "number",
      "reported_value": "number",
      "realized_proceeds": "number",
      "lp_ownership_percent_fully_diluted": "number",
      "final_exit_date": "YYYY-MM-DD or null",
      "valuation_policy": "string",
      "period_change_in_valuation": "number",
      "period_change_in_cost": "number",
      "unrealized_gains_losses": "number",
      "movement_summary": "string",
      "current_quarter_investment_multiple": "number",
      "prior_quarter_investment_multiple": "number",
      "since_inception_irr": "number"
    }}
  ],
  
  "statement_of_operations": [
    {{
      "period": "string",
      "portfolio_interest_income": "number",
      "portfolio_dividend_income": "number",
      "other_interest_earned": "number",
      "total_income": "number",
      "management_fees_net": "number",
      "broken_deal_fees": "number",
      "interest": "number",
      "professional_fees": "number",
      "bank_fees": "number",
      "advisory_directors_fees": "number",
      "insurance": "number",
      "total_expenses": "number",
      "net_operating_income_deficit": "number",
      "net_realized_gain_loss_on_investments": "number",
      "net_change_in_unrealized_gain_loss_on_investments": "number",
      "net_realized_gain_loss_due_to_fx": "number",
      "net_realized_and_unrealized_gain_loss_on_investments": "number",
      "net_increase_decrease_in_partners_capital": "number"
    }}
  ],
  
  "statement_of_cashflows": [
    {{
      "description": "string",
      "amount": "number"
    }}
  ],
  
  "pcap_statement": [
    {{
      "description": "string",
      "amount": "number"
    }}
  ],
  
  "portfolio_company_profile": [
    {{
      "company_name": "string",
      "initial_investment_date": "YYYY-MM-DD",
      "industry": "string",
      "headquarters": "string",
      "company_description": "string",
      "fund_ownership_percent": "number",
      "investor_group_ownership_percent": "number",
      "enterprise_valuation_at_closing": "number",
      "securities_held": "string",
      "ticker_symbol": "string or null",
      "investor_group_members": "string",
      "management_ownership_percent": "number",
      "board_representation": "string",
      "board_members": "string",
      "investment_commitment": "number",
      "invested_capital": "number",
      "reported_value": "number",
      "realized_proceeds": "number",
      "investment_multiple": "number",
      "gross_irr": "number",
      "investment_background": "string",
      "initial_investment_thesis": "string",
      "exit_expectations": "string",
      "recent_events_key_initiatives": "string",
      "company_assessment": "string",
      "valuation_methodology": "string",
      "risk_assessment_update": "string"
    }}
  ],
  
  "portfolio_company_financials": [
    {{
      "company": "string",
      "company_currency": "string",
      "operating_data_date": "YYYY-MM-DD",
      "data_type": "string",
      "ltm_revenue": "number",
      "ltm_ebitda": "number",
      "cash": "number",
      "book_value": "number",
      "gross_debt": "number",
      "debt_1_year": "number",
      "debt_2_years": "number",
      "debt_3_years": "number",
      "debt_4_years": "number",
      "debt_5_years": "number",
      "debt_after_5_years": "number",
      "yoy_percent_growth_revenue": "number",
      "ltm_ebitda_pro_forma": "number",
      "yoy_percent_growth_ebitda": "number",
      "ebitda_margin": "number",
      "total_enterprise_value": "number",
      "tev_multiple": "number",
      "total_leverage": "number",
      "total_leverage_multiple": "number"
    }}
  ],
  
  "footnotes": [
    {{
      "note_number": "number",
      "note_header": "string",
      "operating_data_date": "YYYY-MM-DD or null",
      "description": "string"
    }}
  ],
  
  "reference_values": {{
    "fund_status": ["string"],
    "region": ["string"],
    "currency": ["string"],
    "country": ["string"],
    "legal_form": ["string"],
    "strategy": ["string"],
    "geography_focus": ["string"],
    "sector_focus": ["string"],
    "fees_based_on_before": ["string"],
    "fees_based_on_after": ["string"],
    "management_fees_call_frequency": ["string"],
    "fund_other_info_country": ["string"],
    "valuation_methods": ["string"],
    "multiple_types": ["string"],
    "methods_of_exit": ["string"],
    "exit_styles": ["string"],
    "fixed_or_floating_rate": ["string"],
    "instrument_type": ["string"],
    "deal_sources": ["string"],
    "deal_styles": ["string"],
    "deal_types": ["string"],
    "value_driver_types": ["string"],
    "controls_in_deal": ["string"],
    "investment_status": ["string"],
    "company_type": ["string"]
  }}
}}

**EXTRACTION GUIDELINES:**

1. **Portfolio Summary**: Extract from the summary/overview section
2. **Schedule of Investments**: List ALL portfolio companies with their details
3. **Statement of Operations**: Extract income statement line items by period
4. **Statement of Cashflows**: Extract cash flow statement line items
5. **PCAP Statement**: Extract partnership capital account statement items
6. **Portfolio Company Profile**: Detailed profile for EACH company
7. **Portfolio Company Financials**: Financial metrics for each company
8. **Footnotes**: Extract all footnotes with their references
9. **Reference Values**: Extract unique values found in the document for dropdowns

**NUMERIC HANDLING:**
- Negative numbers: use negative sign (e.g., -1000, not (1000))
- Percentages: store as numbers (e.g., 15.5 for 15.5%)
- Currency: remove symbols, store as numbers
- Missing data: use null

**DATE HANDLING:**
- Convert all dates to ISO format: YYYY-MM-DD
- Quarter ending dates: use the last day of that quarter
- If only year/quarter provided, estimate end date

Return ONLY the JSON object, nothing else."""

VALIDATION_PROMPT = """Please validate and clean the following extracted JSON data. Ensure:
1. All numeric fields contain valid numbers or null
2. All dates are in YYYY-MM-DD format or null
3. All required fields are present
4. Arrays are properly formatted
5. No undefined or invalid values

Original extracted data:
{extracted_data}

Return the cleaned and validated JSON."""

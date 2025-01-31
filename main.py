import requests
import pandas as pd
import streamlit as st

# API-Schlüssel und Basis-URL
API_KEY = st.secrets["api_keys"]["my_api_key"] # Ersetze dies mit deinem API-Schlüssel
BASE_URL = "https://financialmodelingprep.com/api/v3"

# Liste der relevanten Kennzahlen aus dem Excel-Dokument
RELEVANT_METRICS = [
    "priceEarningsRatio",  # KGV (Kurs-Gewinn-Verhältnis)
    "priceToFreeCashFlowRatio",  # KCV (Kurs-Cashflow-Verhältnis)
    "priceToBookRatio",  # KBV (Kurs-Buchwert-Verhältnis)
    "pegRatio",  # PEG-Ratio
    "dividendYield",  # Dividendenrendite
    "returnOnEquity",  # ROE (Return on Equity)
    "operatingCashFlowPerShare",  # Cashflow pro Aktie
    "freeCashFlowPerShare",  # Free Cashflow pro Aktie
    "currentRatio",  # Current Ratio
    "debtEquityRatio",  # Debt-to-Equity-Ratio
    "interestCoverage",  # Zinsdeckungsgrad
    "revenueGrowth",  # Umsatzwachstum
    "netIncomeGrowth",  # Gewinnwachstum
    "cashFlowGrowth",  # Cashflow-Wachstum
    "beta",  # Beta (Volatilität)
]


# Define get_stock_price function
def get_stock_price(symbol):
    url = f"{BASE_URL}/quote/{symbol}?apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]['price']  # Return the current price
        else:
            print(f"No price data found for {symbol}.")
            return None
    else:
        print(f"Error fetching price data: {response.status_code}")
        return None

# Define get_data function
def get_data(url):
    response = requests.get(url)
    return response.json()[0] if response.status_code == 200 and response.json() else None

# Define get_financial_data function
def get_financial_data(symbol):
    # Collect all necessary data
    price = get_stock_price(symbol)
    ratios = get_data(f"{BASE_URL}/ratios/{symbol}?apikey={API_KEY}")
    income = get_data(f"{BASE_URL}/income-statement/{symbol}?limit=1&apikey={API_KEY}")
    balance = get_data(f"{BASE_URL}/balance-sheet-statement/{symbol}?limit=1&apikey={API_KEY}")
    cash_flow = get_data(f"{BASE_URL}/cash-flow-statement/{symbol}?limit=1&apikey={API_KEY}")
    growth_data = get_data(f"{BASE_URL}/income-statement/{symbol}?limit=2&apikey={API_KEY}")
    
    # Fetch the date from the most recent financial statement
    date = None
    if income:
        date = income.get('date')
    elif balance:
        date = balance.get('date')
    elif cash_flow:
        date = cash_flow.get('date')
    
    return price, ratios, income, balance, cash_flow, growth_data, date

# Define calculate_missing_metrics function
def calculate_missing_metrics(symbol, relevant_data, price, income, balance, cash_flow, growth_data):
    # Helper values
    shares_outstanding = (income.get('weightedAverageShsOut') if income else None) or (balance.get('commonStockSharesOutstanding') if balance else None)
    
    # Price-based ratios
    if relevant_data.get('priceEarningsRatio') == 'N/A' and price and income:
        eps = income.get('epsdiluted') or income.get('eps')
        if eps and eps != 0: relevant_data['priceEarningsRatio'] = price / eps
        
    if relevant_data.get('priceToBookRatio') == 'N/A' and price and balance and shares_outstanding:
        book_value = balance.get('totalStockholdersEquity')
        if book_value and shares_outstanding != 0:
            relevant_data['priceToBookRatio'] = price / (book_value / shares_outstanding)
    
    # Cash flow metrics
    if cash_flow:
        if relevant_data.get('priceToFreeCashFlowRatio') == 'N/A' and price and shares_outstanding:
            fcfe = cash_flow.get('freeCashFlow')
            if fcfe and shares_outstanding != 0:
                relevant_data['priceToFreeCashFlowRatio'] = price / (fcfe / shares_outstanding)
        
        if relevant_data.get('operatingCashFlowPerShare') == 'N/A' and shares_outstanding:
            ocf = cash_flow.get('operatingCashFlow')
            if ocf: relevant_data['operatingCashFlowPerShare'] = ocf / shares_outstanding
    
    # Balance sheet metrics
    if balance:
        if relevant_data.get('currentRatio') == 'N/A':
            current_assets = balance.get('totalCurrentAssets')
            current_liabs = balance.get('totalCurrentLiabilities')
            if current_assets and current_liabs:
                relevant_data['currentRatio'] = current_assets / current_liabs
                
        if relevant_data.get('debtEquityRatio') == 'N/A':
            debt = balance.get('totalDebt')
            equity = balance.get('totalStockholdersEquity')
            if debt and equity and equity != 0:
                relevant_data['debtEquityRatio'] = debt / equity
    
    return relevant_data

# Define get_financial_ratios function
def get_financial_ratios(symbol):
    price, ratios, income, balance, cash_flow, growth_data, date = get_financial_data(symbol)
    if not ratios:
        print(f"No ratio data found for {symbol}")
        return None, None
    
    relevant_data = {metric: ratios.get(metric, "N/A") for metric in RELEVANT_METRICS}
    relevant_data = calculate_missing_metrics(symbol, relevant_data, price, income, balance, cash_flow, growth_data)
    
    return pd.DataFrame([relevant_data]),date

def compare_with_target_values(df):
    """
    Vergleicht Finanzkennzahlen eines DataFrames mit definierten Zielwerten.
    
    Parameter:
    df (pd.DataFrame): DataFrame mit den Spalten der Finanzkennzahlen.
    
    Rückgabe:
    pd.DataFrame: DataFrame mit booleschen Werten, die anzeigen, ob Zielwerte erfüllt sind.
    """
    # Definition der Zielwerte und Vergleichsoperationen
    target_config = {
        "beta": {"target": 1, "op": "lt"},        # Beta < 1
        "cashFlowGrowth": {"target": 5, "op": "gt"},  # > 5 %
        "netIncomeGrowth": {"target": 5, "op": "gt"},
        "revenueGrowth": {"target": 5, "op": "gt"},
        "pegRatio": {"target": 1, "op": "lt"},
        "priceToBookRatio": {"target": 1, "op": "lt"},
        "priceEarningsRatio": {"target": 15, "op": "lt"},
        "priceToFreeCashFlowRatio": {"target": 10, "op": "lt"},
        "debtEquityRatio": {"target": 0.5, "op": "lt"},
        "returnOnEquity": {"target": 10, "op": "gt"},
        "currentRatio": {"target": 1.5, "op": "gt"},
        "dividendYield": {"target": 3, "op": "gt"},
        "interestCoverage": {"target": 3, "op": "gt"}
    }

    # Konvertiere alle relevanten Spalten in numerische Werte
    numeric_columns = list(target_config.keys())
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce")

    # DataFrame für Ergebnisse
    results = pd.DataFrame(index=df.index)

    # Führe Vergleiche vektorisiert durch
    for col, config in target_config.items():
        target = config["target"]
        op = config["op"]
        
        if op == "lt":
            results[f"{col}_Erfüllt"] = df[col] < target
        elif op == "gt":
            results[f"{col}_Erfüllt"] = df[col] > target

    # Kennzeichne NaN-Werte explizit
    results = results.where(df[numeric_columns].notna().all(axis=1), other="Daten fehlerhaft")

    return results
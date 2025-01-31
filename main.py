import requests
import pandas as pd

# API-Schlüssel und Basis-URL
API_KEY = "ef5TkFN4ie3aTKWdVwwrvTvrjoR9eJDz"  # Ersetze dies mit deinem API-Schlüssel
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

# Funktion zum Abrufen von Finanzkennzahlen
def get_financial_ratios(symbol):
    url = f"{BASE_URL}/ratios/{symbol}?apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            # Filtere nur die relevanten Kennzahlen
            relevant_data = {key: data[0].get(key, "N/A") for key in RELEVANT_METRICS}
            return relevant_data
        else:
            print(f"Keine Daten für {symbol} gefunden.")
            return None
    else:
        print(f"Fehler bei der API-Anfrage: {response.status_code}")
        return None

# Funktion zum Abrufen des Aktienkurses
def get_stock_price(symbol):
    url = f"{BASE_URL}/quote/{symbol}?apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]['price']  # Rückgabe des aktuellen Preises
        else:
            print(f"Keine Preisinformationen für {symbol} gefunden.")
            return None
    else:
        print(f"Fehler bei der API-Anfrage: {response.status_code}")
        return None

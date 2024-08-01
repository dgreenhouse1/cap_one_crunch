import tabula
import re
import pandas as pd

def extract_transaction(row):
    # Extract the transaction date, post date, and merchant name from the row
    dates = re.findall(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d+)', row)
    if dates:
        if len(dates) >= 1:
            trans_date = dates[0]
        if len(dates) >= 2:
            post_date = dates[1]

    row = row.replace(trans_date, "", 1)
    row = row.replace(post_date, "", 1)
    merchant_name_match = re.match(r'([^$]+)', row)
    if merchant_name_match:
        merchant_name = merchant_name_match.group(0)
        row = row.replace(merchant_name, "", 1)

    amount_match = re.match(r'\$[\d,.]+', row)
    if amount_match:
        amount_str = amount_match.group(0)
        amount_str = amount_str.replace(',', '')
        amount_str = amount_str.replace('$', '')
        amount = float(amount_str)
        row = row.replace(amount_match.group(0)+'\r', "", 1)
    else:
        amount = None

    foreign_currency_amount_match = re.match(r'\$[\d,.]+', row)
    if foreign_currency_amount_match:
        foreign_currency_amount_str = foreign_currency_amount_match.group(0)
        foreign_currency_amount_str = foreign_currency_amount_str.replace(',', '')
        foreign_currency_amount_str = foreign_currency_amount_str.replace('$', '')
        foreign_currency_amount = float(foreign_currency_amount_str)
        row = row.replace(foreign_currency_amount_match.group(0)+'\r', "", 1)
    else:
        foreign_currency_amount = None

    foreign_currency_match = re.match(r'[A-Z]{3}', row)
    if foreign_currency_match:
        foreign_currency = foreign_currency_match.group(0)
        row = row.replace(foreign_currency+'\r', "", 1)
    else:
        foreign_currency = None

    exchange_rate_match = re.match(r'[\d,.]+', row)
    if exchange_rate_match:
        exchange_rate = float(exchange_rate_match.group(0))
    else:
        exchange_rate = None
    



    transaction = {
        "transaction_date": trans_date,
        "post_date": post_date,
        "merchant_name": merchant_name,
        "amount": amount,
        "foreign_currency_amount": foreign_currency_amount,
        "foreign_currency": foreign_currency,
        "exchange_rate": exchange_rate
    }

    return transaction

#sample_table_text = """DAVID L GREENHOUSE #3554: Payments, Credits and Adjustments\rTrans DatePost DateDescriptionAmount\rJul 1Jul 1CAPITAL ONE AUTOPAY PYMTAuthDate 01-Jul- $52.00\rDAVID L GREENHOUSE #3554: Transactions\rTrans DatePost DateDescriptionAmount\rJun 7Jun 8www.bueromarkt-ag.deZoellnitzDEU$62.22\r$57.06\rEUR\r0.917068467 Exchange Rate\rJun 8Jun 10Lidl sagt DankeBerlin$75.11\r$68.88\rEUR\r0.917054986 Exchange Rate\rJun 10Jun 11Lidl sagt DankeBerlin$4.51\r$4.14\rEUR\r0.917960089 Exchange Rate\rJun 10Jun 11DM-Drogerie MarktBerlin$17.24\r$15.81\rEUR\r0.917053364 Exchange Rate\rJun 11Jun 12Lidl sagt DankeBerlin$23.94\r$22.17\rEUR\r0.926065163 Exchange Rate\rJun 14Jun 15Lidl sagt DankeBerlin$13.01\r$11.99\rEUR\r0.921598770 Exchange Rate\rJun 14Jun 15DM Drogerie MarktBerlin$12.59\r$11.60\rEUR\r0.921366164 Exchange Rate\rJun 15Jun 17Lidl sagt DankeBerlin$51.33\r$47.71\rEUR\r0.929475940 Exchange Rate\rJun 16Jun 17Northe  178106Stockholm$11.86\r$11.02\rEUR\r0.929173693 Exchange Rate\rJun 17Jun 19ProfitroomPoznanPOL$795.22\r$3,227.40\rPLN\r4.058499535 Exchange Rate"""


# Path to the PDF file
pdf_path = "/Users/dgreenhouse/Downloads/Statement_072024_3554.pdf"

# Lists to store the tables and transactions
tables = []
transactions = []

# Read all tables from each page of the PDF
all_tables = tabula.read_pdf(pdf_path, pages="all", lattice=True)

# Add each table to the "tables" list
for table in all_tables:
    print("entering loop")
    # Get the rows from the table
    rows = table.values.tolist()
    for r in rows:

        r = re.sub(r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b)', r'\t\1', r)
        r_split = r.split("\t")

        # Parse forwards until a line with "Transactions" is found
        while r_split[0].find("Transactions") == -1:
            r_split = r_split[1:]
        # Remove the first row, which does not contain transaction data
        r_split = r_split[1:]

        for row in r_split:
            my_transaction = extract_transaction(row)
            transactions.append(my_transaction)

transaction_df = pd.DataFrame(transactions)
transaction_df.to_csv("/Users/dgreenhouse/transactions.csv")



    
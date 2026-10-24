import csv, json

divs = []

# T212 CSV
t212_path = r"C:\Zpersonal\luka\dionice\dividende\06.2026\trading-account-statement_2024-05-01_2026-06-15_en-us_baeae1 - trading-account-statement_2024-05-01_2026-06-15_en-us_baeae1.csv"
with open(t212_path, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        typ = row['Type'].strip()
        if typ != 'DIVIDEND':
            continue
        ticker = row['Ticker'].strip()
        date = row['Date'][:10]
        total = row['Total Amount'].strip()
        fx = float(row['FX Rate'].strip())
        cur, amt = total.split()
        amt = float(amt)
        if cur in ('USD', 'GBP'):
            amount_eur = round(amt / fx, 2)
        else:
            amount_eur = round(amt, 2)
        divs.append({'date': date, 'ticker': ticker, 'amount': amount_eur, 'broker': 't212'})

print(f"T212: {len(divs)} dividends")

# IBKR CSV
ibkr_path = r"C:\Zpersonal\luka\dionice\dividende\06.2026\U15293540_20260401_20260612 (1).csv"
ibkr_divs = []
cur_group = []
cur_currency = None
group_total_native = 0.0

with open(ibkr_path, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) < 6 or row[0] != 'Dividends' or row[1] != 'Data':
            continue
        currency = row[2].strip()
        if currency == 'Total Dividends in EUR':
            continue
        if currency == 'Total in EUR':
            eur_total = float(row[5])
            if cur_currency and cur_currency != 'EUR' and group_total_native:
                rate = eur_total / group_total_native
                for d in cur_group:
                    d['amount'] = round(d.pop('_native') * rate, 2)
                    ibkr_divs.append(d)
            cur_group = []
            cur_currency = None
            group_total_native = 0.0
            continue
        if currency == 'Total':
            group_total_native = float(row[5])
            if cur_currency == 'EUR':
                ibkr_divs.extend(cur_group)
                cur_group = []
                cur_currency = None
                group_total_native = 0.0
            continue
        date = row[3].strip()
        desc = row[4].strip()
        native = float(row[5])
        ticker = desc.split('(')[0].strip()
        cur_currency = currency
        if currency == 'EUR':
            cur_group.append({'date': date, 'ticker': ticker, 'amount': round(native, 2), 'broker': 'ibkr'})
        else:
            cur_group.append({'date': date, 'ticker': ticker, '_native': native, 'broker': 'ibkr'})

print(f"IBKR: {len(ibkr_divs)} dividends")
for d in ibkr_divs:
    print(f"  {d['date']} {d['ticker']:10s} EUR {d['amount']:.2f}")

# IBKR entries missing from the CSV (visible in full statement screenshot)
# GBP rate 321.66/279.60=1.1505, USD rate 49.83/58.12=0.8574
ibkr_missing = [
    {'date': '2025-09-22', 'ticker': 'D',    'amount': round(2.67  * 0.8574, 2), 'broker': 'ibkr'},
    {'date': '2025-09-24', 'ticker': 'EUNY', 'amount': round(24.02 * 0.8574, 2), 'broker': 'ibkr'},
    {'date': '2025-11-14', 'ticker': 'TW.',  'amount': round(39.70 * 1.1505, 2), 'broker': 'ibkr'},
    {'date': '2025-12-20', 'ticker': 'D',    'amount': round(2.67  * 0.8574, 2), 'broker': 'ibkr'},
    {'date': '2025-12-24', 'ticker': 'EUNY', 'amount': round(8.66  * 0.8574, 2), 'broker': 'ibkr'},
    {'date': '2026-03-20', 'ticker': 'D',    'amount': round(2.67  * 0.8574, 2), 'broker': 'ibkr'},
]
ibkr_divs.extend(ibkr_missing)
print(f"IBKR missing added: {len(ibkr_missing)}")

# Croatian manual - single entry
divs_croatian = [{'date': '2026-06-15', 'ticker': 'HT-RA', 'amount': 150.0, 'broker': 'zse'}]

all_divs = sorted(divs + ibkr_divs + divs_croatian, key=lambda d: d['date'])
print(f"\nTotal: {len(all_divs)} dividend entries")
print(f"Sum: EUR {sum(d['amount'] for d in all_divs):.2f}")

js = json.dumps(all_divs)
out = r"C:\Users\lpodobnik\Claude\Tickers\import_dividends.js"
with open(out, "w", encoding='utf-8') as f:
    f.write(f"const newDivs = {js};\n")
    f.write("const existing = JSON.parse(localStorage.getItem('pf_dividends') || '[]');\n")
    f.write("const merged = [...existing, ...newDivs];\n")
    f.write("localStorage.setItem('pf_dividends', JSON.stringify(merged));\n")
    f.write("console.log('Imported', newDivs.length, 'dividends. Total now:', merged.length);\n")
    f.write("location.reload();\n")
print(f"Written to {out}")

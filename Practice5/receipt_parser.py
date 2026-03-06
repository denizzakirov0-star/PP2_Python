import re
import json

with open("raw.txt", "r", encoding="utf-8") as f:
    text = f.read()

prices = re.findall(r"\d[\d ]*,\d{2}", text)

prices = [p.replace(" ", "") for p in prices]

product_pattern = r"\d+\.\n([^\n]+)"
products = re.findall(product_pattern, text)

total_match = re.search(r"OWERALL:\s*\n?\s*([\d ]+,\d{2})", text)
total = total_match.group(1) if total_match else None

datetime_match = re.search(r"\d{2}\.\d{2}\.\d{4}\s\d{2}:\d{2}:\d{2}", text)
datetime_value = datetime_match.group() if datetime_match else None

payment_match = re.search(r"(Bank Card|Cash)", text)
payment_method = payment_match.group() if payment_match else None

data = {
    "products": products,
    "prices": prices,
    "total": total,
    "datetime": datetime_value,
    "payment_method": payment_method
}

print(json.dumps(data, indent=4, ensure_ascii=False))
import csv

filepath = 'MASTER_BD_ENRICHED.csv'
batch_path = 'batch6_50.csv'

# Load existing data
all_data = []
with open(filepath, 'r', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = list(reader.fieldnames)
    for row in reader:
        all_data.append(row)

# Load batch data
new_batch = []
with open(batch_path, 'r', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        new_batch.append(row)

# Append and deduplicate
seen = set([row['Company'].lower() for row in all_data])
for row in new_batch:
    if row['Company'].lower() not in seen:
        item = {col: '' for col in fieldnames}
        item.update(row)
        all_data.append(item)
        seen.add(row['Company'].lower())

# Write back
with open(filepath, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_data)

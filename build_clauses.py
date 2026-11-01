
import json
from pathlib import Path

from app.clause_extractor import extract_clauses

INPUT_FILES = [
    "tec_33010_2025_iot_gateway.json",
    "tec_48060_2026_lan_switch.json",
    "tec_67010_2026.json",
    "tec_93009_2024_mtcte_procedure_v3.json",
]

input_folder = Path("data/processed")
output_file = input_folder / "clauses.json"

all_clauses = []

for filename in INPUT_FILES:
    file_path = input_folder / filename

    if not file_path.exists():
        print(f"File not found: {filename}")
        continue

    with open(file_path, encoding="utf-8") as file:
        pages = json.load(file)

    document_count = 0

    for page in pages:
        clauses = extract_clauses(
            page["text"],
            page["document_id"],
            page["page_number"]
        )

        all_clauses.extend(clauses)
        document_count += len(clauses)

    print(f"{filename}: {document_count} clauses")

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(all_clauses, file, indent=2, ensure_ascii=False)

print("\nTotal clauses:", len(all_clauses))
print("Saved to:", output_file)

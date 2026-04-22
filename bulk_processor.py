import csv
from prompt import build_prompt

def process_csv(file_path, product):

    results = []

    with open(file_path, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            prompt = build_prompt(
                row["name"],
                row["role"],
                row["company"],
                row["industry"],
                product,
                "professional"
            )

            results.append({
                "name": row["name"],
                "prompt": prompt
            })

    return results

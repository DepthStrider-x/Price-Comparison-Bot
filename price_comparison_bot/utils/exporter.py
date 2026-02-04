import pandas as pd
import json
import os

def export_results(results, output_dir="data"):
    """
    Exports the results to JSON, CSV, and Excel.
    results: List of normalized product dictionaries.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # JSON Export (The definitive source)
    json_path = os.path.join(output_dir, "combined_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Tabular Export (CSV/Excel)
    if results:
        df = pd.DataFrame(results)
        
        # Reorder columns if possible for better readability
        preferred_order = ["site", "title", "price", "recommended", "url"]
        columns = [c for c in preferred_order if c in df.columns] + [c for c in df.columns if c not in preferred_order]
        df = df[columns]

        csv_path = os.path.join(output_dir, "results.csv")
        df.to_csv(csv_path, index=False)

        xlsx_path = os.path.join(output_dir, "results.xlsx")
        df.to_excel(xlsx_path, index=False)
    else:
        # Create empty files if no results
        pd.DataFrame().to_csv(os.path.join(output_dir, "results.csv"))
        pd.DataFrame().to_excel(os.path.join(output_dir, "results.xlsx"))

    return json_path

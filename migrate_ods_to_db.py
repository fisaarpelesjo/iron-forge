"""One-time migration: import TREINOS sheet from ODS into SQLite."""

import re
import zipfile
from pathlib import Path

import db_ops

ODS_PATH = Path(__file__).parent / "log-de-treino-e-progressao.ods"


def parse_treinos():
    with zipfile.ZipFile(ODS_PATH) as z:
        content = z.read("content.xml").decode("utf-8")

    m = re.search(r'<table:table table:name="TREINOS"', content)
    if not m:
        raise RuntimeError("TREINOS table not found in ODS")
    start = m.start()
    end = content.find("</table:table>", start) + len("</table:table>")
    chunk = content[start:end]

    rows = []
    for row_m in re.finditer(r"<table:table-row", chunk):
        row_end = chunk.find("</table:table-row>", row_m.start()) + len("</table:table-row>")
        row_xml = chunk[row_m.start():row_end]
        if 'office:value-type="date"' not in row_xml:
            continue

        cells = []
        for cm in re.finditer(
            r"<table:table-cell([^>]*?)(?:/>|>(.*?)</table:table-cell>)",
            row_xml,
            re.DOTALL,
        ):
            attrs = cm.group(1)
            d = re.search(r'office:date-value="([^"]*)"', attrs)
            v = re.search(r'office:value="([^"]*)"', attrs)
            t = re.search(r"<text:p>([^<]*)</text:p>", cm.group(0))
            repeated = re.search(r'table:number-columns-repeated="(\d+)"', attrs)
            n = int(repeated.group(1)) if repeated else 1
            val = (d or v or t)
            val = val.group(1).strip() if val else None
            cells.extend([val] * min(n, 20))
            if len(cells) >= 8:
                break

        if len(cells) < 6:
            continue

        date_val = cells[0]       # YYYY-MM-DD
        training_type = cells[2]  # "TREINO"
        exercise_name = cells[3]
        sets_str = cells[4]
        reps_str = cells[5]
        weight_str = cells[6] if len(cells) > 6 else None
        rpe_str = cells[7] if len(cells) > 7 else None

        if not exercise_name or not date_val:
            continue

        row = {
            "date": date_val,
            "training_type": training_type or "TREINO",
            "exercise_name": exercise_name,
            "sets": int(float(sets_str)) if sets_str else 0,
            "reps": int(float(reps_str)) if reps_str else 0,
        }
        if weight_str:
            try:
                w = float(weight_str.replace(",", "."))
                if w > 0:
                    row["weight"] = w
            except ValueError:
                pass
        if rpe_str:
            try:
                row["rpe"] = float(rpe_str.replace(",", "."))
            except ValueError:
                pass

        rows.append(row)

    return rows


if __name__ == "__main__":
    print("Parsing ODS TREINOS sheet...")
    rows = parse_treinos()
    print(f"Found {len(rows)} rows")

    if not rows:
        print("Nothing to import.")
    else:
        db_ops.import_log_rows(rows)
        print("Import complete.")

        weights = db_ops.get_last_weights()
        print(f"\nLast weight per exercise ({len(weights)} exercises):")
        for name, w in sorted(weights.items()):
            print(f"  {name}: {w}kg")

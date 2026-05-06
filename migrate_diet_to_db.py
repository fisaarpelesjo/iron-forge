"""One-time migration: import ALIMENTOS and DIETA sheets from ODS into SQLite."""

import re
import zipfile
from pathlib import Path

import db_ops

ODS_PATH = Path(__file__).parent / "log-de-treino-e-progressao.ods"

MEAL_HEADERS = {"Refeição", "Refeição", "Refei??o"}
META_HEADERS = {"Densidade_meta", "Proteina_meta", "Densidade_calórica", "Densidade_cal?rica"}


def _parse_rows(table_xml, max_cols=16):
    rows = []
    for row_m in re.finditer(r"<table:table-row", table_xml):
        row_end = table_xml.find("</table:table-row>", row_m.start()) + len("</table:table-row>")
        row_xml = table_xml[row_m.start():row_end]
        cells = []
        for cm in re.finditer(
            r"<table:table-cell([^>]*?)(?:/>|>(.*?)</table:table-cell>)",
            row_xml, re.DOTALL,
        ):
            attrs = cm.group(1)
            d = re.search(r'office:date-value="([^"]*)"', attrs)
            v = re.search(r'office:value="([^"]*)"', attrs)
            t = re.search(r"<text:p>([^<]*)</text:p>", cm.group(0))
            repeated = re.search(r'table:number-columns-repeated="(\d+)"', attrs)
            n = int(repeated.group(1)) if repeated else 1
            val = (d or v or t)
            val = val.group(1).strip() if val else None
            if n > 100:
                cells.append(val)
                break
            cells.extend([val] * n)
            if len(cells) >= max_cols:
                break
        if any(c for c in cells if c):
            rows.append(cells)
    return rows


def _extract_table(content, name):
    m = re.search(rf'<table:table table:name="{re.escape(name)}"', content)
    if not m:
        raise RuntimeError(f"Table '{name}' not found")
    start = m.start()
    end = content.find("</table:table>", start) + len("</table:table>")
    return content[start:end]


def _f(val, default=0.0):
    if val is None:
        return default
    try:
        return float(str(val).replace(",", "."))
    except ValueError:
        return default


def migrate_alimentos(content):
    print("Migrating ALIMENTOS...")
    chunk = _extract_table(content, "ALIMENTOS")
    rows = _parse_rows(chunk)
    count = 0
    for row in rows:
        if not row or not row[0] or row[0] == "Alimento":
            continue
        name = row[0]
        unit = row[1] or "g"
        serving_g = _f(row[2], 100)
        db_ops.upsert_food(
            name=name, unit=unit, serving_g=serving_g,
            protein_g=_f(row[3]), carbo_g=_f(row[4]), fat_g=_f(row[5]),
            calories=_f(row[6]), fiber_g=_f(row[7]), omega3_g=_f(row[8]),
            potassium_mg=_f(row[9]), magnesium_mg=_f(row[10]),
            zinc_mg=_f(row[11]), vitamin_d_ui=_f(row[12]),
        )
        count += 1
    print(f"  {count} foods imported.")


def migrate_dieta(content):
    print("Migrating DIETA...")
    chunk = _extract_table(content, "DIETA")
    rows = _parse_rows(chunk, max_cols=16)

    # Targets: second non-empty row (index 1) has values at [1..11]
    # [None, densidade, proteina, carbo, gordura, calorias, fibra, omega3, potassio, magnesio, zinco, vitd]
    targets_row = None
    for row in rows:
        if row and row[0] is None and row[1] and any(
            c for c in row[2:] if c and c not in META_HEADERS
        ):
            try:
                _f(row[1])  # Densidade value
                targets_row = row
                break
            except Exception:
                pass

    if targets_row:
        db_ops.set_diet_targets(
            protein_g=_f(targets_row[2]),
            carbo_g=_f(targets_row[3]),
            fat_g=_f(targets_row[4]),
            calories=_f(targets_row[5]),
            fiber_g=_f(targets_row[6]),
            omega3_g=_f(targets_row[7]),
            potassium_mg=_f(targets_row[8]),
            magnesium_mg=_f(targets_row[9]),
            zinc_mg=_f(targets_row[10]),
            vitamin_d_ui=_f(targets_row[11]),
        )
        print(f"  Targets: protein={_f(targets_row[2])}g  carbo={_f(targets_row[3])}g  "
              f"fat={_f(targets_row[4])}g  cal={_f(targets_row[5])}")
    else:
        print("  WARNING: could not find targets row.")

    # Meal entries: rows where cells[0] is a meal name (not None, not a header label)
    skip_col0 = {None, "Refeição", "Refeição", "Refei??o"}
    sort_idx = 0
    count = 0
    for row in rows:
        meal = row[0] if row else None
        if not meal or meal in skip_col0:
            continue
        food_name = row[1] if len(row) > 1 else None
        qty_str = row[2] if len(row) > 2 else None
        if not food_name or not qty_str:
            continue
        try:
            qty = float(qty_str)
        except ValueError:
            continue

        food = db_ops.get_food_by_name(food_name)
        if food is None:
            print(f"  WARNING: food '{food_name}' not found in foods table — skipping.")
            continue

        db_ops.add_diet_entry(meal, food["id"], qty, sort_idx)
        sort_idx += 1
        count += 1

    print(f"  {count} diet entries imported.")


if __name__ == "__main__":
    with zipfile.ZipFile(ODS_PATH) as z:
        content = z.read("content.xml").decode("utf-8")

    migrate_alimentos(content)
    migrate_dieta(content)

    print("\nDone. Totals check:")
    result = db_ops.get_diet_totals()
    t = result["totals"]
    g = result["targets"]
    print(f"  Protein:   {t['protein_g']:.1f}g  (target: {g['protein_g'] if g else '?'})")
    print(f"  Carbo:     {t['carbo_g']:.1f}g  (target: {g['carbo_g'] if g else '?'})")
    print(f"  Fat:       {t['fat_g']:.1f}g  (target: {g['fat_g'] if g else '?'})")
    print(f"  Calories:  {t['calories']:.0f}  (target: {g['calories'] if g else '?'})")
    print(f"  Fiber:     {t['fiber_g']:.1f}g  (target: {g['fiber_g'] if g else '?'})")
    print(f"  Omega-3:   {t['omega3_g']:.2f}g  (target: {g['omega3_g'] if g else '?'})")

"""ODS read/write operations for TREINOS and EXERCICIOS sheets."""

import json
import re
import shutil
import zipfile
from datetime import date
from pathlib import Path

ODS_PATH = Path(__file__).parent / "log-de-treino-e-progressao.ods"
SESSION_FILE = Path(__file__).parent / "session.json"
PENDING_FILE = Path(__file__).parent / "pending_log.csv"

TREINO_RANGES = {
    "A": range(0, 8),
    "B": range(8, 15),
    "C": range(15, 18),
}


def is_ods_locked():
    lock = ODS_PATH.parent / f".~lock.{ODS_PATH.name}#"
    return lock.exists()


def _read_content():
    with zipfile.ZipFile(ODS_PATH) as z:
        return z.read("content.xml").decode("utf-8")


def _write_content(content):
    tmp = str(ODS_PATH) + ".tmp"
    with zipfile.ZipFile(ODS_PATH, "r") as zin:
        with zipfile.ZipFile(tmp, "w") as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "content.xml":
                    data = content.encode("utf-8")
                zout.writestr(item, data)
    shutil.move(tmp, str(ODS_PATH))


def _find_table(content, name):
    """Return (start, end) positions of table body in content.xml."""
    m = re.search(rf'<table:table table:name="{re.escape(name)}"', content)
    if not m:
        raise RuntimeError(f"Table '{name}' not found in ODS")
    start = m.start()
    end = content.find("</table:table>", start)
    return start, end


def _cell_end(xml, start):
    """Find end position of a table-cell element starting at 'start'."""
    next_lt = xml.find("<", start + 1)
    next_sc = xml.find("/>", start)
    if next_sc != -1 and (next_lt == -1 or next_sc < next_lt):
        return next_sc + 2
    end_tag = xml.find("</table:table-cell>", start)
    return end_tag + len("</table:table-cell>")


def read_exercises():
    """Return list of {name, sets, reps} for all exercises in EXERCICIOS sheet."""
    content = _read_content()
    start, end = _find_table(content, "EXERCICIOS")
    chunk = content[start:end]
    result = []
    for m in re.finditer(r"<table:table-row", chunk):
        row_end = chunk.find("</table:table-row>", m.start()) + len("</table:table-row>")
        texts = re.findall(r"<text:p>([^<]*)</text:p>", chunk[m.start():row_end])
        if len(texts) >= 3 and texts[0].strip():
            try:
                result.append({
                    "name": texts[0].strip(),
                    "sets": int(texts[1].strip()),
                    "reps": int(texts[2].strip()),
                })
            except ValueError:
                pass
    return result


def read_previous_weights():
    """Return dict {exercise_name: last_carga} from TREINOS history."""
    content = _read_content()
    start, end = _find_table(content, "TREINOS")
    chunk = content[start:end]
    weights = {}
    for m in re.finditer(r"<table:table-row", chunk):
        row_end = chunk.find("</table:table-row>", m.start()) + len("</table:table-row>")
        row_xml = chunk[m.start():row_end]
        if 'office:value-type="date"' not in row_xml:
            continue
        # Extract office:value for each cell in order
        cells = []
        for cm in re.finditer(r"<table:table-cell([^>]*?)(?:/>|>(.*?)</table:table-cell>)", row_xml, re.DOTALL):
            attrs = cm.group(1)
            v = re.search(r'office:value="([^"]*)"', attrs)
            d = re.search(r'office:date-value="([^"]*)"', attrs)
            t = re.search(r"<text:p>([^<]*)</text:p>", cm.group(0))
            repeated = re.search(r'table:number-columns-repeated="(\d+)"', attrs)
            n = int(repeated.group(1)) if repeated else 1
            val = (d or v or t)
            val = val.group(1).strip() if val else None
            cells.extend([val] * min(n, 20))
            if len(cells) >= 8:
                break
        if len(cells) >= 7:
            ex_name = cells[3]
            carga_str = cells[6]
            if ex_name and carga_str:
                try:
                    c = float(carga_str.replace(",", "."))
                    if c > 0:
                        weights[ex_name] = c
                except ValueError:
                    pass
    return weights


def _count_data_rows(content):
    """Count data rows (non-header) in TREINOS."""
    start, end = _find_table(content, "TREINOS")
    chunk = content[start:end]
    count = 0
    for m in re.finditer(r"<table:table-row", chunk):
        row_end = chunk.find("</table:table-row>", m.start()) + len("</table:table-row>")
        row_xml = chunk[m.start():row_end]
        if 'office:value-type="date"' in row_xml:
            count += 1
    return count


def _make_row_xml(r, date_iso, date_disp, treino, ex_name, sets, reps):
    q = "&quot;"
    amp = "&amp;"
    lt = "&lt;"
    return (
        f'<table:table-row table:style-name="ro1">'
        f'<table:table-cell table:style-name="ce22" table:content-validation-name="val1"'
        f' office:value-type="date" office:date-value="{date_iso}" calcext:value-type="date">'
        f'<text:p>{date_disp}</text:p></table:table-cell>'
        f'<table:table-cell table:style-name="ce9"'
        f' table:formula="of:=IF([.A{r}]={q}{q};{q}{q};YEAR([.A{r}]){amp}{q}-W{q}{amp}TEXT(ISOWEEKNUM([.A{r}]);{q}00{q}))"'
        f' office:value-type="string" office:string-value=""><text:p></text:p></table:table-cell>'
        f'<table:table-cell table:style-name="ce71" table:content-validation-name="val2"'
        f' office:value-type="string" calcext:value-type="string"><text:p>{treino}</text:p></table:table-cell>'
        f'<table:table-cell table:style-name="ce16" table:content-validation-name="val3"'
        f' office:value-type="string" calcext:value-type="string"><text:p>{ex_name}</text:p></table:table-cell>'
        f'<table:table-cell table:style-name="ce20"'
        f' table:number-matrix-columns-spanned="1" table:number-matrix-rows-spanned="1"'
        f' table:formula="of:=IF([.D{r}]={q}{q};{q}{q};IFERROR(INDEX([$EXERCICIOS.B:.B];MATCH(TRIM([.D{r}]);TRIM([$EXERCICIOS.A:.A]);0));{q}{q}))"'
        f' office:value-type="float" office:value="{sets}"><text:p>{sets}</text:p></table:table-cell>'
        f'<table:table-cell table:style-name="ce20"'
        f' table:number-matrix-columns-spanned="1" table:number-matrix-rows-spanned="1"'
        f' table:formula="of:=IF([.D{r}]={q}{q};{q}{q};IFERROR(INDEX([$EXERCICIOS.C:.C];MATCH(TRIM([.D{r}]);TRIM([$EXERCICIOS.A:.A]);0));{q}{q}))"'
        f' office:value-type="float" office:value="{reps}"><text:p>{reps}</text:p></table:table-cell>'
        f'<table:table-cell table:style-name="ce22"/>'
        f'<table:table-cell table:style-name="ce22"/>'
        f'<table:table-cell table:style-name="ce20"'
        f' table:formula="of:=IFERROR([.E{r}]*[.F{r}]*[.G{r}];0)"><text:p/></table:table-cell>'
        f'<table:table-cell table:style-name="ce20"'
        f' table:formula="of:=IF([.H{r}]={q}{q};{q}{q};IF([.H{r}]{lt}=8;{q}AUMENTAR{q};IF([.H{r}]=9;{q}MANTER{q};{q}REDUZIR{q})))">'
        f'<text:p/></table:table-cell>'
        f'<table:table-cell table:style-name="ce20"'
        f' table:formula="of:=IF(ROW()=2;{q}{q};IFERROR(LOOKUP(2;1/([.$D$2]:INDEX([.$D:.$D];ROW()-1)=[.D{r}]);[.$G$2]:INDEX([.$G:.$G];ROW()-1));{q}{q}))">'
        f'<text:p/></table:table-cell>'
        f'<table:table-cell table:style-name="ce20"'
        f' table:formula="of:=IF([.J{r}]={q}AUMENTAR{q};[.G{r}]+2.5;IF([.J{r}]={q}REDUZIR{q};[.G{r}]-2.5;[.G{r}]))">'
        f'<text:p/></table:table-cell>'
        f'<table:table-cell table:style-name="ce20"/>'
        f'<table:table-cell table:style-name="ce65" table:number-columns-repeated="16371"/>'
        f'</table:table-row>'
    )


def _make_value_cell(value, style="ce25"):
    v = float(value)
    disp = str(int(v)) if v == int(v) else str(v).replace(".", ",")
    return (
        f'<table:table-cell table:style-name="{style}"'
        f' office:value-type="float" office:value="{v}"'
        f' calcext:value-type="float"><text:p>{disp}</text:p></table:table-cell>'
    )


def _update_conditional_format(content, last_row):
    """Replace TREINOS conditional-formats block with clean range up to last_row."""
    q = "&quot;"
    lt = "&lt;"
    new_cf = (
        f'<calcext:conditional-formats>'
        f'<calcext:conditional-format calcext:target-range-address="TREINOS.D2:TREINOS.M{last_row}">'
        f'<calcext:condition calcext:apply-style-name="ConditionalStyle_2" calcext:value="formula-is([.$J2]={q}AUMENTAR{q})" calcext:base-cell-address="TREINOS.D2"/>'
        f'<calcext:condition calcext:apply-style-name="ConditionalStyle_3" calcext:value="formula-is([.$J2]={q}REDUZIR{q})" calcext:base-cell-address="TREINOS.D2"/>'
        f'<calcext:condition calcext:apply-style-name="ConditionalStyle_4" calcext:value="formula-is([.$J2]={q}MANTER{q})" calcext:base-cell-address="TREINOS.D2"/>'
        f'</calcext:conditional-format>'
        f'<calcext:conditional-format calcext:target-range-address="TREINOS.A2:TREINOS.B{last_row}">'
        f'<calcext:condition calcext:apply-style-name="ConditionalStyle_1" calcext:value="formula-is([.$A2]{lt}{lt}$a0)" calcext:base-cell-address="TREINOS.A2"/>'
        f'</calcext:conditional-format>'
        f'</calcext:conditional-formats>'
    )
    m = re.search(r'<calcext:conditional-formats>.*?</calcext:conditional-formats>', content, re.DOTALL)
    if m and 'TREINOS' in m.group(0):
        content = content[:m.start()] + new_cf + content[m.end():]
    return content


def gerar_treino(treino_type):
    """
    Add training rows to ODS for the given type (A/B/C).
    Returns list of {row, name, sets, reps} dicts (row = 0-indexed for getCellByPosition).
    """
    treino_type = treino_type.upper()
    if treino_type not in TREINO_RANGES:
        raise ValueError(f"Invalid treino type: {treino_type}")

    if is_ods_locked():
        raise RuntimeError("ODS is open in LibreOffice — close it first.")

    all_ex = read_exercises()
    exercises = [all_ex[i] for i in TREINO_RANGES[treino_type] if i < len(all_ex)]

    content = _read_content()
    n_data = _count_data_rows(content)

    # Find insertion point: after last data row in TREINOS
    t_start, t_end = _find_table(content, "TREINOS")
    chunk = content[t_start:t_end]
    last_data_end_local = 0
    for m in re.finditer(r"<table:table-row", chunk):
        row_end = chunk.find("</table:table-row>", m.start()) + len("</table:table-row>")
        if 'office:value-type="date"' in chunk[m.start():row_end]:
            last_data_end_local = row_end
    insert_pos = t_start + last_data_end_local if last_data_end_local else t_end

    today = date.today()
    date_iso = today.strftime("%Y-%m-%d")
    date_disp = today.strftime("%d/%m/%Y")

    new_xml = ""
    session_exercises = []
    for idx, ex in enumerate(exercises):
        r = n_data + 2 + idx  # 1-based spreadsheet row
        new_xml += _make_row_xml(r, date_iso, date_disp, treino_type, ex["name"], ex["sets"], ex["reps"])
        session_exercises.append({
            "row": r - 1,  # 0-indexed for getCellByPosition
            "name": ex["name"],
            "sets": ex["sets"],
            "reps": ex["reps"],
        })

    new_content = content[:insert_pos] + new_xml + content[insert_pos:]
    new_last_row = n_data + 1 + len(exercises)  # header=1 + all data rows
    new_content = _update_conditional_format(new_content, new_last_row)
    _write_content(new_content)
    return session_exercises


def update_row_weights(row_0idx, carga, rpe=None):
    """
    Update Carga (col G) and RPE (col H) for the row at row_0idx.
    Returns True on success, False if ODS is locked.
    """
    if is_ods_locked():
        return False

    content = _read_content()
    t_start, t_end = _find_table(content, "TREINOS")
    chunk = content[t_start:t_end]

    # Find the row at row_0idx
    rows = list(re.finditer(r"<table:table-row", chunk))
    if row_0idx >= len(rows):
        return False

    m = rows[row_0idx]
    row_end_local = chunk.find("</table:table-row>", m.start()) + len("</table:table-row>")
    row_start_abs = t_start + m.start()
    row_end_abs = t_start + row_end_local
    row_xml = chunk[m.start():row_end_local]

    # Find all cell start positions in row
    cell_pos = [cm.start() for cm in re.finditer(r"<table:table-cell", row_xml)]
    if len(cell_pos) < 8:
        return False

    # G = cell index 6, H = cell index 7
    g_start = cell_pos[6]
    g_end = _cell_end(row_xml, g_start)
    h_start = cell_pos[7]
    h_end = _cell_end(row_xml, h_start)

    new_g = _make_value_cell(carga)
    new_h = _make_value_cell(rpe) if rpe is not None else row_xml[h_start:h_end]

    new_row = row_xml[:g_start] + new_g + row_xml[g_end:h_start] + new_h + row_xml[h_end:]
    new_content = content[:row_start_abs] + new_row + content[row_end_abs:]
    _write_content(new_content)
    return True


def write_session(treino_type, exercises):
    data = {
        "date": date.today().strftime("%Y-%m-%d"),
        "treino": treino_type.upper(),
        "exercises": exercises,
    }
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def clear_pending():
    if PENDING_FILE.exists():
        PENDING_FILE.unlink()

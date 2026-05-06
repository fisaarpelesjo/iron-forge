"""Remove the TREINOS sheet from the ODS file. Backs up first."""

import re
import shutil
import zipfile
from pathlib import Path

ODS_PATH = Path(__file__).parent / "log-de-treino-e-progressao.ods"
BACKUP_PATH = ODS_PATH.with_suffix(".ods.bak")


def remove_treinos_sheet():
    shutil.copy2(ODS_PATH, BACKUP_PATH)
    print(f"Backup saved to {BACKUP_PATH.name}")

    with zipfile.ZipFile(ODS_PATH, "r") as zin:
        content = zin.read("content.xml").decode("utf-8")
        other_files = {
            item.filename: zin.read(item.filename)
            for item in zin.infolist()
            if item.filename != "content.xml"
        }
        infos = {item.filename: item for item in zin.infolist()}

    # Remove <table:table name="TREINOS">...</table:table>
    m = re.search(r'<table:table table:name="TREINOS"', content)
    if not m:
        print("TREINOS sheet not found — nothing to remove.")
        return

    t_start = m.start()
    t_end = content.find("</table:table>", t_start) + len("</table:table>")
    content = content[:t_start] + content[t_end:]
    print("Removed TREINOS table element.")

    # Remove calcext:conditional-formats block that references TREINOS
    cf_m = re.search(r"<calcext:conditional-formats>.*?</calcext:conditional-formats>", content, re.DOTALL)
    if cf_m and "TREINOS" in cf_m.group(0):
        content = content[: cf_m.start()] + content[cf_m.end() :]
        print("Removed TREINOS conditional-formats block.")

    tmp = str(ODS_PATH) + ".tmp"
    with zipfile.ZipFile(ODS_PATH, "r") as zin:
        with zipfile.ZipFile(tmp, "w") as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "content.xml":
                    data = content.encode("utf-8")
                zout.writestr(item, data)

    shutil.move(tmp, str(ODS_PATH))
    print("ODS updated.")


if __name__ == "__main__":
    remove_treinos_sheet()

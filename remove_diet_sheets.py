"""Remove ALIMENTOS and DIETA sheets from ODS. Backs up first."""

import re
import shutil
import zipfile
from pathlib import Path

ODS_PATH = Path(__file__).parent / "log-de-treino-e-progressao.ods"
BACKUP_PATH = ODS_PATH.with_suffix(".ods.bak2")


def remove_sheet(content, name):
    m = re.search(rf'<table:table table:name="{re.escape(name)}"', content)
    if not m:
        print(f"  Sheet '{name}' not found — skipping.")
        return content
    start = m.start()
    end = content.find("</table:table>", start) + len("</table:table>")
    content = content[:start] + content[end:]
    print(f"  Removed sheet '{name}'.")
    return content


if __name__ == "__main__":
    shutil.copy2(ODS_PATH, BACKUP_PATH)
    print(f"Backup saved to {BACKUP_PATH.name}")

    with zipfile.ZipFile(ODS_PATH, "r") as zin:
        content = zin.read("content.xml").decode("utf-8")

    content = remove_sheet(content, "ALIMENTOS")
    content = remove_sheet(content, "DIETA")

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

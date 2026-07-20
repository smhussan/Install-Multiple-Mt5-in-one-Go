"""
Installs additional MetaTrader 5 terminal copies, continuing on from
whatever copies already exist. Drives the actual install wizard
directly (this installer build doesn't honor /auto, so this clicks
through it instead, using the real control IDs read off your wizard).

USAGE
  1. Put this script in the SAME folder as mt5setup.exe.
  2. Open an ADMIN Command Prompt / PowerShell in that folder.
  3. python install_mt5_copies.py
  4. Reports the next free index, asks how many new copies, installs
     them one by one -- no clicking needed.

Each finished install auto-launches its own MetaTrader 5 terminal
(account login screen) as a side effect of the installer itself --
that's normal. Expect one extra window per copy installed; this
script only drives the SETUP wizard, it doesn't touch those.

    pip install pywinauto
"""

import os
import re
import subprocess
import sys
import time

from pywinauto import Desktop

INSTALLER = "mt5setup.exe"          # <-- change if your installer exe has a different name
BASE_DIR = r"C:\Program Files"      # <-- change if your copies live somewhere else
BASE_NAME = "MetaTrader 5"
WIZARD_TITLE_RE = ".*MetaTrader.*Setup.*"

# Control auto_ids, read straight off the real wizard with inspect_mt5_setup.py
AUTO_ID_SETTINGS = "316"       # "Settings" button on the license page
AUTO_ID_PATH_EDIT = "260"      # "Installation folder:" edit box
AUTO_ID_MQL5_CHECKBOX = "273"  # "Open MQL5.community website" checkbox
AUTO_ID_NEXT = "12324"         # "Next >"
AUTO_ID_FINISH = "12325"       # "Finish"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) or "."


def find_next_index():
    pattern = re.compile(rf"^{re.escape(BASE_NAME)}(?:-(\d+))?$", re.IGNORECASE)
    highest = -1
    for entry in os.listdir(BASE_DIR):
        m = pattern.match(entry)
        if m:
            n = int(m.group(1)) if m.group(1) else 0
            highest = max(highest, n)
    return highest + 1


def target_path(index):
    if index == 0:
        return os.path.join(BASE_DIR, BASE_NAME)
    return os.path.join(BASE_DIR, f"{BASE_NAME}-{index}")


def run_wizard(path):
    dlg = Desktop(backend="uia").window(title_re=WIZARD_TITLE_RE)
    dlg.wait("exists visible ready", timeout=30)

    # License page -> "Settings" opens the installation-folder page
    dlg.child_window(auto_id=AUTO_ID_SETTINGS, control_type="Button").click_input()

    # Installation-folder page
    edit = dlg.child_window(auto_id=AUTO_ID_PATH_EDIT, control_type="Edit")
    edit.wait("exists visible ready", timeout=15)
    edit.set_edit_text(path)

    checkbox = dlg.child_window(auto_id=AUTO_ID_MQL5_CHECKBOX, control_type="CheckBox")
    try:
        if checkbox.exists() and checkbox.get_toggle_state() != 0:
            checkbox.click_input()
    except Exception:
        pass  # non-critical -- worst case the MQL5.community page opens in a browser

    dlg.child_window(auto_id=AUTO_ID_NEXT, control_type="Button").click_input()

    # Install runs, then lands on the Finish page -- can take a while
    finish_btn = dlg.child_window(auto_id=AUTO_ID_FINISH, control_type="Button")
    finish_btn.wait("exists visible ready", timeout=180)
    finish_btn.click_input()

    # Wait for the wizard window itself to close before starting the next one
    dlg.wait_not("exists", timeout=30)


def install_copy(index):
    path = target_path(index)
    print(f"[{index}] installing -> {path}")
    subprocess.Popen([INSTALLER], cwd=SCRIPT_DIR)
    try:
        run_wizard(path)
    except Exception as e:
        print(f"[{index}] automation error: {e}")
        print(f"[{index}] check the wizard window manually before re-running.")
        return False
    print(f"[{index}] done (its MT5 terminal will pop up a login screen -- that's normal).")
    return True


def main():
    if not os.path.isfile(os.path.join(SCRIPT_DIR, INSTALLER)):
        print(f"Can't find \"{INSTALLER}\" next to this script -- check the INSTALLER variable at the top.")
        sys.exit(1)
    if not os.path.isdir(BASE_DIR):
        print(f"Can't find \"{BASE_DIR}\" -- check the BASE_DIR variable at the top.")
        sys.exit(1)

    start = find_next_index()
    last = BASE_NAME if start == 1 else f"{BASE_NAME}-{start - 1}"
    print(f"Existing copies detected, last one is \"{last}\". Next free index is {start}.")

    try:
        count = int(input("How many new MT5 copies do you want to install? ").strip())
    except ValueError:
        print("Enter a whole number.")
        sys.exit(1)
    if count <= 0:
        print("Nothing to do.")
        return

    for i in range(count):
        ok = install_copy(start + i)
        if not ok:
            print("Stopping -- fix the issue above before continuing.")
            sys.exit(1)
        time.sleep(2)

    print(f"\nInstalled {count} new copies: index {start} through {start + count - 1}.")


if __name__ == "__main__":
    main()

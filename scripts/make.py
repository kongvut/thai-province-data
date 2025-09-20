#!/usr/bin/env python3
# scripts/make.py
# Orchestrate validate -> export formats -> export API

import subprocess
import sys
import os

SCRIPTS = os.path.dirname(os.path.abspath(__file__))

STEPS = [
    ["0_validate_data.py"],
    ["1_export_file_format.py", "--overwrite"],
    ["2_export_api.py", "--overwrite"],
]

def run_step(cmd):
    """Run one step, exit if fails."""
    script_path = os.path.join(SCRIPTS, cmd[0])
    full_cmd = [sys.executable, script_path] + cmd[1:]
    print(f"\n🚀 Running: {' '.join(full_cmd)}")
    try:
        subprocess.run(full_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n⛔ Step failed: {cmd[0]} (exit {e.returncode})")
        sys.exit(e.returncode)
    except FileNotFoundError:
        print(f"\n⛔ Script not found: {script_path}")
        sys.exit(1)

def main():
    for cmd in STEPS:
        run_step(cmd)
    print("\n🏁 All steps completed successfully.")

if __name__ == "__main__":
    main()

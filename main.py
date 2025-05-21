# main.py

import sys
import os

print("Python executable:", sys.executable)
print("PYTHONPATH:", os.environ.get("PYTHONPATH"))

from agents.manager.manager_agent import ManagerAgent

def main():
    print("🔍 BittyScout is starting...")

    manager = ManagerAgent()
    manager.run()

    print("✅ BittyScout has finished this run.")

if __name__ == "__main__":
    main()

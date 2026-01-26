# Start the FastAPI app via the project's virtual environment using uvicorn (reload enabled)
import os, sys, subprocess

# Choose correct venv path: 'Scripts' for Windows, 'bin' for Mac/Linux
path = "Scripts" if sys.platform == "win32" else "bin"
cmd = [os.path.join("venv", path, "python"), "-m", "uvicorn", "app.main:app", "--reload"]

subprocess.run(cmd)
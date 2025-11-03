-- Developed by Sumit & Chirag 

Setup and Run Instructions
==========================

1. Check if Python is installed

   Open Command Prompt (Windows) or Terminal (macOS/Linux) and run:

       python --version

   or

       python3 --version

   - If you see the Python version (e.g. Python 3.x.x), Python is installed.
   - If you get an error like "command not found", Python is not installed.  
     Proceed to step 2.

2. Install latest Python version

   - Download & Run the Python installer.
   - Follow the installation steps.
   - Make sure to check "Add Python to PATH" during installation if prompted.

3. Verify Python installation

   Open a new Command Prompt or Terminal window and run:

       python --version

   You should see the installed Python version.

4. Check pip (Python package installer)

   Run:

       pip --version

   - If pip is not recognized, run:

       python -m ensurepip --upgrade

5. Install required Python packages

   Run the following commands to install required packages:

       pip install PyQt5
       pip install matplotlib

6. Run the application

   To start the app, run:

       python scheduler_gui.py

---

If you encounter any errors during installation or running, reach out on GitHub.
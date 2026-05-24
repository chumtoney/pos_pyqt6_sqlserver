# Step 1 Create a virtual environment

- Create a virtual environment:

```bash
python -m venv .venv
```

- Activate the virtual environment:

```bash
# For Command Prompt
venv\Scripts\activate

# For PowerShell
venv\Scripts\Activate.ps1
```

**Note**: If you get an execution policy error in PowerShell, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

# Step 2 Install Required Packages

- With the virtual environment activated, install dependencies:

```bash
pip install -r requirements.txt
```

- This will install:
  - `PyQt6` - GUI framework
  - `pyodbc` - SQL Server connection
  - `python-dotenv` - Environment configuration

# Step 3: Run the Application

From the project directory with the virtual environment activated:

```bash
python src/app.py
```

Or run directly from the src folder:

```bash
cd src
python app.py
```

The login dialog will appear. Log in with your configured database credentials.

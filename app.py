from flask import Flask, request, jsonify, render_template
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os

load_dotenv()

scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(
    os.getenv("GOOGLE_CREDENTIALS_PATH"),
    scopes=scope
)

app = Flask(__name__)

# --- Google Sheets Setup ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
client = gspread.authorize(creds)

# Open the spreadsheet
sheet = client.open("Performance Sheet - JKTVS")

@app.route('/')
def index():
    """Render the main page with client dropdown, excluding 'Clients' worksheet."""
    client_list = sheet.worksheets()  # List of all worksheet objects
    # Extract titles and exclude "Clients"
    client_names = [ws.title for ws in client_list if ws.title != 'Clients']

    return render_template('index.html', clients=client_names)

@app.route('/get_client_data', methods=['POST'])
def get_client_data():
    """Fetch and return data for the selected client."""
    client_name = request.json.get('client_name')

    if not client_name:
        return jsonify({"error": "Client name is required"}), 400

    try:
        worksheet = sheet.worksheet(client_name)  # Open the corresponding worksheet
        data = worksheet.get_all_values()  # Get all data
        
        headers = data[0]  # First row as headers
        rows = data[1:]  # Remaining rows as data

        return jsonify({"headers": headers, "rows": rows})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5002) # for local
    #app.run(debug=False, host='0.0.0.0', port=8053) # for production
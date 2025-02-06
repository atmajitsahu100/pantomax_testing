from elasticsearch import Elasticsearch
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Step 1: Elasticsearch Connection
def query_elasticsearch(es_host, index, query):
    es = Elasticsearch([es_host])
    response = es.search(index=index, body=query)
    hits = response['hits']['hits']
    return [hit['_source'] for hit in hits]

# Step 2: Google Sheets Setup
def setup_google_sheet(credentials_file, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return sheet

# Step 3: Write Data to Google Sheet
def write_to_google_sheet(sheet, data):
    if not data:
        print("No data to write.")
        return

    # Extract headers from the first document
    headers = list(data[0].keys())
    sheet.append_row(headers)

    # Write each document's values
    for record in data:
        row = [record.get(header, "") for header in headers]
        sheet.append_row(row)

# Main Function
def main():
    # Elasticsearch details
    es_host = "https://1f6ce74a17ea4b2282e51a64302b089c.us-central1.gcp.cloud.es.io:443"  # Replace with your Elasticsearch host
    index = "ats"         # Replace with your index name
    query = {
        "query": {
            "match_all": {}
        }
    }

    # Google Sheets details
    credentials_file = "ats1.json"  # Replace with your service account JSON file
    sheet_name = "jeet124"              # Replace with your Google Sheet name

    # Fetch data from Elasticsearch
    data = query_elasticsearch(es_host, index, query)

    # Set up Google Sheet and write data
    sheet = setup_google_sheet(credentials_file, sheet_name)
    write_to_google_sheet(sheet, data)

if __name__ == "__main__":
    main()

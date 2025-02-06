import requests
from requests.auth import HTTPBasicAuth

# Configuration
JIRA_URL = "https://swiggy.atlassian.net/jira/software/c/projects/RCA/issues/?jql=project%20%3D%20%22RCA%22%20AND%20Status%20not%20in%20%28Deferred%2C%20%22Issue%20not%20Valid%22%2C%20REJECTED%2C%20%22Closed%20%28Duplicate%29%22%29%20AND%20project%20%21%3D%20Architecture%20AND%20created%20%3C%3D%20-90d%20ORDER%20BY%20created%20DESC"  # Jira API endpoint

USERNAME = "atmajit.sahoo_int@external.swiggy.in"                             # Your Jira account email

API_TOKEN = "ATATT3xFfGF0YX_1jgxuXr-rwxZtLw-R_tvRpl5A9R4o4BRk2FdSa1XqhJ3u7z4AbOqh950x2ZoRWaX5X6glDUnmRR88AGOWDooSiNHW9Skj-ZrFXmTCLgLigMaUj47oJWpjcr2_kLc_HdSkWkqKLeyTtQeIoPXD99vru0kjRhwtnzLh9-uO_mY=9062FCD5"
         
JQL_QUERY = 'severity = "S1"'          # Adjust based on your Jira configuration

# Headers for API request
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Payload for the API request
payload = {
    "jql": JQL_QUERY,
    "maxResults": 50  # Adjust as needed
}

# Make the API request
try:
    response = requests.post(
        JIRA_URL,
        json=payload,
        headers=headers,
        auth=HTTPBasicAuth(USERNAME, API_TOKEN)
    )
    response.raise_for_status()  # Raise an error for HTTP issues
    data = response.json()
    print(f"Total issues fetched: {data['total']}")

    for issue in data['issues']:
        print(f"Issue Key: {issue['key']}, Summary: {issue['fields']['summary']}")
except Exception as e:
    print("Error fetching issues:", e)

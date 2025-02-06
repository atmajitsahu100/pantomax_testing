import requests
from requests.auth import HTTPBasicAuth
from collections import defaultdict

# Replace with your Jira domain, email, and API token
JIRA_DOMAIN = "swiggy.atlassian.net"
EMAIL = "atmajit.sahoo_int@external.swiggy.in"
API_TOKEN = "ATATT3xFfGF0YX_1jgxuXr-rwxZtLw-R_tvRpl5A9R4o4BRk2FdSa1XqhJ3u7z4AbOqh950x2ZoRWaX5X6glDUnmRR88AGOWDooSiNHW9Skj-ZrFXmTCLgLigMaUj47oJWpjcr2_kLc_HdSkWkqKLeyTtQeIoPXD99vru0kjRhwtnzLh9-uO_mY=9062FCD5"

# API URL
url = f"https://{JIRA_DOMAIN}/rest/api/3/search"

# Query Parameters
params = {
    "jql": 'severity = "S1"',
    "maxResults": 50
}

# Headers
headers = {
    "Accept": "application/json"
}

# Make the GET request
response = requests.get(url, headers=headers, auth=HTTPBasicAuth(EMAIL, API_TOKEN), params=params)

# Check the response
if response.status_code == 200:
    data = response.json()
    print("Issues fetched successfully!")
    
    # Dictionary to store counts of S1 issues per organization
    org_severity_count = defaultdict(int)

    # Process each issue
    for issue in data.get("issues", []):
        fields = issue.get("fields", {})
        
        # Replace 'customfield_XXXX' with the actual field ID for the organization field in Jira
        org_name = fields.get("customfield_XXXX", "Unknown Organization")  # Replace with actual org field key
        org_severity_count[org_name] += 1

    # Print the counts for each organization
    print("\nSeverity 1 Issues by Organization:")
    for org, count in org_severity_count.items():
        print(f"{org}: {count}")
else:
    print(f"Failed to fetch issues: {response.status_code} - {response.text}")

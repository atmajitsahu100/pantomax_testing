import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

def load_json_data(file_path):
    """Load and parse JSON data from a file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading JSON data: {e}")
        return None

def count_canary_deployments(data):
    """Count unique canary deployments for each organization, ignoring duplicate IDs."""
    counts = {}
    seen_ids = set()  # To track already counted deployment IDs

    try:
        for hit in data['hits']['hits']:
            source = hit['_source']
            org = source['detail']['context']['org']
            deployment_strategy = source['detail']['deploymentStrategy']
            deployment_id = source['detail']['context']['id']

            # Only count if the deployment is 'canary' and ID has not been seen
            if deployment_strategy == "canary" and deployment_id not in seen_ids:
                counts[org] = counts.get(org, 0) + 1
                seen_ids.add(deployment_id)  # Mark this ID as seen
    except KeyError as e:
        print(f"Missing key in data: {e}")
    
    return counts


def count_rollback_deployments(data):
    """
    Count rollback deployments per organization from the given data.
    """
    rollback_counts = {}
    for hit in data.get("hits", {}).get("hits", []):
        detail = hit.get("_source", {}).get("detail", {})
        if detail.get("deploymentType") == "rollback":
            org = detail.get("context", {}).get("org", "unknown")
            rollback_counts[org] = rollback_counts.get(org, 0) + 1
    return rollback_counts

def count_hotfix_deployments(data):
    """
    Count hotfix deployments for each organization.

    Args:
        data (dict): The data containing deployment details.

    Returns:
        dict: A dictionary with organization names as keys and the count of hotfix deployments as values.
    """
    hotfix_counts = {}
    seen_ids = set()  # Track unique IDs to avoid duplicate counting

    try:
        for hit in data['hits']['hits']:
            source = hit['_source']
            org = source['detail']['context']['org']
            deployment_type = source['detail']['deploymentType']
            unique_id = source['id']  # Use the unique ID to avoid duplicates

            if deployment_type == "hotfix" and unique_id not in seen_ids:
                seen_ids.add(unique_id)
                hotfix_counts[org] = hotfix_counts.get(org, 0) + 1
    except KeyError as e:
        print(f"Missing key in data: {e}")

    return hotfix_counts

def count_ephemeral_environments(data):
    """
    Count ephemeral environments by their statuses (created, initiating, running) per organization.
    """
    ephemeral_counts = {}
    for hit in data.get("hits", {}).get("hits", []):
        source = hit.get("_source", {})
        if source.get("envType") == "ephemeral":
            org = source.get("org", "unknown")
            status = source.get("status", "unknown")
            if org not in ephemeral_counts:
                ephemeral_counts[org] = {"created": 0, "initiating": 0, "running": 0}
            if status in ephemeral_counts[org]:
                ephemeral_counts[org][status] += 1
    return ephemeral_counts   


def authenticate_google_sheets(credentials_file):
    """Authenticate and return a gspread client."""
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
        return gspread.authorize(creds)
    except Exception as e:
        print(f"Error authenticating Google Sheets: {e}")
        return None

def get_or_create_spreadsheet(client, spreadsheet_name, share_email):
    """Retrieve or create a spreadsheet, and share it if newly created."""
    try:
        spreadsheet = client.open(spreadsheet_name)
    except gspread.SpreadsheetNotFound:
        spreadsheet = client.create(spreadsheet_name)
        spreadsheet.share(share_email, perm_type='user', role='writer')
    return spreadsheet

def prepare_org_data(org, metrics_data, org_index):
    """Prepare table data for a specific organization with serial numbers and collapsible grouping."""
    data = []
    header = ["Sl. No.", "Metric", "Frequency", "Unit", "Links", "Week 39", "Week 38", "Week 37", "Week 36"]

    # Add the organization row with a serial number.
    data.append([f"{org_index}. {org}"])
    data.append(header)

    metric_index = 1  # To keep track of the metric serial number

    for metric in metrics_data:
        if metric.get("category"):
            # If the metric is a category, add it as a separate row without serial number
            data.append([metric["name"], "", "", "", "", "", "", "", ""])
        else:
            # Add the metric details, including the serial number
            row = [
                metric_index,
                metric.get("name", ""),
                metric.get("frequency", ""),
                metric.get("unit", ""),
                metric.get("link", ""),
                metric.get("week_39", 0),
                metric.get("week_38", 0),
                metric.get("week_37", 0),
                metric.get("week_36", 0)
            ]
            data.append(row)
            metric_index += 1  # Increment the serial number for non-category rows

    # Add a blank row for collapsible grouping
    data.append([""])
    return data


def update_google_sheet(worksheet, data):
    """Write prepared data into the Google Sheets worksheet."""
    try:
        worksheet.clear()
        worksheet.update(data)
    except Exception as e:
        print(f"Error updating Google Sheets: {e}")

def main():
    data_file = 'canary.json'
    credentials_file = 'ats1.json'
    spreadsheet_name = "page 0 scorecard"
    share_email = 'atmajit.sahoo_int@external.swiggy.in'
    data_file_rollback = 'rollback.json'
    data_file_ephemeral = 'ephemeral.json'
    data_file_hostfix='hostfix.json'

    data1 = load_json_data(data_file_hostfix)

    if not data1:
        return

    hotfix_counts = count_hotfix_deployments(data1)

    data = load_json_data(data_file)
    if not data:
        return

    canary_rejections_counts = count_canary_deployments(data)


    data_rollback = load_json_data(data_file_rollback)
    if not data_rollback:
        return

    rollback_counts = count_rollback_deployments(data_rollback)

    client = authenticate_google_sheets(credentials_file)
    if not client:
        return

    data_ephemeral = load_json_data(data_file_ephemeral)
    if not data_ephemeral:
        return

    ephemeral_counts = count_ephemeral_environments(data_ephemeral)
   

    spreadsheet = get_or_create_spreadsheet(client, spreadsheet_name, share_email)
    worksheet = spreadsheet.sheet1

    consolidated_data = []
    orgs = (
        set(canary_rejections_counts.keys())
        .union(set(hotfix_counts.keys()))
        .union(set(rollback_counts.keys()))
        .union(set(ephemeral_counts.keys()))
    )

    metrics_template = [
        # Incident Management
        {"name": "Incident Management", "category": True},
        {"name": "No. of Sev1 Incidents", "frequency": "Weekly", "unit": "", "link": "Jira dashboard", "week_39": 0, "week_38": 0, "week_37": 0, "week_36": 0},
        {"name": "No. of S2 & S3 Incidents", "frequency": "Fortnightly", "unit": "", "link": "Sheet", "week_39": 0, "week_38": 0, "week_37": 0, "week_36": 0},
        {"name": "MTTR/MTTD for S2/S3 Incidents", "frequency": "Fortnightly", "unit": "", "link": "Sheet", "week_39": 0, "week_38": 0, "week_37": 0, "week_36": 0},
        {"name": "No. of P0 AIs from Sev 1 RCAs beyond SLA", "frequency": "Weekly", "unit": "", "link": "Jira dashboard", "week_39": 0, "week_38": 0, "week_37": 0, "week_36": 0},
        {"name": "No. of P1 AIs from Sev 1 RCAs beyond SLA", "frequency": "Weekly", "unit": "", "link": "Jira dashboard", "week_39": 0, "week_38": 0, "week_37": 0, "week_36": 0},
        {"name": "No. of Production Support Tickets", "frequency": "Weekly", "unit": "", "link": "Jira dashboard", "week_39": 0, "week_38": 0, "week_37": 0, "week_36": 0},
        {"name": "No. of P1 Security Incidents", "frequency": "Weekly", "unit": "", "link": "", "week_39": 0, "week_38": 0, "week_37": 0, "week_36": 0},
        {"name": "Ops Genie Alerts", "frequency": "Weekly", "unit": "", "link": "Sheet", "week_39": 0, "week_38": 0, "week_37": 0, "week_36": 0},

        # Deployment Metrics
        {"name": "Deployment Metrics", "category": True},
        {"name": "No. of Deployment Rollbacks", "frequency": "Weekly", "unit": "", "link": "Dashboard", "week_39": 0, "week_38": 0, "week_37": 0, "week_36": 0},
        {"name": "No. of Canary Rejections", "frequency": "Weekly", "unit": "", "link": "Dashboard", "week_39": 0, "week_38": 0, "week_37": 0, "week_36": 0},
        {"name": "No. of Hot Fixes", "frequency": "Weekly", "unit": "", "link": "Dashboard", "week_39": 0, "week_38": 0, "week_37": 0, "week_36": 0},
        {"name": "No. of Repos with build times > 20mins", "frequency": "Weekly", "unit": "", "link": "Dashboard", "week_39": 0, "week_38": 0, "week_37": 0, "week_36": 0},
        {"name": "No. of Services with GoLang Anti Pattern", "frequency": "Weekly", "unit": "Number", "link": "Dashboard", "week_39": 0, "week_38": 0, "week_37": 0, "week_36": 0},

        # Quality Metrics
        {"name": "Quality Metrics", "category": True},
        {"name": "No. of Sanity Build Failures", "frequency": "Weekly", "unit": "", "link": "Dashboard", "week_39": 0, "week_38": 0, "week_37": 0, "week_36": 0},
        {"name": "Ephemeral Environments - One click %", "frequency": "Weekly", "unit": "", "link": "", "week_39": 0, "week_38": 0, "week_37": 0, "week_36": 0},
        {"name": "Needed action for the upcoming AWS Scheduled events", "frequency": "Weekly", "unit": "", "link": "Jira dashboard", "week_39": 0, "week_38": 0, "week_37": 0, "week_36": 0},

        # Deployable Units
        {"name": "Deployable Units", "category": True},
        {"name": "No of Deployable Units", "frequency": "Weekly", "unit": "", "link": "Dashboard", "week_39": 0, "week_38": 0, "week_37": 0, "week_36": 0},

        # Cost Spikes
        {"name": "Cost Spikes", "category": True},
        {"name": "Net Cost Increases across the all PODs", "frequency": "Weekly", "unit": "Dollars", "link": "Dashboard", "week_39": 0, "week_38": 0, "week_37": 0, "week_36": 0},
        {"name": "Total Cost increase across all the PODs", "frequency": "Weekly", "unit": "Dollars", "link": "Dashboard", "week_39": 0, "week_38": 0, "week_37": 0, "week_36": 0}
    ]



    for org_index, org in enumerate(orgs, start=1):
        metrics = [metric.copy() for metric in metrics_template]
        for metric in metrics:
            if metric["name"] == "No. of Deployment Rollbacks":
                metric["week_39"] = rollback_counts.get(org, 0)
            if metric["name"] == "No. of Canary Rejections":
                metric["week_39"] = canary_rejections_counts.get(org, 0)
            if metric["name"] == "No. of Hot Fixes":
                metric["week_39"] = hotfix_counts.get(org, 0)
            if metric["name"] == "No. of Ephemeral Environments Created":
                metric["week_39"] = ephemeral_counts.get(org, {}).get("created", 0)
            if metric["name"] == "No. of Ephemeral Environments Initiating":
                metric["week_39"] = ephemeral_counts.get(org, {}).get("initiating", 0)
            if metric["name"] == "No. of Ephemeral Environments Running":
                metric["week_39"] = ephemeral_counts.get(org, {}).get("running", 0)

        org_data = prepare_org_data(org, metrics, org_index)
        consolidated_data.extend(org_data)

    update_google_sheet(worksheet, consolidated_data)
    print("Metrics data successfully added or updated in Google Spreadsheet!")


if __name__ == "__main__":
    main()
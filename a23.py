import gspread
from oauth2client.service_account import ServiceAccountCredentials
import csv
import json



def count_canary_deployments(file_path):

    with open(file_path, 'r') as file:
        data = json.load(file)


    count = 0


    for hit in data['hits']['hits']:
        source = hit['_source']
        org = source['detail']['context']['org']
        deploymentStrategy = source['detail']['deploymentStrategy']
    
    
        if org == "food-bl" and deploymentStrategy == "canary":
            count += 1


    print("Count:", count)
    return count


data_file = 'canary.json'
organization = 'food-bl'
canary_rejections_count = count_canary_deployments(data_file)


data = [
    ["Sl. No.", "Metric", "Frequency", "Unit", "Links", "Week 39", "Week 38", "Week 37", "Week 36"],
    [1, "No. of Canary Rejections", "Weekly", "", "Dashboard", canary_rejections_count, 0, 0, 0]
]

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("ats1.json", scope)
client = gspread.authorize(creds)


spreadsheet_name = "Canary Rejections"
try:
    spreadsheet = client.open(spreadsheet_name)
except gspread.SpreadsheetNotFound:
    spreadsheet = client.create(spreadsheet_name)
    spreadsheet.share('atmajit.sahoo_int@external.swiggy.in', perm_type='user', role='writer')

worksheet = spreadsheet.sheet1


worksheet.clear()


worksheet.append_rows(data)

print(f"Canary Rejections data for {organization} successfully added or updated in Google Spreadsheet!")

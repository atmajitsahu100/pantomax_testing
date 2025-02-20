import gspread
from oauth2client.service_account import ServiceAccountCredentials
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import AuthenticationException
import warnings


warnings.filterwarnings("ignore")

try:
   
    es = Elasticsearch(
        "https://localhost:9200",           
        basic_auth=("elastic", "6_s2=t8kytgygh"),  
        verify_certs=False                     
    )


    index_name = "my-index"  
    query = {
        "query": {
            "match_all": {}  
        },
        "size": 1000
    }

    response = es.search(index=index_name, body=query)

    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("ats1.json", scope)
    client = gspread.authorize(creds)

   
    
    spreadsheet = client.create("Elasticsearch Data Sheet")
    spreadsheet.share('atmajit.sahoo_int@exterl.swiggy.in', perm_type='user', role='writer')
    worksheet = spreadsheet.sheet1

    headers = ["ID", "Title", "Description"]  
    worksheet.append_row(headers)


    for hit in response['hits']['hits']:
        source = hit["_source"]
        row = [
            source.get("id", ""),          
            source.get("title", ""),     
            source.get("description", "") 
        ]
        worksheet.append_row(row)

    print("Data successfully added to Google Spreadsheet!")

except AuthenticationException as e:
    print(f"Authentication failed: {e}")
    print("Please verify your Elasticsearch username and password.")
except Exception as e:
    print(f"An error occurred: {e}")

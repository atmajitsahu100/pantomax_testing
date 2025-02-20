import openpyxl
import os

sensitive_data = {
    "api_key": "1234-abcd-5678-efgh",
    "password": "mysecretpassword",
    "token": "abcdef123456"
}

workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.title = "Sensitive Data"

sheet['A1'] = "Field"
sheet['B1'] = "Value"
sheet['A2'] = "API Key"
sheet['B2'] = sensitive_data["api_key"]
sheet['A3'] = "Password"
sheet['B3'] = sensitive_data["password"]
sheet['A4'] = "Token"
sheet['B4'] = sensitive_data["token"]

vba_code = """
Sub Auto_Open()
    MsgBox "This is a malicious macro!"
End Sub
"""
workbook.create_vba_project()
vba_project = workbook.vba_project
vba_module = vba_project.add_module("Module1")
vba_module.code = vba_code

file_name = "dangerous_excel.xlsx"
workbook.save(file_name)
os.chmod(file_name, 0o777)

print(f"Excel file '{file_name}' created with sensitive data, malicious macro, and weak permissions.")

user_input = "<script>alert('Hacked!');</script>"
sheet['A5'] = "User Input"
sheet['B5'] = user_input

workbook.save(file_name)
print("File saved with user input that could be exploited for XSS or other attacks.")

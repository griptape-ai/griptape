# Google Sheets

These tools enable LLMs to read from and write to Google Sheets worksheets. Before using those tools, make sure to download the service account credentials JSON file and share your spreadsheet with the service account. For more information refer to the `gspread` [auth docs](https://docs.gspread.org/en/latest/oauth2.html).

## GoogleSheetsReaderTool

To read from a spreadsheet:

```python
ToolStep(
    "read all spreadsheet values from the 2nd and 3rd columns",
    tool=GoogleSheetsReaderTool(
        auth_key_path=os.path.expanduser("~/Desktop/service_account.json"),
        spreadsheet_key="<Google Sheets spreadsheet ID>",
        worksheet_name="<optional worksheet name, defaults to the first worksheet>"
    )
)
```

## GoogleSheetsWriterTool

To write to a spreadsheet:

```python
ToolStep(
    "Create a spreadsheet with columns for 2022 months in the MM/YYYY format, last column for totals, and rows for profit, revenue, and loss",
    tool=GoogleSheetsWriterTool(
        auth_key_path=os.path.expanduser("~/Desktop/service_account.json"),
        spreadsheet_key="<Google Sheets spreadsheet ID>",
        worksheet_name="<optional worksheet name, defaults to the first worksheet>"
    )
)
```
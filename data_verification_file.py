from openpyxl import Workbook

class DataVerificationFile:
    
    def __init__(self, filename):
        self.workbook = Workbook()
        self.filename = filename
        self.data_types = {
            "missing_seed": {
                    "question": "The following fields are missing seed, could you provide your drilling information."
                    "input_headings": [
                        "Seed Planted",
                        "Drill Rate",
                        "Drill Date",
                        "Unit price"
                    ],
                    "data_headings": [
                        "Field Group",
                        "Field Name",
                        "Crop",
                        "Variety"
                    ]
                }
        }
        

    def add_year(self, year, data_obj):
        year_sheet = self.workbook.create_sheet(str(year), 0)

        for key in data_obj:
            self.add_missing_data(year_sheet, data_obj, key)

    def add_missing_data(self, sheet, obj, key):
        data_type = self.data_types[key]
        row = 3
        column = 3
        for heading in data_type["data_headings"]:
            sheet.cell(row=row, column=column, value=heading)
            column += 1
        for heading in data_type["input_headings"]:
            sheet.cell(row=row, column=column, value=heading)
            column += 1
        column = 1
        row +=1
        sheet.cell(row=row, column=column, value=data_type["question"])
        column += 2

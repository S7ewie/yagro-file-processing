from openpyxl import Workbook
from openpyxl.styles import PatternFill, GradientFill, Border, Side, Alignment, Protection, Font
import pandas as pd
from styles_and_what_not import YAGRO_GREEN

class DataVerificationFile:
    
    def __init__(self):
        self.workbook = Workbook()
        self.filename = "filename"
        self.data_types = {
            "missing_seed": {
                    "question": "The following fields are missing seed information, could you provide your drilling information.",
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
                },
            "missing_fert": {
                    "question": "The following fields are missing fertiliser information, could you provide your drilling information.",
                    "input_headings": [
                        "Fertiliser Product",
                        "Application Rate",
                        "Application Date",
                        "Unit price"
                    ],
                    "data_headings": [
                        "Field Group",
                        "Field Name",
                        "Crop",
                        "Variety"
                    ]
                },
            "missing_chem": {
                    "question": "The following fields are missing chemical information, could you provide your drilling information.",
                    "input_headings": [
                        "Chemical Product",
                        "Application Rate",
                        "Application Date",
                        "Unit price"
                    ],
                    "data_headings": [
                        "Field Group",
                        "Field Name",
                        "Crop",
                        "Variety"
                    ]
                },
            "missing_product_price": {
                "question": "The following products are missing a unit price, could you provide one. (Please indicate a pack quantity if the price supplied is for more thatn 1 L/kg).",
                "input_headings": [
                    "Unit price",
                    "Unit",
                    "Quantity of pack if applicable"
                ],
                "data_headings": [
                    "Product Name"
                ]
            }
        }
        self.style = {
            "font": Font(name='Comic Sans MS', size=12, bold=False, italic=False, vertAlign=None, underline='none', strike=False, color='121212')
        }
        

    def add_year(self, year, data_missing, field_analysis):
        year_sheet = self.workbook.create_sheet(str(round(year)), 0)
        year_sheet["A1"] = "Data Verification"

        row = 3
        column = 3

        for item in data_missing:
            data_type = self.data_types[item["name"]]
            for heading in data_type["data_headings"]:
                year_sheet.cell(row=row, column=column, value=heading)
                column += 1
            for heading in data_type["input_headings"]:
                year_sheet.cell(row=row, column=column, value=heading)
                column += 1
            column = 1
            row +=1
            year_sheet.cell(row=row, column=column, value=data_type["question"])
            column += 2

            if "fields" in item:
                for field in item["fields"]:
                    field_data = field_analysis[field]
                    year_sheet.cell(row=row, column=column, value=field_data["fgroup"])
                    column += 1
                    year_sheet.cell(row=row, column=column, value=field_data["name"])
                    column += 1
                    year_sheet.cell(row=row, column=column, value=field_data["crop"])
                    column += 1
                    year_sheet.cell(row=row, column=column, value=field_data["variety"])

                    column = 3
                    row += 1
            elif "products" in item:
                for product in item["products"]:
                    year_sheet.cell(row=row, column=column, value=product)

            row += 2
        
        self.add_global_format(year_sheet)
        

    def add_global_format(self, sheet):
        # this is not how it should be done but i cba to figure it out rn
        columns_to_width = ['C', 'D', 'E', 'F', "G", 'H', 'I', 'J']
        sheet.column_dimensions['A'].width = 75
        sheet.column_dimensions['B'].width = 5
        for i in columns_to_width:
            sheet.column_dimensions[i].width = 25
        for row in sheet.iter_rows(min_row=1, max_col=10):
            for cell in row:
                cell.font = self.style["font"]
                if cell.column == 1:
                    cell.alignment = Alignment(wrap_text=True)
                    # fill = GradientFill(stop=(YAGRO_GREEN.hex, "FFFFFF"))
                    # cell.fill = fill

    def save(self, name):
        filename = name + " - Data Verification.xlsx"
        writer = pd.ExcelWriter(filename, engine='openpyxl')
        writer.book = self.workbook
        writer.save()
        
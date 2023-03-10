import pandas as pd
from collections import defaultdict

class SingleYearFile:

    def __init__(self, dataframe):
        self.df = dataframe
        self.original_data = dataframe
        self.missing_prices = pd.DataFrame()
        self.fields_with_problems = []
        self.fields_missing_item = defaultdict(list)
        self.fields_missing_seed_list = []
        self.fields_missing_fert_list = []
        self.fields_missing_chem_list = []
        self.changes_made = defaultdict(list)
        self.field_analysis = {}
        self.field_analysis_df = pd.DataFrame()
        self.problem_units = [
            {
                "old_unit": "Seed",
                "crops": ["maize"],
                "new_unit": "kg",
                "conversion": (15/50000)
            },
            {
                "old_unit": "SBUnit",
                "crops": ["sugar"],
                "new_unit": "kg",
                "conversion": (2)
            }
        ]
        self.filename = ""
        self.non_fert_crops = ['beans', 'peas']
        self.adjustment_obj = [
            {
                "name": "unit",
                "title": "Unit Adjustments",
                "headings": [
                    "Crop",
                    "Original Unit",
                    "New Unit"
                ],
                "keys": [
                    "crop",
                    "original_unit",
                    "new_unit"
                ]
            },
            {
                "name": "product_price",
                "title": "Product Prices Inferred",
                "headings": [
                    "Product Name",
                    "Price Used"
                ],
                "keys": [
                    "product_name",
                    "price"
                ]
            },
            {
                "name": "variety",
                "title": "Varieties Inferred",
                "headings": [
                    "Field Name",
                    "Original Variety",
                    "New Variety"
                ],
                "keys": [
                    "field_name",
                    "original_variety",
                    "new_variety"
                ]
            }
        ]

    def get_croplist(self):
        return sorted(self.df["Crop Group"].unique())

    def get_varietylist(self):
        return sorted(self.df["Variety"].unique())

    def get_unitlist(self):
        return sorted(self.df["Units"].unique())

    def get_crop_variety_obj(self):
        crop_varieties = {}
        for crop in self.croplist:
            crop_varieties[crop] = self.df[self.df["Crop Group"]
                                           == crop]["Variety"].unique()
        return crop_varieties

    def get_fields(self):
        return self.df["Field Defined Name"].unique()

    def get_file_year(self):
        return self.df["Year"].unique()[0]

    def get_problem_fields_data(self):
        prob_fields = self.fields_with_problems

        df_to_return = self.df.loc[self.df['Field Defined Name'].isin(
            prob_fields)].sort_values(
                "Field Defined Name"
            )
        
        return df_to_return

    year = property(get_file_year)
    fields = property(get_fields)
    croplist = property(get_croplist)
    varietylist = property(get_varietylist)
    crop_variety_obj = property(get_crop_variety_obj)
    units = property(get_unitlist)

    problem_fields_data = property(get_problem_fields_data)

    # missing data properties
    def get_missing_seed(self):
        fields_missing_seed_df = pd.DataFrame(columns=self.df.columns)

        for field in self.fields:
            field_df = self.df[self.df["Field Defined Name"] == field]

            headings_present = field_df['Heading'].unique()
            crop = field_df["Crop Group"].iloc[0]
            seeds_subsection = field_df[field_df["Heading"]
                                        == "Seed / Plants"]
            seeds = seeds_subsection["Product Name"]
            variety = field_df['Variety'].iloc[0]
            seed_units_present = seeds_subsection["Units"].tolist()

            if "Seed / Plants" not in headings_present:
                self.append_list_to_problem_list(field)
                self.fields_missing_seed_list.append(field)
                self.fields_missing_item["missing_seed"].append(field)
                fields_missing_seed_df = fields_missing_seed_df.append(
                    field_df)
            else:
                if crop == variety:

                    new_variety = seeds.tolist()[0]

                    if len(seeds.tolist()) > 1:
                        row_max = seeds_subsection[seeds_subsection['Quantity']
                                                   == seeds_subsection['Quantity'].max()]
                        new_variety = row_max['Product Name'].tolist()[0]

                    self.log_change("variety", {
                        "field_name": field,
                        "original_variety": variety,
                        "new_variety": new_variety
                    })
                    field_df = field_df.assign(Variety=new_variety)
                    self.df.drop(
                        self.df[self.df["Field Defined Name"] == field].index, inplace=True)
                    self.df = self.df.append(field_df)

                # Checks units in the seeds to see if any conversions can be made
                for problem_obj in self.problem_units:
                    OLD_UNIT = problem_obj["old_unit"]
                    unit_CROPS = problem_obj["crops"]
                    NEW_UNIT = problem_obj["new_unit"]
                    CONVERSION_FACTOR = problem_obj["conversion"]
                    for unit_CROP in unit_CROPS:
                        if (unit_CROP in crop.lower()) & (any(OLD_UNIT in c for c in seed_units_present)):
                            field_df.loc[(field_df["Units"] == OLD_UNIT),
                                         "Quantity"] = field_df["Quantity"] * CONVERSION_FACTOR
                            field_df.loc[(field_df["Units"] == OLD_UNIT),
                                         "Av Field Unit Price GBP"] = field_df["Value GBP"] / field_df["Quantity"]
                            field_df.loc[(field_df["Units"] == OLD_UNIT),
                                         "Rate per Application Area ha"] = field_df["Quantity"] / field_df["Application Area ha"]
                            field_df.loc[(field_df["Units"] ==
                                          OLD_UNIT), "Units"] = NEW_UNIT
                            self.df.drop(
                                self.df[self.df["Field Defined Name"] == field].index, inplace=True)
                            self.log_change("unit", {
                                "crop": crop,
                                "original_unit": OLD_UNIT,
                                "new_unit": NEW_UNIT
                            })
                            self.df = self.df.append(field_df)

        return fields_missing_seed_df

    fields_missing_seed = property(get_missing_seed)

    def get_missing_fert(self):
        fields_missing_fert_df = pd.DataFrame(columns=self.df.columns)
        for field in self.fields:
            field_df = self.df[self.df["Field Defined Name"] == field]

            headings_present = field_df['Heading'].unique()
            crop = field_df["Crop Group"].iloc[0]

            if "Fertiliser" not in headings_present:
                should_there_be_fert = True
                for i in self.non_fert_crops:
                    if i.lower() in crop.lower():
                        should_there_be_fert = False

                if should_there_be_fert:
                    self.append_list_to_problem_list(field)
                    self.fields_missing_fert_list.append(field)
                    self.fields_missing_item["missing_fert"].append(field)
                    fields_missing_fert_df = fields_missing_fert_df.append(
                        field_df)

        return fields_missing_fert_df

    fields_missing_fert = property(get_missing_fert)

    def get_missing_chem(self):
        fields_missing_chem_df = pd.DataFrame(columns=self.df.columns)
        for field in self.fields:
            field_df = self.df[self.df["Field Defined Name"] == field]

            headings_present = field_df['Heading'].unique()

            if not (("Herbicides" in headings_present) and ("Fungicides" in headings_present)):
                if not ("Chemical" in headings_present):
                    self.append_list_to_problem_list(field)
                    self.fields_missing_chem_list.append(field)
                    self.fields_missing_item["missing_chem"].append(field)
                    fields_missing_chem_df = fields_missing_chem_df.append(field_df)

        return fields_missing_chem_df

    fields_missing_chem = property(get_missing_chem)

    def get_clean_fields(self):
        clean_fields_df = pd.DataFrame(columns=self.df.columns)
        for field in self.fields:
            if field not in self.fields_with_problems:
                field_df = self.df[self.df["Field Defined Name"] == field]
                clean_fields_df = clean_fields_df.append(field_df)
        return clean_fields_df

    clean_fields = property(get_clean_fields)

    # Methods

    def do_field_analysis(self):
        for field in self.fields:
            field_df = self.df[self.df["Field Defined Name"] == field]
            AREA = field_df["Application Area ha"].mode().to_list()[0]
            FGROUP = field_df["Field Group"].mode().to_list()[0]
            CROP = field_df["Crop Group"].mode().to_list()[0]
            VARIETY = field_df["Variety"].mode().to_list()[0]

            self.field_analysis[field] = {
                "area": AREA,
                "fgroup": FGROUP,
                "crop": CROP,
                "variety": VARIETY,
                "name": field
            }
        # TODO:- marge the field analysis objects into a dataframe for better analysis later on, such as area calculations

        self.field_analysis_df = pd.DataFrame.from_dict(self.field_analysis, orient="index")

    # Error Logging

    def log_change(self, change_type, change_object):

        def add_product_price_change(change_object):
            self.changes_made["product_price"].append({
                "product_name": change_object["product_name"],
                "price": change_object["price"]
            })

        def add_variety_change(change_object):
            self.changes_made["variety"].append({
                "field_name": change_object["field_name"],
                "original_variety": change_object["original_variety"],
                "new_variety": change_object["new_variety"]
            })

        def add_unit_change(change_object):
            self.changes_made["unit"].append({
                "crop": change_object["crop"],
                "original_unit": change_object["original_unit"],
                "new_unit": change_object["new_unit"]
            })

        changes_functions = {
            "product_price": add_product_price_change, "variety": add_variety_change, "unit": add_unit_change}

        changes_functions[change_type](change_object)

    def append_list_to_problem_list(self, field):
        if field not in self.fields_with_problems:
            self.fields_with_problems.append(field)

    # Price checks

    def check_product_prices(self):
        df2 = pd.DataFrame(
            {'Product Name': self.df["Product Name"].unique()})

        df2['unit prices'] = [list(set(self.df['Av Field Unit Price GBP'].loc[self.df['Product Name'] == x['Product Name']]))
                              for _, x in df2.iterrows()]

        # complete_products = pd.DataFrame(columns=df.columns)
        missing_prices = pd.DataFrame(columns=df2.columns)

        df3 = pd.DataFrame(columns=self.df.columns)

        for index, row in df2.iterrows():
            rows_to_add = self.df[self.df["Product Name"]
                                  == row["Product Name"]]
            if 0 in row["unit prices"]:
                if len(row["unit prices"]) > 1:
                    row["unit prices"].remove(0)
                    new_price = row["unit prices"][0]
                    self.log_change("product_price", {"product_name": row["Product Name"],
                                                      "price": new_price})
                    rows_to_add.loc[(rows_to_add['Av Field Unit Price GBP']
                                     == 0), 'Av Field Unit Price GBP'] = new_price
                    rows_to_add.loc[(rows_to_add['Value GBP'] == 0),
                                    'Value GBP'] = rows_to_add["Av Field Unit Price GBP"] * rows_to_add["Quantity"]
                else:
                    missing_prices = missing_prices.append(row)
            df3 = df3.append(rows_to_add)

        self.df = df3
        self.missing_prices = missing_prices

    def contents_page_format(self, book):
        contents_sheet = book.create_sheet("Data Verification", 0)

        book_sheets = [
            {
                "name": "Summary Page",
                "desc": "A summary of the data missing key info; the unique varieties per crop; area summary by crop and variety; lists of the fields missing key info"
            },
            {
                "name": "Change Logs",
                "desc": "Changes made to the data will show on this page, this is to keep track of anything the program did and should be checked thoroughly to make sure the changes are sensible."
            },
            {
                "name": "Missing Seed",
                "desc": "All the data associated with fields that are missing seed are included on this page."
            },
            {
                "name": "Missing Fert",
                "desc": "All the data associated with fields that are missing fert are included on this page."
            },
            {
                "name": "Missing Chem",
                "desc": "All the data associated with fields that missing fert are included on this page."
            },
            {
                "name": "Complete Data",
                "desc": "Any data associated with fields that contain all of the key info. This will include products that are missing price."
            },
            {
                "name": "Products Missing Price",
                "desc": "A list of products that could not have their price inferred."
            },
            {
                "name": "Original Data",
                "desc": "A copy of the original data uploaded should it need to be referred to."
            },
            {
                "name": "Outputs",
                "desc": "Any data labelled as outputs in the original file, doesn't have a huge amount of success so expect to be empty."
            },
            {
                "name": "Inputs",
                "desc": "A list of rows that are ready to have info put in for the fields that are missing key info."
            }
        ]

        contents_sheet['A1'] = "Data Verification"
        contents_sheet['A3'] = "This spreadsheet contains the cleaned and checked data for the year indicated in the name of the workbook."

        contents_sheet['A5'] = "The following sheets are included in this workbook:"
        
        row = 6
        col = 1
        
        for sheet in book_sheets:
            contents_sheet.cell(column=col, row=row, value=sheet["name"])
            contents_sheet.cell(column=col+1, row=row, value=sheet["desc"])
            row += 1

        contents_sheet.cell(column=col, row=row, value="Please see individual pages for more info as to how to understand this document.")

        return book

    def methods_page_format(self, book):
        methods_sheet = book.create_sheet("Method", 1)

        methods_sheet["A1"] = "Data Verification Steps"
        methods_sheet["A2"] = "Below is a list of steps that should be followed to understand and use this document correctly."

        steps = [
            "Summary Page",
            """
            Check summary page to see the number of fields that are missing seed, fert or chem. As a rule of thumb, if it's over 50% (top left) then 
            nothing more should be done and the data verification will be done in two steps
            """,
            "Check the varieties listed there make sense, you'll get to know common names but worth a check here and there to make sure they are of the correct crop",
            "Check the units listed are only kg, g, t, L, mL; if any others are present then either convert or separate into a different sheet and label appropriately",
            "Change Logs",
            "Check that the changes make sense, mainly where new varieties have been selected",
            "Missing Info",
            "The following pages have all the rows associated with any field missing that info. If a field is missing both seed and fert it will appear on both pages, so it will be duplicated.",
            "Use these pages as reference, to check if the rows supplied look like any kind of contract spraying (typically 1 or two rows of chemicals per field)",
            "Use the Needs Inputs page to combine any of the missing field data when answers come back, this page doesn't have duplicated data and inputs can be copied straight in.",
            "Complete Data",
            "Checks here should be: units, varieties then prices. Units need to be on the list above, varieties must not be similar to the crop, they should be a distinct variety name.",
            "A list of the products with no price can be found on the Products Missing Price.",
            """
            It's important to check the farm's price check data (if there is some) to see if these prices can be filled in. 
            Prices should ideally be from the same harvest year, however you can go back 1 year for a price if it is not present for the current harvest year. 
            So in 2021, prices from 2020 and 2021 are acceptable.
            """,
            """
            Generally, if there any more than 10 rows left without a price they should be moved to a new sheet and labelled 
            appropriately because it is awkward and time consuming to change many rows on the platform.
            """,
            "Original Data",
            "Here for reference.",
            "Outputs",
            "Not implemented yet.",
            "Inputs",
            "When the farm's data verification has been returned the info can be put in here. Rates, dates, unit prices and product names, then value and quantity can be calculated.",
            "For seed rows, the product name can be either the variety there or, if it was not labelled correctly, the new seed planted that the farm should have provided.",
            "Often the farm will provide more than 1 fertiliser product/application, just copy the rows where appropriate.",
            "Needs Inputs",
            "The completed rows from Inputs can be copied into here and then the same checks that were completed on Complete Data can be done here (units, varieties, prices etc)."
        ]

        row = 4
        col = 1
        
        for step in steps:
            methods_sheet.cell(column=col, row=row, value=step)
            row += 1

        return book

    def summary_page_format(self, book):
        
        no_of_fields = self.fields.size

        summary_sheet = book.create_sheet("Summary Page", 0)
        summary_sheet['A1'] = "Data Summary"
        summary_sheet['A2'] = "Number of fields:"
        summary_sheet['B2'] = no_of_fields

        summary_sheet['A4'] = "Number of fields missing seed:"
        no_miss_seed = len(self.fields_missing_item["missing_seed"])
        perc_miss_seed = (no_miss_seed / no_of_fields)
        summary_sheet['B4'] = no_miss_seed
        summary_sheet['B5'] = perc_miss_seed
        summary_sheet['B5'].number_format = '0%'

        summary_sheet['A7'] = "Number of fields missing fert:"
        no_miss_fert = len(self.fields_missing_item["missing_fert"])
        perc_miss_fert = (no_miss_fert / no_of_fields)
        summary_sheet['B7'] = no_miss_fert
        summary_sheet['B8'] = perc_miss_fert
        summary_sheet['B8'].number_format = '0%'

        summary_sheet['A10'] = "Number of fields missing chem:"
        no_miss_chem = len(self.fields_missing_item["missing_chem"])
        perc_miss_chem = (no_miss_chem / no_of_fields)
        summary_sheet['B10'] = no_miss_chem
        summary_sheet['B11'] = perc_miss_chem
        summary_sheet['B11'].number_format = '0%'

        row = 13
        col = 1
        for key in self.crop_variety_obj:
            summary_sheet.cell(column=col, row=row, value=key)
            separator = ', '
            col_value = separator.join(self.crop_variety_obj[key])
            summary_sheet.cell(column=col+1, row=row, value=col_value)
            row += 1

        #??List the areas associated with crops etc

        col = 1
        row += 2

        summary_sheet.cell(row=row, column=col, value="Area summary")
        row += 1

        summary_sheet.cell(row=row, column=col, value="By Crop")
        summary_sheet.cell(row=row, column=col+1, value="Area (ha)")
        row += 1 
        for crop in self.croplist:
            summary_sheet.cell(row=row, column=col, value=crop)
            col += 1
            summary_sheet.cell(row=row, column=col, value=self.field_analysis_df[self.field_analysis_df["crop"] == crop]['area'].sum())
            row += 1
            col += -1

        row += 1
        col = 1

        summary_sheet.cell(row=row, column=col, value="By Variety")
        summary_sheet.cell(row=row, column=col+1, value="Area (ha)")
        row += 1 
        for variety in self.varietylist:
            summary_sheet.cell(row=row, column=col, value=variety)
            summary_sheet.cell(row=row, column=col + 1, value=self.field_analysis_df[self.field_analysis_df["variety"] == variety]['area'].sum())
            row += 1

        col = 1
        row += 1
        summary_sheet.cell(row=row, column=col, value="Units in file")
        col += 1
        sep = ', '
        summary_sheet.cell(row=row, column=col, value=sep.join(self.units))

        # List problem field off to the side

        row = 1
        col = 5
        for key in self.fields_missing_item:
            # if len(self.fields_missing_item[key]) > 0:
            summary_sheet.cell(row=row, column=col, value=key)
            row += 1
            for item in self.fields_missing_item[key]:
                summary_sheet.cell(column=col, row=row, value=item)
                row += 1
            row = 1
            col += 2

        return book

    def change_logs_format(self, book):
        change_logs = book.create_sheet("Change Logs", 1)
        change_logs['A1'] = "Data Adjustment Logs"
        change_logs['A2'] = "The following changes were made to the data by the checker, please take a careful look to make sure they all make sense:"
        change_logs['A3'] = "Common errors here include: selecting a cover crop as the main variety."

        row = 5
        column = 1
        for change in self.adjustment_obj:
            if change["name"] in self.changes_made:
                change_logs.cell(row=row, column=column,
                                 value=change["title"])
                row += 1
                for heading in change["headings"]:
                    change_logs.cell(row=row, column=column, value=heading)
                    column += 1
                row += 1
                column = 1
                for item in self.changes_made[change["name"]]:
                    for key in change["keys"]:
                        change_logs.cell(
                            row=row, column=column, value=item[key])
                        column += 1
                    row += 1
                    column = 1
                column = 1
                row += 2

        return book

    def inputs_page_format(self, book, year, writer):
        inputs_df = pd.DataFrame(columns=self.df.columns)

        input_objs = [
            {
                "name": "Missing Seed",
                "list": self.fields_missing_seed_list,
                "cat_name": "Seed / Plants"
            },
            {
                "name": "Missing Fertiliser",
                "list": self.fields_missing_fert_list,
                "cat_name": "Fertiliser"
            },
            {
                "name": "Missing Chemical",
                "list": self.fields_missing_chem_list,
                "cat_name": "Chemical"
            }
        ]
        for input_type in input_objs:
            inputs_df.append(
                {"Heading Category": input_type["name"]}, ignore_index=True)
            for field in input_type["list"]:
                obj_to_insert = {
                    "Field Defined Name": self.field_analysis[field]["name"],
                    "Field Group": self.field_analysis[field]["fgroup"],
                    "Application Area ha": self.field_analysis[field]["area"],
                    "Crop Group": self.field_analysis[field]["crop"],
                    "Variety": self.field_analysis[field]["variety"],
                    "Heading Category": "Variable Costs",
                    "Heading": input_type["cat_name"],
                    "Status": "Completed",
                    "Year": str(round(year))
                }

                # append row to the dataframe
                inputs_df = inputs_df.append(
                    obj_to_insert, ignore_index=True)
            inputs_df.append({}, ignore_index=True)

        inputs_df.to_excel(writer, "Inputs Page")

        return book, writer

    def get_data_for_verification(self):
        data_list = []
        for key in self.fields_missing_item:
            data_list.append({
                "name": key,
                "fields": self.fields_missing_item[key]
            })
        data_list.append({
            "name": "missing_product_price",
            "products": self.missing_prices["Product Name"].unique()
        })
        return data_list

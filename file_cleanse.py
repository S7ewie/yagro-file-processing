import pandas as pd
from data_verification_file import DataVerificationFile
from single_year_file import SingleYearFile
from collections import defaultdict
from openpyxl import Workbook

class FileCleanse:
    # Properties
    def __init__(self, dataframe=pd.DataFrame()):
        self.all_years_df = dataframe
        self.outputs_info = pd.DataFrame()
        self.rebate_info = pd.DataFrame()
        self.separated_crops = {}
        self.changes_made = defaultdict(list)
        self.incomplete_data = []
        self.filename = ""
        self.directory = ""
        self.mandatory_headings = ["seed", "fertiliser", "herbicide"]
        self.dvf = DataVerificationFile()
        self.validity = True

    @property
    def all_years_df(self):
        return self._all_years_df

    @all_years_df.setter
    def all_years_df(self, new_df: pd.DataFrame):
        new_df, validity = self.column_name_checks(new_df)
        self.validity = validity
        print("File is valid: ", validity)
        if validity:
            # First drop any columns with nothing in
            new_df.dropna(axis=1, how='all', inplace=True)

            # Drop rows with any missing values (takes care of subtotal rows)
            new_df.dropna(inplace=True)

            # Drop rows where quantity is 0
            new_df.drop(new_df[new_df["Quantity"] == 0].index, inplace=True)
            
            # Drop any rows to do with fixed costs
            new_df.drop(new_df[new_df["Heading Category"] ==
                            "Fixed Costs"].index, inplace=True)
            
            # Deal with rebates
            self.rebate_info = new_df[new_df["Heading"] == "Rebates"]
            new_df.drop(self.rebate_info.index, inplace=True)

            # Deal with outputs
            self.outputs_info = new_df[new_df["Heading Category"] == "Outputs"]
            new_df.drop(self.outputs_info.index, inplace=True)

            # Cast as floats incase of any random string numbers
            new_df["Av Field Unit Price GBP"] = new_df["Av Field Unit Price GBP"].astype(float)
            new_df["Quantity"] = new_df["Quantity"].astype(float)
            self._all_years_df = new_df
        else:
            self._all_years_df = pd.DataFrame()

    # properties of the farm
    def get_croplist(self):
        print("Columns below:")
        print(self.all_years_df.columns)
        return sorted(self.all_years_df["Crop Group"].unique())

    def get_productlist(self):
        return sorted(self.all_years_df["Product Name"].unique())

    def get_fgroups(self):
        return sorted(self.all_years_df["Field Group"].unique())

    def get_fnames(self):
        return sorted(self.all_years_df["Field Defined Name"].unique())

    def get_all_years(self):
        return sorted(self.all_years_df["Year"].unique())

    def get_separated_crops_list(self):
        return sorted(list(self.separated_crops.keys()))

    croplist = property(get_croplist)
    productlist = property(get_productlist)
    fgroups = property(get_fgroups)
    fnames = property(get_fnames)
    years = property(get_all_years)
    separated_crops_list = property(get_separated_crops_list)

    def column_name_checks(self, dataframe):
        if dataframe.empty:
            return dataframe, False
        else:
            print(dataframe.columns)
            mandatory_columns = [
                "Heading Category",
                "Product Name",
                "Field Group",
                "Crop Group",
                "Variety",
                "Rate per Application Area ha",
                "Application Area ha",
                "Quantity",
                "Av Field Unit Price GBP"
            ]
            for name in mandatory_columns:
                if name not in dataframe.columns:
                    print(f"Column not found: {name}")
                    if name == "Av Field Unit Price GBP":
                        if "Unit Price GBP" in dataframe.columns:
                            dataframe.rename(columns={"Unit Price GBP": "Av Field Unit Price GBP"}, inplace=True)
                            continue
                    elif name == "Rate per Application Area ha":
                        if "Quantity per Application Area ha" in dataframe.columns:
                            dataframe.rename(columns={"Quantity per Application Area ha": "Rate per Application Area ha"}, inplace=True)
                            continue
                    elif name == "Crop Group":
                        if "Crop" in dataframe.columns:
                            dataframe.rename(columns={"Crop": "Crop Group"}, inplace=True)
                            continue
                    elif name == "Quantity":
                        dataframe["Quantity"] = dataframe["Rate per Application Area ha"] * dataframe["Application Area ha"]
                        continue

                print("Does this get executed if there was one missing and it got changed")
                return dataframe, False
        return dataframe, True

    def adjust_df_for_year(self, year):
        return self.all_years_df[self.all_years_df["Year"] == year]

    def do_checks(self):
        print("I'ma doing the checks :angry-italian-hand-gestures:")

        self.dvf.add_fnames_for_checking(self.fnames)

        for year in self.years:

            working_df = SingleYearFile(self.adjust_df_for_year(year))

            # Farm name
            farm_name = self.filename
            macro_filename = "OUTPUTS/" + farm_name + " - FPU - " + \
                str(round(year)) + " - MACRO.xlsx"

            # Set up
            book = Workbook()
            writer = pd.ExcelWriter(macro_filename, engine='openpyxl')
            writer.book = book
            writer.sheets.update((ws.title, ws) for ws in book.worksheets)

            # Data pages
            working_df.check_product_prices()
            working_df.fields_missing_seed.to_excel(
                writer, "Missing Seed")
            working_df.fields_missing_fert.to_excel(
                writer, "Missing Fert")
            working_df.fields_missing_chem.to_excel(
                writer, "Missing Chem")
            working_df.clean_fields.to_excel(
                writer, "Complete Data")
            working_df.missing_prices.to_excel(
                writer, "Products Missing Price")
            working_df.original_data.to_excel(writer, "Original Data")

            # self.outputs_info.to_excel(writer, "Outputs")

            # Needs inputs
            working_df.problem_fields_data.to_excel(writer, "Needs Inputs")

            # Farm data needed for these pages
            working_df.do_field_analysis()
            book = working_df.summary_page_format(book)
            book = working_df.change_logs_format(book)
            book, writer = working_df.inputs_page_format(book, year, writer)

            # instructions and ref
            book = working_df.contents_page_format(book)
            book = working_df.methods_page_format(book)

            # add to data verification
            self.dvf.add_year(year, working_df.get_data_for_verification(), working_df.field_analysis)
            self.dvf.save(farm_name)

            std = book['Sheet']
            book.remove(std)

            writer.save()

    # Crop Separation

    def separate_crop(self, crop):
        self.separated_crops[crop] = self.all_years_df[self.all_years_df["Crop Group"] == crop]
        self.all_years_df.drop(
            self.all_years_df[self.all_years_df["Crop Group"] == crop].index, inplace=True)

    def delete_crop_from_dataframe(self, crop):
        self.all_years_df.drop(
            self.all_years_df[self.all_years_df["Crop Group"] == crop].index, inplace=True)

    def delete_fgroup_from_dataframe(self, fgroup):
        self.all_years_df.drop(
            self.all_years_df[self.all_years_df["Field Group"] == fgroup].index, inplace=True)

    def check_for_completeness(self):
        is_complete = True
        for year in self.years:
            year_df = self.all_years_df[self.all_years_df["Year"] == year]
            for heading in self.mandatory_headings:
                if not any(heading in c.lower() for c in year_df["Heading"].unique()):
                    self.log_incomplete_data(year, heading)
                    is_complete = False

        for year in self.years:
            output_year_df = self.outputs_info[self.outputs_info["Year"] == year]
            if len(output_year_df.index) == 0:
                self.log_incomplete_data(year, "output")
                is_complete = False
        return is_complete

    def log_incomplete_data(self, year, heading_missing):
        self.incomplete_data.append(
            (round(year), heading_missing.capitalize()))

    def rename_product(self, old_product, new_product):
        print("renaming your god damn product from ", old_product, " to ", new_product)
        self.changes_made["product"].append({"old_product_name": old_product, "new_product_name": new_product})
        self.all_years_df.loc[self.all_years_df[self.all_years_df["Product Name"]
                                                == old_product].index, 'Product Name'] = new_product
        print("renamed")

    def rename_field(self, old_field_name, new_field_name):
        print("renaming your god damn field from ", old_field_name, " to ", new_field_name)
        self.all_years_df.loc[self.all_years_df[self.all_years_df["Field Defined Name"]
                                                == old_field_name].index, 'Field Defined Name'] = new_field_name
        print("renamed!")

    def pre_commit(self):
        print("Running pre-commit")

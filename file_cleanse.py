import pandas as pd
from data_verification_file import DataVerificationFile
from single_year_file import SingleYearFile
from collections import defaultdict
from openpyxl import Workbook

class FileCleanse:
    # Properties
    def __init__(self):
        self.all_years_df = pd.DataFrame()
        self.outputs_info = pd.DataFrame()
        self.separated_crops = {}
        self.changes_made = defaultdict(list)
        self.incomplete_data = []
        self.filename = ""
        self.directory = ""
        self.mandatory_headings = ["seed", "fertiliser", "herbicide", "output"]
        self.dvf = DataVerificationFile()

    @property
    def all_years_df(self):
        return self._all_years_df

    @all_years_df.setter
    def all_years_df(self, new_df):
        if 'Quantity' in new_df.columns:
            new_df.dropna(inplace=True)
            new_df.drop(new_df[new_df["Quantity"] == 0].index, inplace=True)
            new_df.drop(new_df[new_df["Heading Category"] ==
                               "Fixed Costs"].index, inplace=True)
            self.outputs_info = new_df[new_df["Heading Category"] == "Outputs"]
            new_df.drop(self.outputs_info.index, inplace=True)
        self._all_years_df = new_df

    # properties of the farm
    def get_croplist(self):
        return self.all_years_df["Crop Group"].unique()

    def get_productlist(self):
        return self.all_years_df["Product Name"].unique()

    def get_fgroups(self):
        return self.all_years_df["Field Group"].unique()

    def get_all_years(self):
        return self.all_years_df["Year"].unique()

    def get_separated_crops_list(self):
        return list(self.separated_crops.keys())

    croplist = property(get_croplist)
    productlist = property(get_productlist)
    fgroups = property(get_fgroups)
    years = property(get_all_years)
    separated_crops_list = property(get_separated_crops_list)

    def adjust_df_for_year(self, year):
        return self.all_years_df[self.all_years_df["Year"] == year]

    def add_to_dvf_file(self, dvf, stuff):
        pass

    def do_checks(self):
        print("I'ma doing the checks :angry-italian-hand-gestures:")

        for year in self.years:

            working_df = SingleYearFile(self.adjust_df_for_year(year))

            filename = self.filename + " - FPU - " + \
                str(round(year)) + " - MACRO.xlsx"

            book = Workbook()
            writer = pd.ExcelWriter(filename, engine='openpyxl')
            writer.book = book

            writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

            working_df.check_product_prices()
            working_df.do_field_analysis()
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

            book = working_df.summary_page_format(book, year)
            book, writer = working_df.inputs_page_format(book, year, writer)

            self.dvf.add_year(year, working_df.get_data_for_verification())

            std = book['Sheet']
            book.remove(std)

            writer.save()

        # dvf_filename = self.filename + " - Data Verification.xlsx"
        # DVF_book.save(dvf_filename)

    # Crop Separation

    def separate_crop(self, crop):
        self.separated_crops[crop] = self.all_years_df[self.all_years_df["Crop Group"] == crop]
        self.all_years_df.drop(
            self.all_years_df[self.all_years_df["Crop Group"] == crop].index, inplace=True)

    def delete_crop_from_dataframe(self, crop):
        self.all_years_df.drop(
            self.all_years_df[self.all_years_df["Crop Group"] == crop].index, inplace=True)

    def check_for_completeness(self):
        is_complete = True
        for year in self.years:
            year_df = self.all_years_df[self.all_years_df["Year"] == year]
            for heading in self.mandatory_headings:
                if not any(heading in c.lower() for c in year_df["Heading"].unique()):
                    self.log_incomplete_data(year, heading)
                    is_complete = False
        return is_complete

    def log_incomplete_data(self, year, heading_missing):
        self.incomplete_data.append(
            (round(year), heading_missing.capitalize()))

    def rename_product(self, old_product, new_product):
        self.all_years_df.loc[self.all_years_df[self.all_years_df["Product Name"]
                                                == old_product].index, 'Product Name'] = new_product

    def pre_commit(self):
        print("Running pre-commit")
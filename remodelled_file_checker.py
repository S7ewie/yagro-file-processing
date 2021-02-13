import tkinter as tk
from PIL import Image, ImageTk
from itertools import count
import tkinter.filedialog
from tkinter import ttk
from openpyxl import Workbook
import pandas as pd
import math
from collections import defaultdict
from single_year_file import SingleYearFile


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

            # self.dvf.add_year(working_df.get_data_for_verification())

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


class DataVerificationFile:

    def __init__(self):
        self.workbook = Workbook()


class SampleFiles:
    def __init__(self):
        self.sample_product_applications_columns = ["Field Group", "Heading Category", "Heading", "Status", "Product Name", "Quantity", "Units", "Value GBP",
                                                    "Actual/Issued Date", "Application Area ha", "Av Field Unit Price GBP", "Crop Group", "Field Defined Name", "Rate per Application Area ha", "Variety", "Year"]
        self.sample_yield_file_columns = ["Field Group", "Field Name", "Harvest Area (Ha)", "Crop", "Variety", "Harvest Year",
                                          "Yield", "Quantity", "Unit", "Moisture", "Quality / Grade", "Harvest Date", "Yield Source", "Record Date"]

    def export_file(self, doc_type):
        doc_types = {"gatekeeper": self.sample_product_applications_columns,
                     "yield": self.sample_yield_file_columns}
        df_to_export = pd.DataFrame(columns=doc_types[doc_type])
        writer = pd.ExcelWriter(f'Sample-{doc_type}-columns.xslx')
        df_to_export.to_excel(writer, "Sample file")
        writer.save()


class GuiApplication:
    def __init__(self, root):
        self.master = root
        self.YAGRO_GREEN = '#006838'
        self.dataframeObj = FileCleanse()

        root.configure(background=self.YAGRO_GREEN)

        images_frame = tk.Frame(self.master)
        images_frame.pack(padx=0, pady=0, fill='x')

        images_inner_frame = tk.Frame(images_frame)
        images_inner_frame.pack()

        path = 'YAGROPLSLOGO.png'
        im = Image.open(path)
        img = ImageTk.PhotoImage(im, master=root)
        panel = tk.Label(images_inner_frame, image=img)
        panel.grid(row=0, column=1)

        # Choose file

        file_choose_frame = tk.Frame(root)
        file_choose_frame.pack(padx=0, pady=0, fill='x')

        file_inner_frame = tk.Frame(file_choose_frame)
        file_inner_frame.pack()

        choose_file_lbl = tk.Label(file_inner_frame, text="Choose File Here")
        choose_file_lbl.grid(row=0, column=0, padx=5, pady=15)

        open_csv_button = tk.Button(file_inner_frame, text='Upload csv', command=self.UploadAction,
                                    activebackground=self.YAGRO_GREEN, activeforeground="#fff")
        open_csv_button.grid(row=0, column=1, padx=5, pady=5)

        file_entry_lbl = tk.Label(file_inner_frame, text="Enter Farm Name")
        file_entry_lbl.grid(row=0, column=2, padx=5, pady=5)

        self.filename_entry = tk.Entry(file_inner_frame, exportselection=0)
        self.filename_entry.grid(row=0, column=3, padx=5, pady=5)

        # File Details

        file_details = tk.Frame(root)
        file_details.pack(padx=0, pady=0, fill='x')

        file_details_holder = tk.Frame(file_details)
        file_details_holder.pack()

        file_details_inner_frame = tk.Frame(file_details_holder)
        file_details_inner_frame.grid(row=0, column=0, padx=5)

        file_name_label_label = tk.Label(
            file_details_inner_frame, text="File name:")
        file_name_label_label.grid(row=0, column=0, padx=5, pady=5)

        self.file_name_label = tk.Label(file_details_inner_frame,
                                        text="Upload file above")
        self.file_name_label.grid(row=0, column=1, padx=5, pady=5)

        choose_file_type_lbl = tk.Label(
            file_details_inner_frame, text="File type:")
        choose_file_type_lbl.grid(row=1, column=0, padx=5, pady=5)

        OPTIONS = [
            "Gatekeeper",
            "Muddy Boots"
        ]

        initial_type = tk.StringVar(root)
        initial_type.set(OPTIONS[0])  # default value

        file_type_dropdown = tk.OptionMenu(
            file_details_inner_frame, initial_type, *OPTIONS)
        file_type_dropdown.grid(row=1, column=1, padx=5, pady=5)

        sample_files_inner_frame = tk.Frame(file_details_holder)
        sample_files_inner_frame.grid(row=0, column=1, padx=5)

        sample_files_lbl = tk.Label(
            sample_files_inner_frame, text="Download a sample file:")
        sample_files_lbl.grid(row=0, column=0, pady=5)

        SAMPLE_FILES = [
            "Product Applications",
            "Yield"
        ]

        initial_type = tk.StringVar(root)
        initial_type.set(SAMPLE_FILES[0])  # default value

        self.sample_file_type_dropdown = tk.OptionMenu(
            sample_files_inner_frame, initial_type, *SAMPLE_FILES)
        self.sample_file_type_dropdown.grid(row=1, column=0, padx=5, pady=5)

        sample_file_download_btn = tk.Button(
            sample_files_inner_frame, text="Download")
        sample_file_download_btn.grid(row=2, column=0, padx=5, pady=5)

        # List Boxes

        box_frames = tk.Frame(root)
        box_frames.pack(padx=0, pady=10, fill="x")

        style = ttk.Style()
        style.theme_create('pastel', settings={
            ".": {
                "configure": {
                    "background": '#fff',  # All except tabs
                    "font": 'red'
                }
            },
            "TNotebook": {
                "configure": {
                    "background": '#fff',  # Your margin color
                    # margins: left, top, right, separator
                    "tabmargins": [2, 2, 2, 2],
                }
            },
            "TNotebook.TFrame": {
                "configure": {
                    "background": "#234e12"
                }
            },
            "TNotebook.Tab": {
                "configure": {
                    "background": '#eee',  # tab color when not selected
                    # [space between text and horizontal tab-button border, space between text and vertical tab_button border]
                    "padding": [10, 2],
                    "foreground": "#000"
                },
                "map": {
                    # Tab color when selected
                    "background": [("selected", self.YAGRO_GREEN)],
                    "expand": [("selected", [1, 1, 1, 0])],  # text margins
                    "foreground": [("selected", "#fff")],
                }
            }
        })

        style.theme_use("pastel")

        tab_control = ttk.Notebook(box_frames)
        tab_control.pack(pady="5")

        # Completeness Checks

        completeness_check_tab = ttk.Frame(tab_control)
        tab_control.add(completeness_check_tab, text='Completeness Checks')

        complete_check_info_frame = tk.Frame(completeness_check_tab)
        complete_check_info_frame.pack()

        self.completeness_check_btn = tk.Button(
            complete_check_info_frame, text="Check file for completeness", command=self.check_completeness)
        self.completeness_check_btn.grid(row=0, column=0, padx=5, pady=5)

        self.completeness_check_lbl = tk.Label(
            complete_check_info_frame, text="Waiting for file", wraplength=300, anchor="e", justify=tk.LEFT)
        self.completeness_check_lbl.grid(row=0, column=1, padx=5, pady=5)

        self.completeness_check_table_frame = tk.Frame(completeness_check_tab)
        self.completeness_check_table_frame.pack()

        # Crop Management

        tab1 = ttk.Frame(tab_control)
        tab_control.add(tab1, text='Crop Management')

        box_inner_frames = tk.Frame(tab1)
        box_inner_frames.pack()

        crops_label = tk.Label(box_inner_frames, text="Crops")
        crops_label.grid(row=0, column=0, padx=5, pady=10)

        self.my_listbox = tk.Listbox(box_inner_frames, selectmode=tk.MULTIPLE)
        self.my_listbox.grid(row=1, column=0, padx=5, pady=10)

        crops_to_sep_label = tk.Label(
            box_inner_frames, text="Crops To Separate")
        crops_to_sep_label.grid(row=0, column=1, padx=5, pady=10)

        self.sep_listbox = tk.Listbox(box_inner_frames, selectmode=tk.MULTIPLE)
        self.sep_listbox.grid(row=1, column=1, padx=5, pady=10)

        deleted_crops_label = tk.Label(box_inner_frames, text="Deleted Crops")
        deleted_crops_label.grid(row=0, column=2, padx=5, pady=10)

        self.deleted_listbox = tk.Listbox(
            box_inner_frames, selectmode=tk.MULTIPLE)
        self.deleted_listbox.grid(row=1, column=2, padx=5, pady=10)

        # Crop Commands

        crop_btn_frame = tk.Frame(box_inner_frames)
        crop_btn_frame.grid(row=2, column=0, padx=5, pady=10)

        self.delete_button = tk.Button(
            crop_btn_frame, text="Delete", command=self.delete)
        self.delete_button.grid(row=0, column=0, padx=5, pady=5)

        self.separate_button = tk.Button(
            crop_btn_frame, text="Separate", command=self.separate)
        self.separate_button.grid(row=0, column=1, padx=5, pady=5)

        # Move Back Commands

        # moveback_btn_frame = tk.Frame(box_inner_frames)
        # moveback_btn_frame.grid(row=2, column=1, padx=5, pady=10)

        # moveback_button = tk.Button(
        #     moveback_btn_frame, text="Move Back", command=delete)
        # moveback_button.grid(row=0, column=0, padx=5, pady=5)

        # Undelete Commands

        # undelete_btn_frame = tk.Frame(box_inner_frames)
        # undelete_btn_frame.grid(row=2, column=2, padx=5, pady=10)

        # undelete_button = tk.Button(
        #     undelete_btn_frame, text="Undo", command=sedelete)
        # undelete_button.grid(row=0, column=0, padx=5, pady=5)

        # Field Group Management

        fgroup_tab = ttk.Frame(tab_control)
        tab_control.add(fgroup_tab, text="Field Groups")

        fgroup_inner_frame = tk.Frame(fgroup_tab)
        fgroup_inner_frame.pack()

        self.fgroup_listbox = tk.Listbox(
            fgroup_inner_frame, selectmode=tk.SINGLE)
        self.fgroup_listbox.grid(row=0, column=0, padx=5, pady=5)

        self.fgroup_btn = tk.Button(fgroup_inner_frame,
                                    text="Delete Field Group")
        self.fgroup_btn.grid(row=1, column=0, pady=5)

        self.fgroup_removed_listbox = tk.Listbox(
            fgroup_inner_frame, selectmode=tk.SINGLE)
        self.fgroup_removed_listbox.grid(row=0, column=1, padx=5, pady=5)

        self.fgroup_removed_btn = tk.Button(fgroup_inner_frame,
                                            text="Move Field Group Back")
        self.fgroup_removed_btn.grid(row=1, column=1, pady=5)

        # Product Management

        product_tab = ttk.Frame(tab_control)
        tab_control.add(product_tab, text="Products")

        product_inner_frames = tk.Frame(product_tab)
        product_inner_frames.pack()

        product_listbox_inner_frame = tk.Frame(product_inner_frames)
        product_listbox_inner_frame.grid(row=0, column=0)

        self.product_listbox = tk.Listbox(
            product_listbox_inner_frame, selectmode=tk.SINGLE)
        self.product_listbox.grid(row=0, column=0)

        product_editing_inner_frame = tk.Frame(product_inner_frames)
        product_editing_inner_frame.grid(row=0, column=1)

        self.product_entry = tk.Entry(product_editing_inner_frame)
        self.product_entry.grid(row=0, column=0)

        self.product_btn = tk.Button(product_editing_inner_frame,
                                     text="Submit new product name")
        self.product_btn.grid(row=1, column=0, pady=5)

        # Check commands

        command_master_frame = tk.Frame(root)
        command_master_frame.pack(padx=0, pady=0, fill="x")

        deleted_crops_label = tk.Label(
            command_master_frame, text="Commands and dat")
        deleted_crops_label.pack(padx=0, pady=5, fill="x")

        check_cmds_frame = tk.Frame(command_master_frame, padx=5, pady=5)
        check_cmds_frame.pack(padx=0, pady=10)

        self.run_button = tk.Button(
            check_cmds_frame, text="Run Checks", command=self.run_checks)
        self.run_button.grid(row=0, column=0, padx=5, pady=5)

        self.print_tings_button = tk.Button(
            check_cmds_frame, text="Print some tings", command=self.print_some_tings)
        self.print_tings_button.grid(row=0, column=2, padx=5, pady=5)

    def UploadAction(self, event=None):
        self.reset_listbox()
        filename = tkinter.filedialog.askopenfilename()
        # directory = tkinter.filedialog.askdirectory()
        df = pd.read_csv(filename)
        self.dataframeObj.all_years_df = df
        # self.dataframeObj.filename = directory
        self.file_name_label.config(text=filename)
        self.completeness_check_lbl.config(
            text="Waiting to check...")
        self.prime_listboxes_for_liftoff()

    def prime_listboxes_for_liftoff(self):
        self.universal_listbox_update(
            self.my_listbox, self.dataframeObj.croplist)
        self.universal_listbox_update(
            self.product_listbox, self.dataframeObj.productlist)
        self.universal_listbox_update(
            self.fgroup_listbox, self.dataframeObj.fgroups)

    def universal_listbox_update(self, listbox, list_to_add):
        for item in sorted(list_to_add):
            listbox.insert(tk.END, item)

    def reset_listbox(self):
        self.my_listbox.delete(0, tk.END)

    def delete(self):
        sel = self.my_listbox.curselection()
        for index in sel[::-1]:
            self.dataframeObj.delete_crop_from_dataframe(
                self.my_listbox.get(index))
            self.my_listbox.delete(index)

    def separate(self):
        sel = self.my_listbox.curselection()
        for index in sel[::-1]:
            self.dataframeObj.separate_crop(self.my_listbox.get(index))
            self.my_listbox.delete(index)
            self.universal_listbox_update(
                self.sep_listbox, self.dataframeObj.separated_crops_list)

    def run_checks(self):
        if self.dataframeObj.all_years_df.shape[0] != 0:
            print("running checks")
            self.dataframeObj.filename = self.filename_entry.get()
            self.dataframeObj.do_checks()
            print("we're all done!")

    def download_sample_file(self):
        filetype = self.sample_file_type_dropdown

    def add_incomplete_data_listbox(self, errors):
        error_listbox = tk.Listbox(
            self.completeness_check_table_frame, selectmode=tk.NONE)
        error_listbox.pack()
        self.update_incomplete_listbox(error_listbox, errors)

    def update_incomplete_listbox(self, listbox, errors):
        for item in errors:
            listbox.insert(tk.END, (str(item[0]) + ": " + item[1]))

    def check_completeness(self):
        if self.dataframeObj.all_years_df.shape[0] != 0:
            self.completeness_check_lbl.config(
                text="Checking file for completeness...")
            if self.dataframeObj.check_for_completeness():
                self.completeness_check_lbl.config(text="You're all set!")
            else:
                self.completeness_check_lbl.config(
                    text="Looks like the data isn't all there, take a look below to see what's missing.")
                self.add_incomplete_data_listbox(
                    self.dataframeObj.incomplete_data)

        else:
            self.completeness_check_lbl.config(
                text="Looks like there's no file uploaded")

    def rename_product(self):
        old_product_name = self.product_listbox.get(tk.ANCHOR)
        new_product_name = self.product_entry.get()
        self.dataframeObj.rename_product(old_product_name, new_product_name)
        self.prime_listboxes_for_liftoff()

    def print_some_tings(self):
        print(self.dataframeObj.changes_made)
        if self.dataframeObj.all_years_df.shape[0] != 0:
            print(self.dataframeObj.croplist)
            print(self.dataframeObj.separated_crops)
            print(self.dataframeObj.changes_made)


def execute_order_66():
    root = tk.Tk()
    root.title('YAGRO File Checker')
    root.geometry("800x750")
    GuiApplication(root)
    root.mainloop()


if __name__ == '__main__':
    execute_order_66()
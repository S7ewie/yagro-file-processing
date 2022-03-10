import tkinter as tk
from PIL import Image, ImageTk
import tkinter.filedialog
from tkinter import messagebox
from tkinter import ttk
import pandas as pd
from file_cleanse import FileCleanse
from sample_files import SampleFiles
from styles_and_what_not import YAGRO_GREEN
from online_farm_check_gui import OnlineChecker
from muddy_boots import MuddyBoots


class GuiApplication:
    def __init__(self, root):
        self.master = root
        self.dataframeObj = FileCleanse()
        self.sample_files = SampleFiles()
        self.muddy_boots_converter = MuddyBoots()

        root.configure(background=YAGRO_GREEN.colour)

        images_frame = tk.Frame(root)
        images_frame.pack(padx=0, pady=0, fill='x')

        images_inner_frame = tk.Frame(images_frame)
        images_inner_frame.pack()

        yagro_lbl = tk.Label(images_inner_frame, text="YAGRO")
        yagro_lbl.config(font=("Arial", 44))
        yagro_lbl.grid(row=0, column=0)

        master_notebook = tk.Frame(root)
        master_notebook.pack(padx=0, pady=5, fill='x')

        main_tab_control = ttk.Notebook(master_notebook)
        main_tab_control.pack(fill='x')

        file_checking_tab = ttk.Frame(main_tab_control)
        main_tab_control.add(file_checking_tab, text='File Checking')

        # Choose file

        file_choose_frame = tk.Frame(file_checking_tab)
        file_choose_frame.pack(padx=0, pady=0, fill='x')

        file_inner_frame = tk.Frame(file_choose_frame)
        file_inner_frame.pack()

        choose_file_lbl = tk.Label(file_inner_frame, text="Choose File Here")
        choose_file_lbl.grid(row=0, column=0, padx=5, pady=15)

        open_csv_button = tk.Button(file_inner_frame, text='Upload csv', command=self.UploadAction,
                                    activebackground=YAGRO_GREEN.colour, activeforeground="#fff")
        open_csv_button.grid(row=0, column=1, padx=5, pady=5)

        file_entry_lbl = tk.Label(file_inner_frame, text="Enter Farm Name")
        file_entry_lbl.grid(row=0, column=2, padx=5, pady=5)

        self.filename_entry = tk.Entry(file_inner_frame, exportselection=0)
        self.filename_entry.grid(row=0, column=3, padx=5, pady=5)

        # Check commands

        command_master_frame = tk.Frame(file_checking_tab)
        command_master_frame.pack(padx=0, pady=0, fill="x")

        check_cmds_frame = tk.Frame(command_master_frame, padx=5, pady=5)
        check_cmds_frame.pack(padx=0, pady=10)

        self.run_button = tk.Button(
            check_cmds_frame, text="Run Checks", command=self.run_checks)
        self.run_button.grid(row=0, column=0, padx=5, pady=5)

    def UploadAction(self, event=None):
        self.reset_listbox()
        filename = tkinter.filedialog.askopenfilename()
        if filename != '':
            # df = pd.read_csv(filename, thousands=',')
            print("LOADING FILE")
            df = pd.read_csv(filename)

            file_type = self.upload_file_type.get()
            print(file_type)
            
            if file_type == "Muddy Boots":
                print("Converting for muddy boots")
                df = self.muddy_boots_converter.clean_dataframe(df)

            self.dataframeObj = FileCleanse(dataframe=df)
            if len(self.dataframeObj.all_years_df.columns) == 0:
                self.show_message("Looks like there was a problem sorting the column names, check the file")
                return
            self.config_gui_on_upload(filename=filename)
            self.show_message("File uploaded successfully.")
        else:
            self.show_message("No file selected!")

    def config_gui_on_upload(self, filename=None):
        text_to_write = "Mulitfile" if filename == None else filename
        self.file_name_label.config(text=text_to_write)
        # self.completeness_check_lbl.config(
        #     text="Waiting to check...")
        self.prime_listboxes_for_liftoff()

    def prime_listboxes_for_liftoff(self, invalidate=True):
        print("HERE")
        self.universal_listbox_update(
            self.my_listbox, self.dataframeObj.croplist, invalidate=invalidate)
        print("BUT NOT HERE")
        self.universal_listbox_update(
            self.product_listbox, self.dataframeObj.productlist, invalidate=invalidate)
        self.universal_listbox_update(
            self.fgroup_listbox, self.dataframeObj.fgroups, invalidate=invalidate)
        self.universal_listbox_update(
            self.fname_listbox, self.dataframeObj.fnames, invalidate=invalidate)

    def universal_listbox_update(self, listbox, list_to_add, invalidate=False):
        if invalidate:
            listbox.delete(0, tk.END)
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
            self.show_message("Checks Complete")

    def download_sample_file(self):
        print("things")


        # self.sample_files.export_file(filetype)
        # self.show_message(f"Exported {filetype}!")

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
            # self.completeness_check_lbl.config(
            #     text="Checking file for completeness...")
            if self.dataframeObj.check_for_completeness():
                # self.completeness_check_lbl.config(text="You're all set!")
                print("nope")
            else:
                # self.completeness_check_lbl.config(
                #     text="Looks like the data isn't all there, take a look below to see what's missing.")
                self.add_incomplete_data_listbox(
                    self.dataframeObj.incomplete_data)

        else:
            # self.completeness_check_lbl.config(
            #     text="Looks like there's no file uploaded")
            print("yep")

    def rename_product(self):
        old_product_name = self.product_listbox.get(tk.ANCHOR)
        new_product_name = self.product_entry.get()
        self.dataframeObj.rename_product(old_product_name, new_product_name)
        self.prime_listboxes_for_liftoff()

    def rename_field(self):
        old_field_name = self.fname_listbox.get(tk.ANCHOR)
        new_field_name = self.fname_entry.get()
        self.dataframeObj.rename_field(old_field_name, new_field_name)
        self.prime_listboxes_for_liftoff()

    def delete_fgroup(self):
        sel = self.fgroup_listbox.curselection()
        for index in sel[::-1]:
            self.dataframeObj.delete_fgroup_from_dataframe(
                self.fgroup_listbox.get(index))
            self.fgroup_listbox.delete(index)

    def print_some_tings(self):
        print(self.dataframeObj.changes_made)
        if self.dataframeObj.all_years_df.shape[0] != 0:
            print(self.dataframeObj.croplist)
            print(self.dataframeObj.separated_crops)
            print(self.dataframeObj.changes_made)

    def show_message(self, message):
        messagebox.showinfo(
            title="Warning, Warning, High Voltage!", message=message)


def execute_order_66():
    root = tk.Tk()
    root.title('YAGRO File Checker')
    root.geometry("700x350")
    GuiApplication(root)
    root.mainloop()


if __name__ == '__main__':
    execute_order_66()

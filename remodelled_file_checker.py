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


class GuiApplication:
    def __init__(self, root):
        self.master = root
        self.dataframeObj = FileCleanse()
        self.sample_files = SampleFiles()

        root.configure(background=YAGRO_GREEN.colour)

        images_frame = tk.Frame(root)
        images_frame.pack(padx=0, pady=0, fill='x')

        images_inner_frame = tk.Frame(images_frame)
        images_inner_frame.pack()

        yagro_lbl = tk.Label(images_inner_frame, text="YAGRO")
        yagro_lbl.config(font=("Arial", 44))
        yagro_lbl.grid(row=0, column=0)

        # path = 'YAGROPLSLOGO.png'
        # im = Image.open(path)
        # img = ImageTk.PhotoImage(im, master=root)
        # panel = tk.Label(images_inner_frame, image=img)
        # panel.grid(row=0, column=1)

        master_notebook = tk.Frame(root)
        master_notebook.pack(padx=0, pady=5, fill='x')

        main_tab_control = ttk.Notebook(master_notebook)
        main_tab_control.pack(fill='x')

        file_checking_tab = ttk.Frame(main_tab_control)
        main_tab_control.add(file_checking_tab, text='File Checking')

        oneline_farm_tab = ttk.Frame(main_tab_control)
        main_tab_control.add(oneline_farm_tab, text='Online Farm Checking')

        # self.online_checking = OnlineChecker(oneline_farm_tab)

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

        open_multifile_button = tk.Button(file_inner_frame, text='Upload multi-file', command=self.MultiUploadAction,
                                          activebackground=YAGRO_GREEN.colour, activeforeground="#fff")
        open_multifile_button.grid(row=1, column=2, padx=5, pady=5)

        # File Details

        file_details = tk.Frame(file_checking_tab)
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

        box_frames = tk.Frame(file_checking_tab)
        box_frames.pack(padx=0, pady=0, fill="x")

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
                    "background": [("selected", YAGRO_GREEN.colour)],
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
            fgroup_inner_frame, selectmode=tk.MULTIPLE)
        self.fgroup_listbox.grid(row=0, column=0, padx=5, pady=5)

        self.fgroup_btn = tk.Button(fgroup_inner_frame,
                                    text="Delete Field Group", command=self.delete_fgroup)
        self.fgroup_btn.grid(row=1, column=0, pady=5)

        self.fgroup_removed_listbox = tk.Listbox(
            fgroup_inner_frame, selectmode=tk.SINGLE)
        self.fgroup_removed_listbox.grid(row=0, column=1, padx=5, pady=5)

        self.fgroup_removed_btn = tk.Button(fgroup_inner_frame,
                                            text="Move Field Group Back")
        self.fgroup_removed_btn.grid(row=1, column=1, pady=5)

        # Field Name Management

        field_name_tab = ttk.Frame(tab_control)
        tab_control.add(field_name_tab, text="Field Names")

        fname_inner_frame = tk.Frame(field_name_tab)
        fname_inner_frame.pack()

        self.fname_listbox = tk.Listbox(
            fname_inner_frame, selectmode=tk.SINGLE)
        self.fname_listbox.grid(row=0, column=0, padx=5, pady=5)

        self.fname_entry = tk.Entry(fname_inner_frame)
        self.fname_entry.grid(row=1, column=0)

        self.fname_btn = tk.Button(fname_inner_frame,
                                   text="Rename Field", command=self.rename_field)
        self.fname_btn.grid(row=2, column=0, pady=5)

        self.fname_changed_listbox = tk.Listbox(
            fname_inner_frame, selectmode=tk.SINGLE)
        self.fname_changed_listbox.grid(row=0, column=1, padx=5, pady=5)

        # changes_tree = ttk.Treeview(changes_inner_frame)

        # fname_change_tree['columns'] = ("Old Product Name", "New Product Name")

        # changes_tree.column("#0", width=0, stretch=tk.NO)
        # changes_tree.column("Old Product Name", anchor=tk.W, width=120)
        # changes_tree.column("New Product Name", anchor=tk.W, width=220)

        # changes_tree.heading("#0", text="", anchor=tk.W)
        # changes_tree.heading("Old Product Name", text="Old Product Name", anchor=tk.W)
        # changes_tree.heading("New Product Name", text="New Product Name", anchor=tk.W)

        # changes_tree.insert(parent='', index='end', iid=0, text="", values=("Spicey herb", "Mega Spicy Herb XL"))

        # changes_tree.pack()

        # NEEDS SOME WORK
        self.fname_removed_btn = tk.Button(fname_inner_frame,
                                           text="Undo Field Name Change")
        self.fname_removed_btn.grid(row=1, column=1, pady=5)

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
                                     text="Submit new product name", command=self.rename_product)
        self.product_btn.grid(row=1, column=0, pady=5)

        # Change Logs Management

        changes_tab = ttk.Frame(tab_control)
        tab_control.add(changes_tab, text="Change Logs")

        changes_inner_frame = tk.Frame(changes_tab)
        changes_inner_frame.pack()

        changes_tree = ttk.Treeview(changes_inner_frame)

        changes_tree['columns'] = ("Old Product Name", "New Product Name")

        changes_tree.column("#0", width=0, stretch=tk.NO)
        changes_tree.column("Old Product Name", anchor=tk.W, width=120)
        changes_tree.column("New Product Name", anchor=tk.W, width=220)

        changes_tree.heading("#0", text="", anchor=tk.W)
        changes_tree.heading("Old Product Name",
                             text="Old Product Name", anchor=tk.W)
        changes_tree.heading("New Product Name",
                             text="New Product Name", anchor=tk.W)

        changes_tree.insert(parent='', index='end', iid=0, text="", values=(
            "Spicey herb", "Mega Spicy Herb XL"))

        changes_tree.pack()
        # Check commands

        command_master_frame = tk.Frame(file_checking_tab)
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

    def MultiUploadAction(self, event=None):
        filenames = tkinter.filedialog.askopenfilenames()
        print(filenames)
        master_file = pd.DataFrame(
            columns=self.sample_files.sample_product_applications_columns)
        for file in filenames:
            df = pd.read_csv(file)
            if self.dataframeObj.column_name_checks(df)[1]:
                master_file = pd.concat([master_file, df])
            else:
                self.show_message(
                    "One or more of the files uploaded is not valid, please check the column headings carefully to make sure everything is there and it matches those in the sample file.")
                return
        self.dataframeObj = FileCleanse(dataframe=master_file)
        self.config_gui_on_upload()
        self.show_message("Files uploaded successfully.")

    def UploadAction(self, event=None):
        self.reset_listbox()
        filename = tkinter.filedialog.askopenfilename()
        if filename != '':
            # df = pd.read_csv(filename, thousands=',')
            df = pd.read_csv(filename)
            self.dataframeObj = FileCleanse(dataframe=df)
            self.config_gui_on_upload(filename=filename)
            self.show_message("File uploaded successfully.")
        else:
            self.show_message("No file selected!")

    def config_gui_on_upload(self, filename=None):
        text_to_write = "Mulitfile" if filename == None else filename
        self.file_name_label.config(text=text_to_write)
        self.completeness_check_lbl.config(
            text="Waiting to check...")
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

    def rename_field(self):
        old_field_name = self.fname_listbox.get(tk.ANCHOR)
        new_field_name = self.fname_entry.get()
        self.dataframeObj.rename_product(old_field_name, new_field_name)
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
    root.geometry("800x750")
    GuiApplication(root)
    root.mainloop()


if __name__ == '__main__':
    execute_order_66()

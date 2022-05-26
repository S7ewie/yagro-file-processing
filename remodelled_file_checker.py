import tkinter.filedialog
from tkinter import messagebox
import pandas as pd
from file_cleanse import FileCleanse
from muddy_boots import MuddyBoots


class GuiApplication:
    def __init__(self):
        self.dataframeObj = FileCleanse()
        self.muddy_boots_converter = MuddyBoots()

    def upload_action(self):
        filename = tkinter.filedialog.askopenfilename()
        if filename != '':
            # df = pd.read_csv(filename, thousands=',')
            print("LOADING FILE")
            df = pd.read_csv(filename)
            file_type = ""
            if file_type == "Muddy Boots":
                df = self.muddy_boots_converter.clean_dataframe(df)

            self.dataframeObj = FileCleanse(dataframe=df)
            if len(self.dataframeObj.all_years_df.columns) == 0:
                self.show_message("Looks like there was a problem sorting the column names, check the file")
                return
            self.show_message("File uploaded successfully.")
        else:
            self.show_message("No file selected!")

    def run_checks(self):
        if self.dataframeObj.all_years_df.shape[0] != 0:
            print("running checks")
            self.dataframeObj.filename = self.filename_entry.get()
            self.dataframeObj.do_checks()
            print("we're all done!")
            self.show_message("Checks Complete")

    def show_message(self, message):
        messagebox.showinfo(
            title="Warning, Warning, High Voltage!", message=message)


def execute_order_66():
    app = GuiApplication()
    app.upload_action()


if __name__ == '__main__':
    execute_order_66()

from tkinter import messagebox, filedialog as fd
import pandas as pd
from file_cleanse import FileCleanse
from muddy_boots import MuddyBoots
from datetime import datetime

class GuiApplication:
    def __init__(self):
        self.dataframeObj = FileCleanse()
        self.muddy_boots_converter = MuddyBoots()

    def upload_action(self):
        filename = fd.askopenfilename()
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
            return True
        self.show_message("No file selected!")
        return False

    def run_checks(self):
        if self.dataframeObj.all_years_df.shape[0] != 0:
            print("running checks")
            todays_date = datetime.today().strftime('%Y-%m-%d')
            self.dataframeObj.filename = f"{todays_date}-new-farm"
            self.dataframeObj.do_checks()
            print("we're all done!")
            self.show_message("Checks Complete")

    def show_message(self, message):
        messagebox.showinfo(
            title="Warning, Warning, High Voltage!", message=message)


def execute_order_66():
    app = GuiApplication()
    if app.upload_action():
        app.run_checks()


if __name__ == '__main__':
    execute_order_66()

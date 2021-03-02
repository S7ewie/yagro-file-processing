import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk
import pandas as pd
from styles_and_what_not import YAGRO_GREEN
from database_operations import DatabaseOperations

class OnlineChecker:
    def __init__(self, root):
        self.db_ops = DatabaseOperations()

        title_lbl = tk.Label(root, text="Choose a farm below to analyse the data that is on platform.", bg="#FFFFFF", wraplength=150)
        title_lbl.grid(row=0, column=0, padx=10, pady=10)

        self.farms_list_box = tk.Listbox(root, selectmode=tk.SINGLE, exportselection=0)
        self.farms_list_box.grid(row=1, column=0, padx=10, pady=10)
        self.farms_list_box.bind("<<ListboxSelect>>", self.farm_callback)

        self.years_list_box = tk.Listbox(root, selectmode=tk.SINGLE, exportselection=0)
        self.years_list_box.grid(row=1, column=1, padx=10, pady=10)

        self.prime_for_action()

    def prime_for_action(self):
        farms = self.db_ops.get_groups()
        self.universal_listbox_update(self.farms_list_box, farms, invalidate=True)

    def universal_listbox_update(self, listbox, list_to_add, invalidate=False):
        if invalidate:
            listbox.delete(0,tk.END)
        for item in sorted(list_to_add):
            listbox.insert(tk.END, item)

    def farm_callback(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            farm = event.widget.get(index)
            years = self.db_ops.get_years_for_group(farm)
            self.universal_listbox_update(self.years_list_box, years, invalidate=True)
        else:
            print("in the else statement")
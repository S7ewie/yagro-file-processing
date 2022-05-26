import pandas as pd
import os

class MuddyBoots:

    def __init__(self):
        self.wanted_columns = [
            "Field Name",
            "Crop",
            "Variety",
            "Cost Category",
            "Activity Date",
            "Product/Operation",
            "Treated Area",
            "Rate",
            "Rate Unit",
            "Total Cost"
        ]

        self.mandatory_columns = [
            "Heading Category",
            "Product Name",
            "Field Defined Name",
            "Crop Group",
            "Rate per Application Area ha",
            "Application Area ha",
            "Value GBP",
            "Actual/Issued Date",
            "Heading",
            "Units"
        ]
        pass


    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:

        if df is None:
            print("returning due to nil dataframe")
            return 
        
        print("about to pipe")
        df =  (
                df.pipe(self.column_name_check)
                .pipe(self.column_rename)
                .pipe(self.column_select)
                .pipe(self.filter_heading_category)
                .pipe(self.column_type_conversion)
                .pipe(self.split_unit_column)
                .pipe(self.column_generation)
        )

        return df
        

    def get_file(self, file:str) -> pd.DataFrame:
        cwd = os.getcwd()
        path = os.path.join(cwd, file)
        if not os.path.isfile(path):
            return None

        df = pd.read_csv(file)
        return df



    def column_name_check(self, df: pd.DataFrame) -> pd.DataFrame:

        if df is None:
            return None
        
        for column in self.wanted_columns:
            if column not in df.columns:
                print(f"Couldn't find column: {column}")
                return pd.DataFrame()
            
        return df


    def column_rename(self, df: pd.DataFrame) -> pd.DataFrame:

        if df is None:
            return None

        column_name_dict = {
            "Field Name": "Field Defined Name",
            "Crop": "Crop Group",
            "Cost Category": "Heading Category",
            "Activity Date": "Actual/Issued Date",
            "Product/Operation": "Product Name",
            "Treated Area": "Application Area ha",
            "Rate": "Rate per Application Area ha",
            "Rate Unit": "Units",
            "Total Cost": "Value GBP"
        }

        df = df.rename(columns=column_name_dict)

        return df

    def column_select(self, df: pd.DataFrame) -> pd.DataFrame:
        
        if df is None:
            return None

        safe_cols = []

        for x in self.mandatory_columns:
            if x in df.columns:
                safe_cols.append(x)

        df = df[safe_cols]

        return df

    def filter_heading_category(self, df: pd.DataFrame) -> pd.DataFrame:

        if df is None:
            return None

        heading_cat_col = "Heading Category"

        if heading_cat_col in df.columns:
            df = df[df[heading_cat_col] == "Product"]
            return df
        else:
            print("Returning None because Heading Category not in dataframe")
            return None

    def column_type_conversion(self, df: pd.DataFrame) -> pd.DataFrame:
        df["Value GBP"] = df["Value GBP"].str.replace(",", "").astype('float64')

        df["Actual/Issued Date"] = pd.to_datetime(df['Actual/Issued Date'])

        return df


    def column_generation(self, df: pd.DataFrame) -> pd.DataFrame:
        if df is None:
            print("Returning because of a nil dataframe")
            return None


        df["Field Group"] = ""
        df["Status"] = "Completed"
        df["Heading Category"] = "Variable Costs"

        rate_col = "Rate per Application Area ha"
        area_col = "Application Area ha"

        cols_of_interest = [rate_col, area_col]

        if self._check_list_is_in_list(df.columns, cols_of_interest):
            df["Quantity"] = df[rate_col] * df[area_col]
        else:
            print(f"Needed columns not present: {rate_col} or {area_col}")
            print(df.columns)
            return None
        
        value_col = "Value GBP"

        if value_col not in df.columns:
            print(f"Returning because {value_col} not present")
            return None
        
        print(df.dtypes)
        
        df["Av Field Unit Price GBP"] = df["Value GBP"] / df["Quantity"]

        crop_col = "Crop Group"
        if crop_col not in df.columns:
            print(f"Needed columns not present: {crop_col}")
            print(df.columns)
            return None

        df["Variety"] = df[crop_col]

        
        max_date = df["Actual/Issued Date"].max()
        df["Year"] = max_date.year


        print("ABOUT TO RETURN FROM PIPE")
        print(df.columns)
        return df
    
    def _check_list_is_in_list(self, main_list: list, sub_list: list) -> bool:

        main_set = set(main_list)
        sub_set = set(sub_list)

        return sub_set.issubset(main_set)


    def split_unit_column(self, df: pd.DataFrame) -> pd.DataFrame:
        
        if df is None:
            return 

        df["Units"] = df["Units"].str[0:-3]

        return df
import pandas as pd

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

# -*- coding: utf-8 -*-
"""FEMA_GIS_EXPORT_Streamlit.ipynb
06 November 2024
Created by LTJG Andrew Orser, USCG 
Built for FEMA TN Helene response
Created in Google Colab


"""

import streamlit as st
import pandas as pd
import pytz
from datetime import datetime
from io import BytesIO

st.title("ICS-204 Export File Transformer for GIS")

# File uploader for users to upload .xlsx files
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file:
    # Read and transform the uploaded file
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.replace('\n', '').str.strip()
    
    # Define divisions and rows to delete
    new_rows = []
    divisions = ['10 - Carter', '13 - Claiborne', '15 - Cocke', '29 - Grainger', '30 - Greene',
                 '32 - Hamblen', '37 - Hawkins', '45 - Jefferson', '46 - Johnson', '78 - Sevier',
                 '82 - Sullivan', '86 - Unicoi', '90 - Washington']
    rows_to_delete = []

    # Loop to expand rows based on Division condition
    #for index, row in df.iterrows():
      #  if row['Division'] == 'Throughout Designated Counties':
        #    for division in divisions:
        #        new_row = row.copy()
          #      new_row['Division'] = division
          #      new_rows.append(new_row)
          #  rows_to_delete.append(index)

    # Remove rows and add new ones
     df1 = df.drop(rows_to_delete)
  #  df1 = pd.concat([df1, pd.DataFrame(new_rows)])

    # Modify Division values based on conditions
    df1.loc[df1['Division'] == 'Not Set', 'Division'] = 'NA - ' + df1.loc[df1['Division'] == 'Not Set', 'Division']
    df1.loc[df1['Division'] == 'Branch Office', 'Division'] = 'NA - ' + df1.loc[df1['Division'] == 'Branch Office', 'Division']

    # Transform columns
    df1['temp'] = df1['Division']
    df1['temp'] = df1['temp'].str[5:]
    df1['Division'] = df1['Division'].str[:2]
    df1["County"] = df1["temp"]
    df1 = df1.drop("temp", axis=1)

    # Convert Division to string
    df1['Division'] = df1['Division'].astype(str)

    # Assign Branch values
    branch_I_divisions = ['47', '78', '45', '15', '30', '32', '37', '29', '34', '13']
    branch_II_divisions = ['86', '90', '10', '46', '82']

    # Create Branch column
    df1['Branch'] = '' 

    df1.loc[df1['Division'].isin(branch_I_divisions), 'Branch'] = 'I'
    df1.loc[df1['Division'].isin(branch_II_divisions), 'Branch'] = 'II'


    # Export df1 as Excel file with current date in filename

    # Define local time zone
    central_timezone = pytz.timezone('US/Central')
    
    # Get the current time in CT
    central_time = datetime.now(central_timezone)
    
    # Format date
    current_date = central_time.strftime("%d%b%y")
    
    current_date = datetime.now().strftime("%d%b%y")
    excel_filename = f"GIS_204_Export_{current_date}.xlsx"
    output = BytesIO()
    df1.to_excel(output, index=False)
    output.seek(0)

    # Provide download link in Streamlit
    st.download_button(label="Download Transformed Excel File", data=output, file_name=excel_filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

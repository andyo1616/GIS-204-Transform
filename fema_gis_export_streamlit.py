# -*- coding: utf-8 -*-
"""FEMA_GIS_EXPORT_Streamlit.ipynb
18 November 2024
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

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.replace('\n', '').str.strip()
else:
    st.warning("Please upload an Excel file.")

# Define divisions and rows to delete
new_rows = []
divisions = ['10 - Carter', '13 - Claiborne', '15 - Cocke', '29 - Grainger', '30 - Greene',
                 '32 - Hamblen', '37 - Hawkins', '45 - Jefferson', '46 - Johnson', '78 - Sevier',
                 '82 - Sullivan', '86 - Unicoi', '90 - Washington']
tn_dict = {'County': {0: 'Carter', 1: 'Clairborne', 2: 'Cocke', 3: 'Grainger', 4: 'Greene', 5: 'Hamblen', 6: 'Hancock',
                            7: 'Hawkins', 8: 'Jefferson', 9: 'Johnson', 10: 'Seveir', 11: 'Sullivan', 12: 'Unicoi', 13: 'Washington'},
                 'Branch': {0: 'II', 1: 'I', 2: 'I', 3: 'I', 4: 'I', 5: 'I', 6: 'I',
                            7: 'I', 8: 'II', 9: 'I', 10: 'I', 11: 'II', 12: 'II', 13: 'II'},
                 'Division': {0: '10 - Carter', 1:'13 - Claiborne', 2:'15 - Cocke', 3: '29 - Grainger', 4: '30 - Greene',
                              5: '32 - Hamblen', 6: 'Hancock', 7: '37 - Hawkins', 8: '45 - Jefferson', 9: '46 - Johnson', 10: '78 - Sevier',
                              11: '82 - Sullivan', 12: '86 - Unicoi', 13: '90 - Washington'},
                 'Longitude': {0: -82.127478, 1: -83.660416, 2: -83.121183, 3: -83.50962, 4: -82.845827, 5: -83.275211, 6: -83.221826,
                               7: -82.944688, 8: -83.446312, 9: -81.851772, 10: -83.524192, 11: -82.304143, 12: -82.516883, 13: -82.49742},
                 'Latitude': {0: 36.292721, 1: 36.485855, 2: 35.925437, 3: 36.276259, 4: 36.175351, 5: 36.203454, 6: 36.523646,
                              7: 36.441163, 8: 36.050984, 9: 36.454937, 10: 35.784656, 11: 36.512915, 12: 36.063347, 13: 36.293297}}
tn_dat = pd.DataFrame(tn_dict)

rows_to_delete = []

# Loop to expand rows based on Division condition
for index, row in df.iterrows():
  if row['Division'] == 'Throughout Designated Counties' and row['Branch'] != 'Mobile Emergency Response Support':
    for division in divisions:
      new_row = row.copy()
      new_row['Division'] = division
      division_data = tn_dat[tn_dat['Division'] == division]
      if not division_data.empty:
        new_row['Latitude'] = division_data.iloc[0]['Latitude']
        new_row['Longitude'] = division_data.iloc[0]['Longitude']
        new_row['Address'] = 'Centroid of County'                
      new_rows.append(new_row)
    rows_to_delete.append(index)

# Remove rows and add new ones
df1 = df.drop(rows_to_delete)
df1 = pd.concat([df1, pd.DataFrame(new_rows)])
df1 = df1.reset_index(drop=True)

# Modify Division values based on conditions
df1.loc[df1['Division'] == 'Not Set', 'Division'] = 'NA - ' + df1.loc[df1['Division'] == 'Not Set', 'Division']
df1.loc[df1['Division'] == 'Branch Office', 'Division'] = 'NA - ' + df1.loc[df1['Division'] == 'Branch Office', 'Division']
df1.loc[df1['Division'] == 'Throughout Designated Counties', 'Division'] = 'NA - ' + df1.loc[df1['Division'] == 'Throughout Designated Counties', 'Division']

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

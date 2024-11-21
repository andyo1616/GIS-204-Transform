# -*- coding: utf-8 -*-
"""FEMA_GIS_EXPORT_Streamlit.ipynb
Version 1.12
22 November 2024
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

# File uploader for ICS_215_EXPORT
uploaded_file_215 = st.file_uploader("Choose an Excel file for ICS_215_EXPORT", type="xlsx")

# File uploader for COMMUNICATIONS_LIST_FACILITIES(ICS_205A)
uploaded_file_205A = st.file_uploader("Choose an Excel file for COMMUNICATIONS_LIST_FACILITIES(ICS_205A)", type="xlsx")

# Checkbox to enable or disable the loop
enable_loop = st.checkbox("Enable 'Throughout Designated Counties' loop", value=True)

if uploaded_file_215 and uploaded_file_205A:
    # Load both files into dataframes
    df_215 = pd.read_excel(uploaded_file_215)
    df_215.columns = df_215.columns.str.replace('\n', '').str.strip()
    df_215.reset_index(drop=True, inplace=True)  # Ensure unique index

    df_205A = pd.read_excel(uploaded_file_205A)
    df_205A.columns = df_205A.columns.str.replace('\n', '').str.strip()
    df_205A.reset_index(drop=True, inplace=True)  # Ensure unique index

    # Merge facilities from df_205A into df_215
    df_merged = pd.merge(
        df_215,
        df_205A[['Facility Name', 'Facility Type']],
        left_on='Facility',
        right_on='Facility Name',
        how='left'
    )

    # Drop the extra 'Facility Name' column
    df_merged.drop(columns=['Facility Name'], inplace=True)

    # Fill missing Facility Type values with "No Work Assignment"
    df_merged['Facility Type'] = df_merged['Facility Type'].fillna("No Work Assignment")

    # Reorder columns to place Facility Type after Facility
    columns = list(df_merged.columns)
    facility_index = columns.index('Facility')
    columns.insert(facility_index + 1, columns.pop(columns.index('Facility Type')))
    df_merged = df_merged[columns]

    # Add rows for each facility in df_205A if not present in df_215
    for _, facility_row in df_205A.iterrows():
        if facility_row['Facility Name'] not in df_merged['Facility'].values:
            new_row = pd.Series(index=df_merged.columns)
            new_row['Facility'] = facility_row['Facility Name']
            new_row['Facility Type'] = facility_row['Facility Type']
            df_merged = pd.concat([df_merged, pd.DataFrame([new_row])], ignore_index=True)

    # Add rows for "Throughout Designated Counties" loop if enabled
    if enable_loop:
        new_rows = []
        divisions = ['10 - Carter', '13 - Claiborne', '15 - Cocke', '29 - Grainger', '30 - Greene',
                     '32 - Hamblen', '37 - Hawkins', '45 - Jefferson', '46 - Johnson', '78 - Sevier',
                     '82 - Sullivan', '86 - Unicoi', '90 - Washington']
        for _, row in df_merged.iterrows():
            if row.get('Division', '') == 'Throughout Designated Counties':
                for division in divisions:
                    new_row = row.copy()
                    new_row['Division'] = division
                    new_rows.append(new_row)
        df_merged = pd.concat([df_merged, pd.DataFrame(new_rows)], ignore_index=True)

    # Drop duplicate rows if they exist
    df_merged.drop_duplicates(inplace=True)

    # Transform columns as needed
    df_merged['temp'] = df_merged['Division']
    df_merged['temp'] = df_merged['temp'].str[5:]  # Extract county name
    df_merged['Division'] = df_merged['Division'].str[:2]  # Extract division number
    df_merged['County'] = df_merged['temp']
    df_merged.drop("temp", axis=1, inplace=True)

    # Convert Division to string
    df_merged['Division'] = df_merged['Division'].astype(str)

    # Assign Branch values
    branch_I_divisions = ['47', '78', '45', '15', '30', '32', '37', '29', '34', '13']
    branch_II_divisions = ['86', '90', '10', '46', '82']

    # Create Branch column
    df_merged['Branch'] = ''
    df_merged.loc[df_merged['Division'].isin(branch_I_divisions), 'Branch'] = 'I'
    df_merged.loc[df_merged['Division'].isin(branch_II_divisions), 'Branch'] = 'II'

    # Export the final DataFrame as an Excel file with a timestamp
    central_timezone = pytz.timezone('US/Central')
    central_time = datetime.now(central_timezone)
    current_date = central_time.strftime("%d%b%y")
    excel_filename = f"GIS_204_Export_{current_date}.xlsx"
    output = BytesIO()
    df_merged.to_excel(output, index=False)
    output.seek(0)

    # Provide download link in Streamlit
    st.download_button(
        label="Download Transformed Excel File",
        data=output,
        file_name=excel_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("Please upload both Excel files.")

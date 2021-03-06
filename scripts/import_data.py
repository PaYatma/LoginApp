# Load packages
import os 
import itertools
import pandas as pd

from  datetime import date


# Function to import all data
def import_data(regex:str, tab_name:str):
    
    # Directory
    path = "C:/Users/Yatma Sarr/Desktop/Linh TP/Docs"

    # Keep only files ending up with ".xlsx"
    files = list(itertools.compress(os.listdir(path), [regex in x for x in os.listdir(path)]))

    # Import countries name
    countries_list = pd.read_csv(path+"/countries.csv")[["CODE", "NAME"]]

    # Remove the space after the code name e.g from 'AT ' to 'AT'
    countries_list.CODE = [x.strip().upper() for x in countries_list.CODE]
    countries = countries_list.assign(NAME = ['Grece' if x == 'GK' else y for (x, y) in zip(countries_list.CODE, countries_list.NAME)])

    # Function to get country name from country code
    def getcountryname(code):
        try:
            return countries.query("CODE == @code").NAME.values[0].strip()
        except:
            return "Unknown"

    # Function to import data
    def import_tabs(path, filename, submission_type:str):
        ''' Retrieve all sheets name except the ones beginning with "Temp"'''
        reading = pd.ExcelFile(path + "/" + filename)
        sheets = reading.sheet_names
        ''' Exclude Temp into the sheets names '''
        mysheets = list(itertools.compress(sheets, ["Temp" not in x for x in sheets]))

        ''' Append all tables in a list '''
        df = []
        for xx in mysheets:
                onecountry = pd.read_excel(reading, xx, skiprows=2, usecols=lambda x: 'Unnamed' not in x).iloc[:,[0, -1]]
                cols = list(onecountry.columns)
                onecountry = onecountry.rename(columns= {x:x.strip() for x in cols}).dropna(axis = 0, how = 'all')
                onecountry = onecountry.assign(Code = xx.split(" ")[0].upper(),
                                            Country = getcountryname(xx.split(" ")[0].upper()),
                                            Study = 'Pre-Market' if xx.split(" ")[1] == "Pre" else 'Post-Market',
                                            Version = "1.0", 
                                            Date=str(date.today()), 
                                            Submission=submission_type)
                df.append(onecountry)

        ''' Concatenate all list of tables in one single table '''
        data = pd.concat(df)

        return data


    # Run the import function
    datalist = [import_tabs(path=path, filename=files[0], submission_type="Competent Authority"),
                import_tabs(path=path, filename=files[1], submission_type="Ethics Committee")]

    # Concatenate all list of tables in one single table
    data = pd.concat(datalist)

    # Reorder columns
    mydata = data[['Code', 'Country', 'Study', 'Submission', 'Documents', 'Note', 'Date']]
    
    # Save data in csv format
    mydata.to_csv(path + "/../Output/" + tab_name + ".csv", index=False)

    return mydata

######################
# Run function
######################
tab_Am = import_data(regex="ment Am", tab_name="America")
tab_Asia = import_data(regex="ment ASIA", tab_name="Asia")
tab_Europ = import_data(regex="ment EU ", tab_name="Europe")
tab_MidEast = import_data(regex="ment for ME", tab_name="MiddleEast")

# TODO: Reformat names of countries across CSV to facilitate parsing and clean up script aka get rid of the try statements

from datetime import date, timedelta
import pandas as pd
import re


def CSV_To_Dates(file):
    """
    :param file: CSV file to be read as data frame
    :return: keys to be used in a dictionary to parse the John Hopkins' file
    dates of first confirmed local transmission and countries. Dates have been reformated accordingly
    countries could also be reformated to further optimize the script
    """

    df_borderShutdown = pd.read_csv(file)
    keys_countries = list(df_borderShutdown[df_borderShutdown.head().columns.values[1]])
    keys_countries = [contr.strip() for contr in keys_countries]
    firstLocal_dates = list(df_borderShutdown[df_borderShutdown.head().columns.values[2]])

    # Reformat dates to parse death_agg
    DatesRegex = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})")
    date_cols = []
    for date in firstLocal_dates:
        try:
            monthGroup = DatesRegex.search(str(date)).group(1)
            monthGroup = "0" + monthGroup if len(monthGroup) == 1 else monthGroup
            dayGroup = DatesRegex.search(str(date)).group(2)
            dayGroup = "0" + dayGroup if len(dayGroup) == 1 else dayGroup
            yearGroup = DatesRegex.search(str(date)).group(3)
        except AttributeError:  # when the float value is found i.e. it means that our CSV does not have first day of local transmission
            if type(date) is float:
                date_cols.append(str(date))
                continue
        else:
            date_cols.append(DatesRegex.sub(f"{yearGroup}-{monthGroup}-{dayGroup}", str(date)))
    return keys_countries, date_cols


# Recalculate dates

def numDeaths(n, keys_countries, date_cols):
    """

    :param n: number of days
    :param keys_countries: iterable containing countries
    :param date_cols: iterable containing dates that will be recalculated based on number of days
    :return: dictionary containing number of deaths per country
    """

    datesToParse = []
    for d in date_cols:
        if d != "nan":
            datesToParse.append(str(date.fromisoformat(d) + timedelta(days=n)))
        else:
            datesToParse.append(d)

    data_dict = {}
    for e, country in enumerate(keys_countries):
        data_dict.setdefault(country, datesToParse[e])

    df_deathAgg = pd.read_csv("death_agg.csv", index_col="Country/Region")
    indices = list(df_deathAgg.index)
    manual_update = []
    countries_deaths = {}
    for i, c in enumerate(indices):
        try:
            if data_dict[c] != "nan":  # nan == no date of first local transmission in our CSV
                print(f"{c} has {df_deathAgg.iloc[i][data_dict[c]]} deaths on {data_dict[c]}")
                countries_deaths.setdefault(c, df_deathAgg.iloc[i][data_dict[c]])
        except KeyError as error:
            print(f"{error}, {c} must be manually update it")
            manual_update.append(c)
            continue
    return countries_deaths


def updated_CSV(updated_file, deaths):
    """
    :param updated_file: copy of data frame to be update it
    :param deaths: dictionary containing deaths after specified time frame
    :return: None, but saves new CSV in working directory with updated data
    """

    numDeaths_col = list(updated_file.head(0))[-2]
    country_col = list(updated_file.head(0))[1]
    # May rework parsing if the following issue arises:
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
    for n, row in enumerate(updated_file.index):
        try:
            print(updated_file[numDeaths_col][n])
            updated_file[numDeaths_col][n] = deaths[updated_file[country_col][n]]
            print(updated_file[numDeaths_col][n])
        except KeyError as e:
            print(f"{e} must be manually update it")
    updated_file.to_csv("sample.csv", index=False)


num = input("Please insert number of days after first day of confirmed local transmission")
borderShutdownCSV = "Covid19_LocalTrans_BorderShutdowns_Deaths - Data.csv"
copy_df_borderShutdown = pd.read_csv(borderShutdownCSV)
countries, columns = CSV_To_Dates(borderShutdownCSV)
updated_CSV(copy_df_borderShutdown, numDeaths(num, countries, columns))

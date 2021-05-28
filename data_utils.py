import pandas as pd
from pathlib import Path
# The path to the directory containing the data
from config.infos_script import path_to_data

"""
The job of this script is to extract the useful informations from the relevant source and provide a pandas dataframe 
containing them.
"""


def month_index(month):
    """
    :param month: month of the year
    :return: a number corresponding to each month from 1 to 12
    """
    month_nb = {'Janvier': 1,
                'Fevrier': 2,
                'Février': 2,
                'Mars': 3,
                'Avril': 4,
                'Mai': 5,
                'Juin': 6,
                'Juillet': 7,
                'Aout': 8,
                'Septembre': 9,
                'Octobre': 10,
                'Novembre': 11,
                'Decembre': 12,
                'Décembre': 12
                }
    return month_nb[month]


def available_months(year):
    """
    goes into the file system to see what .ods files exist in the directory for the given year
    :param year: -
    :return: a list of the names of the available months in the directory eg. ['Janvier', 'Fevrier']
    """
    month_list = ["Janvier", "Fevrier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Aout", "Septembre",
                  "Octobre", "Novembre", "Decembre", "Décembre"]
    available = []
    for month in month_list:
        file_path = Path(f"{path_to_data}{year}/{month_index(month)}-Cours{month}.ods")
        if file_path.is_file():
            available += month
    return available


def data_extraction(year, month):
    """
    Extracts data from odt sheets and returns useful dataframe
    We assume the following directory setup : [path_to_data]/[year]
    and the data files to be named : [month_number]-Cours[month].ods
    for exemple we'd have HeuresDeCours/2021/3-CoursMars.odt
    :param month: -
    :param year: -
    :return: a pandas dataframe containing every useful information for the generation of bills
    :raises FileNotFoundError: that needs to be handled in the menu if the file isn't found.
    """
    # TODO error handling in menu
    file_path = Path(f"{path_to_data}{year}/{month_index(month)}-Cours{month}.ods")
    if not file_path.is_file():
        # Gestion des erreurs d'accents dans le nommage des fichiers
        if month == 'Février':
            month = 'Fevrier'
        elif month == 'Fevrier':
            month = 'Février'
        elif month == 'Décembre':
            month = 'Decembre'
        elif month == 'Decembre':
            month = 'Décembre'
        file_path = Path(f"{path_to_data}{year}/{month_index(month)}-Cours{month}.ods")
    xls = pd.ExcelFile(file_path)
    df2 = pd.read_excel(xls, 'Feuille2', engine="odf")
    return df2


def student_extraction():
    """

    :return: a pandas database containing students name, surname, address and sex
    """
    file_path = Path(f"{path_to_data}Infos_élèves.ods")
    df = pd.read_excel(file_path)
    return df

import pandas as pd
import os.path
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
                'Mars': 3,
                'Avril': 4,
                'Mai': 5,
                'Juin': 6,
                'Juillet': 7,
                'Aout': 8,
                'Septembre': 9,
                'Octobre': 10,
                'Novembre': 11,
                'Décembre': 12,
                }
    return month_nb[month]


def available_months(year):
    """
    goes into the file system to see what .ods files exist in the directory for the given year
    :param year: -
    :return: a list of the names of the available months in the directory eg. ['Janvier', 'Fevrier']
    """


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
    # TODO gérer les / \ selon linux windows (vérifier s'il faut faire ça)
    file_path = f"{path_to_data}{year}/{month_index(month)}-Cours{month}.ods"
    if not os.path.isfile(file_path):
        # Gestion des erreurs d'accents dans le nommage des fichiers
        if month == 'Février':
            month = 'Fevrier'
        elif month == 'Fevrier':
            month = 'Février'
        file_path = f"{path_to_data}{year}/{month_index(month)}-Cours{month}.ods"
    xls = pd.ExcelFile(file_path)
    df2 = pd.read_excel(xls, 'Feuille2', engine="odf")
    return df2

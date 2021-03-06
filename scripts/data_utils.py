import pandas as pd
from pathlib import Path
# The path to the directory containing the data
from config.infos_script import path_to_data
from math import isnan
from scripts.types_utils import MissingColumnClientError, MissingRowDataError

"""
The job of this script is to extract the useful informations from the relevant source and provide a pandas dataframe 
containing them.
"""


def empty_cell(value):
    """
    check if a cell from a dataframe is empty
    :param value:
    :return: True if cell is NaN or '' else False
    """
    if isinstance(value, str):
        return value == ""
    else:
        return isnan(value)


def has_address(client):
    """
    Check if a client from the Infos_élèves dataframe has a specified address or not
    :param client: a pd.dataframe row
    :return: True if an address is specified, else False
    """
    no_address = empty_cell(client.Rue) or empty_cell(client["Code Postal"]) or empty_cell(client.Ville)
    return not no_address


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
    goes into the file system to see what .xlsx/.ods files exist in the directory for the given year
    :param year: -
    :return: a list of the names of the available months in the directory eg. ['Janvier', 'Fevrier']
    The list is empty is no relevant file was found
    """
    month_list = ["Janvier", "Fevrier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Aout", "Septembre",
                  "Octobre", "Novembre", "Decembre", "Décembre"]
    available = []
    for month in month_list:
        file_path = Path(f"{path_to_data}{year}/{month_index(month)}-Cours{month}.ods")
        if not file_path.is_file():
            file_path = Path(f"{path_to_data}{year}/{month_index(month)}-Cours{month}.xlsx")
        if file_path.is_file():
            # Making sure months in the 'available' list won't have accents
            accent_check = {'Février': 'Fevrier', 'Décembre': 'Decembre'}
            if month in accent_check:
                month = accent_check[month]
            available += [month]
    return available


def data_extraction(year, month):
    """
    Extracts data from odt sheets and returns useful dataframe
    We assume the following directory setup : [path_to_data]/[year]
    and the data files to be named : [month_number]-Cours[month].xlsx (or ods)
    for exemple we'd have HeuresDeCours/2021/3-CoursMars.odt
    :param month: -
    :param year: -
    :return: a pandas dataframe containing every useful information for the generation of bills
    :raises FileNotFoundError: that needs to be handled in the menu if the file isn't found.
    """
    file_path = Path(f"{path_to_data}{year}/{month_index(month)}-Cours{month}.ods")
    if not file_path.is_file():  # si le fichier est en .xlsx
        file_path = Path(f"{path_to_data}{year}/{month_index(month)}-Cours{month}.xlsx")
        xls = pd.ExcelFile(file_path)
        df2 = pd.read_excel(xls, 'Feuille2')
    else:
        xls = pd.ExcelFile(file_path)
        df2 = pd.read_excel(xls, 'Feuille2', engine="odf")

    # Renaming rows names
    df2 = df2.set_index("Informations")

    # Cleaning the dataframe of its empty columns
    df2.dropna(axis=1, how='all', inplace=True)

    # Spelling test of rows names
    correct_names = ['Donné', 'Payé', 'Payé en CESU', 'Reste à payer précédent', 'Reste à payer', 'Tarif Horaire',
                     'Nbre heures donné', 'Nbre heures payé']
    rows_names = [j.name for i, j in df2.iterrows()]
    test = [(correct_names[i], rows_names[i]) for i in range(len(correct_names)) if correct_names[i] != rows_names[i]]
    if len(test) > 0:
        raise MissingRowDataError(test, year, month, month_index(month))

    return df2.fillna(0)


def client_extraction():
    """

    :return: a pandas database containing students name, surname, address and sex
    """
    file_path = Path(f"{path_to_data}Infos_élèves.ods")
    if not file_path.is_file():
        file_path = Path(f"{path_to_data}Infos_élèves.xlsx")
    df = pd.read_excel(file_path)
    # Cleaning the dataframe of its empty rows
    df.dropna(axis=0, how='all', inplace=True)

    # Spelling test of columns names
    correct_names = ['Prénom', 'Nom', 'Sexe (F/M)', 'Rue', 'Code Postal', 'Ville', 'Pays', 'Complément d\'adresse',
                     'Elèves rattachés']
    test = [(correct_names[i], df.columns[i]) for i in range(len(correct_names)) if correct_names[i] != df.columns[i]]
    if len(test) > 0:
        raise MissingColumnClientError(test)

    return df

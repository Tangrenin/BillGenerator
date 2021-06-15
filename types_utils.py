from dataclasses import dataclass


@dataclass(frozen=True)
class Address:
    street: str
    zipcode: str
    city: str
    country: str = "France"
    other: str = ""

    def __post_init__(self):
        if isinstance(self.zipcode, float):
            object.__setattr__(self, 'zipcode', f'{self.zipcode:g}')


# Custom error classes
class Error(Exception):
    """Base class for other exceptions"""
    pass


class DuplicateStudentsError(Error):
    """Raises when multiple students with the same name are found in a data sheet"""
    def __init__(self, name):
        self.name = name
        self.message = f"\nL'élève {name} a été trouvé.e plusieurs fois dans le tableau d'heures de cours.\n" \
                       f"Veuillez spécifier le nom des élèves de manière unique.\n" \
                       f"Ex: Nina, Nina -> Nina B., Nina C.\n" \
                       f"/!\\ Pensez à mettre à jour Infos_élèves en conséquence /!\\"
        super().__init__(self.message)


class MissingRowDataError(Error):
    """Raises when a row that should be present in a data sheet in missing or misspelled"""
    def __init__(self, misspelled_rows, year, month, month_index):
        """
        :param misspelled_rows: [(correct_name, misspelled_name)]
        the list of misspelled_rows and their correction
        :param year: the year from which file there is a mistake
        :param month: the month from which file there is a mistake ex: 'Juillet'
        :param month_index: the month index ex : 7
        """
        self.message = f"Les lignes suivantes sont mal orthographiées dans '{year}/{month_index}-Cours{month}.ods'\n"
        for (correct_name, misspelled_name) in misspelled_rows:
            self.message += f"- [{misspelled_name}] devrait s'écrire [{correct_name}]\n"
        self.message += "Veuillez corriger ces noms de lignes."
        super().__init__(self.message)


class MissingColumnClientError(Error):
    """Raises when a column that should be present in the client database in missing or misspelled"""
    def __init__(self, misspelled_columns):
        """
        :param misspelled_columns: [(correct_name, misspelled_name)]
        the list of misspelled_rows and their correction
        """
        self.message = "Les colonnes suivantes sont mal orthographiées dans 'Infos_élèves.ods' :\n"
        for (correct_name, misspelled_name) in misspelled_columns:
            self.message += f"- [{misspelled_name}] devrait s'écrire [{correct_name}]\n"
        self.message += "Veuillez corriger ces noms de colonnes."
        super().__init__(self.message)

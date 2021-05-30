from dataclasses import dataclass


@dataclass(frozen=True)
class Address:
    street: str
    zipcode: str
    city: str
    country: str = "France"
    other: str = ""


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
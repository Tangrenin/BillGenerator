from dataclasses import dataclass


@dataclass(frozen=True)
class Address:
    street: str
    zipcode: str
    city: str
    country : str = "France"
    other: str = ""

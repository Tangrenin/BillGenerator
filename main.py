from datetime import date
from execution import execute
from types_utils import DuplicateStudentsError
import re


def safe_input(min_val, max_val, default, question=""):
    while True:
        try:
            if question != "":
                print(question)
            answer = input()
            # the user can choose the default option by simply pressing Enter
            if answer == "":
                return default
            number = int(answer)
            if number < min_val or number > max_val:
                raise ValueError
            return number
        except ValueError:
            print("\nEntrée invalide. Veuillez écrire une des valeurs proposées.")


def menu():
    months = {1: 'Janvier',
              2: 'Fevrier',
              3: 'Mars',
              4: 'Avril',
              5: 'Mai',
              6: 'Juin',
              7: 'Juillet',
              8: 'Aout',
              9: 'Septembre',
              10: 'Octobre',
              11: 'Novembre',
              12: 'Decembre'}
    today = date.today()
    # Default date is last month
    default_year = today.year - 1 if today.month == 1 else today.year
    default_month = 12 if today.month == 1 else today.month

    print("=======================================")
    print("Génération de documents administratifs")
    print("=======================================\n")
    print("(Pour sélectionner le choix par défaut, appuyez simplement sur Entrée)\n")
    print("Quel document voulez vous générer ?")
    prompt = "0 - Tous [défaut] \n1 - Facture \n2 - Attestation"
    user_doc_choice = safe_input(0, 2, 0, prompt)

    prompt = f"\nPour quelle année voulez-vous générer des documents ? [défaut : {default_year}]"
    user_year_choice = safe_input(2010, today.year, default_year, prompt)

    if user_doc_choice == 1:  # Factures
        print("\nPour quel mois voulez-vous générer ces documents ?")
        prompt = f"Entrez un nombre : (1 - Janvier, 2 - Février, etc) \n[défaut : {default_month} {default_year}]"
        user_month_choice = safe_input(1, 12, default_month, prompt)
        user_month_choice = months[user_month_choice]
        execute(user_year_choice, user_month_choice, 'facture')
    elif user_doc_choice == 2:  # Attestations
        execute(user_year_choice, default_month, 'attestation')
    elif user_doc_choice == 0:  # Générer tous les documents de l'année choisie
        execute(user_year_choice, default_month, 'all')


if __name__ == '__main__':
    try:
        menu()
    except KeyError as e:
        print(f"Erreur : le nom de la colonne ou ligne suivante d'un tableau a été modifiée : {e.args[0]} ")
        print("Veuillez le renommer correctement")
    except AttributeError as e:
        key_name = e.args[0]
        key_name = re.search(r"attribute '(.*)'$", key_name)[1]
        print(f"Erreur : le nom de la colonne ou ligne suivante d'un tableau a été modifiée : {key_name} ")
        print("Veuillez le renommer correctement")
    except DuplicateStudentsError as e:
        print(f"Attention, le nom suivant a été retrouvé plusieurs fois dans un tableau d'heures de cours : {e.name}")
        print("Veuillez spécifier les noms d'élèves pour qu'ils soient uniques")
    except FileNotFoundError as e:
        print(f"Le fichier suivant n'existe pas ou n'est pas à sa place : {e.filename}")

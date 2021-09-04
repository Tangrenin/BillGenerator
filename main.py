from datetime import date
from scripts.execution import execute
from scripts.types_utils import DuplicateStudentsError, MissingRowDataError, MissingColumnClientError
from scripts.data_templates_generator import data_templates_generation


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
    prompt = "0 - Tous [défaut] \n1 - Facture \n2 - Attestation \n3 - Génération des feuilles de données"
    user_doc_choice = safe_input(0, 3, 0, prompt)

    if user_doc_choice == 3:
        print("***** Génération de la base de donnée des élèves... *****")
        print("***** Génération des feuilles de comptabilité de l'année en cours... *****")
        data_templates_generation(today.year)
        print("***** Génération terminée *****\n")
        print("PS : Pas d'inquiétudes, si des documents étaient déjà présents, ils n'ont pas été re-générés ou écrasés")
        return 0

    prompt = f"\nPour quelle année voulez-vous générer des documents ? [défaut : {default_year}]"
    user_year_choice = safe_input(2010, today.year, default_year, prompt)

    if user_doc_choice == 1:  # Factures
        print("\nPour quel mois voulez-vous générer ces documents ?")
        prompt = f"Entrez un nombre : (1 - Janvier, 2 - Février, etc) \n" \
            f"[défaut : {months[default_month]} {default_year}]"
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
    except (MissingRowDataError, MissingColumnClientError, DuplicateStudentsError) as e:
        print(e.message)
    except FileNotFoundError as e:
        print(f"Le fichier suivant n'existe pas ou n'est pas à sa place : {e.filename}")

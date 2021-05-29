from pdf_builder import pdf_build
from data_utils import data_extraction, available_months, student_extraction
from types_utils import Address
from datetime import date
import config.infos_yann as yannou

current_date = date.today()
# TODO print students whose data have been unused for each month when processing


def find_student(student, data):
    """
    Finds a student from the database in the data dataframe, and returns the column containing relevant informations
    relative to this student
    :param student: a pd.dataframe row from the Infos_élèves dataframe
    :param data: a pd.dataframe containing infos relative to courses from a certain month
    :return:  a pd.dataframe column containing the info relative to a specific student for the month data contains
    information about
    """
    for candidate in data:
        prenom = candidate.split(' ')[0]
        if student.Prénom == prenom:
            # We check if the column label also contains a surname
            if len(candidate.split(' ')) > 1:
                # If there's a surname, we recreate it if it contains multiple words
                nom = candidate.split(' ', 1)
                # If there's a '.' at the end of the beginning of the surname, we remove it : Léa B. -> Léa B
                nom = nom[:-1] if nom[-1] == '.' else nom
                if student.Nom.startswith(nom):
                    return data[candidate]
            else:
                return data[candidate]
    # If no candidate is found
    return None


def bill_number_gen(year, month, student_number):
    month_nb = {'Janvier': '01',
                'Fevrier': '02',
                'Février': '02',
                'Mars': '03',
                'Avril': '04',
                'Mai': '05',
                'Juin': '06',
                'Juillet': '07',
                'Aout': '08',
                'Septembre': '09',
                'Octobre': '10',
                'Novembre': '11',
                'Decembre': '12',
                'Décembre': '12'}
    # zfill fills the student_number with 0's so that there are always 2 digits
    return str(year) + month_nb[month] + str(student_number).zfill(2)


def gen_all_factures(document_type, year, month):
    """
    generates all bills for a given month of a given year
    - fetches the appropriate data
    - puts together the variables that will be needed for building the pdf
    - calls the pdf builder pdf_build with following args :
    TODO complete doc
    template_vars :
    output_name :

    :param document_type: -
    :param month: month about which bills should be generated
    :param year: year about which bills should be generated
    :return: nothing
    """
    # gets the data
    students = student_extraction()
    data = data_extraction(year, month)
    data = data.set_index("Informations")

    unregistered_students = {candidate for candidate in data}
    for index, student in students.iterrows():
        # We look for the corresponding student in the data sheet
        # TODO find_student peut renvoyer None, l'étudiant de la DB n'a pas été trouvé. Il faut prévenir l'user
        student_info = find_student(student, data)
        # Since we found the student, he is registered in the database and can be removed from the following set
        unregistered_students.remove(student_info.name)

        # Generate bill identification
        bill_number = bill_number_gen(year, month, index)

        # puts together the necessary variables
        # TODO gérer output_name
        output_name = ''
        template_vars = {
            "month": month,
            "year": year,
            # Generated infos
            "bill_gen_date": current_date,
            "bill_number": bill_number,
            # Students database info
            "student_firstname": student.Prénom,
            "student_surname": student.Nom,
            "student_sex": student["Sexe (F/M)"],
            "student_address": Address(street=student.Rue,
                                       zipcode=student["Code Postal"],
                                       city=student.Ville,
                                       country=student.Pays,
                                       other=student["Complément d'adresse"]),
            # Student monthly bills info
            "nb_hours": student_info["Nbre heures donné"],
            "hourly_rate": student_info["Tarif Horaire"],
            "already_paid": student_info["Nbre heures payé"],
            "left_to_pay": student_info["Reste à payer"],
            "CESU": student_info["Payé en CESU"],
            # Teacher info
            "teacher_firstname": yannou.firstname,
            "teacher_surname": yannou.surname,
            "teacher_address": yannou.adresse,
            "teacher_siret": yannou.siret,
            "teacher_SAP": yannou.SAP}

        # calls the pdf builder
        pdf_build(template_vars, document_type, output_name)
    print("Attention, les élèves suivants ont été détectés dans les tableaux d'heures de cours mais ne se trouvent pas"
          "dans la base de données")
    print(unregistered_students)
    print("Cela peut être des étudiants qui ont arrêté les cours et ont été supprimés de la base de données")
    print("Ou bien une faute dans l'orthographe d'un nom d'élève a pu être commise dans un fichier d'heures de cours")


def gen_all_attest(document_type, year, month):
    """
    generates all attestations for a given year
    - fetches the appropriate data
    - puts together the variables that will be needed for building the pdf
    - calls the pdf builder
    :param document_type: -
    :param month: unused parameter
    :param year: year about which attestations should be generated
    :return: nothing
    """
    # gets the data
    data = {}
    months = available_months(year)
    for m in months:
        data[m] = data_extraction(year, m)
        data[m] = data[m].set_index("Informations")
    students = student_extraction()

    for student in students:

        # puts together the necessary variables
        output_name = ''
        template_vars = {
            "year": year,
            # Generated infos
            "attest_gen_date": current_date,
            # Students database info
            "student_firstname": student.Prénom,
            "student_surname": student.Nom,
            "student_sex": student["Sexe (F/M)"],
            "student_address": Address(street=student.Rue,
                                       zipcode=student["Code Postal"],
                                       city=student.Ville,
                                       country=student.Pays,
                                       other=student["Complément d'adresse"]),
            # Teacher info
            "teacher_firstname": yannou.firstname,
            "teacher_surname": yannou.surname,
            "teacher_address": yannou.adresse,
            "teacher_siret": yannou.siret,
            "teacher_SAP": yannou.SAP}

        # calls the pdf builder
        pdf_build(template_vars, document_type, output_name)


def execute(document_type, year, month):
    """
    calls the appropriate function according to the document_type that is asked for
    :param month:
    :param year:
    :param document_type: the type of document that is to be generated
    :return: nothing
    """
    gen_function = {
        'facture': gen_all_factures,
        'attestation': gen_all_attest,
    }
    if document_type == 'all':
        for func in gen_function:
            gen_function[func](document_type, year, month)
    else:
        gen_function[document_type](document_type, year, month)

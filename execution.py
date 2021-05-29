from pdf_builder import pdf_build
from data_utils import data_extraction, available_months, student_extraction, month_index
from types_utils import Address
from datetime import date
import config.infos_yann as yannou

current_date = date.today()


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
    # zfill fills the student_number with 0's so that there are always 2 digits
    return str(year) + str(month_index(month)).zfill(2) + str(student_number).zfill(2)


def warning(unregistered_students, unfound_students):
    if len(unregistered_students) > 0:
        print("Attention, les élèves suivants ont été détectés dans les tableaux d'heures de cours mais ne se trouvent "
              "pas dans la base de données")
        print(unregistered_students)
        print("Vérifiez que ce sont bien des étudiants qui n'ont pas eu de cours pendant cette période")
        print("Sinon, c'est qu'il y a une faute pour ces élèves\n")

    if len(unfound_students) > 0:
        print("Attention, les élèves suivants ont été détectés dans la base de données mais ne se trouvent "
              "pas dans les tableaux d'heures de cours")
        print(unfound_students)
        print("Vérifiez que ce sont bien des étudiants qui n'ont pas eu de cours pendant cette période")
        print("S'ils ont arrêté et reçu leur attestation, songez à les supprimer de Infos_élèves")
        print("Sinon, il y a une faute pour ces élèves\n")


def gen_all_factures(document_type, year, month):
    """
    generates all bills for a given month of a given year
    - fetches the appropriate data
    - puts together the variables that will be needed for building the pdf
    - calls the pdf builder pdf_build with following args :
    template_vars : a dict containing all necessary informations to build the document
    output_name : the concatenation of the path from the output folder and the file name
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
    unfound_students = set()
    for index, student in students.iterrows():
        # We look for the corresponding student in the data sheet
        student_info = find_student(student, data)
        if student_info is not None:
            # Since we found the student, he is registered in the database and can be removed from the following set
            unregistered_students.remove(student_info.name)

            # Generate bill identification
            bill_number = bill_number_gen(year, month, index)

            # puts together the necessary variables
            file_name = "Fac_" + student.Nom.replace(' ', '') + student.Prénom + f"-{month_index(month)}_{year}"
            output_name = f"{document_type}/{year}/{month}/{file_name}"
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
                "total_amount": student_info["Donné"],
                "already_paid": student_info["Payé"],
                "left_to_pay": student_info["Reste à payer"],
                # Teacher info
                "teacher_firstname": yannou.firstname,
                "teacher_surname": yannou.surname,
                "teacher_address": yannou.adresse,
                "teacher_siret": yannou.siret,
                "teacher_SAP": yannou.SAP}

            # calls the pdf builder
            pdf_build(template_vars, document_type, output_name)
        else:  # The student hasn't been found in the billing sheets
            unfound_students.add(f"{student.Prénom} {student.Nom}")
    warning(unregistered_students, unfound_students)


def gen_all_attest(document_type, year, month):
    """
    generates all attestations for a given year
    - fetches the appropriate data
    - puts together the variables that will be needed for building the pdf
    - calls the pdf builder pdf_build with following args :
    template_vars : a dict containing all necessary informations to build the document
    output_name : the concatenation of the path from the output folder and the file name
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

    # Sets to handle missing students from the billing sheets or the database
    unregistered_students = set()
    unfound_students = {f"{student.Prénom} {student.Nom}" for i, student in students.iterrows()}

    for index, student in students.iterrows():
        # Initialization of the yearly and monthly variables
        total_paid = 0
        total_cesu = 0
        monthly_nb_hours = {}
        monthly_hour_rate = {}
        monthly_paid = {}

        for m in months:
            # We load in the set all names in the billing sheet and will remove those that are found
            unregistered_students.update({candidate for candidate in data[m]})
            student_info = find_student(student, data[m])
            if student_info is not None:
                # We found the student, he is registered in the database and can be removed from the following sets
                unfound_students.remove(f"{student.Prénom} {student.Nom}")
                unregistered_students.remove(student_info.name)

                total_paid += student_info["Payé"]
                total_cesu += student_info["Payé en CESU"]
                monthly_nb_hours[m] = student_info["Nbre heures payé"]
                monthly_hour_rate[m] = student_info["Tarif Horaire"]
                monthly_paid[m] = student_info["Payé"]

        # puts together the necessary variables
        file_name = "Attest_" + student.Nom.replace(' ', '') + student.Prénom + f"-{year}"
        output_name = f"{document_type}/{year}/{file_name}"
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
            # Student yearly/monthly bills info
            "total_paid": total_paid,
            "total_cesu": total_cesu,
            "monthly_nb_hours": monthly_nb_hours,
            "monthly_hour_rate": monthly_hour_rate,
            "monthly_paid": monthly_paid,
            # Teacher info
            "teacher_firstname": yannou.firstname,
            "teacher_surname": yannou.surname,
            "teacher_address": yannou.adresse,
            "teacher_siret": yannou.siret,
            "teacher_SAP": yannou.SAP}

        # calls the pdf builder
        pdf_build(template_vars, document_type, output_name)
    warning(unregistered_students, unfound_students)


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

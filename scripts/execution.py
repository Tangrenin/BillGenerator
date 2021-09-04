from scripts.pdf_builder import pdf_build
from scripts.data_utils import data_extraction, available_months, client_extraction, month_index, has_address
from scripts.types_utils import Address, DuplicateStudentsError
from datetime import date
import config.infos_teacher as yannou

current_date = date.today()


def find_attached_students(client, data):
    """
    Finds in a data sheet the information relative to the students linked with a client from the database
    :param client: a pd.dataframe row containing the fiscal infos relative to a client
    :param data: a pd.dataframe containing the billing info for each student
    :return: a tuple of two elements :
    attached_students_info : a list of pd.dataframe columns, each columns is for a specific student linked to the client
    unfound_students : a set of all linked students not found in the data sheet
    """
    student_names = client["Elèves rattachés"].split(' ; ')
    attached_students_info = []  # res list
    unfound_students = set()
    for name in student_names:
        name_occurrence = list(data.columns).count(name)
        if name_occurrence > 1:  # check if a student is found multiple times
            raise DuplicateStudentsError(name)
        elif name_occurrence == 0:
            unfound_students.add(name)
        else:
            attached_students_info += [data[name]]
    return attached_students_info, unfound_students


def bill_number_gen(year, month, client_number):
    # zfill fills the student_number with 0's so that there are always 2 digits
    return str(year) + str(month_index(month)).zfill(2) + str(client_number).zfill(2)


def warning(unregistered_students, unfound_students, missing_address):
    if len(unregistered_students) > 0:
        print("Attention, les élèves suivants ont été détectés dans les tableaux d'heures de cours mais ne se trouvent "
              "pas dans la base de données.")
        print(unregistered_students)
        print("Vérifiez que ce sont bien des étudiants qui n'ont pas eu de cours pendant cette période.")
        print("Sinon, c'est qu'il y a une faute pour ces élèves.\n")

    if len(unfound_students) > 0:
        print("Attention, les élèves suivants ont été détectés dans la base de données mais ne se trouvent "
              "pas dans les tableaux d'heures de cours.")
        print(unfound_students)
        print("Vérifiez que ce sont bien des étudiants qui n'ont pas eu de cours pendant cette période.")
        print("S'ils ont arrêté et reçu leur attestation, songez à les supprimer de Infos_élèves.")
        print("Sinon, il y a une faute pour ces élèves.\n")

    if len(missing_address) > 0:
        print("Les clients suivants n'ont pas d'adresse présente dans Infos_élèves.")
        print(missing_address)
        print("Les documents seront générés avec \"Adresse inconue\" pour adresse.")
        print("Pensez quand même à leur demander leur adresse.\n")


def gen_facture(year, month, client, data, document_type='facture'):
    """
    Note : Calls the pdf builder pdf_build with following args :
    template_vars : a dict containing all necessary informations to build the document
    relative_output_path : the concatenation of the path from the output folder and the file name
    file_name: the final pdf file name (without the extension)
    :param year: string : AAAA
    :param month: string of the month in French
    :param client: a pd.dataframe row containing client financial infos
    :param data: a pd.dataframe containing billing infos for a month
    :param document_type: string
    :return: a tuple of two elements :
    unfound_students : the students from the database not found in data
    registered_students : the students in data that correspond to students in the database
    """
    unfound_students = set()
    registered_students = set()

    # We look for the students attached to each client in data sheets
    query_results = find_attached_students(client, data)

    # The students hasn't been found in the billing sheets
    unfound_students.update(query_results[1])

    # Billing vars for a client
    nb_hours_student = {}
    hourly_rate_student = {}
    total_amount_student = {}
    already_paid_client = 0
    left_to_pay_client = 0
    for student_info in query_results[0]:
        # Since we found the student, he is registered in the database and can be added to the following set
        registered_students.add(student_info.name)

        nb_hours_student[student_info.name] = student_info["Nbre heures donné"]
        hourly_rate_student[student_info.name] = student_info["Tarif Horaire"]
        total_amount_student[student_info.name] = student_info["Donné"]
        already_paid_client += student_info["Payé"]
        left_to_pay_client += student_info["Reste à payer"]

    # Generate bill identification
    bill_number = bill_number_gen(year, month, client.name)  # here client.name refers to the row index in the DB

    # puts together the necessary variables
    file_name = "Fac_" + client.Nom.replace(' ', '') + client.Prénom + f"-{month_index(month)}_{year}"
    relative_output_path = f"Factures/{year}/{month_index(month)}-{month}/"
    template_vars = {
        "month": month,
        "year": year,
        "title": file_name,
        # Generated infos
        "bill_gen_date": current_date,
        "bill_number": bill_number,
        # Students database info
        "client_firstname": client.Prénom,
        "client_surname": client.Nom,
        "client_sex": client["Sexe (F/M)"],
        "client_address": Address(street=client.Rue,
                                  zipcode=client["Code Postal"],
                                  city=client.Ville,
                                  country=client.Pays,
                                  other=client["Complément d'adresse"]),
        # Student monthly bills info
        "nb_hours_student": nb_hours_student,
        "hourly_rate_student": hourly_rate_student,
        "total_amount_student": total_amount_student,
        # Client monthly bills info
        "already_paid_client": already_paid_client,
        "left_to_pay_client": left_to_pay_client,
        # Teacher info
        "teacher_firstname": yannou.firstname,
        "teacher_surname": yannou.surname,
        "teacher_address": yannou.adresse,
        "teacher_siret": yannou.siret,
        "teacher_SAP": yannou.SAP}

    # calls the pdf builder
    pdf_build(template_vars, document_type, relative_output_path, file_name)

    return registered_students, unfound_students


def gen_attest(year, client, data, relevant_months, document_type='attestation'):
    """
    Note : Calls the pdf builder pdf_build with following args :
    template_vars : a dict containing all necessary informations to build the document
    relative_output_path : the concatenation of the path from the output folder and the file name
    file_name: the final pdf file name (without the extension)
    :param year: string : AAAA
    :param client: a pd.dataframe row containing client financial infos
    :param data: a dictionary of pd.dataframes containing billing infos for a month, each for a given month
    :param relevant_months: the months we have billing data about
    :param document_type: string
    :return: matched_students, a set of students from the database that were found in at least one data sheet
    """
    matched_students = set()
    # Initialization of the yearly and monthly variables
    total_paid = 0
    total_cesu = 0
    monthly_nb_hours = {}
    monthly_hour_rate = {}
    monthly_paid = {}

    for m in relevant_months:
        students_info = find_attached_students(client, data[m])[0]
        for student in students_info:
            matched_students.add(student.name)

            # Updating yearly and monthly variables
            total_paid += student["Payé"]
            total_cesu += student["Payé en CESU"]
            monthly_nb_hours[m] = student["Nbre heures payé"]
            monthly_hour_rate[m] = student["Tarif Horaire"]
            monthly_paid[m] = student["Payé"]

    # puts together the necessary variables
    file_name = "Attest_" + client.Nom.replace(' ', '') + client.Prénom + f"-{year}"
    relative_output_path = f"Attestations/{year}/"
    template_vars = {
        "year": year,
        "title": file_name,
        # Generated infos
        "attest_gen_date": current_date,
        # Students database info
        "client_firstname": client.Prénom,
        "client_surname": client.Nom,
        "client_sex": client["Sexe (F/M)"],
        "client_address": Address(street=client.Rue,
                                  zipcode=client["Code Postal"],
                                  city=client.Ville,
                                  country=client.Pays,
                                  other=client["Complément d'adresse"]),
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
    pdf_build(template_vars, document_type, relative_output_path, file_name)

    return matched_students


def gen_all_factures(year, month):
    """
    generates all bills for a given month of a given year
    :param month: month about which bills should be generated
    :param year: year about which bills should be generated
    :return: nothing
    """
    print(f"***** Génération des factures de : {month}... *****")

    # gets the data
    clients = client_extraction()
    data = data_extraction(year, month)

    unregistered_students = {student for student in data}  # students in data that are not in the DB
    unfound_students = set()  # Students in the DB that are not in data
    missing_address = set()  # Clients whose address are missing

    for index, client in clients.iterrows():
        gen_results = gen_facture(year, month, client, data)
        unregistered_students.difference_update(gen_results[0])
        unfound_students.update(gen_results[1])
        if not has_address(client):
            missing_address.add(f"{client.Prénom} {client.Nom}")
    print("***** Génération des factures terminée *****\n")
    return unregistered_students, unfound_students, missing_address


def gen_all_attest(year, month):
    """
    generates all attestations for a given year
    :param month: unused parameter
    :param year: year about which attestations should be generated
    :return: nothing
    :raises: AttributeError: if a column-attribute has been modified in Infos_élèves or a row-attribute in data sheets
    """
    print("***** Génération des attestations... *****")

    # gets the data
    data = {}
    relevant_months = available_months(year)
    if len(relevant_months) == 0:
        print("Aucune donnée d'heures de cours n'a été trouvée. Les attestations générées seront vierges")
    for m in relevant_months:
        data[m] = data_extraction(year, m)
    clients = client_extraction()

    # Sets of every students from any sheet that are not in the database
    unregistered_students = set()
    for m in relevant_months:
        unregistered_students.update({candidate for candidate in data[m]})
    # Students in the database that aren't found in any sheet from any month
    unfound_students = set()
    missing_address = set()  # Clients whose address are missing

    for index, client in clients.iterrows():
        unfound_students.update({*client["Elèves rattachés"].split(' ; ')})
        if not has_address(client):
            missing_address.add(f"{client.Prénom} {client.Nom}")

    for index, client in clients.iterrows():
        matched_students = gen_attest(year, client, data, relevant_months)
        # Updating the warning sets
        unregistered_students.difference_update(matched_students)
        unfound_students.difference_update(matched_students)
    print("***** Génération des attestations terminée *****\n")
    return unregistered_students, unfound_students, missing_address


def update_warning_sets(old_sets, patch_sets):
    """

    :param old_sets:
    :param patch_sets:
    :return:
    """
    new_sets = map(set.union, old_sets, patch_sets)
    return new_sets


def execute(year, month, document_type):
    """
    calls the appropriate function according to the document_type that is asked for
    :param month:
    :param year:
    :param document_type: the type of document that is to be generated ('facture', 'attestation', 'bilan', 'all')
    :return: nothing
    """
    warning_sets = (set(), set(), set())
    gen_function = {
        'facture': gen_all_factures,
        'attestation': gen_all_attest,
    }
    if document_type == 'all':
        for m in available_months(year):
            gen_results = gen_all_factures(year, m)
            warning_sets = update_warning_sets(warning_sets, gen_results)
        gen_results = gen_all_attest(year, month)
        warning_sets = update_warning_sets(warning_sets, gen_results)
    else:
        gen_results = gen_function[document_type](year, month)
        warning_sets = update_warning_sets(warning_sets, gen_results)
    warning(*warning_sets)

# TODO Ajouter une génération de Bilan annuel avec: CA Annuel, plot du CA mensuel et/ou CA par semaine, avec comparaison
#  à la moyenne
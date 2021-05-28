from pdf_builder import pdf_build
from data_utils import data_extraction, available_months, student_extraction


# TODO print students whose data have been unused for each month when processing

def gen_all_factures(document_type, year, month):
    """
    generates all bills for a given month of a given year
    - fetches the appropriate data
    - puts together the variables that will be needed for building the pdf
    - calls the pdf builder pdf_build with following args :
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

    # TODO check on what exactly to iterate from the students dataframe
    for index, student in students.iterrows():
        # TODO check if a student name from the DB corresponds to a student in data, and match their data
        # We look for the corresponding in the data sheet
        for candidate in data:
            prenom = candidate.split(' ')[0]
            if len(candidate.split(' ')) > 1:
                # If there's a surname, we recreate it if it contains multiple words
                nom = candidate.split(' ', 1)

        # puts together the necessary variables
        # TODO do what the last comments says
        output_name = ''
        template_vars = {}

        # calls the pdf builder
        pdf_build(template_vars, document_type, output_name)


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
    students = []

    for student in students:
        # puts together the necessary variables
        output_name = ''
        template_vars = {}

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

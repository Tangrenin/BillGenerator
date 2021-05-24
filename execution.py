from pdf_builder import pdf_build
from data_utils import data_extraction, available_months


def gen_all_factures(year, month):
    """
    generates all bills for a given month of a given year
    - fetches the appropriate data
    - puts together the variables that will be needed for building the pdf
    - calls the pdf builder
    :param month: month about which bills should be generated
    :param year: year about which bills should be generated
    :return: nothing
    """
    # gets the data
    data = data_extraction(year, month)
    students = []

    for student in students:
        # puts together the necessary variables
        output_name = ''
        template_vars = {}

        # calls the pdf builder
        pdf_build(template_vars, 'facture', output_name)


def gen_all_attest(year, month):
    """
    generates all attestations for a given year
    - fetches the appropriate data
    - puts together the variables that will be needed for building the pdf
    - calls the pdf builder
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
        pdf_build(template_vars, 'attestation', output_name)


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
            gen_function[func](year, month)
    else:
        gen_function[document_type](year, month)

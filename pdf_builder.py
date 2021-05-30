from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
# Directory where bills will be generated (into their proper folder according to year/month)
from config.infos_script import output_directory
import re

"""
The main job of this script is the generation of the pdf documents, according to the document_type that is asked and the
template variables given
"""


def civility(value, short=True):
    """
    Converts 'M' or 'F' for into civilities.
    :param value: should be 'M' or 'F'
    :param short: a bool, True if civilites should be short and False if they should be long
    :return:
    """
    short_civilities = {"M": "M.", "F": "Mme"}
    long_civilities = {"M": "Monsieur", "F": "Madame"}
    try:
        return short_civilities[value] if short else long_civilities[value]
    except KeyError:
        return ''


def money(value):
    """
    Converts a float amount of money into the french formatting  ex 120735.98 -> '120 735,98 €'
    :param value: a float amount of money
    :return: a string representing money in french formatting
    """
    return f"{value:,.2f} €".replace(",", " ").replace('.', ',')


def is_defined(value):
    """

    :param value: -
    :return: True if value is a string, else False
    """
    return isinstance(value, str)


def pdf_build(template_vars, document_type, relative_output_path, file_name):
    """
    generates the document of type document_type, then saves the pdf file named 'file_name.pdf',
    :param template_vars: dictionary that contain all variables needed for the template rendering
    :param document_type: string 'facture' or 'attestation' depending on what document should be created
    :param relative_output_path: a string containing relative path from the output folder
    :param file_name: the pdf file name string  without the .pdf extension
    """
    file_html = f"templates/{document_type}_template.html"
    file_css = f"templates/{document_type}_style.css"

    if not Path(file_html).is_file():
        e = FileNotFoundError()
        e.filename = file_html
        raise e  # TODO la catch, le nom du fichier est dans e.filename
    if not Path(file_css).is_file():
        e = FileNotFoundError()
        e.filename = file_css
        raise e  # TODO la catch, le nom du fichier est dans e.filename

    # Checking a correcting if the file_name contains forbidden characters
    file_name = re.sub(r'[<>:"/\\|?*]', '', file_name)

    # Checking if the path folders and subfolders exist, else create it
    Path(output_directory + relative_output_path).mkdir(parents=True, exist_ok=True)

    pdf_name = Path(output_directory + relative_output_path + file_name + ".pdf")

    # loading the jinja2 environment
    env = Environment(loader=FileSystemLoader('.'))
    env.filters["civility"] = civility
    env.filters["money"] = money
    env.tests["defined"] = is_defined

    # Render and build
    template = env.get_template(file_html)
    html_out = template.render(template_vars)
    HTML(string=html_out).write_pdf(pdf_name, stylesheets=[file_css])

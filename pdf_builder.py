from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader

"""
The main job of this script is the generation of the pdf documents, according to the document_type that is asked and the
template variables given
"""


def pdf_build(template_vars, document_type, output_name):
    """
    generates the document of type document_type, then saves the pdf file named 'output_name.pdf',
    :param template_vars: dictionary that contain all variables needed for the template rendering
    :param document_type: string 'facture' or 'attestation' depending on what document should be created
    :param output_name: the name of the pdf file to be created. WITHOUT the extension '.pdf'
    """
    file_html = f"templates/{document_type}_template.html"
    file_css = f"templates/{document_type}_style.css"
    pdf_name = output_name

    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(file_html)

    html_out = template.render(template_vars)

    HTML(string=html_out).write_pdf(pdf_name, stylesheets=[file_css])

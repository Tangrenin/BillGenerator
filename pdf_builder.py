from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader

"""
Ce script génère le PDF à partir de [BLABLABLA]
"""

file_html = "templates/facture_template.html"
file_css = "templates/facture_style.css"
PDF_name = "Facture1" + ".pdf"

env = Environment(loader=FileSystemLoader('.'))
template = env.get_template(file_html)

# On rentre dans ce dico les variables du fichier HTML
template_vars = {"title": "Exemple de facture",
                 "client": "Frédéric",
                 "flower": "le jasmin"}

html_out = template.render(template_vars)

HTML(string=html_out).write_pdf(PDF_name, stylesheets=[file_css])

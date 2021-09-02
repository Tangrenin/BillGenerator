import shutil
from pathlib import Path
from config.infos_script import path_to_data
from scripts.data_utils import client_extraction

"""
The main job of this script is the generation of the data directory, and both the data sheets and the student database
 inside ready to be used
"""

"""
1. check si le dossier data existe, s'il n'existe pas le créer /*/
2. check si infos_élèves existe, s'il n'existe pas le créer
3. S'il existe extraire (avec data_utils ?) les noms des élèves 
4. Check si le dossier de l'année en cours existe, sinon le creer
5. pour chaque mois de l'année en cours, check si "cours-mois" existe, s'il n'existe pas, le creer et le remplir avec le
 noms des élèves
"""
# TODO trouver comment écrire dans un excel
# TODO décider si ce sera un script à part ou si c'est géré dans le main

# Check if data directory exists, else create it.
Path(path_to_data).mkdir(parents=True, exist_ok=True)

if not Path(f"{path_to_data}Infos_élèves.ods"):
    shutil.copy("templates/Infos_élèves.ods", f"{path_to_data}Infos_élèves.ods")
else:
    clients = client_extraction()
    # creation and flattening of the list of all attached students for every clients
    all_students = [student for students in clients["Elèves rattachés"] for student in students.split(' ; ')]

from ctypes import Structure, c_char_p, c_int, POINTER
import ctypes
import os

class Image(Structure):
    _fields_ = [("path", c_char_p),
                ("date", c_char_p)]

class Other(Structure):
    _fields_ = [("path", c_char_p),
                ("date", c_char_p)]

class Folder(Structure):
    _fields_ = [("images", POINTER(Image)),
                ("image_count", c_int),
                ("others", POINTER(Other)),
                ("other_count", c_int)]

if os.name == 'nt':
    FileUtils = ctypes.CDLL(os.getcwd() + '\\src\\lib\\libFileUtils.dll')
else:
    FileUtils = ctypes.CDLL(os.getcwd() + '/lib/libFileUtils.so')

FileUtils.getImages.argtypes = [c_char_p]
FileUtils.getImages.restype = POINTER(Folder)

FileUtils.freeFolder.argtypes = [POINTER(Folder)]
FileUtils.freeFolder.restype = None

FileUtils.moveFile.argtypes = [c_char_p, c_char_p]
FileUtils.moveFile.restype = c_int

# def get_destination_path():


def get_folder(button_state, path):
    if button_state[0] == '0':
        raise ValueError("Le chemin d'accès spécifié est invalide. Veuillez entrer un chemin de dossier existant et accessible.")
    elif button_state[0] == '1':
        raise ValueError("Le champs du chemin d'accès est vide. Veuillez entrer un chemin valide.")

    folder = FileUtils.getImages(path.encode('utf-8'))
    if not folder:
        raise ValueError("Une erreur s'est produite lors de l'accès au dossier. Vérifiez les permissions ou changez le dossier d'entré.")
    return folder

def check_button_state(button_state, folder, insertname_check_var):
    possible_state = ['2222', '2221', '2212', '2122', '2121', '2112']
    state = ''.join(button_state)
    if not folder:
        raise ValueError("Le chemin d'accès n'a pas été analysé. Veuillez commencer par analyser le chemin d'accès.")
    # if state not in possible_state:
    if state[0] == '1':
        raise ValueError("Le champs du chemin d'accès est vide. Veuillez entrer un chemin valide.")
    elif state[0] == '0':
        raise ValueError("Le chemin d'accès spécifié est invalide. Veuillez entrer un chemin de dossier existant et accessible.")
    if state[1] == '0':
        raise ValueError("Le champs du chemin de sortie est invalide. Veuillez entrer un chemin valide.")
    if state[2] == '0':
        raise ValueError("La méthode de tri sélectionné est invalide. Veuillez choisir une méthode valide pour le tri des documents.")
    if state[3] == '0':
        raise ValueError("La méthode de nommage sélectionné est invalide. Veuillez choisir une méthode valide pour le nommage des documents.")
    if state[2] == '1' and state[3] == '1':
        raise ValueError("Les champs de tri et de nommage sont vides. Veuillez spécifier des méthodes de tri et/ou de nommage des documents.")
    if insertname_check_var == 'on' and state[3] == '1':
        raise ValueError("L'option de remplacage du nom du fichier par sa date requiert l'utilisation d'un mode de renommage. Veuillez entrer un mode de renommage valide.")

def get_destination_path(path, output_path, sorting_type, naming_type, is_inserting_date, date):
    parent_path = output_path if output_path else os.path.dirname(path)
    sorted_subfolders = sorting_type.split('/')
    destination_path = f'{parent_path}'
    file_name = os.path.splitext(os.path.basename(path))
    separators = ['-', '_', ' ']
    dates = date.split('-')
    destination_date = ''

    # subfolders
    for folder in sorted_subfolders:
        i = 0
        destination_path += '\\'
        while i < len(folder):
            char = folder[i]
            if char in separators:
                destination_path += char
            else:
                if char == 'y':
                    destination_path += dates[0]
                    i += 4
                    continue
                elif char == 'm':
                    destination_path += dates[1]
                    i += 2
                    continue
                else:
                    destination_path += dates[2]
                    i += 2
                    continue
            i += 1
    if sorting_type:
        destination_path += '\\'
    
    # naming
    i = 0
    while i < len(naming_type):
        char = naming_type[i]
        if char in separators:
            destination_date += char
        else:
            if char == 'y':
                destination_date += dates[0]
                i += 4
                continue
            elif char == 'm':
                destination_date += dates[1]
                i += 2
                continue
            elif char == 'd':
                destination_date += dates[2]
                i += 2
                continue
            elif char == 'H':
                destination_date += dates[3]
                i += 2
                continue
            elif char == 'M':
                destination_date += dates[4]
                i += 2
                continue
            elif char == 'S':
                destination_date += dates[5]
                i += 2
                continue
        
        i += 1

    # add output folder, sorted folder, filename, date together    
    if is_inserting_date:
        if naming_type:
            # destination_path += file_name[0] + f' ({destination_date})' + file_name[1]
            destination_path += destination_date + ' ' + file_name[0] + file_name[1]
        else:
            destination_path += file_name[0] + file_name[1]
    else:
        destination_path += destination_date + file_name[1]
    
    return destination_path

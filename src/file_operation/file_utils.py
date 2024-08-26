from ctypes import Structure, c_char_p, c_int, POINTER
import customtkinter as CTk
from time import sleep
import tkinter as tk
import threading
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

def move_files(button_state, folder):
    possible_state = ['2222', '2221', '2212', '2122', '2121', '2112']
    state = ''.join(button_state)
    
    if state in possible_state and folder:
        # TODO start moving the files
        print()
    else:
        if not folder:
            raise ValueError("Le chemin d'accès n'a pas été analysé. Veuillez commencer par analyser le chemin d'accès.")
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
            raise ValueError("Les champs de tri et de nommage sont vides. Veuillez spécifier des méthodes de tri et de nommage des documents.")

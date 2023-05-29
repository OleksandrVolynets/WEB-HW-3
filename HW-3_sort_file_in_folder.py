"""This script is for sorting files in selected folder by file types.
    !!!!ATTENTION: Don't use this script for programm folders!!!!!!

    Files in subfolders are also sorted.
    In selected folder are created 5 folders(images, video, documents, audio, archives)
    Depending on the type, the file is moved to one of the following folders:
        'images': ['JPEG', 'PNG', 'JPG', 'SVG'],
        'video': ['AVI', 'MP4', 'MOV', 'MKV'],
        'documents': ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX', 'XLS', 'CSV'],
        'audio': ['MP3', 'OGG', 'WAV', 'AMR'],
        'archives': ['ZIP', 'GZ', 'TAR']
    Files with a type not listed above are not moved.
    Unpacked archives replaced into folder "archives" in folder with archives name 
    Also, name all files and folders are normalized (transliterate cyrillik symbols into latin, 
                                                    all symbols except latin and digit are replaced by "_" )
    Empty folders are deleted       

"""
import os
import shutil
import sys
import re
from pathlib import Path
from threading import Thread

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

TRANSLATION_CYR_LAT = dict(zip(CYRILLIC_SYMBOLS, TRANSLATION))

DICT_FOLDER_FILETYPE = {'images': ['JPEG', 'PNG', 'JPG', 'SVG'],
                        'video': ['AVI', 'MP4', 'MOV', 'MKV'],
                        'documents': ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX', 'XLS', 'CSV'],
                        'audio': ['MP3', 'OGG', 'WAV', 'AMR'],
                        'archives': ['ZIP', 'GZ', 'TAR']}

DICT_ABS_PATH_FILE = {}


def dict_all_files(path):
    global DICT_ABS_PATH_FILE
    for i in os.listdir(path):
        if os.path.isdir(Path(path, i)) and not i in DICT_FOLDER_FILETYPE.keys():
            dict_all_files(Path(path, i))
        else:
            DICT_ABS_PATH_FILE[Path(path, i)] = i
    return DICT_ABS_PATH_FILE


def normalize_folder(folder_name):
    normalize_name = ''

    for ch in folder_name:
        if 'a' <= ch.lower() <= 'z' or ch.isdigit():
            normalize_name += ch
        elif ch in TRANSLATION_CYR_LAT.keys():
            normalize_name += TRANSLATION_CYR_LAT[ch]
        elif ch.lower() in TRANSLATION_CYR_LAT.keys():
            normalize_name += TRANSLATION_CYR_LAT[ch.lower()].upper()
        else:
            normalize_name += '_'
    return normalize_name


def normalize_file(file_name):
    name = os.path.splitext(file_name)
    suffix = name[1]
    normalize_name = ''

    for ch in name[0]:
        if 'a' <= ch.lower() <= 'z' or ch.isdigit():
            normalize_name += ch
        elif ch in TRANSLATION_CYR_LAT.keys():
            normalize_name += TRANSLATION_CYR_LAT[ch]
        elif ch.lower() in TRANSLATION_CYR_LAT.keys():
            normalize_name += TRANSLATION_CYR_LAT[ch.lower()].upper()
        else:
            normalize_name += '_'
    return normalize_name+suffix


def rename_folder(path):
    for f in os.listdir(path):
        abs_path = os.path.join(path, f)
        normalize_path = os.path.join(path, normalize_folder(f))
        if os.path.isdir(abs_path) and re.search('[^a-zA-Z0-9_]+', f):
            os.rename(abs_path, normalize_path)


def create_folders(path):
    for k in DICT_FOLDER_FILETYPE.keys():
        new_folder = os.path.join(path, k)
        if k in os.listdir(path):
            continue
        else:
            os.mkdir(new_folder)


def remove_files(path, dict_files, dict_filetype):
    for k, v in dict_files.items():
        file = os.path.splitext(v)
        suffix = file[1][1:].upper()
        for k1, v1 in dict_filetype.items():
            if suffix in v1 and k1 != 'archives':
                os.replace(k, Path(path, k1, normalize_file(v)))
            elif suffix in v1 and k1 == 'archives':
                shutil.unpack_archive(k, Path(path, k1, file[0]))
            else:
                continue


def del_empty_folders(path):
    for f in os.listdir(path):
        abs_path = Path(path, f)
        if os.path.isdir(abs_path) and not f in DICT_FOLDER_FILETYPE.keys():
            if len(os.listdir(abs_path)) == 0:
                os.removedirs(abs_path)
            else:
                del_empty_folders(abs_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("You need to enter the folder path:")
    else:
        try:
            path = sys.argv[1]
            if os.path.isdir(path):
                thread_1 = Thread(target=dict_all_files, args=(path,))
                thread_1.start()
                create_folders(path)
                thread_1.join()
                remove_files(path, DICT_ABS_PATH_FILE, DICT_FOLDER_FILETYPE)
                rename_folder(path)
                del_empty_folders(path)
        except ValueError:
            print("Something gone wrong... check the path ")

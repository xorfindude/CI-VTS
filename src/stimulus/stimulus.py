import json
import os
from datetime import datetime

"""
Module providing a number of methods for handling stimulus profiles.
"""

_sp_dir = "stimulus/stimulus_profiles/"


def get_sp_dir():
    """
    :return: str of path to store stimulus profiles, stoted global to module
    """
    return _sp_dir


def verify_or_create_sp_dir(func):
    """
    Wrappable function to verify that the directory to store stimulus profiles in exists, create it if it does not.
    This is useful with decorators, no need to reimplement checking for every new method.
    :param func: function to wrap around
    :return: function to wrap around
    """
    try:
        if not os.path.isdir(_sp_dir):
            os.mkdir(_sp_dir)
        return func
    except Exception as e:
        print("Error verifying stimulus profile dir:")
        print(e)


def save_stimulus_profile(profile, path=_sp_dir):
    """
    Save a stimulus profile to the user's machine
    :param profile: formatted data comprising the stimulus profile
    :param path: folder to save profile to
    :return:
    """
    try:
        with open(path + profile["name"] + profile["extension"], 'w') as f:
            json.dump(profile, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print("Error when saving stimulus profile")
        print(e)


@verify_or_create_sp_dir
def make_stimulus_profile(data, file_name=None, description=None, file_ext=".json"):
    """
    :param data: stimulus intervals with duration and intensity
    :param file_name: name of file to save to
    :param description: description of profile
    :param file_ext: file extenstion, recommend using .json
    :return: None
    """
    try:
        if file_name is None:
            done = False
            index = 1
            file_name = "stimulus_profile"
            while not done:
                if not os.path.isfile(_sp_dir + file_name + file_ext):
                    done = True
                else:
                    file_name = "stimulus_profile" + str(index)
                    index = index + 1

        profile = {"name": file_name, "description": description, "date_created": str(datetime.now().date()),
                   "data": data, "extension": file_ext}

        return profile

    except Exception as e:
        print("Error when making stimulus profile:")
        print(e)
        return False


@verify_or_create_sp_dir
def load_stimulus_profile(file_name, file_path=_sp_dir, extension=".json"):
    """
    Load up a stimulus profile from the user's machine.
    :param file_name: name of file containing profile
    :param file_path: folder where file is found
    :param extension: file extension of the loaded file, recommend using .json
    :return: dictionary object created from the structure of the file data
    """
    try:
        with open(file_path + file_name + extension, 'r') as f:
            r_data = json.load(f)
            return r_data
    except Exception as e:
        print("Error when loading stimulus profile:")
        print(e)


@verify_or_create_sp_dir
def get_all_stimulus_profile_names():
    """
    Retrieve all files in the path of a stimulus profile dir
    :return: List of all profile names
    """
    names = []
    try:
        for p in os.listdir(_sp_dir):
            with open(_sp_dir + p, 'r') as f:
                names.append(json.load(f)["name"])
    except Exception as e:
        print("Error when getting stimulus profile names:")
        print(e)
    return names


def delete_stimulus_profile(name, ext=".json"):
    """
    Delete a file containing stimulus profile
    :param name: name of file to delete
    :param ext: extension of file to delete
    :return: bool indicating if deletion was successful.
    """
    try:
        if name is not None:
            os.remove(_sp_dir + name + ext)
            return True
    except Exception as e:
        print("An error occurred when deleting stimulus profile:")
        print(e)
        return False

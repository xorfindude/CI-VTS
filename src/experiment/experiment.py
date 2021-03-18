import json
import os
from datetime import datetime

_ex_dir = "experiment/experiment_profiles/"


def get_ex_dir():
    return _ex_dir


def verify_or_create_ex_dir(func):
    try:
        if not os.path.isdir(_ex_dir):
            os.mkdir(_ex_dir)
        return func
    except Exception as e:
        print("Error when verifying experiment profile dir:")
        print(e)


@verify_or_create_ex_dir
def save_experiment_profile(stimulus_profile=None, experiment_settings=None, file_path=None, file_name=None, description=None, file_ext=".json"):
    try:
        if file_path is None:
            file_path = _ex_dir

        if file_name is None:
            print("kjbfsgsfgnkjbfgkdkfg")
            done = False
            index = 1
            file_name = "experiment_profile"
            while not done:
                if not os.path.isfile(_ex_dir + file_name + file_ext):
                    done = True
                else:
                    file_name = "experiment_profile" + str(index)
                    index = index + 1

        profile = {"name": file_name, "stimulus_profile": stimulus_profile,
                   "settings": experiment_settings, "description": description,
                   "date_created": str(datetime.now().date())}

        with open(file_path + file_name + file_ext, 'w') as f:
            json.dump(profile, f, ensure_ascii=False, indent=4)

        return profile

    except Exception as e:
        print("Error when saving experiment profile")
        print(e)


@verify_or_create_ex_dir
def load_experiment_profile(file_name, file_path=_ex_dir, extension=".json"):
    try:
        with open(file_path + file_name + extension, 'r') as f:
            r_data = json.load(f)
            return r_data
    except Exception as e:
        print("Error when loading experiment profile:")
        print(e)


@verify_or_create_ex_dir
def get_all_experiment_profile_names():
    names = []
    try:
        for p in os.listdir(_ex_dir):
            with open(_ex_dir + p, 'r') as f:
                names.append(json.load(f)["name"])
    except Exception as e:
        print("Error when getting experiment profile names")
        print(e)
    return names



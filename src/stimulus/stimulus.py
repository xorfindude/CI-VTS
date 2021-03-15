import json
import os
from datetime import datetime

_sp_dir = "stimulus/stimulus_profiles/"


def get_sp_dir():
    return _sp_dir


def save_stimulus_profile(data, file_name=None, description=None, file_ext=".json"):
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

        elif os.path.isfile(_sp_dir + file_name + file_ext):
            done = False
            index = 1
            tmp_file_name = file_name + str(index)
            while not done:
                if not os.path.isfile(_sp_dir + tmp_file_name + file_ext):
                    done = True
                    file_name = tmp_file_name
                else:
                    index = index + 1
                    tmp_file_name = file_name + str(index)

        profile = {"name": file_name, "description": description, "date_created": str(datetime.now().date()), "data": data,}

        with open(_sp_dir + file_name + file_ext, 'w') as f:
            json.dump(profile, f, ensure_ascii=False, indent=4)

        return profile

    except Exception as e:
        print("Error when saving profile:")
        print(e)
        return False


def load_stimulus_profile(file_path, extension=".json"):
    try:
        with open(_sp_dir + file_path + extension, 'r') as f:
            r_data = json.load(f)
            return r_data
    except Exception as e:
        print("Error when loading profile:")
        print(e)



def get_all_stimulus_profile_names():
    names = []
    for p in os.listdir(_sp_dir):
        with open(_sp_dir + p, 'r') as f:
            names.append(json.load(f)["name"])
    return names


def update_profile(self, data):
    pass

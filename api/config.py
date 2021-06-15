from yaml import load, FullLoader
from Domoticz import Debug, Error

_config_basedir = None

_config = None

def set_config_location(path):
    global _config_basedir
    _config_basedir = path

def get_mqtt_config(reload=False):
    global _config
    if _config is None or reload:
        try:
            Debug("Loading config from file...")
            with open("{}/{}".format(_config_basedir, "config.yml")) as file:
                _config = load(file, FullLoader)
        except FileNotFoundError:
            Error("Configuration not found...")
            return
    
    return _config

def get_global_device_types_filename():
    return "{}/{}".format(_config_basedir, "device_types.yml")

def get_user_device_types_filename():
    return "{}/{}".format(_config_basedir, "user_types.yml")

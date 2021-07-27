import os
import configparser

file_path = os.path.abspath(__file__)
file_format = os.path.splitext(file_path)[-1]
base_dir = os.path.dirname(os.path.dirname(file_path))
elk_base_dir = os.path.dirname(base_dir)
config_file_path = os.path.join(base_dir, 'security_platform/config.ini')
app_file_path = os.path.join(base_dir, 'security_platform/security_platform')

config_parser = configparser.ConfigParser()
config_parser.read(config_file_path)

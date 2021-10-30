import os
from data_platform.environment import Environment

active_environment = Environment[os.environ['ENVIRONMENT']]
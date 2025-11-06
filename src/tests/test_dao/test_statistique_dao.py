import os 
import pytest 
from datetime import date 
from unittest.mock import patch 
from utils.reset_database import ResetDatabase 
from dao.statistique_dao import StatistiqueDao 
from business_object.statistique import Statistique
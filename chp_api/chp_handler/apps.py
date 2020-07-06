from django.apps import AppConfig
import os
from pathlib import Path

from chp.core.reasoner_std import ReasonerStdHandler


class ChpHandlerConfig(AppConfig):
    name = 'chp_handler'
    BKBS_PATH = Path("bkbs")
    COLLAPSED_BRCA_BKB_PATH = Path("bkbs/brca-50-fusion.bkb")

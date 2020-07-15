from django.apps import AppConfig
import os
from pathlib import Path

from chp.reasoner_std import ReasonerStdHandler


class ChpHandlerConfig(AppConfig):
    name = 'chp_handler'

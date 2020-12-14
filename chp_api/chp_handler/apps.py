from django.apps import AppConfig
import os
import multiprocessing
import logging

from chp.reasoner import ChpJointReasoner, ChpDynamicReasoner
from chp_data.bkb_handler import BkbDataHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChpApiConfig(AppConfig):
    logger.info('Running CHP API Configuration.')
    name = 'chp_handler'

    # Used for distrbuted reasoning
    # Get Hosts File if it exists
    #parent_dir = os.path.dirname(os.path.realpath(__file__))
    #HOSTS_FILENAME = os.path.join(parent_dir, 'hosts')
    #NUM_PROCESSES_PER_HOST = multiprocessing.cpu_count()
    #if not os.path.exists(HOSTS_FILENAME):
    hosts_filename = None
    num_processes_per_host = 0

    # Instantiate BKB handler
    bkb_handler = BkbDataHandler(
        bkb_major_version='coulomb',
        bkb_minor_version='1.0'
    )

    logger.info('Instantiating reasoners.')
    # Instantiate Reasoners
    dynamic_reasoner = ChpDynamicReasoner(
        bkb_handler=bkb_handler,
        hosts_filename=hosts_filename,
        num_processes_per_host=num_processes_per_host)
    joint_reasoner = ChpJointReasoner(
        bkb_handler=bkb_handler,
        hosts_filename=hosts_filename,
        num_processes_per_host=num_processes_per_host)

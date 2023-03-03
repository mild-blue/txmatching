import time
import cProfile
import logging
import sys
import argparse

from txmatching.database.services.txm_event_service import get_txm_event_complete
from txmatching.web import create_app
from txmatching.database.migrate_db import migrate_db
from txmatching.database.services.config_service import get_configuration_parameters_from_db_id_or_default
from txmatching.data_transfer_objects.patients.out_dtos.conversions import to_lists_for_fe



if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--nolog', action='store_false', dest='log')
  parser.set_defaults(log=True)
  parser.add_argument('--data', dest='data', default='mock') 
  args = parser.parse_args()

  app = create_app()
  if not args.log:
    logging.disable(logging.ERROR)
    
  migrate_db(app.config['SQLALCHEMY_DATABASE_URI'])

  if args.data == 'mock':
    txm_event_id = 3
    configuration_db_id = 2
  elif args.data == 'high_res':
    txm_event_id = 2
    configuration_db_id = 3

  with app.app_context():
    start = time.time()
    txm_event = get_txm_event_complete(txm_event_id)
    print('Loading txm_event took: {:4f}s'.format(time.time()-start))

    config_parameters = get_configuration_parameters_from_db_id_or_default(txm_event, configuration_db_id)
    
    start = time.time()
    cProfile.run('to_lists_for_fe(txm_event, config_parameters)', sort='cumtime')

    print('Run took: {:.4f}s'.format(time.time()-start))
    pass
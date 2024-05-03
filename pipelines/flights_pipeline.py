import pandas as pd
import json
import sys
import os

from datetime import datetime

root_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, root_dir)

from etls.flights_etl import extract_flights_information, transform_to_csv

def run_pipeline(kwargs):
	""" 
	    Get the flights JSON response. Transform its contents
	    to CSV files regarding:
		- Best flights
		- Other flights
		- Search parameters
		- Price insights
	"""
	trajectory = f'{kwargs["departure_id"]}:{kwargs["arrival_id"]}'
	search_date = datetime.now().strftime('%Y%m%d')

	outbound_date = kwargs['outbound_date'].replace('-','')
	return_date = kwargs['return_date'].replace('-', '')

	branch_dir = f'{trajectory}/{outbound_date}-{return_date}/{search_date}'

	# Extract bronze data
	response = extract_flights_information(branch_dir, kwargs)

	# Separate silver data
	silver_output_dir = os.path.join(root_dir, f'data/output/{branch_dir}/silver')
	transform_to_csv(response, silver_output_dir)

	return {'statusCode': 200}

if __name__ == '__main__':
	run_pipeline(kwargs)
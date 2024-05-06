import pandas as pd
import datetime
import requests
import json
import copy
import sys
import os

root_dir = os.path.dirname(os.path.dirname(__file__))

sys.path.insert(0, root_dir)

from utils.constants import FLIGHTS_API_KEY

def get_api_request(
            engine: str,
            departure_id: str,
            arrival_id: str,
            outbound_date: str,
            return_date: str,
            currency: str,
            hl: str
        ) -> dict:
    """
        Send GET request to fetch flights.
    """
    url = "https://serpapi.com/search.json"

    params = dict(
        engine=engine, 
        departure_id=departure_id, 
        arrival_id=arrival_id, 
        outbound_date=outbound_date, 
        return_date=return_date, 
        currency=currency, 
        hl=hl,
        api_key=FLIGHTS_API_KEY
    )

    response = requests.get(
        url,
        params
    )

    return response.json()

def extract_flights_information(branch_dir:str, flight_information:dict) -> dict:
    """
        Save extracted raw data
        as JSON file.
    """
    outbound_date = flight_information['outbound_date']
    outbound_date = outbound_date.replace('-', '')

    departure_id = flight_information['departure_id']

    if 'return_date' in flight_information.keys():
        return_date = flight_information['return_date']
        return_date = return_date.replace('-', '')
    
    arrival_id = flight_information['arrival_id']

    response = get_api_request(**flight_information)

    print(response)

    response['best_trips'] = response['best_flights']
    del response['best_flights']

    response['other_trips'] = response['other_flights']
    del response['other_flights']

    date = datetime.datetime.now().strftime('%Y%m%d')

    output_dir = os.path.join(root_dir, f'data/output/{branch_dir}')
    json_output_dir = os.path.join(output_dir, 'bronze')
    silver_output_dir = os.path.join(output_dir, 'silver')
	
    if not (os.path.exists(json_output_dir)):
        os.makedirs(json_output_dir)
    if not (os.path.exists(silver_output_dir)):
        os.makedirs(silver_output_dir)
	
    filename = "raw.json"
    raw_output_dir = os.path.join(json_output_dir, filename)

    filedir = os.path.join(json_output_dir, filename)

    with open(filedir, 'w') as json_file:
        json.dump(response, json_file)

    return response

def transform_flights(flights: list) -> list:
    """
        Reshape flights JSON file.
    """
    # output_filenames = []
    data = []

    for f, flight in enumerate(flights):
        da = flight['departure_airport']
        aa = flight['arrival_airport']

        # Information
        flight_information = dict(
            da_name = da['name'],
            da_id = da['id'],
            da_time = da['time'],
            aa_name = aa['name'],
            aa_id = aa['id'],
            aa_time = aa['time'],
            duration = flight['duration'],
            airplane = flight['airplane'],
            airline = flight['airline'],
            airline_logo = flight['airline_logo'],
            travel_class = flight['travel_class'],
            flight_number = flight['flight_number'],
            legroom = flight['legroom'],
            additional_information = ', '.join(flight['extensions'])
        )

        data.append(flight_information)
    
    columns = list(flight_information.keys())
    
    # return columns, data, output_filenames
    return data

def transform_layovers(layovers: list) -> dict:
    """
        Reshape layovers JSON file.
    """
    # output_filenames = []
    data = []

    for l, lay in enumerate(layovers):

        # Information
        layover_information = dict(
            duration = lay['duration'],
            name = lay['name'],
            id = lay['id']
        )

        data.append(layover_information)
    
    columns = list(layover_information.keys())
    
    # return columns, data, output_filenames
    return data

def transform_trips(trips_json:list) -> dict:
    """
        Reshape trips JSON file.
    """
    flight_information = []
    layover_information = []
    trip_information = []

    # `best_flights` contains `trips`, called flights.
    for trip in trips_json:
        # Flights
        flights = trip['flights']
        
        flight_data = transform_flights(flights)
        flight_information.append(flight_data)

        # Layovers
        layovers = trip['layovers']
        layover_data = transform_layovers(layovers)
        layover_information.append(layover_data)

        # Trip information
        trip_data = copy.deepcopy(trip)
        del trip_data['layovers']
        del trip_data['flights']
        
        trip_information.append(trip_data)

    return flight_information, layover_information, trip_information

def generate_flight_csv(flights_json: dict, trips_output_dir:str, trip_category:str) -> None:
    """
        Helper function to generate flight CSVs.
        : trip_category either [`best_flights`, `other_flights`]
    """
    flights_output_dir = os.path.join(trips_output_dir, 'flights')
    layovers_output_dir = os.path.join(trips_output_dir, 'layover')
    trip_info_output_dir = os.path.join(trips_output_dir, 'trip_information')

    if not os.path.exists(trips_output_dir):
        os.makedirs(trips_output_dir)
    if not os.path.exists(flights_output_dir):
        os.makedirs(flights_output_dir)
    if not os.path.exists(layovers_output_dir):
        os.makedirs(layovers_output_dir)
    if not os.path.exists(trip_info_output_dir):
        os.makedirs(trip_info_output_dir)

    best_trips = flights_json[trip_category]

    flight_information, layover_information, trip_information = transform_trips(best_trips)

    # Saving flight information
    for i, (flight_info, layover_info, trip_info) in enumerate(zip(flight_information, layover_information, trip_information)):
        # Concatenate the multiple flights in a trip, to one dataframe
        flight_filename = f'trip_{i}.csv'

        print(flight_filename)
        fl_concat_dfs = []
        fl_output_dir = os.path.join(flights_output_dir, flight_filename)
        for f, flight in enumerate(flight_info):
            df = pd.DataFrame(flight, columns=list(flight.keys()), index=[0])
            fl_concat_dfs.append(df)
        
        concatenated_df = fl_concat_dfs[0]
        for dfc in fl_concat_dfs[1:]:
            concatenated_df = pd.concat([concatenated_df, dfc], axis=0)

        print(concatenated_df)
        concatenated_df.to_csv(fl_output_dir)

        # Concatenate the multiple layovers in a trip, to one dataframe
        layover_filename = f'layover_{i}.csv'

        print(layover_filename)
        layover_concat_dfs = []
        lay_output_dir = os.path.join(layovers_output_dir, layover_filename)
        for l, layover in enumerate(layover_info):
            df = pd.DataFrame(layover, columns=list(layover.keys()), index=[0])
            layover_concat_dfs.append(df)
        
        concatenated_layover_df = layover_concat_dfs[0]
        for dfc in layover_concat_dfs[1:]:
            concatenated_layover_df = pd.concat([concatenated_layover_df, dfc], axis=0)

        concatenated_layover_df.to_csv(lay_output_dir)
        print(concatenated_layover_df)

        # Save trip information
        trip_info_filename = f'info_trip_{i}.csv'
        trip_info_concat_dfs = []
        tinfo_output_dir = os.path.join(trip_info_output_dir, trip_info_filename)

        df = pd.DataFrame(trip_info, columns=list(trip_info.keys()), index=[0])        
        df.to_csv(tinfo_output_dir)
        print(df)

def transform_to_csv(flights_json: dict, silver_output_dir: str):
    """
        Decouple raw data into multiple csv.
    """
    # Search parameters
    ## This might want to be saved in logs
    search_parameters = flights_json['search_parameters']

    df = pd.DataFrame.from_dict(search_parameters, orient='index')

    search_parameters_output_dir = os.path.join(silver_output_dir, 'search_parameters.csv')
    df.to_csv(search_parameters_output_dir, encoding='utf-8', index=False)

    # Best flights
    ## This can be its own feature
    print('[i] Generating best trips.')
    best_trips_output_dir = os.path.join(silver_output_dir, 'best_trips')
    generate_flight_csv(flights_json, best_trips_output_dir, 'best_trips')
    
    # Other flights
    ## This can be its own feature
    print('[i] Generating other trips.')
    other_trips_output_dir = os.path.join(silver_output_dir, 'other_trips')
    generate_flight_csv(flights_json, other_trips_output_dir, 'other_trips')

if __name__ == '__main__':
    extract_flights()
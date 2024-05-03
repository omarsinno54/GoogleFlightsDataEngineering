This project is still in development. Stay tuned for the end result!

# ✈️ Google Flights ETL Pipeline
In this project we build an ETL pipeline, that extracts data using the Google Flights API (serpapi).

It would be interesting to have a ready tool to analyze patterns in word frequency in different subreddits.

# ⏳ When will this project be finished?
This project will be considered complete once the following features are added:
- Ability to run jobs with Apache Airflow
- Features are portable
- Dockerization
- Diagram

# 🗂️ Folder Structure
```
+ ---- config
    config.conf
+ ---- data
    + --- input
    + --- output
            + --- {DEPARTURE AIRPORT}:{ARRIVAL AIRPORT}
                + --- {TRIP START DATE}-{TRIP END DATE}
                    + --- {SEARCH DATE}
                        + --- bronze
                            raw.json
                        + --- silver
                            + --- best_trips
                                + --- flights
                                + --- layover
                                + --- trip_information
                            + --- other_trips
                                + --- flights
                                + --- layover
                                + --- trip_information
                            search_paramters.csv
                        + --- gold
            ...
+ ---- etls
        flights_etl.py
+ ---- pipelines
        flights_pipeline.py
+ ---- utils
        constants.py
```

`config`: Contains `config.conf`, which contains the SERP API Key used to send the API request. You will have to create the config file and add your credentials, as below:

```
[api_keys]
flights_api_key = *api key*
```

`data`:
- `input` any cached data that might be referred to. 
- `output` contains the output JSON and CSV data.
  - `bronze` contains the raw JSON data as output from the API requested.
  - `silver` contains **compiled** data, as personally found necessary to be compiled.
    - `best_trips` contains the information compiled with respect to the best prices & and shorter trip times (according to Google Flights).
      - `flights`
      - `layover`
      - `trip_information`
    - `other_trips` contains the other available trips found on Google Flights.
      - `flights`
      - `layover`
      - `trip_information`
  - `search_parameters` are logged in this folder, which are the parameters used for the search.

`etls`: The script used for data extraction, transformation, and loading.

`pipelines`: Orchestrates the ETL scripts and functions to form a pipeline-like flow.

`utils`: contains a `constants.py` script, which uses the `ConfigParser` library to parse the config file defined earlier.

# 🏃🏽‍♂️ How To Run

1. First make sure to set the `config.conf` file as described above. 

2. Using the terminal `cd` into `pipelines` and run the `flights_pipeline.py` script.

```
python3 flights_pipeline.py
```

# 🔧 Improvements to be added soon!
1. Add data caching feature.
2. Add arguments to modify:
   1. Departure date
   2. Return date (optional)
   3. Filters
   4. Departure airpot
   5. Arrival airport
3. Dockerize project.
4. Use Apache Airflow for orchestration and visual web server.
5. Load data on AWS.


# ℹ️ Reference
1. SERP API documentation: https://serpapi.com/google-flights-api#api-parameters-search-query-departure-id

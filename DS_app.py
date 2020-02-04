import numpy as np
import pandas as pd
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Calculate needed dates
session = Session(engine)
last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
twelve_months_ago = dt.datetime.strptime(last_date[0], '%Y-%m-%d') - dt.timedelta(days=365)
session.close()

# Set trip dates
trip_start = '2016-09-15'
trip_end = '2016-09-25'

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def index():
    return  (
        f"Welcome to my App!<br/>"
        f"<h3>Available Routes:</h3><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the data and precipitation scores
    prcp_last_twelve_months = session.query(Measurement.date, func.avg(Measurement.prcp)).\
    filter(Measurement.date > twelve_months_ago).\
    group_by(Measurement.date).\
    order_by(Measurement.date).all()

    session.close()

    # Convert the query results to a Dictionary using date as the key and prcp as the value.
    prcp_data = []
    for date, prcp in prcp_last_twelve_months:
        date_dict = {}
        date_dict["date"] = date
        date_dict["prcp"] = prcp
        prcp_data.append(date_dict)

    # Return the JSON representation of your dictionary.
    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Get all stations
    stations = session.query(Station.station, Station.name).all()
    
    session.close()

    # Return a JSON list of stations from the dataset
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # query for the dates and temperature observations from a year from the last data point
    tobs_last_twelve_months = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date > twelve_months_ago).\
    order_by(Measurement.date).all()
    session.close()

    #Return a JSON list of Temperature Observations (tobs) for the previous year
    return jsonify(tobs_last_twelve_months)

@app.route("/api/v1.0/<start>")
def tobs_stats_search_start(start):

    if start > str(last_date[0]):
        return "Sorry, that date is outside of our database's date range"
    
    else:
        # Create our session (link) from Python to the DB
        session = Session(engine)

        # query for the dates and temperature observations from the date input by user
        results_start_date = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
        session.close()

        return jsonify(results_start_date)

@app.route("/api/v1.0/<start>/<end>")
def tobs_stats_search_start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    if start > str(last_date[0]):
        return "Sorry, that date is outside of our database's date range"
    elif end > str(last_date[0]):
        # query for the dates and temperature observations from the date input by user
        results_start_date = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
        
        return (
            f"Sorry, the end date is outside of our database's date range<br/>"
            f"We will give you the results until {last_date[0]}<br/>" 
            f"Minimum Temperature: {results_start_date[0][0]}<br/>"
            f"Average Temperature: {round(results_start_date[0][1],2)}<br/>"
            f"Maximum Temperature: {results_start_date[0][2]}<br/>"
            )
        
    else:
        
        # query for the dates and temperature observations from a year from the last data point
        results_start_end_date = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

        #Return a JSON list of Temperature Observations (tobs) for the previous year
        return jsonify(results_start_end_date)

    session.close()

# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)
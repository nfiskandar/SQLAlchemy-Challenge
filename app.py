import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

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
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    session = Session(engine)

    # Query all prcp data
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    first_date = session.query(Measurement.date).order_by(Measurement.date).first()
    session.close()
    
    """List all available api routes."""
    return (
        f"SQLAlchemy Homework - Surfs Up!<br/>"
        f"Step 2- Climate App<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br/>"
        f"<br/>"
        f"Please note the following for query on date.<br/>"
        f"Date format: YYYY-MM-DD<br/>"
        f"First: based on start date only <br/>"
        f"<br/>"
        f"Route based on start date:<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/>"
        f"Change YYYY-MM-DD with the date you selected<br/>"
        f"<br/>"
        f"Second: based on start date and end date<br/>"
        f"First YYYY-MM-DD after /v1.0 is for start date.<br/>"
        f"Last YYYY-MM-DD is for end date.<br/>"
        f"<br/>"
        f"Route based on start date and end date:<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br/>"
        f"Change both YYYY-MM-DD with the date you selected.<br/>"
        f"<br/>"
        f"Please select between {first_date[0]} and {last_date[0]}"
        )


@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all prcp data
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list 
    weather_data = []
    for date, prcp in results:
        weather_dict = {}
        weather_dict["date"] = date
        weather_dict["prcp"] = prcp
        weather_data.append(weather_dict)

    return jsonify(weather_data)

@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all prcp data
    results = session.query(Station.station, Station.name, Station.latitude , Station.longitude , Station.elevation).all()

    session.close()

    # Create a dictionary from the row data and append to a list 
    stations_data = []
    for station, name, latitude, longitude, elevation in results:
        stations_dict = {}
        stations_dict["station"] = station
        stations_dict["name"] = name
        stations_dict["latitude"] = latitude
        stations_dict["longitude"] = longitude
        stations_dict["elevation"] = elevation
        stations_data.append(stations_dict)

    return jsonify(stations_data)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all prcp data
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    lastdate_yr = int(last_date[0].split('-')[0])
    lastdate_mth = int(last_date[0].split('-')[1])
    lastdate_day = int(last_date[0].split('-')[2])
    
    from dateutil.relativedelta import relativedelta
    a_year_ago = dt.date(lastdate_yr, lastdate_mth, lastdate_day) - relativedelta(years=1)
    
    #results = session.query(Measurement.date, Measurement.tobs).all()
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= a_year_ago).all()
    
    session.close()

    # Create a dictionary from the row data and append to a list 
    temperature_data = []
    for date, tobs in results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        temperature_data.append(temp_dict)

    return jsonify(temperature_data)

@app.route("/api/v1.0/<start>")
def startdate(start):
    """When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    All_temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs            ), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= last_date[0]).all()
        
    session.close()

    return jsonify(All_temps)

    return jsonify({"error": f"No Data for selected start date."}), 404

@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):
    """When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""
       
    All_temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        
    session.close()

    return jsonify(All_temps)

    return jsonify({"error": f"No Data for selected start date."}), 404

if __name__ == '__main__':
    app.run(debug=True)

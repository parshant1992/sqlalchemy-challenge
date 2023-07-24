# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt
import numpy as np
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
app = Flask(__name__)
#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all the available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/<br/>"
        f"/api/v1.0/start/end/<br/>"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    """List of precipitation of last 12 months of data."""

    # Create our session (link) from Python to the DB
    session = Session(engine)
    most_recent_date= dt.datetime(2017, 8, 23)

    one_year_ago = most_recent_date  - dt.timedelta(days=366) 
    # Perform a query to retrieve the data and precipitation scores

    prcp_date = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date>=one_year_ago).all()
    session.close()
     
    #Convert the query results from your precipitation analysis 
    # (i.e. retrieve only the last 12 months of data) to a 
    # dictionary using date as the key and prcp as the value
    precipitation = []
    for date, prcp in prcp_date:
        prcp_dict = {}
        prcp_dict[date] = prcp
        precipitation.append(prcp_dict)
    return jsonify(precipitation)
    
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset"""
    # Create our session (link) from Python to the DB
    session = Session(engine)    
    # Design a query to calculate the total number of stations in the dataset

    station_query = session.query(func.count(func.distinct(Measurement.station))).all()
    
    session.close()
    #list of stations from the dataset
    station_list = list(np.ravel(station_query))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return list of temperature observations for the previous year"""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    most_recent_date= dt.datetime(2017, 8, 23)

    one_year_ago = most_recent_date  - dt.timedelta(days=366)

    most_stations = session.query( Measurement.station , func.count(Measurement.station)).group_by( Measurement.station ).\
               order_by(func.count(Measurement.station).desc()).all()
    active_station = most_stations[0][0]
    session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.station == active_station).all()
    tempe_query = session.query(func.distinct(Measurement.tobs), func.count(Measurement.tobs)).group_by(Measurement.tobs).filter(Measurement.date >= one_year_ago).filter(Measurement.station == active_station)
    
    session.close()
    #Return a list of temperature observations for the previous year
    tem_obseved = []
    for date, tobs in tempe_query:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tem_obseved.append(tobs_dict)
    return jsonify(tem_obseved)



@app.route("/api/v1.0/start/")
def start (start):

   
# Create our session (link) from Python to the DB
    session = Session(engine)
    """Return a list of the minimum temperature, the average temperature, and the 
     maximum temperature for a specified start range"""
    Day_temp_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()
    temperature_data = []
    for result in Day_temp_results:
        temperature_data.append({
            "TMIN": result.TMIN,
            "TAVG": result.TAVG,
            "TMAX": result.TMAX
        })
    return jsonify(temperature_data)

@app.route("/api/v1.0/start/end/")    
def startEnd (start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Return a list of the minimum temperature, the average temperature, and the 
     maximum temperature for a specified start end range"""
    multi_temp_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    # Convert the query results to a list of dictionaries

    temperature_data = []
    for result in multi_temp_results:
        temperature_data.append({
            "TMIN": result.TMIN,
            "TAVG": result.TAVG,
            "TMAX": result.TMAX
        })
    return jsonify(multi_temp_results)
# ###########################


# Flask Setup
if __name__ == '__main__':
    app.run(debug=True) 
################################################





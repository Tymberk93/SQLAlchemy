# Import Dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

# Set up database
engine = create_engine("sqlite:///Resources/hawaii.sqlite", pool_pre_ping=True)

# Reflect 
Base = automap_base()

# Reflect tables
Base.prepare(engine, reflect=True)

# Table Reference
measurement = Base.classes.measurement
station = Base.classes.station

# Set up FLASK
app = Flask(__name__)

# Flask & Precipiation route

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br><br>"
        f"<a href='http://127.0.0.1:5000/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br>"
        f"<a href='http://127.0.0.1:5000/api/v1.0/stations'>/api/v1.0/stations</a><br>"
        f"<a href='http://127.0.0.1:5000/api/v1.0/tobs'>/api/v1.0/tobs</a><br>"
        f"<a href='http://127.0.0.1:5000/api/v1.0/2016-07-29'>/api/v1.0/&lt;start date &gt;</a>            use date format:YYYY-MM-DD <br>"
        f"<a href='http://127.0.0.1:5000/api/v1.0/2016-07-29/2017-07-29'>/api/v1.0/&lt;start date &gt;/&lt;end date&gt;</a>      use date format:YYYY-MM-DD"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

# Python to Database session
    session = Session(engine)

    """Return a dictionary of precipitation measurements"""

    results = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >=  (dt.date(2017,8,23)- dt.timedelta(days=365))).\
    order_by(measurement.date).all()
    session.close()

# Convert list

    all_prcp = []
    for date,precip in results:
        date_dict = {}
        date_dict[date] = precip
        all_prcp.append(date_dict)

    return jsonify(all_prcp)

# Station route

@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)
    """Return a list of all the stations"""

    stations_data = session.query(station.station).all()
    session.close()

# Convert list

    stations = list(np.ravel(stations_data))

    return jsonify(stations)

# Tobs route
@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    """Return a list of all dates and its tobs (Most Active Station)"""

    most_active = session.query(measurement.date,measurement.tobs).filter(measurement.station == 'USC00519281').\
    filter(measurement.date >= (dt.date(2017,8,23)- dt.timedelta(days=365))).\
    order_by(measurement.date).all()

    session.close()
    mostactive_tobs = list(np.ravel(most_active))

    return jsonify(mostactive_tobs)

# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

@app.route("/api/v1.0/<start>")
def start_tob(start):

    session = Session(engine)



    start_query = (session.query(measurement.date, func.min(measurement.tobs), func.max(measurement.tobs), \
                             func.avg(measurement.tobs)).filter((measurement.date) >= start).group_by(measurement.date).all())
    
    session.close()

    tob_list = []
    for date, min,max,avg in start_query:
        start_tob = {}
        start_tob["date"] = date
        start_tob["tobs_min"] = min
        start_tob["tobs_max"] = max
        start_tob["tobs_avg"] = avg
        tob_list.append(start_tob)
 
    return jsonify(tob_list)

#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>/<end>")
def start_end_tob(start,end):
    session = Session(engine)
    """Return a JSON list of temperature observations from the provided dates."""
    start_end_results = (session.query(measurement.date, func.min(measurement.tobs), func.max(measurement.tobs), \
              func.avg(measurement.tobs)).filter((measurement.date) >= start, measurement.date <= end).group_by(measurement.date).all())
    
    session.close()

    start_end_tobs = []
    for date, min,max,avg in start_end_results:
        start_end_tob = {}
        start_end_tob["date"] = date
        start_end_tob["min_tobs"] = min
        start_end_tob["max_tobs"] = max
        start_end_tob["avg_tobs"] = avg
        start_end_tobs.append(start_end_tob)
 
    return jsonify(start_end_tobs) 



if __name__ == '__main__':
    app.run(debug=True)
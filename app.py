from concurrent.futures.process import _chain_from_iterable_of_lists
from doctest import REPORT_ONLY_FIRST_FAILURE
from flask import Flask, render_template
from flask import g
from flask_caching import Cache
import mysql.connector
from flask import request
from flask import abort, redirect, url_for
from datetime import datetime
import geopy.distance
from mysql.connector import pooling

app  = Flask(__name__)
config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}
app = Flask(__name__)
# tell Flask to use the above defined config
app.config.from_mapping(config)
cache = Cache(app)



'''
@app.route('/')
def hello():
    return "<h2>Hello, World!!</h2>"
'''

'''
#Connection pool
poolname = "connpool"
poolsize = 5

connectionpool = mysql.connector.pooling.MySQLConnectionPool(pool_name=poolname, pool_size=poolsize, pool_reset_session=True, host="ds11newsever.mysql.database.azure.com",
  user="ds_project_11",
  password="this_is_1_password",
  database="test",
  use_pure=True)

mydb = connectionpool.get_connection()
'''

#Database connection

def connect_db():
    db = mysql.connector.connect(
    host="ds11newsever.mysql.database.azure.com",
    user="ds_project_11",
    password="this_is_1_password",
    database="test",
    use_pure=True,
    )
    return db


@app.before_request
def before_request():
    #print("Before request")
    g.mydb = connect_db()
    #g.reportList = getAllReports()
    #g.reviewList = getAllReviews()


@app.teardown_request
def teardown_request(exception):
    #print("After teardown request")
    g.mydb.close()

@app.before_first_request
def before_first_request():
    #print("First request")
    g.mydb = connect_db()
    mycursor = g.mydb.cursor()

    #Get all police stations
    mycursor.execute("SELECT * FROM police_stations")
    myresults = mycursor.fetchall()
    global policeStationList
    policeStationList = myresults

    #Get all suburbs
    mycursor.execute("SELECT suburb_id,suburb_latitude,suburb_longitude FROM suburb ORDER BY suburb_name")
    myresults = mycursor.fetchall()
    global suburbList
    suburbList = myresults

    #Get all suburb to LGAs
    mycursor.execute("SELECT * FROM sub_to_lga")
    myresults = mycursor.fetchall()
    global suburblgaList
    suburblgaList = myresults

    #Get all crimes rates by LGA
    mycursor.execute("SELECT lga,SUM(lga_rate_per_100000_population) FROM area_offence_count GROUP BY lga")
    myresults = mycursor.fetchall()
    global crimeList
    crimeList = myresults

    #Get
    global reportList
    reportList = getAllReports()
    global reviewList
    reviewList = getAllReviews()

    #Close cursor
    mycursor.close()


#Get all reports (refresh this function to update list)
#@cache.cached(timeout=500, key_prefix='getAllReports')
def getAllReports():
    mycursor = g.mydb.cursor()
    mycursor.execute("SELECT * FROM report")
    myresults = mycursor.fetchall()
    mycursor.close()
    return myresults


#Get all reviews (refresh this function function to update list)
#@cache.cached(timeout=500, key_prefix='getAllReviews')
def getAllReviews():
    mycursor = g.mydb.cursor()
    mycursor.execute("SELECT * FROM review")
    myresults = mycursor.fetchall()
    mycursor.close()
    return myresults


@app.route('/')
def index():    
    return render_template('index.html',
                            policeStations=policeStationList,
                            reports=reportList,
                            suburbs=suburbList,
                            reviews=reviewList,
                            subLGAs=suburblgaList,
                            crimes=crimeList)


@app.route('/reportform', methods=['GET', 'POST'])
def reportform():
    add_report()
    return render_template('reportform.html')


@app.route('/add_report', methods=['GET', 'POST'])
def add_report():
    #Check whether the form is complete
    form = request.form
    if len(form.getlist('inptTitle')) != 0 or len(form.getlist('inputDescription')) != 0 or len(form.getlist('userLat')) != 0 or len(form.getlist('userLng')) != 0:
        
        #Get the user's current latlng
        strUserLat= request.form.getlist('userLat')[0]
        strUserLng= request.form.getlist('userLng')[0]

        suburbId = -1

        #if the user's current latlng are undefined, then redirect back to the report page
        if strUserLat != "undefined" or strUserLng != "undefined" or strUserLat != "" or strUserLng != "":
            redirect(url_for('index'))
            userLat = float(strUserLat)
            userLng = float(strUserLng)
            #Get the user's current suburb_id
            suburbId = getUserSuburb(userLat,userLng)
        else:
            redirect(url_for('index'))
            

        title= form.getlist('inputTitle')[0]
        description= form.getlist('inputDescription')[0]
        dangerRating= form.getlist('inputDangerRating')[0]
        areaDangerRating= form.getlist('inputAreaDangerRating')[0]

        #Convert dangerating and areadangerating into integer values
        if dangerRating == "option1":
            dangerRatingInt = 1
        elif dangerRating == "option2":
            dangerRatingInt = 2
        elif dangerRating == "option3":
            dangerRatingInt = 3
        elif dangerRating == "option4":
            dangerRatingInt = 4
        else:
            dangerRatingInt = 5
        
        
        if areaDangerRating == "option1":
            areaDangerRatingInt = 1
        elif areaDangerRating == "option2":
            areaDangerRatingInt = 2
        elif areaDangerRating == "option3":
            areaDangerRatingInt = 3
        elif areaDangerRating == "option4":
            areaDangerRatingInt = 4
        else:
            areaDangerRatingInt = 5

        #Get the current datetime 
        now = datetime.now()
        
        currentTime = now.strftime('%Y-%m-%d %H:%M:%S')

        #Execute command
        mycursor = g.mydb.cursor()

        mycursor.execute("INSERT INTO report(report_title, report_description, report_datetime, suburb_id, report_lat, report_lng, report_safety_level, report_willingness_to_return) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (title, description, currentTime, suburbId, userLat, userLng, dangerRatingInt, areaDangerRatingInt))
        
        g.mydb.commit()

        mycursor.close()

        #Update reportList global variable
        global reportList
        reportList = getAllReports()

        return redirect(url_for('index'))
    else:
    
        return redirect(url_for('reportform'))

def getUserSuburb(lat,lng):

    myresults = suburbList
    #For every suburb, calculate the closesest suburb to the inputted one based on coordinates

    coords_1 = (float(lat), float(lng))
    coords_2 = (myresults[0][1], myresults[0][2])
    shortestDistanceSuburb = [myresults[0][0],geopy.distance.distance(coords_1, coords_2).km]
    
    for item in myresults:
        coords_2 = (item[1], item[2])
        dist = geopy.distance.distance(coords_1, coords_2).km
        if shortestDistanceSuburb[1] > dist:
            shortestDistanceSuburb[0] = item[0]
            shortestDistanceSuburb[1] = dist

    return shortestDistanceSuburb[0]

@app.route('/reviewform', methods=['GET', 'POST'])
def reviewform():
    add_review()
    return render_template('reviewform.html')


@app.route('/add_review', methods=['GET', 'POST'])
def add_review():
    #Check whether the form is complete
    form = request.form
    
    if len(form.getlist('inptTitle')) != 0 or len(form.getlist('inputDescription')) != 0 or len(form.getlist('userLat')) != 0 or len(form.getlist('userLng')) != 0:
        
        #Get the user's current latlng
        strUserLat= form.getlist('userLat')[0]
        strUserLng= form.getlist('userLng')[0]

        
        suburbId = -1

        #if the user's current latlng are undefined, then redirect back to the report page
        if strUserLat != "undefined" or strUserLng != "undefined" or strUserLat != "" or strUserLng != "":
            userLat = float(strUserLat)
            userLng = float(strUserLng)
            #Get the user's current suburb_id
            suburbId = getUserSuburb(userLat,userLng)
        else:
            redirect(url_for('index'))
            

        title= form.getlist('inputTitle')[0]
        description= form.getlist('inputDescription')[0]
        areaDangerRating= form.getlist('inputSafetyRating')[0]

        #Convert areadangerating into integer values
        
        if areaDangerRating == "option1":
            areaDangerRatingInt = 1
        elif areaDangerRating == "option2":
            areaDangerRatingInt = 2
        elif areaDangerRating == "option3":
            areaDangerRatingInt = 3
        elif areaDangerRating == "option4":
            areaDangerRatingInt = 4
        else:
            areaDangerRatingInt = 5

        #Get the current datetime 
        now = datetime.now()
        
        currentTime = now.strftime('%Y-%m-%d %H:%M:%S')

        #Get current review rating (work in progress)
        pastDangerRatingInt = -1


        #Execute command
        mycursor = g.mydb.cursor()

        mycursor.execute("INSERT INTO review(review_title, review_description, review_datetime, suburb_id, review_rating, review_past_rating) VALUES (%s,%s,%s,%s,%s,%s)", (title, description, currentTime, suburbId, areaDangerRatingInt, pastDangerRatingInt))
        
        g.mydb.commit()

        mycursor.close()

        #Update reviewList global variable
        global reviewList
        reviewList = getAllReviews()
        
        return redirect(url_for('index'))
    else:
        return redirect(url_for('reviewform'))
    


if __name__ == "__main__":
    app.run()
    
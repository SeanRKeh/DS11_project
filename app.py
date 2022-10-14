from flask import Flask, render_template
import mysql.connector
from flask import request
from flask import abort, redirect, url_for
from datetime import datetime
import geopy.distance

app  = Flask(__name__)

'''
@app.route('/')
def hello():
    return "<h2>Hello, World!!</h2>"
'''

mydb = mysql.connector.connect(
  host="ds11newsever.mysql.database.azure.com",
  user="ds_project_11",
  password="this_is_1_password",
  database="test",
  use_pure=True,
)

#Get all police stations
mycursor = mydb.cursor()
mycursor.execute("SELECT * FROM police_stations")
myresults = mycursor.fetchall()
mycursor.close()

policeStationList = myresults

#Get all suburbs
mycursor = mydb.cursor()
mycursor.execute("SELECT suburb_id,suburb_latitude,suburb_longitude FROM suburb ORDER BY suburb_name")
myresults = mycursor.fetchall()
mycursor.close()

suburbList = myresults

reportList = []

def getAllReports():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM report")
    myresults = mycursor.fetchall()
    mycursor.close()

    global reportList
    reportList = myresults

getAllReports()

@app.route('/')
def index():    

    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM report")
    myresults = mycursor.fetchall()
    mycursor.close()
    print(myresults)

    return render_template('index.html',policeStations=policeStationList,reports=reportList)

@app.route('/reportform', methods=['GET', 'POST'])
def reportform():
    add_report()
    return render_template('reportform.html')


@app.route('/add_report', methods=['GET', 'POST'])
def add_report():
    #Check whether the form is complete
    form = request.form
    print(form.getlist('userLng'))
    if len(form.getlist('inptTitle')) != 0 or len(form.getlist('inputDescription')) != 0 or len(form.getlist('userLat')) != 0 or len(form.getlist('userLng')) != 0:
        
        #Get the user's current latlng
        strUserLat= request.form.getlist('userLat')[0]
        
        strUserLng= request.form.getlist('userLng')[0]
        #if the user's current latlng are undefined, then redirect back to the report page
        if form.getlist('userLat')[0] == "undefined" or form.getlist('userLng')[0] == "undefined":
            redirect(url_for('index'))
        else:
            userLat = float(strUserLat)
            userLng = float(strUserLng)

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

        #Get the user's current suburb_id
        suburbId = getUserSuburb(userLat,userLng)

        #Execute command
        mycursor = mydb.cursor()

        mycursor.execute("INSERT INTO report(report_title, report_description, report_datetime, suburb_id, report_lat, report_lng, report_safety_level, report_willingness_to_return) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (title, description, currentTime, suburbId, userLat, userLng, dangerRatingInt, areaDangerRatingInt))
        
        mydb.commit()

        mycursor.close()

        #Update reportList global variable
        getAllReports()

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
    # add_report()
    return render_template('reviewform.html')
    

if __name__ == "__main__":
    app.run(debug = True)
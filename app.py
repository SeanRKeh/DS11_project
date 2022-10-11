from flask import Flask, render_template
import mysql.connector
from flask import request
from flask import abort, redirect, url_for
from datetime import datetime

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

@app.route('/')
def index():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM police_stations")
    myresults = mycursor.fetchall()
    mycursor.close()
    return render_template('index.html',policeStations=myresults)

@app.route('/reportform', methods=['GET', 'POST'])
def reportform():
    add_report()
    return render_template('reportform.html')


@app.route('/add_report', methods=['GET', 'POST'])
def add_report():
    #Check whether the form is complete
    form = request.form
    if len(form.getlist('inptTitle')) != 0 or len(form.getlist('inputDescription')) != 0:

        title= request.form.getlist('inputTitle')[0]
        description= request.form.getlist('inputDescription')[0]
        dangerRating= request.form.getlist('inputDangerRating')[0]
        areaDangerRating= request.form.getlist('inputAreaDangerRating')[0]

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
        getUserSuburb("Monash")
        currentTime = now.strftime('%Y-%m-%d %H:%M:%S')

        #Get the user's current suburb_id


        #c.execute("INSERT INTO report(Item, Shack, Paym_Reference, Amount) VALUES (%s,%s,%s,%s)", (title, description, dangerRatingInt, areaDangerRatingInt))
        #conn.commit()

        return redirect(url_for('index'))
    else:
        print("hell nah")
    
        return redirect(url_for('reportform'))

def getUserSuburb(suburb):
    mycursor = mydb.cursor()
    statement = ("SELECT suburb_name FROM police_stations WHERE suburb_name=(%s)", (suburb))
    #mycursor.execute("SELECT suburb_id FROM suburb WHERE suburb_name=(%s)", (suburb))
    mycursor.execute("SELECT suburb_id FROM suburb")
    
    myresults = mycursor.fetchall()
    print((myresults))
    #mycursor.close()

if __name__ == "__main__":
    app.run(debug = True)
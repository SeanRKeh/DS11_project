import mysql.connector
mydb = mysql.connector.connect(
  host="ds-project-11-db.mysql.database.azure.com",
  user="ds_project_11",
  password="this_is_1_password",
  database="test"
)

mycursor = mydb.cursor()

mycursor.execute("SELECT * FROM police_stations")

myresult = mycursor.fetchall()

for x in myresult:
  print(x)
from flask import Flask, render_template
import mysql.connector

app  = Flask(__name__)

'''
@app.route('/')
def hello():
    return "<h2>Hello, World!!</h2>"
'''
mydb = mysql.connector.connect(
  host="ds-project-11-db.mysql.database.azure.com",
  user="ds_project_11",
  password="this_is_1_password",
  database="test",
  use_pure=True,
)
@app.route('/')
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug = True)
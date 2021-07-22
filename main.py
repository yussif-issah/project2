from flask import Flask,request,render_template,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import mariadb
import json
import sys
import psycopg2
import mysql.connector
import pyodbc


app=Flask(__name__)

app.config['SECRET_KEY']="secret"
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:hayatu88@localhost:5432/citizen'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= True


db=SQLAlchemy(app)
ma=Marshmallow(app)


class Data(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(100))
    firstname=db.Column(db.String(100))
    lastname=db.Column(db.String(100))
    password=db.Column(db.String(100))

    def __repr__(self):
        return f'Data(id={id},email={self.email},firstname={self.firstname},lastname={self.lastname},password={self.password})'

class DataSchema(ma.Schema):
    class Meta:
        fields=("firstname","lastname","email")

db.init_app(app)







@app.route("/" ,methods=["GET","POST"])
def home():
    return render_template("home.html")


@app.route("/all",methods=["GET","POST"])
def processData():
    if request.method == "GET":
        return render_template("home.html")

    if request.method=="POST":
        fname=request.form.get("firstname")
        lname=request.form.get("lastname")
        email=request.form.get("email")
        password=request.form.get("password")
        database=request.form.get("db")

        if database =="postgres":
            user=Data(firstname=fname,lastname=lname,email=email,password=password)
            db.session.add(user)
            db.session.commit()
            return render_template("home.html")
            
        elif database=="mysql":
            mydb = mysql.connector.connect(host="localhost",user="root",password="", database="citizen")
            mycursor = mydb.cursor()
            sql = "INSERT INTO data (firstname, lastname,email,password) VALUES (%s, %s,%s,%s)"
            val = (fname, lname,email,password)
            mycursor.execute(sql, val)
            mydb.commit()
            return render_template("home.html")


        elif database == "mariadb":
            try:
                conn = mariadb.connect(user="root",password="hayatu88",host="127.0.0.1",port=3306,database="citizen")
            except mariadb.Error as e:
                print(f"Error connecting to MariaDB Platform: {e}")
                sys.exit(1)
            cur = conn.cursor()
            try: 
                cur.execute("INSERT INTO data (firstname,lastname,email,pass) VALUES ('{}','{}','{}','{}')".format(fname,lname,email,password)) 
            except mariadb.Error as e: 
                print(f"Error: {e}")
            conn.commit() 
            return render_template("home.html",message="Your Data has been stored in Our Mariadb Successfully")


        elif database =="msserver":
            conn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};""Server=HAYATU;" "Database=citizen;""Trusted_Connection=yes;")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO citizen.dbo.data (firstname,lastname,email,password) VALUES ('{}','{}','{}','{}')".format(fname,lname,email,password))
            conn.commit()
            return render_template("home.html",message="Your Data has been stored in Our MsServer Successfully")
        else:
            return render_template("home.html")

@app.route("/get-data/<int:database>")
def retrieveData(database):
    if database == 1:
        dataschema=DataSchema(many=True)
        all_data=Data.query.all()
        data=[]
        for row in dataschema.dump(all_data):
            res=[]
            res.append(row['firstname'])
            res.append(row['lastname'])
            res.append(row['email'])
            data.append(tuple(res))
        
        return render_template("results.html",results=data)
    elif database==2:
        mydb = mysql.connector.connect(host="localhost",user="root",password="", database="citizen")
        mycursor = mydb.cursor()
        sql = "SELECT * FROM  data"
        mycursor.execute(sql)
        data=mycursor.fetchall()
        print(data[0])
        return render_template("results.html",results=data)
    elif database == 3:
         conn = mariadb.connect(user="root",password="hayatu88",host="127.0.0.1",port=3306,database="citizen")
         cur = conn.cursor()
         cur.execute("SELECT * FROM  data")
         data = cur.fetchall()
         return render_template("results.html",results=data)

    elif database==4:
        conn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};""Server=HAYATU;" "Database=citizen;""Trusted_Connection=yes;")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM  citizen.dbo.data")
        data=cursor.fetchall()
        return render_template("results.html",results=data)


if __name__=="__main__":
    app.run(debug=True)




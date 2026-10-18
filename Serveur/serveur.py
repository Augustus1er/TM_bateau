from flask import Flask, render_template
import sqlite3
import configparser
from flask import render_template
import paho.mqtt.publish as publish
import paho.mqtt.client as reciver
import datetime
import server_get_mesures as getdata
import threading
#-------------------------------------------------
config = configparser.ConfigParser()
config.read('config_flask.conf')
config.sections()
data_base = config['DEFAULT']['data_base']
IP_bateau =config['DEFAULT']['ip_bateau']
BROKER = "augustin.famillehayoz.ch"   # ou l'IP de ton broker (ex: Raspberry)
PORT = 1883
TOPIC = "#"            # "#" = tous les topics, sinon "capteurs/temp"
#----------------------------------------------------
app =Flask(__name__)

#les routes
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/image")
def image ():
    image_url="http://127.0.0.1:5000/static/images/image(0,0,0).png"
    return render_template('image.html', image_url=image_url)
@app.route("/menu")
def menu():
    with open('menu.html', 'r') as f:
        html = f.readlines()
        site = ''.join(html)
    return site
@app.route("/carte")
def carte():
    with open('carte_flask.html', 'r') as f:
        html = f.readlines()
        site = ''.join(html)
    return site
@app.route("/get_results")
def get_results():
    donees=[]
    conn = sqlite3.connect(data_base)
    cur = conn.cursor()
    print(data_base)
    cur.execute("SELECT id,ROUND(temperature,1),date,mode,numero,gps FROM mesures")
    rst = cur.fetchall()

    for row in rst:
        donees.append({'id':row[0],'temperature':row[1],'date':row[2],'mode':row[3],'numero':row[4],'gps':row[5]})
    print (donees)
    return donees
@app.route("/tableau")
def tableau():
    return render_template("tableau.html")
@app.route("/control")
def control():
    return render_template("control.html")
@app.route("/get_last")
def get_last():
    conn = sqlite3.connect(data_base)
    cur = conn.cursor()
    print(data_base)
    cur.execute("SELECT id,ROUND(temperature,1),date,mode,numero,gps FROM mesures WHERE id = (SELECT MAX(id) FROM mesures)")
    rst = cur.fetchall()
    a=[]
    for row in rst:
         a.append({'id':row[0],'temperature':row[1],'date':row[2],'mode':row[3],'numero':row[4],'gps':row[5]})
    return a[0]
@app.route("/arret")
def arret():
    #envoie un message mqtt
    print('envoie du message')
    msgs = [{'topic': f"command", 'payload': f"arret;{datetime.datetime.now()}"}]
    publish.multiple(msgs, hostname=IP_bateau)
    return "l'envoie a bien ete effectuer "
@app.route("/reprendre")
def reprendre():
    #envoie un message mqtt
    print('envoie du message')
    msgs = [{'topic': f"command", 'payload': f"avance;{datetime.datetime.now()}"}]
    publish.multiple(msgs, hostname=IP_bateau)
    return "l'envoie a bien ete effectuer "
@app.route("/mesures")
def mesures():
    #envoie un message mqtt
    print('envoie du message')
    msgs = [{'topic': f"command", 'payload': f"mesures;{datetime.datetime.now()}"}]
    publish.multiple(msgs, hostname=IP_bateau)
    return "l'envoie a bien ete effectuer "
@app.route("/moyenne")    
def moyenne():
    t=0
    mesures=0
    conn = sqlite3.connect(data_base)
    cur = conn.cursor()
    print(data_base)
    cur.execute("SELECT temperature FROM mesures")
    rst = cur.fetchall()

    for row in rst:
        t+=row[0]
        mesures+=1
    
    result =str(t/mesures)
    return result
thread = threading.Thread(target=getdata.main)
thread.daemon = True  # s'arrête quand le programme principal se termine
thread.start()    
app.run(host='0.0.0.0', port=5000)

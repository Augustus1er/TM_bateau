import paho.mqtt.client as mqtt
import os 
import time
import re 
import sqlite3

BROKER = "augustin.famillehayoz.ch"   # ou l'IP de ton broker (ex: Raspberry)
PORT = 1883
TOPIC = "mesures"            # "#" = tous les topics, sinon "capteurs/temp"
data_base = "db_serveur.db"
def initialisation_db():
    conn = sqlite3.connect(data_base)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS mesures(
        id integer primary key ,
        temperature FLOAT,
        date TEXT,
        mode TEXT,
	numero INTEGER,
        gps TEXT
    )   
    """)
    conn.commit()
    conn.close()

def save_to_db (message):
    
    mesures=message.split('#')
     
    temperature=float(mesures[0])
    date_jour=mesures[1]
    mode=mesures[2]
    points_gps=mesures[3]
    n_serie =1
    conn = sqlite3.connect(data_base)
    cur = conn.cursor()

    cur.execute("INSERT INTO mesures ( temperature,date,mode,numero,gps) VALUES ( ?,?,?,?,?)",
                    (temperature, date_jour, mode, n_serie,str(points_gps)))
    conn.commit()

    conn.close()

def mqtt_connect(client, userdata, flags, rc):
       print("✅ Connecté au broker MQTT")
       client.subscribe(TOPIC)
       print(f"📡 Abonné au topic: {TOPIC}")


def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8", errors="replace")#fais en sort de pouvoir lire
    print(f"📩 {msg.topic} -> {payload}")
    if msg.topic=='arret':
        pass 
    else:
        save_to_db(payload)
        
def main():
	initialisation_db()
	client = mqtt.Client()
	client.on_connect = mqtt_connect
	client.on_message = on_message
	client.connect(BROKER, PORT, keepalive=60)
	client.loop_forever()

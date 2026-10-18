import conduite
from gpiozero import Servo
import datetime
import configparser
import random
import sqlite3
import os
import re
import threading #permet les boucle en meme temps
import time
from gps3 import gps3
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

#------------------met les moteur au minimum----------------------
conduite.allumage()

# -------------------config---------------------------
#on recupere les infos du fichier de config
configuration = input('quel mode voulez vous utiliser ?')   
if configuration != "TEST" and configuration != "test" and configuration != "SKI" and configuration != "ski": #attention ici si on rajoute d'autre mode faut rajouté des conditions
    print("configuration non reconnue, utilisation de la configuration par défaut")
    configuration = "DEFAULT"
else:
    print(f"configuration {configuration} utilisée")
    configuration = configuration.upper() #pour eviter les probleme de majuscule ou pas
config = configparser.ConfigParser()
config.read('config.conf')
config.sections()
nbr_mesures:int = int(config[configuration]['nbr_mesures'])
attente:float = float(config[configuration]['attente'])
data_base = config[configuration]['data_base']
date_jour:str = str(datetime.datetime.now())


mesures:dict = dict()
points_gps:list = []   #liste des balise a suivre
host = "augustin.famillehayoz.ch"  #atention a changer l'ip 
gps_socket = gps3.GPSDSocket()
data_stream = gps3.DataStream()
gps_socket.connect()
gps_socket.watch()
#------------------------

BROKER = "augustin.famillehayoz.ch"   # ou l'IP de ton broker (ex: Raspberry)
PORT = 1883
TOPIC = "#"            # "#" = tous les topics
mode ="avance"
# ----------def fonctions--------------
#on défini les fonctions
def mqtt_connect(client, userdata, flags, rc):
       print(" Connecté au broker MQTT")
       client.subscribe(TOPIC)
       print(f" Abonné au topic: {TOPIC}")


def on_message(client, userdata, msg):
    #ici ondefini les actions a effectuer suivant la topic recu.
    payload = msg.payload.decode("utf-8", errors="replace")#fais en sort de pouvoir lire
    print(f"{msg.topic} -------> {payload}")
    message=payload.split(";")[0]
    global mode
    if message=='arret':
        mode="arret"
    elif message=='avance':
        mode="avance"
    elif message=='mesures':
        envoie_mesures()

def numero_serie()->int :
    conn = sqlite3.connect(data_base)
    cur = conn.cursor()
    cur.execute("SELECT max(numero)+1 FROM mesures")#selection de l'element le plus grand +1
    numero=cur.fetchall()[0][0]

    if numero== None:
        global n_serie
        n_serie = '1'
    else:

        n_serie = numero
    return n_serie

def mesures_temperature()->int:  # on mesure la temperature
    os.system('cat /sys/bus/w1/devices/28-00000582a982/w1_slave')
    device_file = '/sys/bus/w1/devices/28-00000582a982/w1_slave'
    f = open(device_file, 'r')
    lines = f.readlines()
    temperature = int(re.search(r"(?<=t=)\d*", lines[1])[0]) / 1000
    return temperature

def moyenne_gps()->list[int,int]:
    latitude = 0
    longitude = 0
    for i in range(nbr_mesures):
        points=prise_position()
        latitude += float(points[0])
        longitude += float(points[1])
    return [latitude/nbr_mesures, longitude/nbr_mesures]

def envoie_mesures()->None:
    msgs = [{'topic': f"mesures", 'payload': f"{mesures_temperature()}#{date_jour}#{configuration}#{conduite.position()}"},]
    # publish multiple messages
    publish.multiple(msgs, hostname=host)

def recup_data()->None:
    client = mqtt.Client()
    client.on_connect = mqtt_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, keepalive=60)
    client.loop_forever()
    
def main()->None:
    #------lancement des boucle en meme temps pour le suivi des balises-------------
    thread = threading.Thread(target=conduite.changement_target) #lance le suivi des balises
    thread2= threading.Thread(target=recup_data)#on regarde en permanace si on recoit des nouvelle requetes du serveur
    thread.daemon = True  # s'arrête quand le programme principal se termine
    thread.start()
    thread2.daemon = True  # s'arrête quand le programme principal se termine
    thread2.start()
    ##conduite
    while True:
        while mode =="avance":
            conduite.avance()      
            conduite.vise()      #suivi des boussoles
            conduite.avance()#mettre avance()pour avanver tout le temps
        while mode =="arret":
            conduite.allumage()
        
###---------------plan---------------
#liste des points a suivre (coordonées) + ordre -> dico ou liste avec ordre précis
#prise des coordonées du bateau actuelement -> prise_position()
#calcule de l'angle 
#correction de l'angle + avancer jusque balise -> comme conduite mais avec un point au coordonée de la balise
#une foie le coordonnée pareil (marge de ---)
#passe a la balise d'apres
#une foie que toute les balise on été faites on arrete et on passe en mode allumage



# ---------------------code----------------------



#envoie_mesures() #quand le gps fonctionnera on enleve le try
stop = True
#suivi des balises

signal_lancement = input("Lancement ? (y/n) -> ")

if signal_lancement == "y": #attend un signle avant le lancement
    stop = False
else:
    print("En attente...")
    msg_contrario = input()
    if msg_contrario == "lancer":
        stop = False
    else:
        print("mot non reconnu, en attente...")
while stop:   #quand stop passe a false la boucle se stop et le code continue
    conduite.allumage()
main()



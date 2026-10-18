#---------imports----------
import math
import smbus
from gpiozero import Servo
from time import sleep
import re 
import os
from gps3 import gps3



#-----------configuration -------
#moteurs
esc1 = Servo(12, min_pulse_width=0.001, max_pulse_width=0.002, frame_width=0.02)#le moteur sur le port GPIO12
esc2 = Servo(13, min_pulse_width=0.001, max_pulse_width=0.002, frame_width=0.02)#le moteur sur le port GPIO13
#--------------------------
#
bus = smbus.SMBus(1)
MAG_ADDR = 0x1E

# Calibration
OFFSET_X = -105
OFFSET_Y = -179

# --------------------------------------------------
# Initialisation HMC5883L
# --------------------------------------------------

# Register A
# 0x18 = 75 Hz, 1 sample
bus.write_byte_data(MAG_ADDR, 0x00, 0x18)

# Register B
# Gain
bus.write_byte_data(MAG_ADDR, 0x01, 0x60)

# Mode register
# 0x00 = continuous measurement
bus.write_byte_data(MAG_ADDR, 0x02, 0x00)
alpha = 0.2
filtered_angle = None

#-------------------------------------
liste_target=[[0,0],[1,1]]
target=liste_target[0] #le point qu'oin vise de base
 
#-------------------------------fonctions--------

def allumage():
    esc1.min()
    esc2.min()

def avance():#fait avancer le bateau tout le temps
    esc1.value =- 0.5
    esc2.value =-0.5

def moteur_droite():
    esc2.value = -0.5

def moteur_gauche():
    esc1.value = -0.5

def cap()->float:#retourne le cap
    alpha = 0.2
    filtered_angle = None
    # Ordre des registres HMC5883L :
    # X = 0x03 / 0x04
    # Z = 0x05 / 0x06
    # Y = 0x07 / 0x08

    raw_x = read_s16(0x03)
    raw_z = read_s16(0x05)
    raw_y = read_s16(0x07)

    # Correction des offsets
    mx = raw_x - OFFSET_X
    my = raw_y - OFFSET_Y

    # Calcul du cap
    angle = math.degrees(math.atan2(my, mx))

    if angle < 0:
        angle += 360

    # Initialisation du filtre
    if filtered_angle is None:
        filtered_angle = angle
    else:
        # Différence angulaire correcte autour de 0° / 360°
        diff = (angle - filtered_angle + 180) % 360 - 180
        filtered_angle += alpha * diff
        filtered_angle %= 360

    print(
        f"X={raw_x:6d}  "
        f"Y={raw_y:6d}  "
        f"Z={raw_z:6d}  "
        f"Cap brut={angle:6.1f}°  "
        f"Cap filtré={filtered_angle:6.1f}°"
    )

    return filtered_angle
def vise():   #fait en sorte que le moteur s'arret si il ne permet de faire allez dans le bon sens
    cap_actuel=cap()
    ecart= angle()-cap_actuel

    if ecart > 0:
        if ecart>180:
            moteur_droite()
        else:
            moteur_gauche()
    elif ecart <0:
        if ecart<-180:
            moteur_gauche()
        else:
            moteur_droite()
    elif ecart ==180:
        moteur_droite()
    sleep(0.1)

def angle()->float:#retourne l'angle avec target
    axex =target[0]-float(position()[0])
    axey =target[1]-float(position()[1])
    print(axex,axey)
    if axex==0:
        if axey>0:
            alpha=0
        elif axey<0:
            alpha=180
    elif axey ==0:
        if axex>0:
            alpha =90
        elif axex<0:
            alpha=270

    else:
        alpha =math.atan(((axey)/(axex)))*(180/math.pi)
        print(alpha)
        if axex <0 and axey>0:
            alpha = 180+alpha
        elif axex>0 and axey>0:
            alpha = 90-alpha
        elif axex<0 and axey<0:
            alpha = 180+alpha
        elif axex>0 and axey<0:
            alpha = 360+alpha
    return alpha

def position(): #a finir
    i = 0
    for new_data in gps_socket:    
        if new_data and i<2:
            data_stream.unpack(new_data)
            if i !=0:   
                latitude=str(data_stream.TPV['lat'])
                longitude=str(data_stream.TPV['lon'])
                return[latitude,longitude]
                break 
            else:
                i+=1    

def read_s16(reg):
    """
    Lit un entier signé 16 bits big-endian
    depuis deux registres consécutifs.
    """
    high = bus.read_byte_data(MAG_ADDR, reg)
    low = bus.read_byte_data(MAG_ADDR, reg + 1)

    value = (high << 8) | low

    if value >= 32768:
        value -= 65536

    return value


def distance()->float:   #rajoué l'aproximation des coordonées

    #distance entre la position actuelle le la balise
    distanceX=round(abs(float(target[0])),5) - round(abs(float(position()[0])),5)
    distanceY=round(abs(float(target[1])),5) - round(abs(float(position()[1])),5)
    distanceCarre=distanceX**2+distanceY**2          #pythagore pour rouver la distance entre les deux points
    distance = math.sqrt(distanceCarre)

    return distance

def changement_target():
    global target
    i=0
    NBR_tours = 0
    continuer = True
    while continuer:
        if distance()<0.00001:#précis au metre pres 
            print(f"target {i+1} atteinte")
            target=liste_target[i] #on vise la target
            i+=1
            if i==len(liste_target):
                NBR_tours += 1
                print(f"Le bateau a fait {NBR_tours}")
                sleep(5)
                i=0
        #faire un truc pour arreter le bateau

if __name__ == "__main__":
    #-------------------------------
    gps_socket = gps3.GPSDSocket()
    data_stream = gps3.DataStream()
    gps_socket.connect()
    gps_socket.watch()
    longueur = 50
    print("conduite lancer")
    for i in range (longueur):
        allumage()
        sleep(1)
        vise()
        sleep(0.5)
        allumage()
    print(f"les {longueur} coordonées furent prisent, mise en mode allumage")
    allumage()
    while True:
        sleep(10)
        

#Moduls
import serial #Communication avec un port série
import time #Gestion du temps
import struct #Interprétation du binaire
from collections import namedtuple #utile pour la classe ExpressPacket

#Constantes définies par la documentation
SYNC_BYTE = b'\xA5'
SYNC_BYTE2 = b'\x5A'

GET_INFO_BYTE = b'\x50'
GET_HEALTH_BYTE = b'\x52'
GET_SAMPLE_RATE_BYTE = b'\x59'

STOP_BYTE = b'\x25'
RESET_BYTE = b'\x40'

SCAN_BYTE = b'\x20'

_SCAN_TYPE = {
    'normal': {'byte': b'\x20', 'response': 129, 'size': 5},
    'force': {'byte': b'\x21', 'response': 129, 'size': 5},
    'express': {'byte': b'\x82', 'response': 130, 'size': 84},
}

DESCRIPTOR_LEN = 7
INFO_LEN = 20
HEALTH_LEN = 3
SAMPLE_RATE_LEN = 4

INFO_TYPE = 4
HEALTH_TYPE = 6
SCAN_TYPE = 129
SAMPLE_RATE_TYPE = 21

# Constantes concernant le moteur
MAX_MOTOR_PWM = 1023
DEFAULT_MOTOR_PWM = 660
SET_PWM_BYTE = b'\xF0'

_HEALTH_STATUSES = {
    0: 'Good',
    1: 'Warning',
    2: 'Error',
}
#Gérer les erreurs
class LidarException(Exception):
    "None"
#Gérer les scans en mode express


def twos_comp(val, bits):

    '''Compute the 2's complement of int value val'''

    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val


class ExpressPacket(namedtuple('express_packet', 'distance angle new_scan start_angle')):
    sync1 = 0xa
    sync2 = 0x5
    sign = {0: 1, 1: -1} #signes codés en binaire

    @classmethod
    def decode(cls, data):
        '''Décode les valeurs contenues dans un paquet express'''
        packet = bytearray(data)


        if (packet[0] >> 4) != cls.sync1 or (packet[1] >> 4) != cls.sync2: # Vérification bytes de synchronisation
            raise ValueError('Compilation de données erronées ({})'.format(packet))

        checksum = 0 #vérification de la checksum
        for b in packet[2:]:
            checksum ^= b
        if checksum != (packet[0] & 0b00001111) + ((packet[1] & 0b00001111) << 4):
            raise ValueError('Checksum invalide ({})'.format(packet))

        new_scan = packet[3] >> 7 #On vérifie si le flag new scan est présent sur le packet
        start_angle = (packet[2] + ((packet[3] & 0b1111111) << 8)) / 64.0 #Angle de départ du paquet ( / 2^6 == >> 6)

        d = a = () #création des tuples contenant les distances et les angles
        for i in range(0, 80, 5): #on explore le paquet et on décode les mesures d'angles et de distances
            d += ((packet[i + 4] >> 1) + (packet[i + 5] << 7),) #Pourquoi on "shift" à droite par 2 places si la partie $d\theta_{1}$ a juste 1 bit?
            a += (twos_comp((packet[i + 8] & 0b1111) + ((packet[i + 4] & 0b1) << 4), 5)/8.0,)  #fixed-point-q3 format.
            #print("Valor de ângulo:", twos_comp((packet[i + 8] & 0b1111) + ((packet[i + 4] & 0b1) << 4), 5)/8.0)
            d += ((packet[i + 6] >> 1) + (packet[i + 7] << 7),)
            a += (twos_comp((packet[i + 8] >> 4 & 0b1111) + ((packet[i + 6] & 0b1) << 4), 5)/8.0,)
        return cls(d, a, new_scan, start_angle)



class Lidar(object) :
#Methodes outils
    def __init__(self, port, baudrate=115200, timeout=1):
        '''Initialisation du LIDAR'''
        self._serial = None #Connexion au port sérié
        self.port = port #Port de connexion série
        self.baudrate = baudrate #Vitesse transmission série
        self.timeout = timeout #Delai reponse maxi (s)
        self._motor_speed = DEFAULT_MOTOR_PWM #Vitesse de consigne du moteur
        self.scanning = [False, 0, 'normal'] # [est en train de scanner, type, type (string)]
        self.express_trame = 32 #utilisé pour les scans express(
        self.express_old_data = False  # même que celui ci-dessous
        self.express_data = False  # utilisé pour les scans express (présence d'un paquet de données dans la mémoire)
        self.motor_running = False #Statut du moteur
        self.connect() #On connecte le LIDAR au port COM

    def connect(self):
        '''Se connecter au LIDAR sur le port COM'''
        if self._serial is not None:
            self.disconnect()
        try:
            self._serial = serial.Serial(self.port, baudrate=self.baudrate, parity=serial.PARITY_NONE,
                                         stopbits=serial.STOPBITS_ONE, timeout=self.timeout)
        except serial.SerialException as err:
            raise LidarException("Echec de la connexion : " + str(err))

    def disconnect(self):
        '''Se deconnecter du port COM'''
        if self._serial is None:
            return
        self._serial.close()
    
    # Gestion des commandes
    def send_command(self, byte):
        '''Envoyer une commande au LIDAR'''
        cmd = SYNC_BYTE + byte
        self._serial.write(cmd)

    def read_descriptor(self):
        # Lire le descripteur d'une réponse
        desc = self._serial.read(DESCRIPTOR_LEN)
        if len(desc) != DESCRIPTOR_LEN:
            raise LidarException("Incorrect descriptor len")
        elif not desc.startswith(SYNC_BYTE + SYNC_BYTE2):
            raise LidarException("Incorrect start descriptor")
        else :
            #d_size = desc[2]
            #d_type = desc[-1]
            #is_single = desc[-2]==0
            return desc[2], desc[-2] == 0, desc[-1]

    def read_response(self, d_size):
        '''Lire un réponse de taille d_size'''
        while self._serial.inWaiting() < d_size:
            time.sleep(0.0001) #Variable ajustable
        return self._serial.read(d_size)

    def clean_input(self):
        '''Nettoyer la mémoire vive'''
        if self.scanning[0]:
            return 'Cleanning not allowed during scanning process active !'
        self._serial.flushInput()
        #self.express_trame = 32
        #self.express_data = False

    def _process_scan(self,data):
        '''Décode un scan'''
        #Qualité et vérif 1
        first= bin(data[0])   # first = premier octet en binaire
        print(data)
        quality = data[0]>>2 #Qualite de la mesure
        S =bool(data[0] & 0b1)# Indicateur Nouveau tour
        Sb = bool(data[0]>>1 & 0b1)# Bit de verification
        if S==Sb :
            raise LidarException('S et Sb égaux !')
        #Angle et vérif 2
        check = data[1] & 0b1
        angle = ((data[1]>>1) + (data[2]<<7))/64
        if check != 1:
            raise LidarException('Bit de verif different de 1')
        #Distance
        dist = ((data[3]) + (data[4] << 8))/4
        return S, quality, angle, dist

    def _process_express_scan(self, data, new_angle, trame):
        '''Calcule les angles à partir du packet express décodé'''
        if (new_angle < data.start_angle) and (trame==1):#si on est dans un nouveau tour et que l'on ne l' pas déjà compté
            new_scan = True
        else:
            new_scan = False
        angle = (data.start_angle + (((new_angle - data.start_angle) % 360)/32)*trame - data.angle[trame-1]) % 360 #formule dans la doc
        distance = data.distance[trame-1]#on associe la distance decodee
        return new_scan, None, angle, distance  #nouveau_tour,Qualite,angle,distance


    #Gestion du moteur

    def _send_payload_cmd(self, cmd, payload):
        '''Envoie une commande accompagnée d'un payload'''
        size = struct.pack('B', len(payload)) #Transforms the size of payload into something like 00011010
        #print("size:", size)
        req = SYNC_BYTE + cmd + size + payload #Building the standard request packet
        checksum = 0
        for v in struct.unpack('B' * len(req), req):
            #print('valor do byte:', v)
            checksum ^= v
        #print("Sai!")
        req += struct.pack('B', checksum) #Wrapping up the packet with the checksum at the end
        #print(req)
        self._serial.write(req)

    def set_motor_speed(self, speed=660):
        '''Changer la vitesse de consigne
        La vitesse effective est changée si le moteur est en marche'''
        assert (0 <= speed <= MAX_MOTOR_PWM)
        self._motor_speed = speed
        if self.motor_running:
            self._set_pwm(self._motor_speed)

    def _set_pwm(self, pwm):
        '''Changer la vitesse effective du moteur'''
        payload = struct.pack("<H", pwm)
        self._send_payload_cmd(SET_PWM_BYTE, payload)

    def start_motor(self):
        '''Faire démarrer le moteur à la vitesse de consigne'''
        self._serial.setDTR(False)
        self._set_pwm(self._motor_speed)
        self.motor_running = True

    def stop_motor(self):
        '''Arrêter le moteur'''
        self._set_pwm(0)
        time.sleep(.001)
        self._serial.setDTR(True)
        self.motor_running = False

#Realisation de taches
    def get_health(self):
        '''Recevoir le statut de santé du LIDAR'''
        self.send_command(GET_HEALTH_BYTE)
        d_size,is_single,d_type = self.read_descriptor()
        #Verifications
        if d_size != HEALTH_LEN:
            raise LidarException('Mauvaise taille de reponse')
        if not is_single:
            raise LidarException('Pas en mode de reponse unique')
        if d_type != HEALTH_TYPE:
            raise LidarException('Mauvais type de donnee')
        data = self.read_response(d_size)
        return _HEALTH_STATUSES[data[0]]

    def get_sample_rate(self):
        '''Renvoie les durées pour réaliser une mesure en mode normal et express en microsecondes'''
        self.send_command(GET_SAMPLE_RATE_BYTE)
        d_size,is_single,d_type = self.read_descriptor()
        # Verifications
        if d_size != SAMPLE_RATE_LEN:
            raise LidarException('Mauvaise taille de reponse')
        if not is_single:
            raise LidarException('Pas en mode de reponse unique')
        if d_type != SAMPLE_RATE_TYPE:
            raise LidarException('Mauvais type de donnee')
        data = self.read_response(d_size)
        rate_normal = ((data[0])+(data[1]<<8)) #Mode normal
        rate_express = ((data[2])+(data[3]<<8)) #Mode express
        return rate_normal, rate_express

    def reset(self):
        '''Remet le Lidar à sa configuration originelle'''
        self.send_command(STOP_BYTE)
        time.sleep(0.002) #Ajustable
        self.scanning[0] = False
        self.stop_motor()
        self.clean_input()

    def start_scan(self, scan_type = 'normal'):
        '''Demarre le système de mesure'''
        #Verifications
        if self.scanning[0]:
            return 'Scan deja en cours !'
        statut = self.get_health()
        if statut == _HEALTH_STATUSES[2]:
            print("Essai de redemarrage du lidar")
            self.reset()
            statut = self.get_health()
            if statut == _HEALTH_STATUSES[2]:
                raise LidarException('Echec demarrage scanner')
        elif statut == _HEALTH_STATUSES[1]:
            print('Avertissement detecteur!')
         #Demarrage
        cmd = _SCAN_TYPE[scan_type]['byte']
        if scan_type == 'express':
            self._send_payload_cmd(cmd, b'\x00\x00\x00\x00\x00')
            self.express_trame = 32
            self.express_data = False
        else:
            self.send_command(cmd)
        print("Début du scan")
        #Lecture et vérifications descripteurs
        dsize, is_single, dtype = self.read_descriptor()
        if dsize != _SCAN_TYPE[scan_type]['size']:
            raise LidarException('Mauvaise longueur descripteur')
        if is_single:
            raise LidarException('Pas mode de reponse multiple')
        if dtype != _SCAN_TYPE[scan_type]['response']:
            raise LidarException('Mauvais type de reponse')
        self.scanning = [True, dsize, scan_type]
        print("Descripteur lu")

    def scan(self, scan_type='normal', max_buf_meas = 3000, speed=DEFAULT_MOTOR_PWM):
        '''Lance un scan avec une limite de mémoire vive'''
        #Démarrage
        self.set_motor_speed(speed)
        self.start_motor()
        start = time.time()
        if not self.scanning[0]:
            self.start_scan(scan_type)
        while True:
            #Processus de récupération des données
            now = time.time()
            dsize = self.scanning[1]
            if max_buf_meas:
                data_in_buf = self._serial.inWaiting()
                if data_in_buf > max_buf_meas: #Gestion de la memoire vive
                    print(
                        'Memoire vive saturee:' + str(data_in_buf) +' / ' + str (max_buf_meas)
                        + ' \n Vidage de la memoire...')
                    self.reset()
                    self.start_scan(self.scanning[2])
            if self.scanning[2] == 'normal': #Recuperation du mode "normal"
                raw = self.read_response(dsize)
                yield self._process_scan(raw), now - start
            if self.scanning[2] == 'express': #recuperation du mode "express" (le dernier packet est toujours inexploitable)
                if self.express_trame == 32: #si on a lu le dernier packet en entier
                    self.express_trame = 0 #on revient au début du packet
                    if not self.express_data: #si c'est le 1er packet
                        self.express_data = ExpressPacket.decode(self.read_response(dsize)) #on stocke le packet decode
                    self.express_old_data = self.express_data #les dernieres donnees deviennent les anciennes donnees
                    self.express_data = ExpressPacket.decode(self.read_response(dsize))#on cherche le prochain paquet
                    # while self.express_data.new_scan :#Si il y a une remise à 1 du flag, recommencer les mesures à partir du packet (perte de 1 ou plusieurs packets)
                    #     self.express_old_data=self.express_data
                    #     self.express_data=ExpressPacket.decode(self.read_response(dsize))
                self.express_trame += 1 #on avance dans la trame
                yield self._process_express_scan(self.express_old_data,self.express_data.start_angle,self.express_trame), now - start #on renvoie la mesure pour le packet old




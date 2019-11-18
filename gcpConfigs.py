import sys
import time
import json
import os
import warnings

import google.cloud
import firebase_admin as fa
from firebase_admin import firestore
from firebase_admin import credentials

#import Tconfigs as tcf
import adc_dac_config as adcon


print('opening database connection')
cred = credentials.Certificate(r'/home/pi/Downloads/testcenterstorage-3b7a292e37ae.json')
fa.initialize_app(cred)
db = firestore.client()
print('database request approved')

binary = {'INPUT' : 0,
          'OUTPUT': 1,
          'LOW' : 0,
          'HIGH' : 1}

OUTPUT = binary['OUTPUT']
INPUT = binary['INPUT']
LOW = binary['LOW']
HIGH = binary['HIGH']

class define_test():
    '''
    Builds a class that's later used to pass data back and forth to Google Firestore
    '''
    def test_centerID(self):
        '''
        Request the test center id from the user
        Make a request to Firestore with that test center ID
        Query the docs that are included with the collection from the test center ID results
        If the docs query returns an empty list, have the user double check their ID input
        '''
        while True:
            #x = sys.stdin.readline('Please enter test center ID ')
            y = db.collection(u'testCenter1')
            docs = y.stream()
            z = []
            for doc in docs:
                z.append(doc.id)
            if len(z) != 0:
                self.test_center = u'testCenter1'
                self.docs = z
                break
            else:
                print('No test center found with that name, double check the ID on the housing ')

    def test_check(self):
        while True:
            print(' Please enter test ID ')
            x = input()
            if x not in self.docs:
                #tcf.warning_on(self)
                print('Invalid test id, please select from this list:')
                print(self.docs)
            else:
                #tcf.warning_off()
                y = self.docs.index(x)
                self.testID = self.docs[y]
                break

    def json_read(self):
        cwd = os.getcwd()
        name = self.testID + '.txt'
        if name not in cwd:
            warnings.warn('No Local JSON file to read')
            jClass = {u'timestamp' : 0, u'testID' : self.testID}
            name = self.testID + '.txt'
            with open(name, 'w') as json_file:
                json.dump(jClass, json_file)
        else:
            with open(name, 'r') as json_file: 
                jClass = json.loads(json_file)
        return jClass

    def gcp_check(self):
        try:
            a = db.collection(u'testCenter1').document(self.testID).get()
            y = a.to_dict()
            return y
        except:
            raise ValueError('Document name not found!')

    def get_onoff_parameters(self):
        '''
        Read data from the specified test remotely. Check if there's a newer local copy, and use those parameters instead
        '''
        localJSON = self.json_read()
        jTime = localJSON['timestamp']
        gcpDATA = self.gcp_check()
        gcpTime = gcpDATA['timestamp']
        if jTime > gcpTime:
            print('Loading JSON data')
            y = localJSON
        else:
            y = gcpDATA
        self.description = y['Description']
        self.control = y['Control']
        self.gain = y['GainFactor']
        self.pv = y['PV']
        self.target = y['Target']
        self.type = y['Type']
        self.duty_cycle = y['DutyCycle']
        self.cycle_time = y['CycleTime']
        self.bounces = y['Bounces']
        #self.currents = y['currents']
        self.shot_count = y['Shots']
        self.input = []
        self.time = []
        self.active = False
        self.cycle_start = time.time()
        #self.temp_time = time.time()
        #self.curr_time = time.time()
        self.last_log = time.time()
        self.print_rate = 900
        self.last_state = HIGH
        self.chan_state = HIGH
        self.update_db()
        self.cycle_points = y['CyclePoints']
        self.torque = y['Torque']

    def setCycleTime(self):
        '''
        Read the cycleTime from the test parameters sheet and check that it's in the proper range. If not raise a warning. Cast it as 
        a list for security.
        '''
        if self.cycle_time not in range(1, 101, 1):
            raise ValueError('Cycle times must be whole number between 1 and 100')
            #tcf.warning_on()
        else:
            print('Test cycle time created')

    def setCycles(self):
        '''
        Read the cycle target from the test parameters sheet and check that it's in the proper range. If not raise a warning. Cast it as 
        a tuple to make it immutable
        '''
        if self.target not in range(1, 1000000, 1):
            raise ValueError('Number of cycles must be a whole number, between 1 and 1,000,000')
            #tcf.warning_on()
        else:
            print('Test cycles set point created')

    def setDuty(self):
        '''
        Read the duty cycle from the test parameters sheet and check that it's in the proper range. If not raise a warning. Cast it as 
        a tuple to make it immutable
        '''
        if self.duty_cycle not in range(0, 100, 1):
            raise ValueError('Duty cycle must be a whole number between 1 and 100')
        else:
            print('Test duty cycle created')

    def setTime(self):
        self.cycleStart = (time.time())
        print('Test start time logged')

    def create_on_off_test(self):
        self.test_centerID()
        self.test_check()
        self.get_onoff_parameters()

    def setTorque(self):
        if self.control not in range(0, 6373):
            raise ValueError('Torque setpoints must be between 0 and 6372 in-lbs')
            tcf.warning_on()
        else:
            print('Torque setpoint created')

    def setGain(self):
        global choices = [200, 100, 50, 40, 25, 20] #mA/V
        if self.gain not in choices:
            tcf.warning_on()
            raise ValueError('Gain value not valid. Choose from:')
            print(choices)
        else:
            print('Gain set')

    def convertSig(self):
    #convert in/lbs control setpoint to current value for brake signal
        ftlbs = self.control/12.0 #desired brake torque in ftlbs
        if ftlbs <= 10:
            fiveV = 0
            print('Brake set to minimum torque of 120 in-lbs')
        else: 
            mA = 8.6652e-11*ftlbs**5 - 1.1637e-7*ftlbs**4 + 5.9406e-5*ftlbs**3 - 0.013952*ftlbs**2 + 1.9321*ftlbs + 46.644 #mA needed for brake
            tenV = mA/self.gain #0-10vdc signal
            fiveV = tenV/2.0 #0-5vdc signal
            print ('Brake set to', self.control, 'in-lbs')
        return fiveV

    def parameter_check(self):
        self.setCycleTime()
        self.setCycles()
        self.setTorque()
        self.setGain()
        #self.setDuty()
        self.setTime()

    def update_db(self):
        try:
            ref = db.collection(self.test_center).document(self.testID)
            ref.update({u'timestamp' : self.last_log})
            #ref.update({u'temps': self.temps})
            #ref.update({u'currents': self.currents})
            ref.update({u'PV' : self.pv})
            ref.update({u'Bounces' : self.bounces})
            ref.update({u'Shots' : self.shot_count})
            ref.update({u'Torque' : self.torque})
            print('updates written to gcp')
        except:
            warnings.warn('GCP connectivity error, dumping to JSON')
            jDict = {u'testID' : self.testID, u'timestamp' : self.last_log,
            u'PV' : self.pv, u'Bounces' : self.bounces, u'Shots' : self.shot_count, u'Description' : self.description, 
            u'Type' : self.type, u'DutyCycle' : self.duty_cycle, u'Target' : self.target,
            u'CycleTime' : self.cycle_time, u'Torque' : self.torque } #u'temps': self.temps, u'currents': self.currents,

            name = self.testID + '.txt'
            with open(name, 'w') as json_file:
                json.dump(jDict, json_file)

'''
    def get_mod_parameters(self):
        
        Read data from the specified test remotely. Pull test parameters from the response and store them locally. Use these parameters
        later to create a new instance of the desired test class with the given parameters
        
        y = self.testID.to_dict()
        self.description = y['Description']
        self.torque = y['Torque']
        self.pv = y['PV']
        self.target = y['Target']
        self.duty_cycle = y['DutyCycle']
        self.temps = y['Temps']
        self.currents = y['Currents']
'''
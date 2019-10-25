#import firebase_admin as fa 
import google.cloud
import firebase_admin as fa
from firebase_admin import firestore
from firebase_admin import credentials
import test_configs as tcf
import adc_dac_config as adcon
import sys
import time
import json
import os

print('opening database connection')
cred = credentials.Certificate(r'/home/pi/Downloads/testcenterstorage-3b7a292e37ae.json')
fa.initialize_app(cred)
db = firestore.client()
print('database request approved')

collections = db.collection(u'testCenter1')

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
            x = raw_input()
            if x not in self.docs:
                print('Invalid test id, please select from this list:')
                print(self.docs)
            else:
                y = self.docs.index(x)
                self.testID = self.docs[y]
                break

    def set_parameters(self, y):
            self.description = y['Description']
            self.torque = y['Torque']
            self.pv = y['PV']
            self.type = y['Type']
            self.duty_cycle = y['DutyCycle']
            self.target = y['Target']
            self.cycle_time = y['CycleTime']
            self.bounces = y['Bounces']
            self.currents = y['currents']
            self.temps = y['temps']
            self.shot_count = y['Shots']
            self.input = []
            self.time = []
            self.active = False
            self.cycle_start = time.time()
            self.temp_time = time.time()
            self.curr_time = time.time()
            self.last_log = time.time()
            self.print_rate = 900
            self.last_state = HIGH
            self.chan_state = HIGH

    def get_onoff_parameters(self):
        '''
        Read data from the specified test remotely. Check if there's a newer local copy, and use those parameters instead
        '''
        try:
            a = db.collection(u'testCenter1').document(self.testID).get()
            y = a.to_dict()
        except:
            raise ValueError('Document name not found!')
        name = self.testID + '.txt'
        try: #Try to open a json file with the same testID
            with open(name, 'r') as json_file: 
                jClass = json.load(json_file)
            if jClass['timestamp'] > y['timestamp']: #If the json file is newer, use those values instead of the gcp ones
                set_parameters(jClass)
                update_db() #Update the gcp values using the JSON information
            else:
                set_parameters(y) #If the gcp values are newer, just use those
        except:
            set_parameters(y) #If the JSON file doesn't exist, then use the gcp ones

    def setCycleTime(self):
        '''
        Read the cycleTime from the test parameters sheet and check that it's in the proper range. If not raise a warning. Cast it as 
        a list for security.
        '''
        if self.cycle_time not in range(1, 100, 1):
            raise ValueError('Cycle times must be whole number between 1 and 60')
        else:
            print('Test cycle time created')

    def setCycles(self):
        '''
        Read the cycle target from the test parameters sheet and check that it's in the proper range. If not raise a warning. Cast it as 
        a tuple to make it immutable
        '''
        if self.target not in range(1, 1000000, 1):
            raise ValueError('Number of cycles must be a whole number, between 1 and 1,000,000')
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

    def parameter_check(self):
        self.setCycleTime()
        self.setCycles()
        self.setDuty()
        self.setTime()

    def update_db(self):
        try:
            ref = db.collection(self.test_center).document(self.testID)
            ref.update({u'timestamp' : self.last_log})
            ref.update({u'temps': self.temps})
            ref.update({u'currents': self.currents})
            ref.update({u'PV' : self.pv})
            ref.update({u'Bounces' : self.bounces})
            ref.update({u'Shots' : self.shot_count})
        except:
            jDict = {u'timestamp' : self.last_log, u'temps': self.temps, u'currents': self.currents, u'PV' : self.pv,
             u'Bounces' : self.bounces, u'Shots' : self.shot_count  }
            name = self.testID + '.txt'
            with open(name, 'w') as json_file:
                json.dumps(jDict, json_file)


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

        
        
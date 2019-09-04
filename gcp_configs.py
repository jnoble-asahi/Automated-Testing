import firebase_admin as fa 
from firebase_admin import credentials
from firebase_admin import firestore
import onOffConfigs as oncon
import adc_dac_config as adcon

new = ('New', 'new', 'n')
cont = ('Cont', 'cont', 'Continue', 'continue', 'c')
mod = ('mod', 'Modulating', 'modulating', 'modu')
onf = ('on/off, on off, onoff, onf, on, On/Off, On/off, on/Off, ON/OFF')


cred = credentials.Certificate(r'C:\Users\cmay\Desktop\testcenterstorage-5808b82edc86.json')
fa.initialize_app(cred)
db = firestore.client()

collections = db.collections()

list(collections)

validInput = (new, cont, mod, onf )
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
            x = input('Please enter test center ID ')
            y = db.collection(x)
            docs = y.stream()
            z = []
            for doc in docs:
                z.append(doc.id)
            if len(z) != 0:
                self.test_center = x
                self.docs = z
                break
            else:
                print('No test center found with that name, double check the ID on the housing ')

    def old_or_new(self):
        while True :
            y = input('New Test or Continue?(new / continue)')
            if y not in validInput:
                print('Please type either new or continue')
            else:
                False
        if y in cont:
            self.cont = True
        else:
            self.cont = False
   
    def test_type(self):
        while True :
            x = input('Modulating or on/off test?')
            if x not in validInput:
                print('Please enter either modulating or on/off ')
            else:
                break
        if x in mod:
            self.mod = True
            self.onf = False
        else:
            self.mod = False
            self.onf = True

    def test_check(self, test):
        while True:
            x = input('Please enter test ID')
            if x not in self.docs:
                print('Invalid test id, please select from this list:')
                print(self.docs)
            else:
                y = self.docs.index(x)
                self.testID = self.docs[y]
                break

    def get_onoff_parameters(self):
        '''
        Read data from the specified test remotely. Pull test parameters from the response and store them locally, use these parameters to
        create a new instance of the desired test class with the given parameters
        '''
        y = self.testID.to_dict()
        self.description = y['Description']
        self.torque = y['Torque']
        self.pv = y['PV']
        self.type = y['Type']
        self.duty_cycle = y['DutyCycle']
        self.target = y['Target']
        self.cycletime = y['CycleTime']
        self.bounces = y['Bounces']
        self.currents = y['Currents']
        self.temps = y['Temps']
        self.shotCount = y['Shots']

    def get_mod_parameters(self):
        '''
        Read data from the specified test remotely. Pull test parameters from the response and store them locally. Use these parameters
        later to create a new instance of the desired test class with the given parameters
        '''
        y = self.testID.to_dict()
        self.description = y['Description']
        self.torque = y['Torque']
        self.pv = y['PV']
        self.target = y['Target']
        self.duty_cycle = y['DutyCycle']
        self.temps = y['Temps']
        self.currents = y['Currents']

    def set_test_parameters(self, params):
        '''
        Take the parameters from params and store them in a new test class
        The process will differ slightly depending on whether it's a modulating or on/off test
        '''

    def update_database(self, test):
        '''
        A function for sending parameters from the local test to the remote database
        '''
        


    '''
    If it's a modulating test, set the class instance variables accordingly

    If it's an on/Off test do the same

    If it's continuing an existing test, pull the parameters from firestore

    If it's a new test, create a new document in the test center collection with the test parameters
    '''
        
        
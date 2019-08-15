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
class testDefined():
    '''
    Builds a class that's later used to pass data back and forth to Google Firestore
    '''
    @staticmethod
    def test_centerID(self):
        '''
        Request the test center id from the user
        Make a request to Firestore with that test center ID
        Query the docs that are included with the collection from the test center ID results
        If the docs query returns an empty list, have the user double check their ID input
        '''
        i = 0
        while i < 1:
            x = input('Please enter test center ID ')
            y = db.collection(x)
            docs = y.stream()
            z = []
            for doc in docs:
                z.append(doc.id)
            if len(z) != 0:
                self.test_center = x
                i += 1
            else:
                print('No test center found with that name, double check the ID on the housing ')

    @staticmethod
    def old_or_new(self):
        i = 0
        while i < 1 :
            y = input('New Test or Continue?(new / continue)')
            if y not in validInput:
                print('Please type either new or continue')
            else:
                i += 1
        if y in cont:
            self.cont = True
        else:
            self.cont = False

    @staticmethod   
    def test_type(self):
        i = 0
        while i < 1 :
            x = input('Modulating or on/off test?')
            if x not in validInput:
                print('Please enter either modulating or on/off ')
            else:
                i += 1
        if x in mod:
            self.mod = True
            self.onf = False
        elif x in onf:
            self.mod = False
            self.onf = True
        else:
            pass

    @staticmethod
    def get_doc_list(self, target):
        x = []
        docs = self.test_centerID.stream()
        for doc in docs:
            x.append(doc.id)
        self.docs = x

    @staticmethod
    def test_check(self, test):
        x = input('Please enter test ID')
        if x not in self.docs:
            print('Invalid test id, please select from this list:')
            print(self.docs)
        else:
            self.testID = self.docs[x]

    @staticmethod
    def get_parameters(self, test):
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


    @staticmethod
    def set_test_parameters(self, params):
        '''
        Take the parameters from params and store them in a new test class
        The process will differ slightly depending on whether it's a modulating or on/off test
        '''

    @staticmethod
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
        
        
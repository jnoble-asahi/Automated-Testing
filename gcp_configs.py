import firebase_admin as fa 
from firebase_admin import credentials
from firebase_admin import firestore
import onOffConfigs as oncon
import adc_dac_config as adcon

new = ('New', 'new', 'n')
cont = ('Cont', 'cont', 'Continue', 'continue', 'c')
mod = ('mod', 'Modulating', 'modulating', )

validInput = (new, cont, mod, )
class testDefined():
    '''
    Builds a class that's later used to pass data back and forth to Google Firestore
    '''
    @staticmethod
    def old_or_new(self):
        i = 0
        while i < 1 :
            y = input('New Test or Continue?(new / continue)')
            if y not in validInput:
                pass
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
            if y not in validInput:
                pass
            else:
                i += 1
        if x in mod:
            self.mod = True
        else:
            self.mod = False

    @staticmethod
    def get_doc_list(self, target):
        x = []
        docs = target.get()
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
        Read data from the specified test remotely. Pull test parameters from this data set and store them locally
        '''
        x = self.testID
        y = 

    @staticmethod
    def set_test_parameters(self, params):
        '''
        Take the parameters from params and store them in a new test class
        The process will differ slightly depending on whether it's a modulating or on/off test
        '''

    @staticmethod
    def update_database(self, test, more?):
        '''
        A function for sending parameters from the local test to the remote database
        '''
        


    '''
    If it's a modulating test, set the class instance variables accordingly

    If it's an on/Off test do the same

    If it's continuing an existing test, pull the parameters from firestore

    If it's a new test, create a new document in the test center collection with the test parameters
    '''
        
        
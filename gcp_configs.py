import firebase_admin as fa 
from firebase_admin import credentials
from firebase_admin import firestore

new = ('New', 'new')
cont = ('Cont', 'cont', 'Continue', 'continue')
validInput = ('new', 'New', )
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

    '''
    If it's a modulating test, set the class instance variables accordingly

    If it's an on/Off test do the same

    If it's continuing an existing test, pull the parameters from firestore

    If it's a new test, create a new document in the test center collection with the test parameters
    '''
        
        
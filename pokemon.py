'''
Okay this class allows you to call !wtp from chat
A random pokemon will appear as a silloutted bitmap and then users
will get some time to guess the pkmn before the time is up.

Upon a correct guess or when the time runs out, the correct pokemon 
will display with the corresponding win or loss message.

Features might include something that lets you guess from a 
specific gen of pokemon rather than all of them. For nows we will
only include gen one
'''
from os import listdir
from os.path import isfile, join, dirname, abspath
import re
from random import randint

from PokeAPI import PokeAPI

MESSAGE = "You are now playing Who's That Pokemon" \
          "\n Guess the pokemon in the shadow to win."

class pkmn(object):
    '''This class contains the pokemon to be guessed.
        It also contains functions to output a sillouetted image
        of a given pokemon (filename)
    '''
    papi = PokeAPI()  # ayeee papiii

    LOCK = False

    PATH = "sugimori"
    TIME_TO_START = 5
    TIME_TO_GUESS = 30
    MAX_PKMN = 721

    def __init__(self):
        super(pkmn, self).__init__()

        self.pkmn_data = None
        self.pkmn_id = 0
        self.pkmn_name = ''

        self.initialize() #initialize random id and derived name

    def initialize(self):
        id = pkmn.generate_id()
        data = pkmn.papi.get_pokemon(id)
        name = data['name']

        self.pkmn_data = data
        self.pkmn_id = id
        self.pkmn_name = name

        LOCK = True #sets lock as long as game is still being played
        return

    def display_message(self):
        return MESSAGE

    def display_img(self, silhouette = False):
        #from folder return the appropriate image path to the pokemon
        return pkmn.get_img_path(self.pkmn_id)
        #if sihouette edit the image to mask the pokemon in question

    def check_guess(self, guess):
        if guess == self.pkmn_name:
            return True
        else: return False

    @staticmethod
    def get_img_path(id):
        path = join(dirname(abspath(__file__)), pkmn.PATH)
        files = []
        try:
            files = [f for f in listdir(path) if str(id) in f]
        except FileNotFoundError:
            print("Could not find in ", path)
        except TypeError:
            print("Wrong type dummy")
        finally:
            return join(path, files[0])

    @staticmethod
    def generate_id():
        return randint(1, pkmn.MAX_PKMN)

'''
Design flow:
    1. user launches command
    2. bot generates a random number (pokemon)
    3. bot displays the silloetted image of the pokemon to client
    4. user attempts to guess pokemon name
    5. bot compares the name to the database
    6. if correct or out of time move on - else repeat 4 & 5
    7. display correct image and appropriate win/lose text
'''
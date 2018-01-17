'''
Okay this class allows you to call !wtp from chat
A random pokemon will appear as a silhouetted bitmap and then users
will get some time to guess the pkmn before the time is up.

Upon a correct guess or when the time runs out, the correct pokemon 
will display with the corresponding win or loss message.

Features might include something that lets you guess from a 
specific gen of pokemon rather than all of them. For nows we will
only include gen one
'''
from os import listdir
from os.path import isfile, join, dirname, abspath, basename, splitext
from random import randint

from PokeAPI import PokeAPI
from PIL import Image

import zlib

class pkmn(object):
    '''This class contains the pokemon to be guessed.
        It also contains functions to output a sillouetted image
        of a given pokemon (filename)
    '''
    papi = PokeAPI()  # ayeee papiii
    GEN_DICT = {1:(1, 151), 2:(152, 251), 3:(252, 386),
                4:(387, 493), 5:(494 ,649), 6:(650, 721)}

    DEX = "sugimori"
    COMPRESS='compress_cache'
    KURO = "kuro_cache"

    TIME_TO_START = 5
    TIME_TO_GUESS = 30
    MAX_PKMN = 721

    MESSAGE = "You are now playing Who's That Pokémon!" \
              "\n Guess the pokemon in the shadow to win."

    def __init__(self):
        super(pkmn, self).__init__()

        self.pkmn_data = None
        self.pkmn_id = 0
        self.pkmn_name = ''

        self.LOCK = False
        #self.initialize() #initialize random id and derived name

    def initialize(self,gen=0,id=0):
        '''
        Initializes a pokemon object for use in the Pokemon game.

        If a pokemon gen is not provided, it will use all pokemon.
        Otherwise it will only pick only from that gen

        If an ID is provided, it will generate relevant information for that pokemon in this object
        :param gen: int - The generation (1-6) that the randomizer should choose from
        :param id: int  - The specific id that the pokemon object should fetch info for
        :return:
        '''
        #gen selector
        if gen >= 1 and gen <= 6:
            self.min = self.GEN_DICT[gen][0]
            self.max = self.GEN_DICT[gen][1]
        else:
            self.min = 1
            self.max = self.MAX_PKMN

        if not id:
            id = self.generate_id()
        elif id < 1 or id > self.MAX_PKMN:
            id = 1

        data = self.papi.get_pokemon(id)
        name = data['name']

        self.pkmn_data = data
        self.pkmn_id = id
        self.pkmn_name = name


        self.LOCK = True #sets lock as long as game is still being played
        return

    def generate_id(self):
        return randint(self.min, self.max)

    def display_img(self, silhouette = False):
        '''
        Returns the local image path of this Object's pokemon
        :param silhouette: bool - Generate and return the path of a silhouetted Pokemon?
        :return: img: str       - The local image path of this Pokemon
        '''
        img = self.get_img_path(self.pkmn_id)
        if silhouette:
            img = self.generate_silhouette(img)
        return img

    def display_message(self):
        return self.MESSAGE

    @staticmethod
    def get_img_path(id, folder=DEX):
        path = join(dirname(abspath(__file__)), folder)
        files = ['_']
        try:
            files = [f for f in listdir(path) if ''.join((str(id),splitext(f)[1])) == f]
        except FileNotFoundError:
            print("Could not find {} in {}".format(id, path))
        finally:
            files.sort(key=len)
            return join(path, files[0])

    @staticmethod
    def generate_silhouette(image_path : str, folder=KURO):
        '''
        This method takes the image path from display_img() and then converts it to a silhouette using PIL

        If the image is already in the cache it will return the path of that image
        If the image is not found it will perform pre pixel modifications to the image.
        It will then save the image to the cache and return the path to that image

        :param image_path: str  - The image path of the pokemon
        :param folder: str      - The folder path of the cache
        :return: new_path : str - The path to the silhouetted Pokemon
        '''
        filename = basename(image_path)
        new_path = join(dirname(abspath(__file__)), folder, filename)
        # don't do any work if there is already an image cached
        if isfile(new_path):
            return new_path

        #converts image to rgba pixel data
        image = Image.open(image_path).convert('RGBA')
        pixel_data = list(image.getdata())

        #changes each solid pixel to a black one
        for i,pixel in enumerate(pixel_data):
            if pixel[:3] >= (0,0,0) and pkmn.almost_equals(pixel[3], 255): #pixel[3] >= 10
                pixel_data[i] = (0,0,0,255)
        image.putdata(pixel_data)
        image.save(new_path)

        #returns the path at the end to be referenced
        return new_path

    @staticmethod
    def almost_equals(a, b, thres=50):
        return abs(a - b) < thres

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
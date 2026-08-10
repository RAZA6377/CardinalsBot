import discord
from termcolor import colored

class ColorPrint:
    def __init__(self,
        text : str
        ):
        self.text = text
        
    def success(self):
        try:
            print(colored(self.text, 'black', 'on_green'))
        except:
            print(self.text)
            
            
    def failed(self):
        try:
            print(colored(self.text, 'black', 'on_red'))
        except:
            print(self.text)
    
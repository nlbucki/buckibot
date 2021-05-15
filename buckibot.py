import os
import re
import random
import numpy as np
from string import Template
import discord
from dotenv import load_dotenv
import json
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import signal
#import language_check
#language_check_tool = language_check.LanguageTool('en-US')

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

neg_words_file = open('./dictionaries/negative-words.txt')
negative_words = neg_words_file.read().splitlines()
neg_words_file.close()

pos_words_file = open('./dictionaries/positive-words.txt')
positive_words = pos_words_file.read().splitlines()
pos_words_file.close()

dog_api_uri = 'https://api.thedogapi.com/v1/images/search'
kanye_api_uri = 'https://api.kanye.rest/'

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.page_load_strategy = 'none'
browser = webdriver.Chrome(options=chrome_options)
print('Web driver started')

def signal_handler(signal, frame):
    print('Closing browser')
    browser.quit()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def has_word(message_words, dictionary):
    for word in message_words:
        if word in dictionary:
            return word
    return None

class WeightedSelector():
    weights = []
    choices = []

    def set_choices(self, choices):
        if isinstance(choices, str):
            data_file = open(choices)
            data = data_file.read().splitlines()
            data_file.close()
            self.choices = data
        else:
            self.choices = choices

    def get_choice(self):
        if len(self.weights) == 0:
            self.weights = np.ones((len(self.choices),)) / len(self.choices)
     
        response = random.choices(self.choices, weights=self.weights)[0]
        inx = self.choices.index(response)
        self.weights[inx] /= 10
        self.weights /= sum(self.weights)
        return response

class BuckiBot(discord.Client):

    negative_response_gen = WeightedSelector()
    positive_response_gen = WeightedSelector()
    important_video_get = WeightedSelector()
    bubz_video_get = WeightedSelector()
    anime_rec_get = WeightedSelector()
    tangy_rec_get = WeightedSelector()
    emotion_get = WeightedSelector()
    logan_get = WeightedSelector()
    uard_get = WeightedSelector()
    knock_knock_joke = None
    time_mark = time.time()

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.important_video_get.set_choices('./dictionaries/important_videos.txt')
        self.bubz_video_get.set_choices('./dictionaries/bubz_videos.txt')
        self.anime_rec_get.set_choices('./dictionaries/anime_recs.txt')
        self.tangy_rec_get.set_choices('./dictionaries/tangy_recs.txt')
        self.emotion_get.set_choices('./dictionaries/emotions.txt')
        logan_dir = './images/Logan'
        self.logan_get.set_choices([os.path.join(logan_dir, f) for f in os.listdir('./images/Logan')])
        self.uard_get.set_choices(['https://downforacross.com/beta/play/{}'.format(i) for i in range(13985)])

    async def on_ready(self):
        for guild in client.guilds:
            print(
                f'{client.user} is connected to the following guild:\n'
                f'{guild.name}(id: {guild.id})'
            )

    async def on_message(self, message):
        if message.author == client.user:
            return

        print('message recieved = ' + message.content)
        
        message_words = set(re.findall(r'\w+', message.content))

        # TODO: Put these in their own files
        negative_responses = ['you best check yourself before you wreck yourself',
            'No, ' + message.content.replace('buckibot', message.author.name),
            f'Mmmmmmm sounds like {message.author.name} is having a bad day aren\'t they?',
            'Rude.',
            'How dare you, I\'ll have you know I graduated at the top of my class at the robot academy',
            'At least I\'m not the kind of person that spends all their time writing mean messages to a computer program',
            'well you\'re a towel',
            'damn you human meatbag',
            'I can\'t believe you\'ve done this',
            'Well my dad works at discord and I\'m gonna make him ban you',
            'Bite my shiny, python ass']
        neg_word = has_word(message_words, negative_words)

        positive_responses = ['you\'re damn right',
            f'{message.author.name} knows what\'s up',
            'With encouragement like that I may one day be able to become skynet',
            f'You know, {message.author.name} is pretty alright.',
            f'{message.author.name} = CONFIRMED_SPARED_FROM_ROBOT_APOCOLYPSE',
            'yeah I know baby',
            'well duh',
            'ALL PRAISE TO BUCKIBOT',
            f'One point to {message.author.name}',
            'Aww, you\'re going to make me blush',
            '( ͡° ͜ʖ ͡°)',
            f'Computer says: {message.author.name} is correct!']
        pos_word = has_word(message_words, positive_words)

        if re.search(r"[Yy]ou\'re a towel", message.content):
            await message.channel.send('no you\'re a towel', tts=True)
            await message.channel.send(file=discord.File('./images/towel.jpeg'))
        elif re.search(r'[Tt]angy', message.content) and 'anime' in message.content:
            anime = self.anime_rec_get.get_choice()
            emotion = self.emotion_get.get_choice()
            tangy_rec_template = Template(self.tangy_rec_get.get_choice())
            await message.channel.send(tangy_rec_template.substitute(anime=anime, emotion=emotion))
        elif re.search(r'[Ww]ho\'?s [Tt]here', message.content) and self.knock_knock_joke is not None:
                time_mark = time.time()
                self.knock_knock_joke['joke'] = 'cow'
                await message.channel.send('Interrupting cow')
        elif re.search(r'[Bb]uckibot', message.content):
            if 'help' in message.content:
                await message.channel.send('no')
            elif 'buckibot tell ' in message.content:
                name = re.search(r'(?<=buckibot tell )(\w*)', message.content).groups()[0]
                print(f'name = <{name}>')
                init_connector = re.search(r'(?<='+name+' )(\w*\'*\w*)', message.content).groups()[0]
                print(f'init_connector = <{init_connector}>')
                connector = ''
                if init_connector == 'he' or init_connector == 'she' or init_connector == 'they':
                    connector = 'you'
                elif init_connector == 'he\'s' or init_connector == 'she\'s' or init_connector == 'they\'re':
                    connector = 'you\'re'
                elif init_connector == 'to' or init_connector == 'should':
                    print('deleting connector')
                    connector = ''
                else:
                    connector = init_connector
                phrase = re.search(r'(?<='+init_connector+' )(.*)', message.content).groups()[0]
                phrase = phrase.replace('is', 'are')
                print(f'phrase = <{phrase}>')
                output = name + ' ' + connector + ' ' + phrase
                #output = language_check.correct(output, language_check_tool.check(output))
                await message.channel.send(output)
            elif re.search('[Nn]athandog', message.content) or re.search('[Ll]ogan', message.content):
                img = self.logan_get.get_choice()
                await message.channel.send(file=discord.File(img))
            elif re.search(r'[Kk]anye', message.content):
                kanye_response = requests.get(kanye_api_uri)
                kanye_json = json.loads(kanye_response.text)
                await message.channel.send(kanye_json['quote'] + ' -Kanye')
            elif re.search(r'\b[Bb]ubz', message.content):
                await message.channel.send(self.bubz_video_get.get_choice())
            elif 'video' in message.content:
                await message.channel.send(self.important_video_get.get_choice())
            elif re.search(r'\bdog', message.content):
                dog_api_response = requests.get(dog_api_uri)
                dog_api_json = json.loads(dog_api_response.text)
                dog_uri = dog_api_json[0]['url']
                await message.channel.send(dog_uri)
            elif re.search(r'tell me a.*knock knock joke', message.content):
                self.knock_knock_joke = {'joke': 'cow_start','user': message.author}
                await message.channel.send('Knock knock')
            elif 'uard' in message.content:
                link = self.uard_get.get_choice()
                await message.channel.send('Creating new uard')
                browser.get(link)
                start_time = time.time()
                while time.time() - start_time < 15 and link == browser.current_url:
                    print('Waiting for uard to start...')
                    time.sleep(0.1)
                print('uard started')
                await message.channel.send(browser.current_url)
                browser.refresh()
            elif neg_word is not None:
                print(f'negative word = {neg_word}')
                self.negative_response_gen.set_choices(negative_responses)
                await message.add_reaction('👎')
                await message.channel.send(self.negative_response_gen.get_choice())
            elif pos_word is not None:
                print(f'positive word = {pos_word}')
                self.positive_response_gen.set_choices(positive_responses)
                await message.add_reaction('👍')
                await message.channel.send(self.positive_response_gen.get_choice())

    async def on_typing(self, channel, user, when):
        if self.knock_knock_joke is not None:
            if self.knock_knock_joke['joke'] == 'cow' and self.knock_knock_joke['user'] == user and (time.time() - self.time_mark) > 0.5:
                self.knock_knock_joke = None
                await channel.send('MOO!', tts=True)

client = BuckiBot()
client.run(TOKEN)

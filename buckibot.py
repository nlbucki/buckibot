import os
import re
import random
import numpy as np
from string import Template

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

neg_words_file = open('./dictionaries/negative-words.txt')
negative_words = neg_words_file.read().splitlines()
neg_words_file.close()

pos_words_file = open('./dictionaries/positive-words.txt')
positive_words = pos_words_file.read().splitlines()
pos_words_file.close()

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
    anime_rec_get = WeightedSelector()
    tangy_rec_get = WeightedSelector()
    emotion_get = WeightedSelector()

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.important_video_get.set_choices('./dictionaries/important_videos.txt')
        self.anime_rec_get.set_choices('./dictionaries/anime_recs.txt')
        self.tangy_rec_get.set_choices('./dictionaries/tangy_recs.txt')
        self.emotion_get.set_choices('./dictionaries/emotions.txt')

    async def on_ready(self):
        for guild in client.guilds:
            print(
                f'{client.user} is connected to the following guild:\n'
                f'{guild.name}(id: {guild.id})'
            )

    async def on_message(self, message):
        if message.author == client.user:
            return
        
        message_words = set(re.findall(r'\w+', message.content))

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
        elif 'buckibot' in message.content:
            if 'help' in message.content:
                await message.channel.send('no')
            elif 'video' in message.content:
                await message.channel.send(self.important_video_get.get_choice())
            elif neg_word is not None:
                print(f'negative word = {neg_word}')
                self.negative_response_gen.set_choices(negative_responses)
                await message.add_reaction('👎')
                await message.channel.send(self.negative_response_gen.get_choice(), tts=True)
            elif pos_word is not None:
                print(f'positive word = {pos_word}')
                self.positive_response_gen.set_choices(positive_responses)
                await message.add_reaction('👍')
                await message.channel.send(self.positive_response_gen.get_choice(), tts=True)

client = BuckiBot()
client.run(TOKEN)

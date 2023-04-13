import os
import telebot
import pandas as pd
from datetime import datetime
from time import sleep
from multiprocessing import Process

import market
import stochastic

import config


bot = telebot.TeleBot(config.TOKEN)

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)



class GetData(object):
    def __init__(self):
        self.signal = 'stochastic_signal'

    # write the last row of each currency in file 'last_data.csv'
    def get_last_data(self):
        # write data in csv file
        for pair in os.listdir('Market'):
            last_line = pd.read_csv(f"Market/{pair}").tail(1)
            last_line.to_csv('last_data.csv', index = False, header = False, mode='a')

        # write in txt file
        last_data = pd.read_csv('last_data.csv')
        with open('last_data.txt', 'w') as F:
            F.write(last_data.to_string(index=False))


    def get_signals(self):
        df = pd.read_csv('last_data.csv')
        # dict with signals; {'BTC-USD': '1.0',...}
        signals_dict = {row['Pair']: row[self.signal] for index, row in df.iterrows() if row[self.signal] != 0.0}

        return signals_dict



class Main(object):
    def __init__(self):
        self.get_data = GetData()

    # chat_id = message.chat.id
    def send_message(self, no_s_message):
        # get existing column names and make an empty 'last_data.csv'
        col_names = list(pd.read_csv('last_data.csv').columns.values)
        with open('last_data.csv', 'w') as f:
            f.write(','.join(col_names) + '\n')

        market.main() # get market data
        stochastic.main() # get stochastic and emas values
        self.get_data.get_last_data() # write the last row of each currency in file

        stochastic_signals = self.get_data.get_signals()

        message = '' # the message that will be sent in tg bot

        for key, value in stochastic_signals.items():
            message += key + ': ' + str(value) + '\n'
        if len(message) > 0:
            message = "Stochastic\n--------------------\n{0}".format(message)

        print(message)

        if len(message) > 0:
            bot.send_message(config.CHAT_ID, message)
        else:
            print('There is no signals right now')

         # this message will be sent from bot if no signals
        if no_s_message:
            bot.send_message(config.CHAT_ID, no_s_message)


#  --- MESSAGE HANDLERS ---
# list of all available commands
@bot.message_handler(commands=['help'])
def help(message):
    text = '/help - list of commands\n/check - check a market'
    bot.reply_to(message, text)


# if you need to check signals it any time, type '/check' to bot
@bot.message_handler(commands=['check'])
def check_market(message):
    Main().send_message('There is no signals right now') # this message will be sent from bot if no signals



# --- RUN POLLING AND TIME CHECK CYCLES ---

# every hour in 2 minutes func 'send_message' will receive data, check it for signals and send them if they are
def runtime():
    while True:
        now = datetime.now()
        if now.minute == config.RUNTIME:
            Main().send_message(None)
            sleep(120) # without this it will check signals all the time util minute ends
        sleep(5)


# to take commands polling it shoud be running
def polling():
    text = 'Bot is now running. To see available commands: /help'
    bot.send_message(config.CHAT_ID, text)
    bot.polling(none_stop=True)


# RUN 2 CYCLES SIMULTANEOUSLY
if __name__ == '__main__':
    pr1 = Process(target=polling) # start polling
    pr2 = Process(target=runtime) # check time cycle
    pr1.start()
    pr2.start()




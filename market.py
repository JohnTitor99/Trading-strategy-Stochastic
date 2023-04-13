import os, sys
from pathlib import Path
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
import pandas as pd

import config


pd.set_option('display.max_rows', None) # when print a dataframe, it will print all columns, not only first and last 5 by default
pd.set_option('mode.chained_assignment', None) # avoiding a copy error


#  get dataframe with all financial data
def get_hourly_dataframe(pair, period):
    ticker = yf.Ticker(pair)

    df = ticker.history(period=period, interval=config.INTERVAL)

    del df['Volume']
    del df['Dividends']
    del df['Stock Splits']

    # by default data is used like line index, so this code creates a normal column 'date'
    date = []
    for i in df.index:
        date.append(i)
    df = df.reset_index(drop=True)
    df.insert(0,'date', date)    

    return df


# get rows that are missing until current data
def get_new_data(pair):
    # get last writed date
    last_market_date_str = pd.read_csv(f"Market/{pair}.csv").iloc[-1]['date']
    last_market_date_str = last_market_date_str[:-6]
    last_market_date = datetime.strptime(last_market_date_str, '%Y-%m-%d %H:%M:%S')

    current_date = datetime.now()

    # new period depending on how many much data are missing
    period = current_date - last_market_date
    period = int(period.days)
    
    df = get_hourly_dataframe(pair, f"{str(period+2)}d") # get data for the missing period

    file = pd.read_csv(f"Market/{pair}.csv")
    date_list = file['date'].astype(str).to_list() # list of all dates in file

    new_df = file[0:0] # new rows that will be written later

    # adding new rows to 'new_df'
    for index, row in df.iterrows():
        row['Pair'] = pair
        if str(row['date']) not in date_list:
            new_df.loc[len(new_df)] = row

    return new_df


def main():
    count = len(config.MARKET) -1

    # write data in files for each currrency
    for pair in config.MARKET:
        filename = Path(f"Market/{pair}.csv")

        # write missing rows until current date if file already exists
        if filename.is_file():
            new_df = get_new_data(pair)
    
            new_df.to_csv(f"Market/{pair}.csv", mode='a', header=False, index=False) # add new rows to csv file
            # new_df.to_string(f"MarketTXT/{pair}.txt", mode='a', header=False, index=False) # add new rows to txt file
        
        # create new file if there no file yet and add data by the whole required period
        else:
            df = get_hourly_dataframe(pair, config.PERIOD)
 
            # df.to_string(f"MarketTXT/{pair}.txt", index=False) # write data without empty rows txt

            # insert 'pair' column
            df.insert(loc = 1,
            column = 'Pair',
            value = pair)

            df.to_csv(f"Market/{pair}.csv", index=False, lineterminator='\n') # write data without empty rows csv

        if count > 0:
            print(f"{pair} | Data loaded | Left: {count}")
        else:
            print(f"{pair} | Data loaded | End")


        count -= 1

    print('\n')


if __name__ == "__main__":
    main()
import yfinance as yf
import pandas as pd
import numpy as np

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config


pd.set_option('display.max_rows', None) # when print a dataframe, it will print all columns, not only first and last 5 by default
pd.set_option('mode.chained_assignment', None) # avoiding a copy error


# to get ema we need to find sma at first
def get_sma(symbol_df):
    short_sma = pd.to_numeric(symbol_df['Close'].head(config.EMA_21)).mean()
    long_sma = pd.to_numeric(symbol_df['Close'].head(config.EMA_50)).mean()

    symbol_df['ema_21'] = np.nan
    symbol_df['ema_50'] = np.nan

    symbol_df.loc[config.EMA_21 - 1, 'ema_21'] = short_sma
    symbol_df.loc[config.EMA_50 - 1, 'ema_50'] = long_sma


# this func finds ema for all required periods
def get_ema(symbol_df, ema_period, index):
    e = index
    for i in range(len(symbol_df) - index):
        multiplier = 2 / (ema_period + 1)
        ema_value = (float(symbol_df.iloc[e]['Close']) * multiplier) + (float(symbol_df.iloc[e-1][f"ema_{ema_period}"]) * (1 - multiplier))
        symbol_df.loc[e, f"ema_{ema_period}"] = ema_value
        e += 1


# get values of the stochastic indicator
def get_stochastic(symbol_df):
    symbol_df['stochastic'] = np.nan

    # for calc. stochastic must be data for the whole stoch. period (10 in this case)
    l = 0 # low  point of range of stoch. period calc.
    h = config.KP # high  point of range of shoch. period calc.

    while h <= len(symbol_df):
        st_range_df = symbol_df.iloc[l:h]

        c = float(st_range_df['Close'].iloc[config.KP - 1]) # the most recent closing price
        lp = min(st_range_df['Low'].tolist()) # the lowest price traded of the stoch. period previous trading session
        hp = max(st_range_df['High'].tolist()) # the highest price traded during the same stoch. period
        if hp - lp != 0:
            stochastic_value = (c - lp) / (hp - lp)  * 100 # value of the stochastic indicator
        else:
            stochastic_value = np.nan

        symbol_df.loc[h -1, 'stochastic'] = stochastic_value

        l += 1
        h += 1


# stochastic ma is a simple ma of stochastic line
def get_stochastic_ma(symbol_df):
    symbol_df['stochastic_ma'] = np.nan

    l = config.KP - (config.MP - 2) # low point
    h = config.KP + (config.MP - 1) # high point

    while h <= len(symbol_df):
        d = symbol_df.iloc[l:h]['stochastic'].mean()
        
        symbol_df.loc[h -1, 'stochastic_ma'] = d

        l += 1
        h += 1


# if values satisfy a required conditions, in column 'macd_signal' will be 1.0 if buy and -1.0 if sell; else 0.0
def stochastic_signal(symbol_df, index):
    n = index
    for i in range(n, len(symbol_df)):
        # check: the price is overbought; stochastic crossed ma; it's happend right now; short ema is below long_ema; close price is above l_ema
        if float(symbol_df.iloc[i-1]['stochastic']) >= 80 and \
            float(symbol_df.iloc[i]['stochastic']) < float(symbol_df.iloc[i]['stochastic_ma']) and \
            float(symbol_df.iloc[i-1]['stochastic']) > float(symbol_df.iloc[i-1]['stochastic_ma']) and \
            float(symbol_df.iloc[i]['ema_21']) < float(symbol_df.iloc[i]['ema_50']) and \
            float(symbol_df.iloc[i-1]['Close']) >= float(symbol_df.iloc[i-1]['ema_50']):
            symbol_df.loc[i, 'stochastic_signal'] = -1.0
        # the same like above, but opposite
        elif float(symbol_df.iloc[i-1]['stochastic']) <= 20 and \
            float(symbol_df.iloc[i]['stochastic']) > float(symbol_df.iloc[i]['stochastic_ma']) and \
            float(symbol_df.iloc[i-1]['stochastic']) < float(symbol_df.iloc[i-1]['stochastic_ma']) and \
            float(symbol_df.iloc[i]['ema_21']) > float(symbol_df.iloc[i]['ema_50']) and \
            float(symbol_df.iloc[i-1]['Close']) <= float(symbol_df.iloc[i-1]['ema_50']):
            symbol_df.loc[i, 'stochastic_signal'] = 1.0
        else:
            symbol_df.loc[i, 'stochastic_signal'] = 0.0


# get rows that don't have indicators values
def get_new_data(symbol_df):
    new_df = symbol_df[0:0] # a new df with needed rows

    i = -1
    j = 11 # index 11 is for getting 11 extra rows for cacl. stochastic and stoch. ma
    # get rows without indicators values + 1 previous with indicators (for calculating ema must be its previous value)
    while True:
        if str(symbol_df.iloc[i]['stochastic']) == str(np.nan):
            new_df.loc[len(new_df)] = symbol_df.iloc[i]
        else:
            if j > 0:
                new_df.loc[len(new_df)] = symbol_df.iloc[i]
                j -= 1
            else:
                break
        
        i -= 1

    new_df = new_df.iloc[::-1] # reverse the df
    new_df = new_df.reset_index(drop=True)

    return new_df


def stochastic_trade_logic():
    count = len(os.listdir('Market')) - 1

    # write indicators values in files for each currrency
    for pair in os.listdir('Market'):
        pair = pair.replace('.csv', '')
        symbol_df = pd.read_csv(f"Market/{pair}.csv")

        cols = list(symbol_df.columns.values)

        # calculations in missing rows until current date if file already exists
        if 'stochastic' in cols:
            new_df = None
            # calculate required data for missing rows
            if str(symbol_df.iloc[-1]['stochastic']) == str(np.nan):
                new_df = get_new_data(symbol_df)

                get_ema(new_df, config.EMA_21, 11) # short ema; index 11 is for getting 11 extra rows for cacl. stochastic and stoch. ma
                get_ema(new_df, config.EMA_50, 11) # long ema
                get_stochastic(new_df)
                get_stochastic_ma(new_df)
                stochastic_signal(new_df, 11)

            # write data in file
            if new_df is not None:
                # deleting rows with no indicators data to replace them
                old_data = pd.read_csv(f"Market/{pair}.csv")
                old_data.drop(old_data.tail(len(new_df)-11).index, inplace=True)
                old_data.to_csv(f"Market/{pair}.csv", index=False)

                new_df.drop(new_df.head(11).index, inplace=True)
                new_df.to_csv(f"Market/{pair}.csv", mode='a', header=False, index=False) # add new rows to csv file

            # print progress of process
            if count > 0:
                print(f"Stochastic | {pair} - done | Left: {count}")
            else:
                print(f"Stochastic | {pair} - done | End\n")

        # calculation for all rows
        else:
            get_sma(symbol_df)
            get_ema(symbol_df, config.EMA_21, config.EMA_21) # short ema
            get_ema(symbol_df, config.EMA_50, config.EMA_50) # long ema
            get_stochastic(symbol_df)
            get_stochastic_ma(symbol_df)
            stochastic_signal(symbol_df, config.EMA_50 - 1)

            # write data in file
            if count > 0:
                print(f"Stochastic | {pair} - done | Left: {count}")
            else:
                print(f"Stochastic | {pair} - done | End\n")

            symbol_df.to_csv(f"Market/{pair}.csv", index=False)

        count -= 1


def main():
    stochastic_trade_logic()



if __name__ == "__main__":
    main()
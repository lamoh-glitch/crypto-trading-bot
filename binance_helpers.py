from binance import AsyncClient, BinanceSocketManager
from constants import API_KEY, API_SECRET
from db import create_frame


async def binance_client():
    return await AsyncClient.create(api_key=API_KEY, api_secret=API_SECRET)


async def init_binance_socket_manager():
    client = await binance_client()
    return BinanceSocketManager(client)


async def read_binance_symbol(bm, engine, symbol):
    ts = bm.trade_socket(symbol)
    async with ts as tscm:
        while True:
            msg = await tscm.recv()
            frame = create_frame(msg)
            frame.to_sql(symbol, engine, if_exists="append", index=False)
            print(frame)
import csv
import pandas as pd
from flask import Flask, jsonify

csv_file = 'trades.csv'
header = ['trade_id', 'entry_date', 'exit_date', 'entry_price', 'exit_price', 'quantity']
trades = [
    [1, '2024-01-01', '2024-01-10', 100, 110, 10],
    [2, '2024-01-15', '2024-01-20', 120, 115, 5],
    [3, '2024-02-01', '2024-02-05', 130, 140, 8],
]

with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)
    writer.writerows(trades)

def analyze_trades():
    trades = pd.read_csv(csv_file)
    trades['profit_loss'] = (trades['exit_price'] - trades['entry_price']) * trades['quantity']
    total_trades = len(trades)
    winning_trades = len(trades[trades['profit_loss'] > 0])
    losing_trades = len(trades[trades['profit_loss'] <= 0])
    total_profit_loss = trades['profit_loss'].sum()
    win_rate = winning_trades / total_trades
    risk_reward_ratio = trades[trades['profit_loss'] > 0]['profit_loss'].mean() / abs(trades[trades['profit_loss'] <= 0]['profit_loss'].mean())

    response = {
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'total_profit_loss': total_profit_loss,
        'win_rate': f'{win_rate:.2%}',
        'risk_reward_ratio': f'{risk_reward_ratio:.2f}'
    }
    
    return response

app = Flask(__name__)

@app.route('/analyze_trades', methods=['GET'])
def get_analysis():
    return jsonify(analyze_trades())

if __name__ == '__main__':
    app.run(debug=True)


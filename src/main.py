import os

from data_starter import DataReader
from strategy import Strategy

if __name__ == "__main__":
    """
    data_files = [
        'AMZN',
        'GOOG',
        'NVDA',
        'PLTR',
        'QQQ',
        'SPY',
    ]
    """
    data_files = []
    
    script_dir = os.path.dirname(__file__)
    for file_name in data_files:
        file_path = os.path.join(script_dir, '..', 'data', f'{file_name}.json')
        try:
            data = DataReader.read_file(file_path)
            data = DataReader.aggregate_data_tf(60, 300, data)  # Example aggregation from 1-min to 5-min
            
            strat = Strategy(data) # Test on the 5 minute data.
            trades = strat.run()
            results = strat.evaluate() # Calculate metrics based on trades
            print(f"Results for {file_name}:")
            print(results)
            
        except ValueError as e:
            print(e)
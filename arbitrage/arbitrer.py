import logging
import json
import config
import time
from concurrent.futures import ThreadPoolExecutor, wait
import public_markets

class Arbitrer(object):
    def __init__(self):
        self.markets = []
        self.depths = {}
        self.init_markets(config.markets)
        self.threadpool = ThreadPoolExecutor(max_workers=10)
    def init_markets(self, markets):
        self.market_names = markets
        print(markets)
        for market_name in markets:
            try:
                exec('import public_markets.' + market_name.lower())
                market = eval('public_markets.' + market_name.lower() + '.' + market_name + '()')
                self.markets.append(market)
            except (ImportError, AttributeError) as e:
                print("%s market name is invalid: Ignored (you should check your config file)" %(market_name))
    def __get_market_depth(self, market, depths):
        depths[market.name] = market.get_depth()
    def update_depths(self):
        depths = {}
        futures = []
        for market in self.markets:
            futures.append(self.threadpool.submit(self.__get_market_depth,market,depths))
        wait(futures, timeout = 20)
        return depths
    def tickers(self):
        for market in self.markets:
            logging.verbose("ticker: " + market.name + " - " + str(market.get_ticker()))
    # def tick(self):
        
    def loop(self):
        while True:
            self.depths = self.update_depths()
            print(self.depths)
            time.sleep(config.refresh_rate)
            # self.tickers()
            # self.tick()
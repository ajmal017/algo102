import json

import pendulum
from flask import Blueprint, jsonify
import sys

from lib.error_decorator import safe_run
from data_providers.finnhub.get_data_finnhub import get_stock_data, get_symbols, get_top_picks, get_company_profile, \
    get_recommendation_trends, get_aggregate_indicators, get_tech_ind, get_stock_data_db
from cache import cache
from data_providers.general.breakout import get_breakout_symbols_db

fh = Blueprint("fh", __name__, url_prefix='/fh')

today_ts = pendulum.today('UTC').int_timestamp
current_ts = pendulum.now('UTC').int_timestamp
three_months_ago_ts = pendulum.today('UTC').subtract(months=3).int_timestamp
six_months_ago_ts = pendulum.today('UTC').subtract(months=6).int_timestamp
one_year_ago_ts = pendulum.today('UTC').subtract(years=1).int_timestamp
default_start_end = dict(start=one_year_ago_ts, end=current_ts, timeframe='D')


@safe_run
@fh.route("/hist/<symbol>", defaults=default_start_end)
@fh.route("/hist/<symbol>/<timeframe>/<start>/<end>")
@cache.memoize(timeout=300)
def historical(symbol, start, end, timeframe):
    # candles_df = get_stock_data(symbol=symbol, start=start, end=end, timeframe=timeframe)
    candles_df = get_stock_data_db(symbol=symbol, num_months_ago=13)
    candles = candles_df[['t', 'o', 'h', 'l', 'c', 'v']].rename(columns={
        't': 'time',
        'o': 'open',
        'h': 'high',
        'l': 'low',
        'c': 'close',
        'v': 'volume'
    }).to_dict('records')
    return jsonify(candles)


@fh.route('/symbols')
def fh_symbols():
    return jsonify(get_symbols(return_type='list'))


@fh.route("/tech-ind/<symbol>/<indicator>", defaults=default_start_end)
@fh.route("/tech-ind/<symbol>/<timeframe>/<start>/<end>")
@cache.memoize(timeout=300)
def tech_ind(symbol, indicator, start, end, timeframe):
    return jsonify(get_tech_ind(symbol, indicator=indicator))


breakout_default = dict(window_percentage=2, window_length=15, min_market_cap=100)


@fh.route("/breakouts",defaults=breakout_default)
@fh.route("/breakouts/<window_percentage>/<window_length>/<min_market_cap>")
def breakouts(window_percentage, window_length, min_market_cap):
    df = get_breakout_symbols_db(window_percentage, window_length, min_market_cap)
    return df.to_json(orient='records')


@fh.route('/top-picks')
def fh_top_picks():
    return jsonify(get_top_picks())


@fh.route('/')
def fh_index():
    return 'hello fh'


@fh.route('/company-profile/<symbol>')
def company_profile(symbol):
    return get_company_profile(symbol, return_type='html')


@fh.route('/recommendation-trends/<symbol>')
def recommendation_trends(symbol):
    return jsonify(get_recommendation_trends(symbol))


@fh.route('/aggregate-indicators/<symbol>')
def aggregate_indicators(symbol):
    return jsonify(get_aggregate_indicators(symbol))

from flask import Flask, jsonify, request, redirect, flash, render_template, url_for, Blueprint
import requests, json, collections
from types import SimpleNamespace


bp = Blueprint('VGStats', __name__)


@bp.route('/home', methods=['GET'])
def index():
    platformdict = get_sales_by_platform()
    return render_template('VGStats/index.html', platformdict=platformdict)


def get_data():
    response = requests.get('https://api.dccresource.com/api/games')
    video_games = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
    return video_games


def get_platforms():
    video_games = get_data()
    platforms = {game.platform for game in video_games}
    return platforms


def get_sales_by_platform():
    games = get_data()
    platforms = get_platforms()
    platformdict = {}
    for platform in platforms:
        platformdict[f'{platform}'] = 0
    for game in games:
        platformdict[f"{game.platform}"] += game.globalSales
    platformdict = collections.OrderedDict(sorted(platformdict.items()))
    return platformdict

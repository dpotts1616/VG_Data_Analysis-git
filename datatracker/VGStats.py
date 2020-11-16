from flask import Flask, jsonify, request, redirect, flash, render_template, url_for, Blueprint
import requests, json, collections
from types import SimpleNamespace
import random

bp = Blueprint('VGStats', __name__)


@bp.route('/home', methods=['GET'])
def index():
    platformdict = get_sales_by_platform()
    return render_template('VGStats/index.html', platformdict=platformdict)


@bp.route('/search', methods=('GET', 'POST'))
def game_search():
    if request.method == 'POST':
        game_title = request.form['title']
        games = get_data()
        for game in games:
            if game.name == game_title:
                platforms = get_all_platforms(game.name, games)
                platform_level_sales = get_platform_sales(platforms, game.name, games)
                return render_template('VGStats/search.html', game=game, platforms=platforms, platformdict=platform_level_sales, message=None)
    else:
        return render_template('VGStats/search.html', game=None, message="Sorry, we don't have that game")

@bp.route('/region', methods=['GET'])
def genre_by_region():
    region_data = get_genre_by_region();
    return render_template('VGStats/region.html', dictionary=region_data)


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
        if type(game.year) == int:
            if game.year > 2013:
                platformdict[f"{game.platform}"] += game.globalSales
    platformdict = clean_up_dictionary(platformdict)
    platformdict = collections.OrderedDict(sorted(platformdict.items()))
    return platformdict

def clean_up_dictionary(dictionary):
    empty_values = []
    for x in dictionary:
        if dictionary[x] == 0:
            empty_values.append(x)
    for x in empty_values:
        del dictionary[x]
    return dictionary

def get_all_platforms(title, games):
    platforms = []
    for game in games:
        if game.name == title:
            platforms.append(game.platform)
    return platforms

def get_platform_sales(platforms, title, games):
    platformdict = {}
    for platform in platforms:
        platformdict[f'{platform}'] = 0
    for game in games:
        if game.name == title:
            platformdict[f"{game.platform}"] += game.globalSales
    return platformdict

def get_genre_by_region():
    games = get_data()
    genres = {game.genre for game in games}
    genre_region_dict = {}
    for item in genres:
        genre_region_dict[f'{item}'] = {'NA':0, 'EU':0, 'JP':0, 'Other':0}
    for game in games:
        genre_region_dict[f'{game.genre}']['NA'] += game.naSales
        genre_region_dict[f'{game.genre}']['EU'] += game.euSales
        genre_region_dict[f'{game.genre}']['JP'] += game.jpSales
        genre_region_dict[f'{game.genre}']['Other'] += game.otherSales
    for item in genre_region_dict:
        print(item)
        print(genre_region_dict[item]['NA'])
        print(genre_region_dict[item]['EU'])
        print(genre_region_dict[item]['JP'])
        print(genre_region_dict[item]['Other'])
    return genre_region_dict

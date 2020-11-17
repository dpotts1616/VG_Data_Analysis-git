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
        return render_template('VGStats/search.html', game=None, message=None)


@bp.route('/region', methods=['GET'])
def genre_by_region():
    region_data = get_genre_by_region();
    return render_template('VGStats/region.html', dictionary=region_data)


@bp.route('/publisher_console', methods=('GET', 'POST'))
def publisher_by_console():
    games = get_data()
    consoles = {game.platform for game in games}
    if request.method == 'POST':
        console = request.form['title']
        publisherdata = publisher_by_console(console, games)
        return render_template('VGStats/publisher_console.html', consoles=consoles, dictionary=publisherdata, console=console)
    else:
        return render_template('VGStats/publisher_console.html', consoles=consoles, dictionary=None)


def get_data():
    response = requests.get('https://api.dccresource.com/api/games')
    video_games = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
    return video_games


def get_sales_by_platform():
    games = get_data()
    platforms = {game.platform for game in games}
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
    return genre_region_dict


def publisher_by_console(console, games):
    publishers = {game.publisher for game in games}
    console_publisher_dict = {}
    # console_publisher_dict[f'{console}'] = ()
    for x in publishers:
        console_publisher_dict[f'{x}'] = 0
    for game in games:
        if game.platform == console:
            console_publisher_dict[f'{game.publisher}'] += game.globalSales
    console_publisher_dict = clean_up_dictionary(console_publisher_dict)
    return console_publisher_dict

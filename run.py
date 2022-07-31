from pywinauto import Desktop
import psutil
from pypresence import Presence
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from utils import env


def check_for_tidal():
    json_return = {
        'open': False,
        'playing': False,
        'song_playing': None,
    }
    windows = Desktop(backend="uia").windows()
    for w in windows:
        p_id = w.process_id()  # gets the process_ID on which all applications are running
        process = psutil.Process(p_id)  # finds the name of the process running based on pid
        if 'tidal' in process.name().lower():  # checks if the name of the process is tidal
            json_return['open'] = True
            if w.window_text() == 'TIDAL':
                json_return['playing'] = False
                return json_return
            json_return['playing'] = True
            json_return['song_playing'] = w.window_text()
            return json_return
    return json_return


def get_album_artwork(artist: str, song_name: str):
    client_id = env('SPOTIPY_CLIENT_ID')
    client_secret = env('SPOTIPY_CLIENT_SECRET')
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    track = sp.search(q='artist:' + artist + ' track:' + song_name, type='track')
    try:
        artwork = track['tracks']['items'][0]['album']['images'][0]['url']
    except:
        artwork = None
    return artwork


def start_rich_presence():
    cache_song_playing = ''
    client_id = env('DISCORD_CLIENT_ID')
    RPC = Presence(client_id)
    RPC.connect()
    print('RPC ready and connected to discord.')
    start = int(time.time())
    while True:
        data = check_for_tidal()
        if data['open']:
            if start is None:
                start = int(time.time())
                print('Detected tidal opening')
            if data['song_playing']:
                if cache_song_playing == data['song_playing']:
                    pass
                else:
                    cache_song_playing = data['song_playing']
                    song_playing = data['song_playing'].split(' - ')[0]
                    artist = data['song_playing'].split(' - ')[1]
                    album_artwork = get_album_artwork(artist, song_playing)
                    if album_artwork is None:
                        album_artwork = "tidal"
                    RPC.update(large_image=album_artwork, state='by ' + artist, details=song_playing, start=start,
                               large_text=song_playing + ' by ' + artist)
                    print(f"Detected Song {song_playing}")
            else:
                RPC.update(large_image='tidal', state='Tidal....', details='Just Browsing', start=start)
        else:
            cache_song_playing = ''
            start = None
            RPC.clear()
            pass


start_rich_presence()

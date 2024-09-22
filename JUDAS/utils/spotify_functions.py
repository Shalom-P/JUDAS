import re
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import time
import os
import ast
from dotenv import load_dotenv
load_dotenv(dotenv_path="../sample.env")
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
time_limit = 2
current_playback_device=None

def process_spotify(model_command:str):
    try:
        dict_command = ast.literal_eval(model_command)#.split("<|eot_id|>")[0].split("<|eom_id|>")[0])
    except:
        dict_command = ast.literal_eval(model_command+'}')
    if "playback_control" == dict_command["name"]:
        playback_control(dict_command["parameters"]["control_command"])
        return f"""{dict_command["parameters"]["control_command"]}ed the song"""
    elif "play_something" == dict_command["name"]:
        play_something(dict_command["parameters"]["to_play"],dict_command["parameters"]["type"])
        return f"""played the {dict_command["parameters"]["type"]} {dict_command["parameters"]["to_play"]}"""
    else:
        print("unknown command",flush=True)
    
def playback_control(control_command:str):
    # print(control_command,flush=True)
    global current_playback_device
    scope = (
    "user-library-read user-library-modify "
    "playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private "
    "user-read-private user-read-email user-top-read user-follow-read user-follow-modify "
    "streaming app-remote-control user-read-playback-state user-read-currently-playing user-modify-playback-state"
    )

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                client_secret=client_secret,
                                                redirect_uri=redirect_uri,
                                                scope=scope))
    if "pause" in control_command:
        current_playback_device = sp.current_playback()['device']['id']
        sp.pause_playback()
    elif "repeat" in control_command:
        sp.repeat("track")
    elif "resume" in control_command and current_playback_device!=None:
        sp.start_playback(
            device_id=current_playback_device,
            )
    elif "next" in control_command:
        playback_state = sp.current_playback()['is_playing']
        if playback_state:
            sp.next_track()
    elif "previous" in control_command:
        playback_state = sp.current_playback()['is_playing']
        if playback_state:
            sp.previous_track()
    elif "unlike" in control_command:
        playback_state = sp.current_playback()
        
        if playback_state and playback_state['is_playing']:
            # Get the current track's URI
            current_track = playback_state['item']
            track_uri = current_track['uri']
            
            # Remove the track from the user's saved tracks
            sp.current_user_saved_tracks_delete([track_uri])
    elif "like" in control_command:
        playback_state = sp.current_playback()
        if playback_state and playback_state['is_playing']:
            # Get the current track's URI
            current_track = playback_state['item']
            track_uri = current_track['uri']
            
            # Add the track to the user's saved tracks
            sp.current_user_saved_tracks_add([track_uri])
            print(f'Track added to liked: {current_track["name"]} by {", ".join(artist["name"] for artist in current_track["artists"])}')

def get_following_artists(seed_genres, limit):
    start_time = time.time()
    scope = 'user-follow-read user-library-read'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                client_secret=client_secret,
                                                redirect_uri=redirect_uri,
                                                scope=scope))
    artists = []
    results = sp.current_user_followed_artists(limit=limit)
    while results:
        for artist in results['artists']['items']:
            artist_genres = artist['genres']
            if any(genre in seed_genres for genre in artist_genres):
                artists.append(artist['id'])
                if len(artists)>=limit:
                    results['artists']['next']=False
                    break
            if time.time()-start_time>time_limit:
                results['artists']['next']=False
                break
        if results['artists']['next']:
            results = sp.next(results['artists'])
        else:
            results=False
            break
    if len(artists)==0:
        artists.append("4NHQUGzhtTLFvgF5SZesLK")
    return artists

# Function to get liked tracks filtered by genres
def get_liked_tracks(seed_genres, limit):
    start_time = time.time()
    # Scopes
    scope = 'user-follow-read user-library-read'

    # Authenticate
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                client_secret=client_secret,
                                                redirect_uri=redirect_uri,
                                                scope=scope))
    tracks = []
    results = sp.current_user_saved_tracks(limit=limit)
    while results:
        for item in results['items']:
            
            track = item['track']
            artist = sp.artist(track['artists'][0]['id'])
            artist_genres = artist['genres']
            if any(genre in seed_genres for genre in artist_genres):
                tracks.append(track['id'])
                if len(tracks)>=limit:
                    results['next']=False
                    break
            
            if time.time()-start_time>time_limit:
                results['next']=False
                break

        if results['next']:
            results = sp.next(results)
        else:
            results=False
            break
        if len(tracks)==0:
            tracks.append("0c6xIDDpzE81m2q797ordA")
    return tracks

# Function to get recommendations
def get_recommendations(limit,seed_genres):
    seed_artists = get_following_artists(seed_genres,3)
    seed_tracks = get_liked_tracks(seed_genres,3)
    # Scopes
    scope = 'user-follow-read user-library-read'

    # Authenticate
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                client_secret=client_secret,
                                                redirect_uri=redirect_uri,
                                                scope=scope))
    recommendations = sp.recommendations(seed_artists=seed_artists[:2],  # Limit to max 5 seed artists
                                         seed_genres=seed_genres[:2],
                                         seed_tracks=[seed_tracks[0]],    # Limit to max 5 seed tracks
                                         limit=limit)
    list_of_tracks = []
    recomended_track_ids = []
    for track in recommendations['tracks']:
        recomended_track_ids.append(track['id'])
        list_of_tracks.append(f"{track['name']} by {track['artists'][0]['name']}")
    scope = 'app-remote-control streaming user-read-playback-state user-modify-playback-state'
    
    # Authenticate
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                client_secret=client_secret,
                                                redirect_uri=redirect_uri,
                                                scope=scope))
    list_of_devices = sp.devices()
    sp.start_playback(device_id=list_of_devices['devices'][0]['id'],uris=[f'spotify:track:{x}' for x in recomended_track_ids],position_ms=0)
    return list_of_tracks

def play_something(to_play:str,type:str):
    
    # try:
    # scope = 'app-remote-control streaming user-read-playback-state user-modify-playback-state'
    scope = (
    "user-library-read user-library-modify "
    "playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private "
    "user-read-private user-read-email user-top-read user-follow-read user-follow-modify "
    "streaming app-remote-control user-read-playback-state user-read-currently-playing user-modify-playback-state"
    )

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                client_secret=client_secret,
                                                redirect_uri=redirect_uri,
                                                scope=scope))
    results = sp.search(q=f"{type}:{to_play}", type=type)
    song_list = list()
    if "albums" in results.keys():
        album_id = results['albums']['items'][0]["id"]
        results = sp.album(album_id)
        for idx, track in enumerate(results['tracks']['items']):
            song_list.append(track['id'])
    elif "artists" in results.keys():
        artists_id = results['artists']['items'][0]['id']
        results = sp.artist_top_tracks(artists_id)
        for idx, track in enumerate(results['tracks']):
            song_list.append(track['id'])
    else:
        for idx, track in enumerate(results['tracks']['items']):
            song_list.append(track['id'])
    
    list_of_devices = sp.devices()
    device_id = list_of_devices['devices'][0]['id']
    
    sp.start_playback(device_id=device_id,uris=[f'spotify:track:{x}' for x in song_list],position_ms=0)
    # except Exception as e:
    #     print(e,"not happend")


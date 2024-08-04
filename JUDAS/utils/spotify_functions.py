import re
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import time
# Replace these with your actual client ID, client secret, and redirect URI
client_id = ''
client_secret = ''
redirect_uri = ''
time_limit = 2
current_playback_device=None

def process_spotify(model_command:str):
    print(model_command)
    if "@cntrl" in model_command:
        control_command = model_command.split("@")[1]
        playback_control(control_command)
    elif "@playing" in model_command:
        split = model_command.split("@")[1]
        type_of_input = split.split("type:")[1].split(" name:")[0]
        input = split.split("name:")[1]
        try:
            input = input.split('"')[1]
        except:
            pass
        play_something(type=type_of_input,name=input)
        
def playback_control(control_command:str):
    print(control_command)
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

def play_something(name:str,type:str):
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
    results = sp.search(q=f"{type}:{name}", type=type)
    song_list = list()
    if "albums" in results.keys():
        album_id = results['albums']['items'][0]["id"]
        results = sp.album(album_id)
    if "artists" in results.keys():
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


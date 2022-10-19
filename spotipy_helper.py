from spotipy.oauth2 import SpotifyClientCredentials 
import json, spotipy, time, sys, os, math
import pandas as pd  

# connect to API 
# must intialize environment variables first 
client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
sp.trace = False


def get_pid_from_link(link): 
    '''
    takes in a link to a spotify playlist and returns the playlist id 
    ''' 
    if '?' in link: 
        return link.split('?')[0].split('playlist/')[1] 
    elif 'playlist/' in link: 
        return link.split('playlist/')[1]  
    else: 
        return link 

    


def get_audio_features_by_artist(artist_name, tracks_num=10,to_csv=True):
    '''
    function takes in...
    artist_name = a string indicating the artist's name
    tracks_num = an integer indicating how many tracks you want from that artist
    '''
    artist_name = artist_name   
    track_num = 30
    results = sp.search(q=artist_name, limit=track_num) 
    songs = [] 
    print ("retrieving songs...\n\n") 
    track_ids = [] 
    for i, t in enumerate(results['tracks']['items']): 
        print(' ', i, t['name']) 
        songs.append(t['name'])  
        track_ids.append(t['uri']) 
    print(track_ids)
    audio_features = sp.audio_features(track_ids) 
    # list of dictionaries with audio data respective to track num 

    # alter dictionaries so it includes respective track title 
    audio_features[0]['track_title'] = songs[0] 
    feat0 = audio_features[0] 
    df = pd.DataFrame(feat0, index = [0]) 
    for i in range(1,len(audio_features)): 
        audio_features[i]['track_title'] = songs[i] 
        df.loc[len(df)] = audio_features[i] 

    # change dataframe so track_title is in first position for easy viewing
    key_list = list(feat0.keys())
    new_cols = ['track_title', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'type', 'id', 'uri', 'track_href', 'analysis_url', 'duration_ms', 'time_signature']
    df = df[new_cols]
    df.to_csv(f'{os.getcwd()}/DATA/TEST/A{artist_name}_t{track_num}.csv')
    



def get_audio_features_by_playlist(username, playlist_id, save = True,filename="f"): 
    '''
    functions takes in...
    username = string of the user 
    playlist_id = the alphanumeric id for the playlist (you can use the get_pid_from_link() function to 
    get the id from the share link to a playlist) 
    save = boolean indicating whether you want to save the dataframe or not 

    returns a pandas dataframe containing the audio features for all the tracks in a playlist 
    '''
    
    songs = [] 
    #r = sp.user_playlist_tracks(username,playlist_id)  
    #print (r) 
    #r = {'next':'startswith'}  
    t = get_playlist_tracks(username=username,playlist_id=playlist_id) 
    ids = []
    # for i in range(len(t)): 
    #     r = sp.next(r)
    #     print ("r: ",r) 
    #     t.extend(r['items'])
    for s in t: 
        ids.append(s["track"]["id"]) 
        songs.append(s["track"]["name"]) 
    for i in range(len(ids)): ids[i] = "spotify:track:"+ids[i]  


    # chunk audio feature requests so < 80 each request 
    iter = math.ceil(len(t) / 80)
    #print ("ITER = ",iter," type", type(iter))  
    audio_features_arr = [] 
    #audio_features = sp.audio_features(ids) 
    for i in range(iter): 
        index_start = i*80
        index_end = index_start + 80
        temp_features = sp.audio_features(ids[index_start:index_end]) 
        audio_features_arr.append(temp_features) 
    
    # squish list so not chunked
    audio_features = [] 
    for i in range(len(audio_features_arr)): 
        for k in range(len(audio_features_arr[i])): 
            audio_features.append(audio_features_arr[i][k]) 


    # alter dictionaries so it includes respective track title 
    audio_features[0]['track_title'] = songs[0] 
    feat0 = audio_features[0] 
    df = pd.DataFrame(feat0, index = [0]) 
    for i in range(1,len(audio_features)): 
        audio_features[i]['track_title'] = songs[i] 
        df.loc[len(df)] = audio_features[i] 

    # change dataframe so track_title is in first position for easy viewing
    key_list = list(feat0.keys())
    new_cols = ['track_title', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'type', 'id', 'uri', 'track_href', 'analysis_url', 'duration_ms', 'time_signature']
    df = df[new_cols]

    filepath = f'{os.getcwd()}/DATA/PILOT/U{username}.csv' if (filename == "f") else f"{os.getcwd()}/DATA/PILOT/{filename}.csv" 
    df.to_csv(filepath) 
    print ("SUCCESSFULLY saved ", filepath)  
    return df 



def get_playlist_tracks(username,playlist_id):
    # helper function that returns a list of tracks and their basic data 
    results = sp.user_playlist_tracks(username,playlist_id)
    tracks = results['items'] 
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks 


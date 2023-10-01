import string, random, time, datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect

app = Flask(__name__)

app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'
app.secret_key = ''.join(random.choices(string.__all__, k=16))
TOKEN_INFO = 'token info'

@app.route('/')
def login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('create_monthly_playlist', external = True))


#Util
def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        redirect(url_for('login', external=False))
    
    now = int(time.time())

    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh token'])

    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id= 'c59fd81b1add4a89b8edf5fab81a763b',
        client_secret= '7d302817ecd94da8b3c9b5e26cde9385',
        redirect_uri=url_for('redirect_page', _external=True),
        scope= 'user-library-read playlist-modify-public playlist-modify-private user-top-read'
        )



#Functions
@app.route('/createMonthlyPlaylist')
def create_monthly_playlist():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect('/')
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    user_id = sp.current_user()['id']
    
    month = datetime.date.today().strftime('%B')
    year = datetime.datetime.now().year

    monthly_playlist = sp.user_playlist_create(user_id, f"{month} {year}", True)
    monthly_playlist_id = monthly_playlist['id']

    top_tracks = sp.current_user_top_tracks(limit=30, time_range='short_term')['items']

    song_uris = []
    for song in top_tracks:
        song_uri = song['uri']
        song_uris.append(song_uri)
    sp.user_playlist_add_tracks(user_id, monthly_playlist_id, song_uris)

    return "Success"

        

if __name__ == "__main__":
    app.run()



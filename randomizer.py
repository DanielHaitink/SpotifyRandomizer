import spotipy
import os
import spotipy.util as util
from random import shuffle

os.environ["SPOTIPY_CLIENT_ID"] = ""
os.environ["SPOTIPY_CLIENT_SECRET"] = ""
os.environ["SPOTIPY_REDIRECT_URI"] = ""

scope = 'user-library-read playlist-read-private playlist-modify-private playlist-modify-public'


class FailedAuth(BaseException):
    """Failed authentication for spotify"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class NotFound(BaseException):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class SpotifyAuth:
    def __init__(self, username):
        self._username = username
        self._sp = None

    def wait_for_auth(self):
        token = util.prompt_for_user_token(self._username, scope)

        if token:
            self._sp = spotipy.Spotify(auth=token)
        else:
            raise FailedAuth

    def get_spotify(self):
        return self._sp


def __list_add_tracks__(list_object, tracks):
    for item in tracks["items"]:
        track = item["track"]
        if track["id"] is not None:
            list_object.append(track["id"])
    return list_object


def __add_playlist__(playlist_list, playlists):
    for item in playlists["items"]:
        playlist_list.append(item)
    return playlist_list


def __chunk_list__(data, size):
    return [data[x:x + size] for x in range(0, len(data), size)]


class SpotifyRandomizer:
    """"Randomizes a playlist in spotify"""

    def __init__(self, username, sp):
        self._username = username
        self._sp = sp
        self._playlist = None
        self._random_playlist_name = "{} Random"

    def set_playlist_by_id(self, playlist_id):
        try:
            self._playlist = self._sp.user_playlist(self._username, playlist_id)
        except BaseException:
            raise NotFound("No playlist found")

        if self._playlist is None:
            raise NotFound("No playlist found")

    def set_playlist_by_name(self, name):
        self._playlist = self.__find_playlist__(name)

        if self._playlist is None:
            raise NotFound("No playlist found")

    def __find_playlist__(self, name):
        playlists = self._sp.user_playlists(self._username)

        for item in playlists["items"]:
            if item["name"] == name:
                return item
        return None

    def get_playlist(self):
        return self._playlist

    def get_playlist_tracks(self, playlist=None):
        if playlist is None:
            playlist = self._playlist

        track_list = []
        result = self._sp.user_playlist(self._username, playlist["id"], fields="tracks,next")
        tracks = result["tracks"]
        track_list = __list_add_tracks__(track_list, tracks)

        while tracks["next"]:
            tracks = self._sp.next(tracks)
            track_list = __list_add_tracks__(track_list, tracks)

        return track_list

    def show_playlist_tracks(self):
        tracks = self.get_playlist_tracks()

        if self._playlist is None:
            return
        for i, item in enumerate(tracks['items']):
            track = item['track']
            print("%32.32s %s" % (track['artists'][0]['name'], track['name']))

    def __remove_all_tracks__(self, playlist):
        if playlist is None:
            return

        tracks = self.get_playlist_tracks(playlist)
        for chunk in __chunk_list__(tracks, 100):
            self._sp.user_playlist_remove_all_occurrences_of_tracks(self._username, playlist["id"], chunk)

    def __get_random_playlist__(self):
        return self.__find_playlist__(self._playlist["name"].format(self._random_playlist_name))

    def __create_random_playlist__(self):
        return self._sp.user_playlist_create(self._username,
                                             self._random_playlist_name.format(self._playlist["name"]),
                                             False)

    def get_playlist_size(self, playlist=None):
        if playlist is not None:
            return playlist["tracks"]["total"]
        elif self._playlist is not None:
            return self._playlist["tracks"]["total"]

    def add_tracks_to_playlist(self, tracks, playlist=None):
        if playlist is None and self._playlist is not None:
            playlist = self._playlist
        elif self._playlist is None:
            return

        for chunk in __chunk_list__(tracks, 100):
            self._sp.user_playlist_add_tracks(self._username, playlist["id"], chunk)

    def randomize_playlist(self):
        if self._playlist is None:
            raise TypeError

        random_playlist = self.__get_random_playlist__()

        if random_playlist is None:
            random_playlist = self.__create_random_playlist__()

        if self.get_playlist_size(random_playlist) > 1:
            self.__remove_all_tracks__(random_playlist)

        tracks = self.get_playlist_tracks()
        shuffle(tracks)

        self.add_tracks_to_playlist(tracks, random_playlist)

    def get_all_playlists(self):
        playlist_list = []

        playlists = self._sp.user_playlists(self._username)
        __add_playlist__(playlist_list, playlists)

        while playlists["next"]:
            playlists = self._sp.next(playlists)
            __add_playlist__(playlist_list, playlists)
        return playlist_list

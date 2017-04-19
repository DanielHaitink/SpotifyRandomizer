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

    def waitForAuth(self):
        token = util.prompt_for_user_token(self._username, scope)

        if token:
            self._sp = spotipy.Spotify(auth=token)
        else:
            raise FailedAuth

    def getSpotify(self):
        return self._sp


def __listAddTracks__(listObject, tracks):
    for item in tracks["items"]:
        track = item["track"]
        if track["id"] is not None:
            listObject.append(track["id"])
    return listObject


def __addPlaylistToList__(playlistList, playlists):
    for item in playlists["items"]:
        playlistList.append(item)
    return playlistList


def __chunkList__(data, size):
    return [data[x:x + size] for x in range(0, len(data), size)]


class SpotifyRandomizer:
    """"Randomizes a playlist in spotify"""

    def __init__(self, username, sp):
        self._username = username
        self._sp = sp
        self._playlist = None
        self._randomPostfix = " Random"

    def setPlaylistById(self, playlistId):
        try:
            self._playlist = self._sp.user_playlist(self._username, playlistId)
        except BaseException:
            raise NotFound("No playlist found")

        if self._playlist is None:
            raise NotFound("No playlist found")

    def setPlaylistByName(self, name):
        self._playlist = self.__findPlaylist__(name)

        if self._playlist is None:
            raise NotFound("No playlist found")

    def __findPlaylist__(self, name):
        playlists = self._sp.user_playlists(self._username)

        for item in playlists["items"]:
            if item["name"] == name:
                return item
        return None

    def getPlaylist(self):
        return self._playlist

    def getPlaylistTracks(self, playlist=None):
        if playlist is None:
            playlist = self._playlist

        trackList = []
        result = self._sp.user_playlist(self._username, playlist["id"], fields="tracks,next")
        tracks = result["tracks"]
        trackList = __listAddTracks__(trackList, tracks)

        while tracks["next"]:
            tracks = self._sp.next(tracks)
            trackList = __listAddTracks__(trackList, tracks)

        return trackList

    def showPlaylistTracks(self):
        tracks = self.getPlaylistTracks()

        if self._playlist is None:
            return
        for i, item in enumerate(tracks['items']):
            track = item['track']
            print("%32.32s %s" % (track['artists'][0]['name'], track['name']))

    def __removeAllTracks__(self, playlist):
        if playlist is None:
            return

        tracks = self.getPlaylistTracks(playlist)
        for chunk in __chunkList__(tracks, 100):
            self._sp.user_playlist_remove_all_occurrences_of_tracks(self._username, playlist["id"], chunk)

    def __getRandomPlaylist__(self):
        return self.__findPlaylist__(self._playlist["name"] + self._randomPostfix)

    def __createRandomPlaylist__(self):
        return self._sp.user_playlist_create(self._username, self._playlist["name"] + " Random", False)

    def getPlaylistSize(self, playlist=None):
        if playlist is not None:
            return playlist["tracks"]["total"]
        elif self._playlist is not None:
            return self._playlist["tracks"]["total"]

    def addTracksToPlaylist(self, tracks, playlist=None):
        if playlist is None and self._playlist is not None:
            playlist = self._playlist
        elif self._playlist is None:
            return

        for chunk in __chunkList__(tracks, 100):
            self._sp.user_playlist_add_tracks(self._username, playlist["id"], chunk)

    def randomizePlaylist(self):
        if self._playlist is None:
            raise TypeError

        randomPlaylist = self.__getRandomPlaylist__()

        if randomPlaylist is None:
            randomPlaylist = self.__createRandomPlaylist__()

        if self.getPlaylistSize(randomPlaylist) > 1:
            self.__removeAllTracks__(randomPlaylist)

        tracks = self.getPlaylistTracks()
        shuffle(tracks)

        self.addTracksToPlaylist(tracks, randomPlaylist)

    def getAllPlaylists(self):
        playlistList = []

        playlists = self._sp.user_playlists(self._username)
        __addPlaylistToList__(playlistList, playlists)

        while playlists["next"]:
            playlists = self._sp.next(playlists)
            __addPlaylistToList__(playlistList, playlists)
        return playlistList

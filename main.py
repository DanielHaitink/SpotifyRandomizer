import randomizer as r
import sys


def foundPlaylistByName(rand, playlist):
    try:
        rand.setPlaylistByName(playlist)
    except r.NotFound:
        return False
    return True


def foundPlaylistById(rand, playlist):
    try:
        rand.setPlaylistById(str(playlist))
    except r.NotFound:
        return False
    return True


def playlistFound(rand, playlist):
    return foundPlaylistByName(rand, playlist) or foundPlaylistById(rand, playlist)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = input("Please type in your username: ")

    try:
        auth = r.SpotifyAuth(username)
        auth.waitForAuth()
    except r.FailedAuth:
        print("Authentication failed")
        sys.exit()

    randomizer = r.SpotifyRandomizer(username, auth.getSpotify())

    if len(sys.argv) > 2:
        playlists = sys.argv[2: len(sys.argv)]
    else:
        playlists = input("Please type in playlist(s), separated by comma: ").split(',')

    for playlist in playlists:
        if not playlistFound(randomizer, playlist):
            print("Playlist %s was not found" % (playlist))
            continue
        randomizer.randomizePlaylist()

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


def main():
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
        userPlaylists = [x['name'] for x in randomizer.getAllPlaylists()]
        print("User playlists:")
        for i, item in enumerate(userPlaylists):
            print("{}: {}".format(i + 1, item))

        while True:
            picks = input("Enter the # of the playlist(s), separated by comma, or 'cancel' to cancel: ")
            if picks.lower() == "cancel":
                print("Goodbye!")
                return
            playlists = []
            for pick in picks.split(","):
                pick = pick.strip()
                if not re.match("^[0-9]+$", pick):
                    print('Invalid number "{}"!'.format(pick))
                    continue
                else:
                    pick = int(pick)
                    if pick < 1 or pick > len(userPlaylists):
                        pick = input("The number must be between {}-{}.".format(1, len(userPlaylists)))
                        continue
                    playlists.append(userPlaylists[pick - 1])
            break
    for playlist in playlists:
        if not playlistFound(randomizer, playlist):
            print("Playlist %s was not found" % (playlist))
            continue
        randomizer.randomizePlaylist()

 if __name__ == "__main__":
    main()

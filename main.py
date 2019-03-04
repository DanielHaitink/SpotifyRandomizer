import randomizer as r
import json
import os
import sys
import re


def found_playlist_by_name(rand, playlist):
    try:
        rand.set_playlist_by_name(playlist)
    except r.NotFound:
        return False
    return True


def found_playlist_by_id(rand, playlist):
    try:
        rand.set_playlist_by_id(str(playlist))
    except r.NotFound:
        return False
    return True


def is_playlist_found(rand, playlist):
    return found_playlist_by_name(rand, playlist) or found_playlist_by_id(rand, playlist)


def authenticate_spotify(username):
    try:
        auth = r.SpotifyAuth(username)
        auth.wait_for_auth()
    except r.FailedAuth:
        print("Authentication failed")
        sys.exit()
    auth.stop_server()
    return auth


def print_user_playlists(user_playlists):
    print("User playlists:")
    for i, item in enumerate(user_playlists):
        print("{}: {}".format(i + 1, item))


def get_playlists_by_input(randomizer):
    user_playlists = [x['name'] for x in randomizer.get_all_playlists()]
    print_user_playlists(user_playlists)

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

                if pick < 1 or pick > len(user_playlists):
                    print("The number must be between {}-{}.".format(1, len(user_playlists)))
                    continue

                playlists.append(user_playlists[pick - 1])
        break

    return playlists


def lambda_handler(event, context):

    if os.environ["USER"]:
        username = os.environ["USER"]
    else:
        if len(sys.argv) > 1:
            username = sys.argv[1]
        else:
            username = input("Please type in your username: ")

    auth = authenticate_spotify(username)
    randomizer = r.SpotifyRandomizer(username, auth.get_spotify())

    if os.environ["PLAYLISTS"]:
        playlists = os.environ["PLAYLISTS"].split(',')
    else:
        if len(sys.argv) > 2:
            playlists = sys.argv[2: len(sys.argv)]
        else:
            playlists = get_playlists_by_input(randomizer)

    for playlist in playlists:
        if not is_playlist_found(randomizer, playlist):
            print("Playlist %s was not found" % playlist)
            continue
        randomizer.set_playlist_by_name(playlist)
        randomizer.randomize_playlist()

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


if __name__ == "__main__":
    lambda_handler(None, None)

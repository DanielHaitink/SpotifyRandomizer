<p align="center"><img alt="SpotifyRandomizer" src="SpotifyRandomizer.png" width="350"/></p> <!-- Gross HTML because of GitHub's markdown -->
Creates a spotify list from an existing one, with tracks placed in a random order

## Required packages

To use SpotifyRandomizer, you need [spotipy](https://github.com/plamere/spotipy).
This can be installed by doing: `pip3 install spotipy`

## Setup

First you have to create a spotify application, so you can use spotipy. You can do this at the [spotify website](https://developer.spotify.com/my-applications/). You need to put the client ID, client sectret and redirect URL into `randomizer.py`.

## Run

The script can be ran by doing `python3 main.py`.
In this case the program will ask you for your username and playlist(s) while running.
You can also give that information as an argument, like this `python3 main.py 1234567890 Playlist1 Playlist2 Playlist3`

The playlists can be the name of the playlist or the ID of the playlist (found in the URL). These playlists have to be owned by you.

When you run the program for the first time, it will open the spotify website for authorization. Then you need to copy the redirected URL into the commandline. After this, the program should work.

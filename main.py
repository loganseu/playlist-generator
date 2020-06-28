from Spotify import Spotify
from Youtube import Youtube
import smtplib
import traceback
import json

def send_email(json_file, subject, body):
    server = smtplib.SMTP('smtp.gmail.com')
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(json_file["EMAIL"]["SENDER_EMAIL"], json_file["EMAIL"]["PASSWORD"])
    server.sendmail(json_file["EMAIL"]["SENDER_EMAIL"], json_file["EMAIL"]["RECEIVER_EMAIL"],
                    'From: Playlist Generator\nSubject: {}\n\n{}'.format(subject, body))


def main():
    json_file = json.loads(open("config.json", "r").read())
    try:
        spotify_obj = Spotify(json_file)
        spotify_obj.get_tokens()
        spotify_obj.update_access_token()
        spotify_obj.get_recommended_songs()

        youtube_obj = Youtube(json_file)
        youtube_obj.get_liked_videos(spotify_obj)

        spotify_obj.populate_playlist()

        send_email(json_file, "Music transfer succeeded",
                         "No errors were found. "
                         "{} new songs were added to your playlist.".format(spotify_obj.number_of_songs_added()))

    except Exception as error:
        error_message = "Error: {}\n\n" \
                        "Stacktrace: {}".format(error, traceback.format_exc())
        send_email(json_file, "Playlist generator failed", error_message)

main()
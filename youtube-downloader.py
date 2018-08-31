from __future__ import unicode_literals
import youtube_dl, sys, pyperclip, threading, os, eyed3

# 1. Use Python 36 from CMD using python command or F5 in Atom
# 2. `pip install youtube_dl`
# 3. `pip install pyperclip`
# 4. [Install FFmpeg windows](https://github.com/adaptlearning/adapt_authoring/wiki/Installing-FFmpeg)
# 5. Add ffmpeg to path `C:\Program Files\ffmpeg-20180412-8d381b5-win64-static\bin`

# Getting this working on Mac Machines - must run with python3
# You'll may need to upgrade TLS to v1.2 - best to just use python3 https://news.ycombinator.com/item?id=13539034
# 1. Install HomeBrew ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
# 2. brew install youtube-dl
# 3. pip3.6 install youtube-dl
# 4. pip3.6 install pyperclip
# 5. brew install ffmpeg
# 6. pip3.6 install eyeD3
# 6. pip 3.6 install libmagic
# 7. brew install libmagic

def get_all_command_line_ars():
    if len(sys.argv) > 1:
        # Get address from command line.
        url = ' '.join(sys.argv[1:])
    else:
        # Get address from clipboard.
        url = pyperclip.paste()
        print("URL from the clipboard: " + url)

def check_clipboard_for_youtube_url():
    url = pyperclip.paste()
    if len(url) > 200 :
        url = "Default URL"
    if "https://www.youtube.com" in url:
        if url not in mp3_downloaded_already:
            download_audio(url)
    print("Checking for youtube link...")
    threading.Timer(2.0, check_clipboard_for_youtube_url).start()

def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'no-check-certificate' , True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    mp3_downloaded_already.append(url)
    print("Already downloaded these videos: ")
    print(mp3_downloaded_already)
    add_tags_to_files()

def add_tags_to_files():
    print("Checking For Files Needing Tags")
    walk_through_new_music()

# You can manually check the tags from cmd
# eyeD3 "D:\Music\Tenacious D\Wonderboy ( with lyrics )\00-ACiA1TX0tvA.mp3"
# eyeD3 "C:\Users\miles\Dropbox\New Music\00-20CTa043IA.mp3"

# When I download songs from youtube they lack all the tags they should have.
# This walks through just downloaded songs and corrects the missing tags.
# For tags to work correctly, this must be run from the New Music folder the files were downloaded to
def walk_through_new_music():
    for path, subdirs, files in os.walk(current_working_directory):
       for filename in files:
           set_mp3_path(os.path.join(path, filename))
           if tagging_is_needed():
               print("Adding Tags")
               decide_where_parsed_song_data_goes(parse_song_data(filename))
           else:
               move_file_to_monkey_media_scanned_folder()

def move_file_to_monkey_media_scanned_folder():
    print("Moving File to SendToMonkeyMedia Folder")

def set_mp3_path(path):
    global mp3path
    mp3path = path

def tagging_is_needed():
    if isMp3():
        return hasTitle() == False

def isMp3():
    return mp3path[-4:] == ".mp3"

def hasTitle():
    audiofile = eyed3.load(mp3path)
    return audiofile.tag.title != None

# Adds the song data assuming the structure of Artist - Song
def decide_where_parsed_song_data_goes(song_data):
    # As a default, set the title
    set_title(song_data[0])
    set_artist(song_data[0])
    set_album("Youtube Downloads")
    # Check if we have more than one piece of data
    if len(song_data) > 1:
        set_artist(song_data[0])
        set_title(song_data[1])
    # We have artist and more
    if len(song_data) > 2:
        set_title((" ".join(song_data)))

# Gets the song data from the filename
def parse_song_data(filename):
    song_data = filename.split("-") #Split on the -
    song_data = [x.strip(' ') for x in song_data] #Remove the white space
    song_data = song_data[:-1] #Get rid of the youtube url at the end of the file
    print(song_data)
    return song_data

def set_title(title):
    audiofile = eyed3.load(mp3path)
    audiofile.tag.title = title
    audiofile.tag.save()

def set_album(album):
    audiofile = eyed3.load(mp3path)
    audiofile.tag.album = album
    audiofile.tag.save()

def set_artist(artist):
    audiofile = eyed3.load(mp3path)
    audiofile.tag.artist = artist
    audiofile.tag.save()

current_working_directory = os.path.dirname(os.path.realpath(__file__))
print("Working In: " + current_working_directory)
mp3path = "Default File Path"
mp3_downloaded_already = []
check_clipboard_for_youtube_url()

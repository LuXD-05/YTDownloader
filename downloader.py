import os
import re
import ast
import json
import subprocess
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from httplib2 import ServerNotFoundError
from concurrent.futures import ThreadPoolExecutor

from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText

DOWNLOAD_FOLDER = os.path.join(os.environ.get("USERPROFILE", ""), "Downloads")
HISTORY_FILE = "download_history.json"
FFMPEG_PATH = r"C:\Users\alessio\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1-full_build\bin\ffmpeg.exe"
YTDLP_PATH = "yt-dlp"

if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)

class Downloader :
    
    key = None
    format = None
    quality = None
    split_chapters = False
    filter = ["video", "playlist"]
    default_download_path = None
    api = None
    audio_formats = []
    video_formats = []
    formats = []
    
    def __init__(self):
        # Loads default settings (& options)
        self.load_settings()
        # Build google's api client (for yt)
        self.rebuild_yt_api()
        
    # Loads settings into the app (from .env)
    def load_settings(self):
        self.key = os.getenv("YT_API_KEY")
        self.format = os.getenv("FORMAT")
        self.quality = os.getenv("QUALITY")
        self.split_chapters = os.getenv("SPLIT_CHAPTERS")
        self.filter = os.getenv("FILTER").split(",")
        self.default_download_path = os.getenv("DEFAULT_DOWNLOAD_PATH")
        self.audio_formats = os.getenv("AUDIO_FORMATS").split(",")
        self.video_formats = os.getenv("VIDEO_FORMATS").split(",")
        self.formats = self.video_formats + self.audio_formats
        
    # (Re)builds the yt api object
    def rebuild_yt_api(self):
        if self.key is not None:
            self.api = build("youtube", "v3", developerKey=self.key)
    
    # Sets selected filters   (["video"] / ["playlist"] / ["video", "playlist"])
    def set_filter(self, filters):
        self.filter = filters
        
    #region Search
        
    # Search (search form a term/URL the video(s)/playlist(s) based on params () & filters ())
    def search(self, query):
        
        try:
            
            results = []
            
            # Regex to find if query is a YouTube URL
            match = re.match(r"(https?://)?(www\.)?(youtube\.com|youtu\.be|youtube-nocookie\.com)/(watch\?v=|playlist\?list=|embed/|shorts/|)([a-zA-Z0-9_-]+)", query)
        
            # If query is a YouTube URL
            if match:
                # Gets video/playlist id + searches by it
                id = match.group(5)
                results = self.search_yt_by_id(id, "Playlist" if "list=" in query else "Video")
            # If query is a normal search term
            else:
                results = self.search_yt(query)
            
            return results
    
        except HttpError as e:
            
            MDSnackbar(
                MDSnackbarText(text=f"Error: API key '{self.key}' is invalid or quota exceeded" if e.resp.status == 403 else "An error occurred during search"),
                y="24dp",
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
            ).open()
            
        except ServerNotFoundError as e:
            
            MDSnackbar(
                MDSnackbarText(text=f"Error: Unable to connect to the server or the internet" if e.resp.status == 403 else "An error occurred during search"),
                y="24dp",
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
            ).open()
                        
            return
        
    # Searches YouTube videos/playlists based on a query
    def search_yt(self, query):
        
        results = []
        request = self.api.search().list(q=query, part="snippet", type=",".join(self.filter), maxResults=20, safeSearch="none")
        response = request.execute()
        
        # Format and save each result + return
        for item in response["items"]:
            results.append({
                "id": item["id"]["videoId"] if "videoId" in item["id"] else item["id"]["playlistId"],
                "title": item["snippet"]["title"],
                "type": "Video" if "videoId" in item["id"] else "Playlist",
                "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                "channel": item["snippet"]["channelTitle"]
            })
        return results
        
    # Searches YouTube videos/playlists based on an id
    def search_yt_by_id(self, id, type):
        
        # Searches video if type == Video, otherwise searches playlist
        if type == "Video":
            request = self.api.videos().list(part="snippet", id=id)
        else:
            # request = self.api.playlists().list(part="snippet", id=id)
            MDSnackbar(
                MDSnackbarText(text=f"Playlist search is not currently supported"),
                y="24dp",
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
            ).open()
            
        response = request.execute()
        
        # If response has items, returns first
        if response["items"]:
            item = response["items"][0]
            return [{
                "id": item["id"],
                "title": item["snippet"]["title"],
                "type": type,
                "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                "channel": item["snippet"]["channelTitle"]
            }]
        
        # Otherwise returns []
        return []
    
    #endregion
    
    #region Download
    
    def download(self, items):
        """Main handler for downloads; downloads in parallel (async with threads)."""
        
        # Using ThreadPoolExecutor to download in parallel
        with ThreadPoolExecutor() as executor:
            
            for item in items:
                
                type = None
                url = None
                
                # Type = "playlist" for playlists & videos with chapters + flag, otherwise type = "video"
                # if item["type"] == "Playlist":
                #     url = f"https://www.youtube.com/playlist?list={item['id']}"
                #     type = "playlist"
                # else: 
                url = f"https://www.youtube.com/watch?v={item['id']}"
                type = "chapters" if self.split_chapters and self.video_has_chapters(url) else "video"
                    
                # Run the download in a separate thread
                executor.submit(self.download_item, url, type)
    
    def download_item(self, url, type):

        if not self.default_download_path:
            self.default_download_path = os.path.expanduser("~")

        cmd = [YTDLP_PATH, "--ffmpeg-location", FFMPEG_PATH]

        # Handle audio options
        if self.format in self.audio_formats:
            cmd.extend(["-x", "--audio-format", self.format])

        # Handle video options
        elif self.format in self.video_formats:
            cmd.extend(["--format", self.format])

        # Split chapters
        if self.split_chapters:
            cmd.append("--split-chapters")

        #! PLAYLIST dont work, disabled for now
        #TODO: 
        # 1) Chiedere su reddit,
        # 2) provare template diverso, magari senza %(playlist) folder e tutto in default
        # 3) cambiare logica: fa un'altra funzione che prende tutto da yt api e: O splitta in video con ch e video senza e usa 2 template per scaricarli in batch OPPURE scarica 1 per volta come type video/chapter
        # NEAREST (in use + exec): yt-dlp -x --audio-format "mp3" --split-chapters -o "chapter:%(playlist_title)s/%(title)s/%(section_number)s-%(section_title)s.%(ext)s" "https://www.youtube.com/playlist?list=PLED87UDh2Ybh7avvaAcNU3i4ybQ1pgLGk"
        # IDEAL (doesnt work): yt-dlp --no-download -x --audio-format "mp3" --split-chapters --print "%(playlist_title)s/%(title)s/%(chapters&%(section_number)s %(section_title)s|)s.%(ext)s" "https://www.youtube.com/playlist?list=PLED87UDh2Ybh7avvaAcNU3i4ybQ1pgLGk"
        if type == "playlist":      #! DONT WORK
            template = "chapter:%(playlist_title)s/%(title)s/%(section_number)s-%(section_title)s.%(ext)s"
            # Moves files with no chapters into the playlist folder, while deletes the unsplitted originals
            cmd.extend(["--exec", "if not exist \"%(playlist_title)s\%(title)s\" ( move \"%(filepath)\" \"%(playlist_title)s\" ) else ( del \"%(filepath)\" )"])
        elif type == "chapters":    #* WORKS
            template = "chapter:%(title)s/%(section_number)s-%(section_title)s.%(ext)s"
            # Deletes the original file (unsplitted)
            cmd.extend(["--exec", "del"]) #! "rm" for Linux/MacOS
        else:                       #* WORKS
            template = "%(title)s.%(ext)s"

        cmd.extend([
            "-P", self.default_download_path,
            "-o", template,
            url
        ])

        # Execute download command
        try:
            subprocess.run([arg for arg in cmd if arg], check=True)
            #TODO: MDSnackbar(text=f"Download completato per: {url}").open()
            #TODO: self.save_to_history(url, "Downloaded video/playlist")
        except subprocess.CalledProcessError as e:
            #TODO: MDSnackbar(text=f"Errore durante il download: {str(e)}").open()
            print("Download error")
    
    def video_has_chapters(self, url):
        """Checks if a video has chapters."""
        #! yt-dlp --no-download --ignore-no-formats-error --split-chapters --print "%(chapters)s" f"{url}"
        
        result = subprocess.run(
            [
                YTDLP_PATH, 
                "--no-download",
                "--ignore-no-formats-error",
                "--split-chapters",
                "--print", "%(chapters)s",
                url
            ],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        
        # Cmd failed
        if result.returncode != 0:
            return None
        else:
            output = result.stdout.strip() if result and result.stdout else None
            # No chapters
            if not output or output == "NA":
                return False
            # True if chapters > 0 else False
            else:
                chapters = ast.literal_eval(output)
                return bool(chapters)
        
    #endregion
    
    #region History
    
    # TODO: implement history save & consult
    
    # def save_to_history(self, video_id, title):
    #     history = self.load_history()
    #     history.append({"video_id": video_id, "title": title, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    #     with open(HISTORY_FILE, "w") as f:
    #         json.dump(history, f)
    
    # def load_history():
    #     # if not os.path.exists(HISTORY_FILE):
    #     #     return []
    #     with open(HISTORY_FILE, "r") as f:
    #         return json.load(f)

    #endregion
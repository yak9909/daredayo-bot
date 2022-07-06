import requests
import urllib.parse
from bs4 import BeautifulSoup
import json
import re
import subprocess


def get_redirect_url(url):
    resp = requests.head(url, allow_redirects=False)
    if 'Location' in resp.headers:
        return resp.headers['Location']
    return None


def url2id(video_url: str):
    video_id = None
    parsed = urllib.parse.urlparse(video_url)
    if parsed.netloc == "www.youtube.com":
        query = urllib.parse.parse_qs(parsed.query).get("v")
        if query:
            video_id = query[0]
        else:
            return None
    else:
        video_id = parsed.path.split("/")[-1]

    return video_id


def is_youtube(url):
    if re.match(r'^(https?://(youtu.be/|www.youtube.com/watch\?v=)[0-9,a-z,A-Z]*)', url):
        return True
    return False


class Video:
    def __init__(self, video):
        self.id = url2id(video) if is_youtube(video) else video
        if self.id is None:
            return None
        self.url = "https://youtu.be/" + self.id
        self.oembed_url = "https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v=" + self.id
        self.oembed_response = requests.get(self.oembed_url)

    def get_video_info(self):
        return self.oembed_response.json() if self.oembed_response.status_code == 200 else None
    
    def mp4_direct_link(self, ext, res, fps):
        direct_link = subprocess.check_output(f'yt-dlp -g "{self.url}" -f "[ext={ext}][height<={res}][fps<={fps}]"')
        return direct_link.decode("utf-8")
    
    def mp3_direct_link(self, ext):
        direct_link = subprocess.check_output(f'yt-dlp -g "{self.url}" -f "bestaudio[ext={ext}]"')
        return direct_link.decode("utf-8")

    def is_available(self):
        return self.oembed_response.status_code == 200

    def update_oembed(self):
        self.oembed_response = requests.get(self.oembed_url)
        return self.oembed_response


class Archive():
    def __init__(self, url):
        self.id = url2id(url)

        # アーカイブを取得
        self.url = self.get_archive()

        # アーカイブのURLからタイムスタンプを取得
        self.timestamp = self.get_timestamp()

        self.html = None

        self.video_name = None
        self.channel_name = None

    def is_available(func):
        def check_url(self, *args, **kwargs):
            if self.url:
                return func(self, *args, **kwargs)
        return check_url

    def using_html(func):
        def check_html(self, *args, **kwargs):
            if self.html is None:
                self.html = self.get_html()

            return func(self, *args, **kwargs)
        return check_html

    @is_available
    def get_info(self):
        video_title = self.get_video_title()
        # 不安定
        # channel_name = self.get_channel_name()
        return {"title": video_title, "author_name": None}

    @is_available
    def get_html(self):
        # アーカイブ(YouTube)の取得
        archive_url = f"http://archive.org/wayback/available?url=http://www.youtube.com/watch?v={self.id}&timestamp={self.timestamp}"
        r = requests.get(archive_url).json()
        return requests.get(r['archived_snapshots']['closest']['url']).text

    @is_available
    def get_timestamp(self):
        if self.url:
            timestamp = urllib.parse.urlparse(self.url).path.split("/")[2]#[:8]
            return timestamp
        return None

    @is_available
    @using_html
    def get_video_title(self):
        # HTMLタイトルから動画タイトルを抽出する
        vid_name = BeautifulSoup(self.html, features="lxml").title.text
        vid_name = " - ".join(vid_name.split(" - ")[:-1])
        return vid_name

    @is_available
    @using_html
    def get_channel_name(self):
        channel_name = re.findall(r'(?<=\+json">).*?(?=</script>)', self.html.replace('\n', ''))
        try:
            channel_url = json.loads(channel_name[0])["itemListElement"][0]["item"]["@id"]
            channel_name = json.loads(channel_name[0])["itemListElement"][0]["item"]["name"]
            return channel_name
        except IndexError:
            return None
        except Exception as e:
            print(e)
            return None

    def get_archive(self):
        archive_url = f"http://archive.org/wayback/available?url=http://www.youtube.com/watch?v={self.id}"
        r = requests.get(archive_url)
        if not r.json().get("archived_snapshots"):
            return None
        
        archive = f"https://web.archive.org/web/2oe_/http://wayback-fakeurl.archive.org/yt/{self.id}"
        return get_redirect_url(archive)
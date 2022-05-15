import requests
import urllib.parse
from bs4 import BeautifulSoup
import json
import re


def get_redirect_url(url):
    resp = requests.head(url, allow_redirects=False)
    if 'Location' in resp.headers:
        return resp.headers['Location']
    return None


def url2id(video_url: str):
    video_id = None
    parsed = urllib.parse.urlparse(video_url)
    if parsed.netloc == "www.youtube.com":
        video_id = urllib.parse.parse_qs(parsed.query)["v"][0]
    else:
        video_id = parsed.path.split("/")[-1]

    return video_id


def is_video_available(video_id):
    checker_url = "https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v="
    video_url = checker_url + video_id
    request = requests.get(video_url)

    return request.status_code == 200


class YouTubeArchive:
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
        timestamp = urllib.parse.urlparse(self.url).path.split("/")[2]
        return timestamp

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
        channel_url = json.loads(channel_name[0])["itemListElement"][0]["item"]["@id"]
        channel_name = json.loads(channel_name[0])["itemListElement"][0]["item"]["name"]
        return channel_name

    def get_archive(self):
        archive = f"https://web.archive.org/web/2oe_/http://wayback-fakeurl.archive.org/yt/{self.id}"
        return get_redirect_url(archive)
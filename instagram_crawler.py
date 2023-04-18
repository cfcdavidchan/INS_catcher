import requests
import re
from urllib.parse import urlencode
import json
import os
import time
import httpx
import asyncio

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))


class instagram_crawler:
    headers = {
        'Host': 'www.instagram.com',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.instagram.com/',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
    }
    base_url = 'https://www.instagram.com/graphql/query/?'

    def __init__(self, username: str, store_folder: str = SCRIPT_PATH, overwrite: bool = False, page_sleep_time: int = 1):
        self.username = username
        self.userid = self.get_userid(username)
        self.overwrite = overwrite
        self.page_sleep_time = page_sleep_time
        # create dir to save the pictures and videos
        self.username_dir, self.user_pic_path, self.user_video_path = self.create_userfolder(username=username, store_folder=store_folder)

    def get_userid(self, username):
        find_id_url = 'https://www.instagram.com/' + username
        response = requests.get(find_id_url, headers=self.headers)
        result = re.search('"profilePage_(.*?)"', response.text)
        return result[1]

    def get_params(self, userid, next_page_hash=''):
        param = {
            'query_hash': 'e769aa130647d2354c40ea6a439bfc08',
            'variables': '{"id":"' + str(userid) + '","first":12, "after":"' + next_page_hash + '"}',
        }
        return param

    def download_from_url(self, url: str, filename_path: str):
        if self.overwrite:
            if os.path.exists(filename_path): return  # exist the function to reject the overwrite action
        response = requests.get(url)
        open(f"{filename_path}", "wb").write(response.content)

    async def async_download_from_url(self, url: str, filename_path: str):
        if self.overwrite:
            if os.path.exists(filename_path): return  # exist the function to reject the overwrite action
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            open(f"{filename_path}", "wb").write(response.content)

    def create_userfolder(self, username: str, store_folder: str = SCRIPT_PATH):
        # all username path
        username_dir = os.path.join(store_folder, username)
        user_pic_path = os.path.join(username_dir, "picture")
        user_video_path = os.path.join(username_dir, "video")
        if not os.path.isdir(username_dir): os.makedirs(username_dir)
        if not os.path.isdir(user_pic_path): os.makedirs(user_pic_path)
        if not os.path.isdir(user_video_path): os.makedirs(user_video_path)
        return username_dir, user_pic_path, user_video_path

    def save_post_media(self, media_detail_json: json):
        media_id = media_detail_json.get('id')
        if media_detail_json.get('is_video'):  # storing video
            file_extension = "mp4"
            media_url = media_detail_json.get('video_url')
            media_store_path = os.path.join(self.user_video_path, f"{media_id}.{file_extension}")
        else:  # storing picture
            file_extension = "jpeg"
            media_url = media_detail_json.get('display_url')
            media_store_path = os.path.join(self.user_pic_path, f"{media_id}.{file_extension}")
        self.download_from_url(url=media_url, filename_path=media_store_path)

    async def async_save_post_media(self, media_detail_json: json):
        media_id = media_detail_json.get('id')
        if media_detail_json.get('is_video'):  # storing video
            file_extension = "mp4"
            media_url = media_detail_json.get('video_url')
            media_store_path = os.path.join(self.user_video_path, f"{media_id}.{file_extension}")
        else:  # storing picture
            file_extension = "jpeg"
            media_url = media_detail_json.get('display_url')
            media_store_path = os.path.join(self.user_pic_path, f"{media_id}.{file_extension}")
        await self.async_download_from_url(url=media_url, filename_path=media_store_path)

    def parse_crawled_json(self, crawled_json: json) -> str:
        #  Retrieving the page detail
        page_data = crawled_json.get('data').get('user').get('edge_owner_to_timeline_media')
        posts = page_data.get('edges')
        for post in posts:
            post_detail = post.get('node')
            # multiple videos or pictures in single post
            if post_detail.get('edge_sidecar_to_children'):
                post_media_list = post_detail.get('edge_sidecar_to_children').get('edges')
                for media in post_media_list:
                    self.save_post_media(media.get('node'))
            else:
                self.save_post_media(post_detail)
        page_info = page_data.get('page_info')
        if page_info.get('has_next_page'):
            next_page_hash = page_info.get('end_cursor')
            return next_page_hash
        return ""

    async def async_parse_crawled_json(self, crawled_json: json) -> str:
        #  Retrieving the page detail
        page_data = crawled_json.get('data').get('user').get('edge_owner_to_timeline_media')
        posts = page_data.get('edges')
        for post in posts:
            post_detail = post.get('node')
            # multiple videos or pictures in single post
            if post_detail.get('edge_sidecar_to_children'):
                post_media_list = post_detail.get('edge_sidecar_to_children').get('edges')
                for media in post_media_list:
                    await self.async_save_post_media(media.get('node'))
            else:
                await self.async_save_post_media(post_detail)
        page_info = page_data.get('page_info')
        if page_info.get('has_next_page'):
            next_page_hash = page_info.get('end_cursor')
            return next_page_hash
        return ""

    def request_instagram_url(self, url: str, retry: int = 5) -> json:
        response = requests.get(url=url, headers=self.headers)
        if response.status_code != 200:
            if retry > 0:
                return self.request_instagram_url(url=url)
            else:
                raise RuntimeError(f"Fail to request {url} after multi reties")
        return json.loads(response.text)

    async def async_request_instagram_url(self, url: str, retry: int = 5) -> json:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
        if response.status_code != 200:
            if retry > 0:
                return await self.async_request_instagram_url(url=url)
            else:
                raise RuntimeError(f"Fail to request {url} after multi reties")
        return json.loads(response.text)

    def main(self):
        next_page_hash = ''
        count = 0
        while True:
            url = self.base_url + urlencode(self.get_params(self.userid, next_page_hash=next_page_hash))
            print(f"Crawling {url}")
            response_json = self.request_instagram_url(url=url)
            next_page_hash = self.parse_crawled_json(response_json)
            count += 1
            if not next_page_hash:
                break
            time.sleep(self.page_sleep_time)

    async def async_main(self):
        next_page_hash = ''
        count = 0
        while True:
            url = self.base_url + urlencode(self.get_params(self.userid, next_page_hash=next_page_hash))
            print(f"Crawling {url}")
            response_json = await self.async_request_instagram_url(url=url)
            next_page_hash = await self.async_parse_crawled_json(response_json)
            count += 1
            if not next_page_hash:
                break
            await asyncio.sleep(self.page_sleep_time)


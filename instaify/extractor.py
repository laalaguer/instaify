import os
from pathlib import Path
from datetime import datetime
from .utils import (
    _scan_dir
)

class Extractor():
    def __init__(self, path: str):
        self.path = os.path.abspath(Path(path))
    
    def run(self):
        pass


class IGDownloaderExtractor(Extractor):
    
    def run(self):
        files, _ = _scan_dir(Path(self.path))

        pics = []
        for f in files:
            _path = str(f)
            _suffix = f.suffix
            stem_parts = f.stem.split('_')
            user_handle = stem_parts[0]
            post_timestamp = stem_parts[1]

            dt_object = datetime.fromtimestamp(int(post_timestamp))
            post_date = dt_object.strftime('%Y-%m-%d')
            post_time = dt_object.strftime('%H:%M:%S')

            pics.append({
                'user_handle': user_handle,
                'timestamp': post_timestamp,
                'date': post_date,
                'time': post_time,
                'suffix': _suffix,
                'path': _path
            })
        

        users = {} # group pics by handle and distinct timestamp (post)
        for pic in pics:
            handle = pic['user_handle']
            t = pic['timestamp']

            if not (handle in users):
                users[handle] = {}
            if not (t in users[handle]):
                users[handle][t] = []

            users[handle][t].append(pic)


        pages = []
        for user_key in users:
            page = {
                'page_id': user_key,
                'title': user_key,
                'subtitle': user_key,
                'posts': []
            }

            tmp_posts = []
            for time_key in users[user_key]:
                post = {
                    'timestamp': str(time_key),
                    'title': users[user_key][time_key][0]['date'],
                    'subtitle': users[user_key][time_key][0]['time'],
                    'other': '',
                    'medias': [{'location': x['path'] } for x in users[user_key][time_key]]
                }

                tmp_posts.append(post)
            
            tmp_posts = sorted(tmp_posts, key=lambda element: element['timestamp'], reverse=True)

            page['posts'] = tmp_posts
            pages.append(page)

        return pages


class IGDownloader():
    def __init__(self, ig_downloader_folder: str):
        self.ig_downloader_folder = ig_downloader_folder
    
    def run(self):
        _, dirs = _scan_dir(self.ig_downloader_folder)

        for each_dir in dirs:
            ige = IGDownloaderExtractor(each_dir)
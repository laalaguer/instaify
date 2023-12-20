import os
from pathlib import Path
from datetime import datetime
from .utils import (
    _scan_dir
)


### Interface ###
class Extractor():
    def __init__(self, path: str):
        self.path = os.path.abspath(Path(path))
    
    def run(self):
        pass


### Extractor for IG Downloader
### It only provides a dir of pics / videos
### We need to extract structured info from pics and video names.
class IGDownloaderExtractor(Extractor):
    
    def run(self):
        files, _ = _scan_dir(Path(self.path))

        pics = []
        for f in files:
            _path = str(f)
            _suffix = f.suffix
            stem_parts = f.stem.split('_')
            user_handle = stem_parts[0]
            post_timestamp = None

            for item in stem_parts[1:]:
                try:
                    post_timestamp = int(item)
                    if post_timestamp > 2147483647:
                        raise Exception('breached max value')
                    if post_timestamp < 631123200:
                        raise Exception('lower than 1990.01.01')
                    break
                except:
                    continue

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

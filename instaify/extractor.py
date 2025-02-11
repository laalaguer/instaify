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

def is_timestamp(s: str):
    ''' Check if a number is a suitable timestamp value '''
    try:
        post_timestamp = int(s)
        if post_timestamp > 2147483647:
            raise Exception('breached max value')
        # if post_timestamp < 631123200:
        #     raise Exception('lower than 1990.01.01')
    except:
        return False
    
    return True

def find_timestamp(s: str) -> str:
    parts = s.split('_')
    for part in parts:
        if is_timestamp(part):
            return part
    raise Exception(f'No suitable timestamp found in the string {s}, cannot extract timestamp.')

def extract_user_handle(s: str, timestamp: str) -> str:
    timestamp_index = s.find(timestamp)
    if timestamp_index != -1:
        handle = s[:timestamp_index].rstrip('_')
        return handle
    else:
        raise Exception(f'No timestamp found in the string {s}, cannot extract user handle.')

### Extractor for <IG Downloader>
### for each given folder (a blog) that contains videos and pics,
### We create structured info from pics and video names.
class IGDownloaderExtractor(Extractor):
    
    def run(self):
        ''' Creates structured information from a given blog folder. '''
        files, _ = _scan_dir(Path(self.path))

        pics = []
        for f in files:
            _path = str(f)
            _suffix = f.suffix
            
            # Post timestamp is ...?
            post_timestamp = None # int type

            # Extract timestamp from the file name
            post_timestamp_str = find_timestamp(f.stem)
            post_timestamp = int(post_timestamp_str)

            # Extract user handle from the file name
            user_handle = extract_user_handle(f.stem, post_timestamp_str)

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

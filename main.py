from typing import Iterable, Set, Dict, List, Callable, Tuple, Union
from pathlib import Path
import os
import sys
import json
from datetime import datetime

# Supported types of images and videos
IMG_SUFFIX = ['.bmp', '.gif', '.jpg', '.jpeg', '.png', '.webp', '.avif', '.heic']
VID_SUFFIX = ['.mp4', '.webm', '.hevc']

### OS Functions ###

def get_full_parent(p: Path) -> str:
    '''
    Return the full path of parent of this file or folder.

    Parameters
    ----------
    p : Path
        The path in question

    Returns
    -------
    str
        the full path  or ''
    '''
    try:
        return str(os.path.dirname(p))
    except:
        return ''
    
def _exists(path: str) -> bool:
    return Path(path).exists()

def open_and_read(path: str) -> str:
    content = None
    if _exists(path):
        with open(path, 'r') as f:
            content = f.read()
    else:
        raise Exception(f"file {path} doesn't exist")
    return content


def _join_paths(paths: List[Path]) -> Path:
    return os.path.join(*paths)


def _get_unconflict_path(parent_folder, file_name: str, file_suffix: str):
    try_name = _join_paths([os.path.abspath(Path(parent_folder)), file_name + file_suffix])
    if not _exists(try_name):
        return try_name
    else:
        idx = 1
        while True:
            try_name = _join_paths([os.path.abspath(Path(parent_folder)), file_name + '_' + str(idx) + file_suffix])
            if not _exists(try_name):
                return try_name
            else:
                idx += 1


def _scan_dir(current: Path) -> Tuple[List[Path], List[Path]]:
    ''' Scan the dir, get immediate children. Classify as list of files and list of dirs '''
    files_list = []
    dirs_list = []
    
    # If encounter "permission" error (can't list the dir),
    # jump over it.
    try:
        for x in current.iterdir():
            if x.is_file():
                files_list.append(x)
            elif x.is_dir():
                dirs_list.append(x)
            else:
                print('passed')
                pass
    except Exception as e:
        print(f'scan error: {e}')

    return files_list, dirs_list


def filter_by_suffixes(nodes: Set[Path], include: List[str]=None) -> Set[Path]:
    ''' Filter nodes with desired suffixes
        Note: '.mp4' and '.MP4' are treated equally.
    '''
    if include == None:
        raise Exception('Fill out the suffixes you want')

    _include = [x.lower() for x in include]
    return {x for x in nodes if (not x.is_dir() and (x.suffix.lower() in _include))}


def match_suffixes(p: Union[Path ,str], include: List[str]=None) -> bool:
    return len(filter_by_suffixes([Path(p)], include)) > 0


### Renderer ###

def render_img(template: str, location: str, magic_word: str='{{src}}') -> str:
    '''Render an image according to the location of img and the template string

    Args:
        location (str): location of the img
        template (str): template string.
        magic_word (str): the old word to be replaced.
    '''
    return template.replace(magic_word, location)


def render_vid(template: str, location: str, magic_word: str='{{src}}'):
    '''Render a video according to the location of img and the template string

    Args:
        location (str): location of the video
        template (str): template string.
        magic_word (str): the old word to be replaced.
    '''
    return template.replace(magic_word, location)


def render_post_info(
        template: str, 
        title: str, subtitle: str, other: str, 
        m_1: None="{{title}}", m_2: None="{{subtitle}}", m_3: None="{{other}}"
    ):
    '''Render a post_info

    Args:
        template (str): the template content
        title (str): title
        subtitle (str): subtitle
        other (str): other text
        m_1 (None, optional): magic word in template for title. Defaults to "{{title}}".
        m_2 (None, optional): magic word in template for subtitle. Defaults to "{{subtitle}}".
        m_3 (None, optional): magic word in template for other. Defaults to "{{other}}".
    '''

    return template.replace(m_1, title).replace(m_2, subtitle).replace(m_3, other)


def render_post_medias(template: str, medias: List[str], magic_word: str='{{content}}'):
    m = ''.join(medias)
    return template.replace(magic_word, m)


def render_post(template: str, post_info: str, medias: str, magic_word: str='{{content}}'):
    ''' Render a post with post_info and medias '''
    content = post_info + medias
    return template.replace(magic_word, content)


def render_section(template: str, content: str, magic_word: str='{{content}}'):
    return template.replace(magic_word, content)


def render_headline(
        template: str,
        title: str, subtitle: str,
        m_1: None="{{title}}", m_2: None="{{subtitle}}"
    ):
    return template.replace(m_1, title).replace(m_2, subtitle)


def render_page(template: str, content: str, magic_word: str='{{content}}'):
    return template.replace(magic_word, content)


class Renderer():
    def __init__(self, documents: List, output_dir: str="", output_relative: bool=False, search_dirs: List[str]=None):
        '''A General renderer

        Args:
            documents (List): several pages (json info)
            output_dir (str, optional): under which dir shall the html generated. Defaults to "".
            output_relative (bool, optional): shall that the resource links in html files, be translated to relative to html files itself.
            search_dirs (List[str], optional): search for medias inside the dirs, default search in current working dir and in output_dir.
        '''
        self.documents = documents
        self.output_dir = os.path.abspath(Path(output_dir)) # turn to abs path
        self.output_relative = output_relative # shall be relative render of contents of htmls or not?
        self.toc_filename = _get_unconflict_path(self.output_dir, "index", ".html")
        self.search_dirs = ['./', self.output_dir]
        if search_dirs != None:
            for each in search_dirs:
                self.search_dirs.append(os.path.abspath(each))

    def render_single(self, document: dict):
        ''' Inherit and override this function!
        '''
        pass

    def run(self):

        # Create an array of rendered pages.
        rendered = [
            self.render_single(document) for document in self.documents
        ]

        # Create an array of locations where to store the rendered pages.
        destinations = [
            _get_unconflict_path(
                self.output_dir,
                document.get('page_id', 'page'),
                ".html"
            )
            for document in self.documents
        ]
        
        # Array length must match
        assert len(destinations) == len(rendered) == len(self.documents)

        for destination, content in zip(destinations, rendered):
            with open(destination, 'w') as f:
                f.write(content)


        # Create a table of content file (toc file) as index.html
        tags = []
        for destination in destinations:
            if not self.output_relative:
                url_location = destination
            else:
                url_location = os.path.relpath(destination, self.output_dir)
            
            tags.append(
                f'<a href="{url_location}">{url_location}</a>'
            )
        
        index_content = f'''
        <html>
            <head>
                <meta charset="utf-8">
            </head>
            <body>
                {'<br/>'.join(tags)}
            </body>
        </html>
        '''

        with open(self.toc_filename, 'w') as f:
            f.write(index_content)


class InstagramRenderer(Renderer):

    template_folder = 'instagram_template/'
    headline_template = open_and_read(template_folder + 't_headline.html')
    section_template = open_and_read(template_folder + 't_section.html')
    post_info_template = open_and_read(template_folder + 't_post_info.html')
    img_template = open_and_read(template_folder + 't_post_img.html')
    vid_template = open_and_read(template_folder + 't_post_vid.html')
    post_medias_template = open_and_read(template_folder + 't_post_medias.html')
    post_template = open_and_read(template_folder + 't_post.html')
    page_template = open_and_read(template_folder + 't_page.html')

    def render_single(self, document: dict):
        headline = render_headline(
            self.headline_template,
            document['title'],
            document['subtitle']
        )

        headline_section = render_section(
            self.section_template,
            headline
        )

        posts = []
        for p in document['posts']:
            post_info = render_post_info(
                self.post_info_template,
                p['title'],
                p['subtitle'],
                p['other']
            )

            post_medias = []
            for media in p['medias']:

                media_path = media['location'] # Can be abs path, or non-abs path

                media_abs_path = None
                if os.path.isabs(media_path): # The media path is abs path itself
                    if not _exists(media_path):
                        raise Exception(f'media: {media_path} not found!')
                    else:
                        media_abs_path = media_path
                else:
                    # Go for a search until find one
                    try_paths = [ _join_paths([dir, media_path]) for dir in self.search_dirs ]
                    for each in try_paths:
                        if _exists(each):
                            media_abs_path = each
                            break
                    if media_abs_path == None:
                        raise Exception(f"Couldn't find proper media: {media_path} in \n {self.search_dirs}, tried \n {try_paths}")
                    
                
                media_output_path = None
                if self.output_relative:
                    media_output_path = os.path.relpath(media_abs_path, self.output_dir)
                else:
                    media_output_path = media_abs_path

                if match_suffixes(media_output_path, IMG_SUFFIX):
                    post_medias.append(render_img(self.img_template, media_output_path))
                elif match_suffixes(media_output_path, VID_SUFFIX):
                    post_medias.append(render_vid(self.vid_template, media_output_path))
                else:
                    post_medias.append(f"<p>Unkown type: {media['location']}</p>")
                

            post_medias = render_post_medias(
                self.post_medias_template,
                post_medias
            )

            posts.append(render_post(
                self.post_template,
                post_info,
                post_medias
            ))
        
        posts_sections = []
        for p in posts:
            posts_sections.append(render_section(
                self.section_template,
                p
            ))

        return render_page(
            self.page_template, 
            headline_section + ''.join(posts_sections),
        )


# class Extractor():
#     def __init__(self, path: str):
#         self.path = os.path.abspath(Path(path))
    
#     def run(self):
#         pass


# class IGDownloaderExtractor(Extractor):
    
#     def run(self):
#         files, _ = _scan_dir(Path(self.path))

#         pics = []
#         for f in files:
#             _path = str(f)
#             _suffix = f.suffix
#             stem_parts = f.stem.split('_')
#             user_handle = stem_parts[0]
#             post_timestamp = stem_parts[1]

#             dt_object = datetime.fromtimestamp(int(post_timestamp))
#             post_date = dt_object.strftime('%Y-%m-%d')
#             post_time = dt_object.strftime('%H:%M:%S')

#             pics.append({
#                 'user_handle': user_handle,
#                 'timestamp': post_timestamp,
#                 'date': post_date,
#                 'time': post_time,
#                 'suffix': _suffix,
#                 'path': _path
#             })
        

#         users = {} # group pics by handle and distinct timestamp (post)
#         for pic in pics:
#             handle = pic['user_handle']
#             t = pic['timestamp']

#             if not (handle in users):
#                 users[handle] = {}
#             if not (t in users[handle]):
#                 users[handle][t] = []

#             users[handle][t].append(pic)


#         pages = []
#         for user_key in users:
#             page = {
#                 'page_id': user_key,
#                 'title': user_key,
#                 'subtitle': user_key,
#                 'posts': []
#             }

#             tmp_posts = []
#             for time_key in users[user_key]:
#                 post = {
#                     'timestamp': str(time_key),
#                     'title': users[user_key][time_key][0]['date'],
#                     'subtitle': users[user_key][time_key][0]['time'],
#                     'other': '',
#                     'medias': [{'location': x['path'] } for x in users[user_key][time_key]]
#                 }

#                 tmp_posts.append(post)
            
#             tmp_posts = sorted(tmp_posts, key=lambda element: element['timestamp'], reverse=True)

#             page['posts'] = tmp_posts
#             pages.append(page)

#         return pages


# class IGDownloader():
#     def __init__(self, ig_downloader_folder: str):
#         self.ig_downloader_folder = ig_downloader_folder
    
#     def run(self):
#         _, dirs = _scan_dir(self.ig_downloader_folder)

#         for each_dir in dirs:
#             ige = IGDownloaderExtractor(each_dir)
    

if __name__ == "__main__":

    json_filename = sys.argv[1]
    with open(json_filename, 'r') as f:
        pages = json.load(f)
        ir = InstagramRenderer(pages, './example', True, ['./example'])
        ir.run()
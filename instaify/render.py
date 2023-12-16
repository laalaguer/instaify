from typing import List
import os
from pathlib import Path
from .utils import (
    _exists,
    _join_paths,
    get_unconflict_path,
    open_lib_resource,
    match_suffixes,
    IMG_SUFFIX,
    VID_SUFFIX
)


### Functions ###
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


### Interface ###

class Renderer():
    def __init__(self, documents: List, output_dir: str="", output_relative: bool=False, search_dirs: List[str]=None, create_toc:bool=False):
        '''A General renderer

        Args:
            documents (List): several pages (json info)
            output_dir (str, optional): under which dir shall the html generated. Defaults to "".
            output_relative (bool, optional): shall that the resource links in html files, be translated to relative to html files itself.
            search_dirs (List[str], optional): search for medias inside the dirs, default search in current working dir and in output_dir.
            create_index (bool, optional): create index.html as table of contents or not.
        '''
        self.documents = documents
        self.output_dir = os.path.abspath(Path(output_dir)) # turn to abs path
        self.output_relative = output_relative # shall be relative render of contents of htmls or not?
        self.search_dirs = ['./', self.output_dir]
        if search_dirs != None:
            for each in search_dirs:
                self.search_dirs.append(os.path.abspath(each))
        self.toc_filename = get_unconflict_path(self.output_dir, "index", ".html")
        self.create_toc = create_toc
        

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
            get_unconflict_path(
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

        if self.create_toc:
            with open(self.toc_filename, 'w') as f:
                f.write(index_content)


class InstagramRenderer(Renderer):
    ''' Instagram-like renderer
    '''

    templates = 'instaify.template'
    headline_template = open_lib_resource(templates, 't_headline.html')
    section_template = open_lib_resource(templates, 't_section.html')
    post_info_template = open_lib_resource(templates, 't_post_info.html')
    img_template = open_lib_resource(templates, 't_post_img.html')
    vid_template = open_lib_resource(templates, 't_post_vid.html')
    post_medias_template = open_lib_resource(templates, 't_post_medias.html')
    post_template = open_lib_resource(templates, 't_post.html')
    page_template = open_lib_resource(templates, 't_page.html')

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

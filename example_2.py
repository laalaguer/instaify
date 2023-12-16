''' 
    Example:

    If you have a IG Downloader Chrome plugin and have downloaded some images,

    Simply run this script with the path to the folder to generate HTML pages.
'''

import sys
import os
from pathlib import Path
from instaify.utils import _scan_dir
from instaify.render import InstagramRenderer
from instaify.extractor import IGDownloaderExtractor


class IGDownloaderGenerator():
    def __init__(self, src_folder: str):
        '''
        Args:
            src_folder (str): the source folder that contains your IG Downloader pic folders.
        '''
        self.src_folder = os.path.abspath(Path(src_folder))
    
    def run(self):
        # Looking for dirs
        _, dirs = _scan_dir(Path(self.src_folder))
        
        # Generate intermediary my_pages according to dirs
        my_pages = []
        for each_dir in dirs:
            ige = IGDownloaderExtractor(each_dir)
            pages = ige.run()
            my_pages.append(pages)
        
        # Generate HTMLs according to my_pages
        for pages in my_pages:
            ir = InstagramRenderer(pages, self.src_folder, True, [self.src_folder], False)
            ir.run()


if __name__ == "__main__":

    IG_DOWNLOAD_FOLDER = sys.argv[1]
    object = IGDownloaderGenerator(IG_DOWNLOAD_FOLDER)
    object.run()
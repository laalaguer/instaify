from typing import Iterable, Set, Dict, List, Callable, Tuple, Union
from pathlib import Path
import os
from datetime import datetime
import importlib.resources


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

def open_lib_resource(path: str) -> str:
    content = None
    if _exists(path):
        with open(path, 'r') as f:
            content = f.read()
    else:
        raise Exception(f"file {path} doesn't exist")
    return content


def open_lib_resource(package_name: str, file_path: str) -> str:
    ''' This is the way to load package included static files '''
    content = None
    with importlib.resources.open_text(package_name, file_path) as f:
        content = f.read()
        return content


def _join_paths(paths: List[Path]) -> Path:
    return os.path.join(*paths)

def get_unconflict_path(parent_folder, file_name: str, file_suffix: str):
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

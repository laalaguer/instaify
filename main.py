import sys
import json
from instaify.render import InstagramRenderer

if __name__ == "__main__":

    json_filename = sys.argv[1]
    with open(json_filename, 'r') as f:
        pages = json.load(f)
        ir = InstagramRenderer(pages, './example', True, ['./example'])
        ir.run()
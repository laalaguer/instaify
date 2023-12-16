''' 
    Example:

    Generate HTML pages according to the json and images in the `example` folder.
'''
import json
from instaify.render import InstagramRenderer

if __name__ == "__main__":

    json_filename = './example/example.json'
    with open(json_filename, 'r') as f:
        pages = json.load(f)
        ir = InstagramRenderer(pages, './example', True, ['./example'], True)
        ir.run()
### Extractor (Instagram, Weibo, etc)

1. Accepts a string `Path` as the sole input (dir or a file, or a URL?).
2. Overrides the `run()` function.
3. Output of `run()` is a JSON.

with following output (some fileds can be empty):

```javascript
[
    {
        'user_name': '',
        'user_id': '',

        'display_name': '',
        'display_intro': '',

        'posts': [
            {
                'timestamp': '',
                'text_1': '',
                'text_2': '',
                'text_3': '',
                'medias': [
                    {
                        'location': '', // maybe a remote web location or a local file location
                        'content_type': ''
                    }
                ]
            },
            {
                ... second post
            }
        ]
    },
    {
        ... the second user
    }
]
```
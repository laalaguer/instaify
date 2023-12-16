# Instaify - Instagram Like Homepage Renderer

### Input JSON

```javascript
[
    {
        'page_id': '',
        'title': '',
        'subtitle': '',
        'posts': [
            {
                'title': '',
                'subtitle': '',
                'other': '',
                'medias': [
                    {
                        'location': '', // local file location.
                    }
                ]
            },
            { 
                ... second post
            }
        ]
    },
    {
        ... the second html page
    }
]
```


### Renderer (Turn above JSON into HTML page/pages)

1. Each page will be turned into a html.
2. Will use `page_id.html` to distinct pages saved on the disk (add a random number if conflict occurs).
3. `index.html` will be created as "table of contents" (add a random number of conflict occurs).
4. You can assign a name to as the alternative to `index.html`
# Instaify - Instagram Like Homepage Renderer

### Input JSON

```javascript
[
    {
        "page_id": "",
        "title": "",
        "subtitle": "",
        "posts": [
            {
                "title": "",
                "subtitle": "",
                "other": "",
                "medias": [
                    {
                        "location": "", // local file location.
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


### Output (JSON -> HTML)

1. Each page will be turned into a html.
2. Will use `page_id.html` to distinct pages saved on the disk.
3. `index.html` will be created as "table of contents".
4. Add a random number to file name if conflict occurs.
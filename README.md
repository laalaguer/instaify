# Instaify - Instagram Like HTML Renderer

<img src="./README-1.jpg" width="300"></img>


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


### Render (JSON -> HTML)

1. Each page i turned into a signle html.
3. `index.html` is created as "table of contents".
4. A random number is added to file name if conflict occurs.
#!/usr/bin/python

from __future__ import print_function
import twitter
import colorgram
import urllib, json
from PIL import Image, ImageDraw
import time

print("+-------------------------+")
print("|   UnsplashGradientBot   |")
print("| Written by @jonaskohl13 |")
print("+-------------------------+")
print("")

def ColorHex(rgb):
    r,g,b = rgb
    return "#" + hex(r)[2:] + hex(g)[2:] + hex(b)[2:]

def LerpColor(c1,c2,t):
    return (c1[0]+(c2[0]-c1[0])*t,c1[1]+(c2[1]-c1[1])*t,c1[2]+(c2[2]-c1[2])*t)

def gradient(img, color_a, color_b):
    draw = ImageDraw.Draw(img)

    colors = []
    for i in range(512):
        colors.append(LerpColor(color_a, color_b, float(i) / float(512)))

    for i in range(512):
        r,g,b = colors[i]
        draw.line((0,i,512,i), fill=(int(r),int(g),int(b)))

tw_api = twitter.Api(consumer_key="YOUR_CONSUMER_KEY",
                  consumer_secret="YOUR_CONSUMER_SECRET",
                  access_token_key="YOUR_ACCESS_TOKEN_KEY",
                  access_token_secret="YOUR_ACCESS_TOKEN_SECRET")

us_client_id = "YOUR_CLIENT_ID"

us_photo_random = "https://api.unsplash.com/photos/random/?client_id=" + us_client_id


disallowed_tags = [
    "person",
    "woman",
    "women",
    "man",
    "men",
    "human"
]

def download_data():
    global us_photo_random
    print("Downloading data...", end="")
    response = urllib.urlopen(us_photo_random)
    data = json.loads(response.read())
    print(" Done!")
    return data

def post():
    data = None
    tags_invalid = True
    while tags_invalid:
        data = download_data()
        tags_invalid = False
        if "alt_description" in data and data["alt_description"] is not None:
            keywords = data["alt_description"].split(" ")
            for kw in disallowed_tags:
                if kw in keywords:
                    tags_invalid = True
                    print("Tags invalid!")
                    break

    im_url = data["urls"]["small"]

    print("Downloading image...", end="")
    urllib.urlretrieve(im_url, "unsplash-cache.jpg")
    print(" Done!")

    print("Extracting colors...", end="")
    colors = colorgram.extract("unsplash-cache.jpg", 2)
    print(" Done!")

    grad_img = Image.new("RGB", (512,512), "#FFFFFF")

    print("Generating gradient...", end="")
    gradient(grad_img, colors[0].rgb, colors[1].rgb)
    print(" Done!")

    print("Saving gradient image...", end="")
    grad_img.save("gradient-cache.png", "PNG")
    print(" Done!")

    tweet_text = "Image by "

    if "name" in data["user"] and data["user"]["name"] is not None:
        tweet_text += data["user"]["name"]
    else:
        tweet_text += data["user"]["username"]

    if "twitter_username" in data["user"] and data["user"]["twitter_username"] is not None:
        tweet_text += " (@" + data["user"]["twitter_username"] + ")"

    tweet_text += "\n" + data["links"]["html"]
    tweet_text += "\n\nColors: " + ColorHex(colors[0].rgb) + " and " + ColorHex(colors[1].rgb)
    tweet_text += "\n\n#unsplashgradientbot"

    # post tweet
    print("Publishing Tweet...", end="")
    tw_api.PostUpdate(tweet_text, ["gradient-cache.png", "unsplash-cache.jpg"])
    print(" Done!")

    print("<< Goodbye! >>")


post()


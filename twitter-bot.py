# -*- coding: utf-8 -*-
from __future__ import print_function
from PIL import Image, ImageDraw, ImageFont, ImageColor
from io import BytesIO
import sys
import os
import get_data
import requests


def check_length_greater(image_width, text_string, font_size):
    if len(text_string) * font_size > image_width:
        return True
    return False


def split_text(image_width, text_string, font_size):
    final_strings = []
    str_len_in_pixels = 0
    substring = ""
    for char in text_string:
        str_len_in_pixels += font_size * 0.65
        substring += char
        if str_len_in_pixels > image_width:
            final_strings.append(substring)
            substring = ""
            str_len_in_pixels = 0
    if substring != "":
        final_strings.append(substring)
    return final_strings


def wrap_words(lines):
    pos = 0
    fixed_lines = lines
    for line in lines:
        if pos < len(lines) - 1 and line[-1] != " " and lines[pos + 1][
                0] != " ":
            words_line1 = lines[pos].split(" ")
            words_line2 = lines[pos + 1].split(" ")

            whole_word = words_line1[-1] + words_line2[0]
            words_line2[0] = whole_word

            del words_line1[-1]
            words_line1 = " ".join(words_line1)
            words_line2 = " ".join(words_line2)

            fixed_lines[pos] = words_line1
            fixed_lines[pos + 1] = words_line2
        pos += 1

    # print fixed_lines

    return fixed_lines


# -Create base image for tweet
# -Returns a 2-tuple whose first element is the base image
#  and second element is the starting coordinate
#  of the twitter profile picture


def get_base():
    im = Image.open("templates/base.jpg").convert('RGBA')
    return (im, (30, 20))


# make a transparent overlay for the meme text and draw the text on it
def draw_text(base, text_string, pos_x, pos_y, font_size, font='Arial.ttf'):
    txt = Image.new('RGBA', base.size, (0, 0, 0, 0))
    fnt = ImageFont.truetype('Pillow/Tests/fonts/' + font, font_size)
    # get a drawing context
    d = ImageDraw.Draw(txt)

    if check_length_greater(base.width, text_string, font_size):
        split = split_text(base.width, text_string, font_size)
        split = wrap_words(split)
        height_offset = 0
        for substring in split:
            d.text(
                (pos_x, pos_y + height_offset),
                substring,
                font=fnt,
                fill=(0, 0, 0, 255))
            height_offset += font_size

    else:
        d.text((pos_x, pos_y), text_string, font=fnt, fill=(0, 0, 0, 255))

    return Image.alpha_composite(base, txt)


def draw_display_name(base, name):
    return draw_text(base, name, 90, 25, 15, "ariblk.ttf")


def draw_twitter_handle(base, handle):
    return draw_text(base, handle, 90, 45, 15)


def draw_tweet_text(base, text):
    if len(text) > 140:
        text = text[:139]
    return draw_text(base, text, 30, 80, 25)


def resize_image(image, baseheight):
    # wpercent = (basewidth / float(image.size[0]))
    # hsize = int((float(image.size[1]) * float(wpercent)))
    hpercent = (baseheight / float(image.size[1]))
    wsize = int((float(image.size[0]) * float(hpercent)))
    return image.resize((wsize, baseheight), Image.ANTIALIAS)


def update_memes(titles_subreddit, images_subreddit):
    get_data.get_titles(titles_subreddit, 1000)
    get_data.get_images(images_subreddit, 1000)


def draw_meme_random(titles_subreddit, images_subreddit):
    pic_url = get_data.choose_image("pics/%s_pics.txt" % (images_subreddit))
    if pic_url == 'error':
        print(
            "No data found\nUse python mem.py generate <subreddit-to-get-titles-from> <subreddit-to-get-images-from> to update\n"
        )
        return None
    response = requests.get(pic_url)
    meme_pic = Image.open(BytesIO(response.content)).convert('RGBA')
    meme_pic = resize_image(meme_pic, 500)

    markov_table = markov.generate_table(
        ["text/%s_titles.txt" % (titles_subreddit)])
    text = markov.generate_markov_text(15, 1, markov_table)[0].encode('utf-8')

    base = get_base(meme_pic, text, 20, 5)
    base_pic = base[0]
    coords = base[1]
    out = draw_text(base_pic, text, 10, 10, 20)
    # get a drawing context
    background = out
    foreground = meme_pic
    background.paste(foreground, coords, foreground)
    background.show()

    return background


def compose_tweet(user_display_name, user_twitter_handle, user_icon,
                  tweet_text):
    base = get_base()[0]
    coords = get_base()[1]

    response = requests.get(user_icon)
    profile_icon = Image.open(BytesIO(response.content)).convert('RGBA')
    profile_icon = resize_image(profile_icon, 50)
    base.paste(profile_icon, coords, profile_icon)
    tweet = draw_display_name(base, user_display_name)
    tweet = draw_twitter_handle(tweet, '@' + user_twitter_handle)
    tweet = draw_tweet_text(tweet, tweet_text)
    return tweet


args = sys.argv
if len(args) == 2:
    tweet = get_data.get_tweet(args[1])
    if tweet == None:
        exit(-1)

    name = tweet['name']
    handle = tweet['handle']
    icon = tweet['pic_url']
    text = tweet['tweet_text']

    out = compose_tweet(name, handle, icon, text)
    out.show()
    ans = raw_input("Save this tweet? [Y/N] ").lower()
    while (ans != 'y' and ans != 'n'):
        ans = raw_input("Save this tweet? [Y/N] ")
    if ans == 'y':
        filename = raw_input("Filename: ")
        output_dir = "out_tweets/" + handle + "/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        filename = output_dir + filename + '.png'
        out.save(filename, "PNG")
        print("Saved %s" % (filename))
else:
    print("Usage: \npython twitter-bot.py <user's-twitter-screen-name> \n")

# handle = "realdonaldtrump"
# tweet = get_data.get_tweet(handle)
#
# name = tweet['name']
# handle = tweet['handle']
# icon = tweet['pic_url']
# text = tweet['tweet_text']
#
# compose_tweet(name, handle, icon, text).show()

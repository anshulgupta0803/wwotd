#!/usr/bin/env python3

import os
import textwrap

import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont


class WWOTD():
    def __init__(self, width=1920, height=1080):
        self.basedir = os.path.dirname(os.path.realpath(__file__))
        self.wallpaper_url = 'https://www.bing.com/HPImageArchive.aspx?format=js&idx=-1&n=1'
        self.word_url = 'https://www.merriam-webster.com/word-of-the-day'
        self.width = width
        self.height = height
        self.boxsize = 400
        self.image_path = os.path.join(self.basedir, 'Images')
        if not os.path.exists(self.image_path):
            os.mkdir(self.image_path)
        if not os.path.isdir(self.image_path):
            print(self.image_path + ' is not a directory')
            return
        self.image_name = None

    def __wallpaper(self):
        response = requests.get(self.wallpaper_url).json()
        image_url = 'https://www.bing.com' + \
            response['images'][0]['urlbase'] + '_' + \
            str(self.width) + 'x' + str(self.height) + '.jpg'
        image_title = response['images'][0]['title'].replace(' ', '_')
        image_date = response['images'][0]['startdate']
        image_date = image_date[0:4] + '-' + \
            image_date[4:6] + '-' + image_date[6:8]
        response = requests.get(image_url)
        if not response.ok:
            print('Unable to download the image')
            print(image_url)
            return
        image_data = response.content
        self.image_name = image_date + '-' + image_title + \
            '_' + str(self.width) + 'x' + str(self.height) + '.png'
        if os.path.exists(os.path.join(self.image_path, self.image_name)):
            print('Image already downloaded')
            return
        with open(os.path.join(self.image_path, self.image_name), 'wb') as IMG:
            IMG.write(image_data)

    def __word(self):
        response = requests.get(self.word_url)
        if not response.ok:
            print('Unable to get the word of the day')
            return
        soup = BeautifulSoup(response.text, 'html.parser')
        word = soup.find(
            class_='word-and-pronunciation').find('h1').contents[0]
        category = soup.find(class_='main-attr').contents[0]
        pronunciation = soup.find(class_='word-syllables').contents[0]
        definition = ''
        for content in soup.find(class_='wod-definition-container').find('p').contents:
            try:
                definition += content.contents[0]
            except AttributeError:
                definition += content
        bold_font = ImageFont.truetype(
            os.path.join(self.basedir,
                         'Fonts',
                         'PlayfairDisplay-Bold.ttf'), 40)
        italic_font = ImageFont.truetype(
            os.path.join(self.basedir,
                         'Fonts',
                         'PlayfairDisplay-Italic.ttf'), 18)
        regular_font = ImageFont.truetype(
            os.path.join(self.basedir,
                         'Fonts',
                         'PlayfairDisplay-Regular.ttf'), 16)
        word_image = Image.new(
            'RGBA', (self.width, self.height), (0, 0, 0, 0))

        draw = ImageDraw.Draw(word_image)
        (width, height) = word_image.size
        top_left = ((width - self.boxsize) // 2,
                    (height - self.boxsize) // 2)
        bottom_right = ((width + self.boxsize) // 2,
                        (height + self.boxsize) // 2)
        draw.rectangle([top_left, bottom_right],
                       fill=(0, 0, 0, 180))
        word_w, _ = draw.textsize(word, font=bold_font)
        draw.text((top_left[0] + (self.boxsize - word_w) // 2,
                   top_left[1] + 100), word, font=bold_font)

        category_pronunciation = category + ' | ' + pronunciation
        category_pronunciation_w, _ = draw.textsize(
            category_pronunciation, font=italic_font)
        draw.text((top_left[0] + (self.boxsize - category_pronunciation_w) // 2,
                   top_left[1] + 150), category_pronunciation, font=italic_font)

        draw.line([(top_left[0] + self.boxsize // 4),
                   (top_left[1] + 190),
                   (top_left[0] + 3 * self.boxsize // 4),
                   (top_left[1] + 190)
                   ])

        paragraph = textwrap.wrap(definition, width=50)
        paragraph_height, line_height = top_left[1] + 200, 25
        for line in paragraph:
            line_w, _ = draw.textsize(line, font=regular_font)
            draw.text((top_left[0] + (self.boxsize - line_w) // 2,
                       paragraph_height), line, font=regular_font)
            paragraph_height += line_height

        if self.image_name is None:
            self.__wallpaper()
        background_image = Image.open(
            os.path.join(self.image_path, self.image_name)).convert('RGBA')
        out = Image.alpha_composite(
            background_image, word_image)
        out.save(os.path.join(self.image_path, self.image_name))

    def set_wallpaper(self):
        self.__wallpaper()
        self.__word()
        command = 'gsettings set org.gnome.desktop.background picture-uri '
        file_uri = 'file://' + \
            os.path.abspath(os.path.join(self.image_path, self.image_name))
        gio_module = 'export GIO_EXTRA_MODULES=/usr/lib/x86_64-linux-gnu/gio/modules/'
        os.system(gio_module + ' && ' + command + file_uri)


if __name__ == '__main__':
    WWOTD(1366, 768).set_wallpaper()

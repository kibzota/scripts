#!/usr/bin/env python3
import os
import sys
import requests
import argparse
from lxml import etree

URL_BASE = 'https://www.reddit.com'

def get_arg():
    parser = argparse.ArgumentParser(description='Change your wallpaper by the last one posted in reddit')
    parser.add_argument('--sub', dest='subreddit', type=str, help='type an subreddit')

    args = parser.parse_args()
    return args.subreddit

def get_url(str):
    return '{}/{}'.format(URL_BASE, str)


def connect(site):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
    try:
        html = requests.get(site, headers=headers)
    except:
        html = requests.get(site, headers=headers, verify=False)

    if html.status_code is not 200:
        raise BaseException('Error {}. Invalid Subreddit'.format(html.status_code))

    page = html.text
    tree = etree.HTML(page)

    return tree

def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.3f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.3f%s%s" % (num, 'Yi', suffix)

def download(url):
    name = url.split('/')[-1]
    folder = 'wallpaper'
    img_path = os.path.join(folder, name)
    if not os.path.exists(folder):
        os.makedirs(folder)

    if not os.path.exists(img_path):
        print('Downloading {}'.format(name))
        with open(img_path,'wb') as f:
            result = requests.get(url, stream=True)
            total_length = result.headers.get('content-length')

            dl = 0
            total_length = int(total_length) if total_length else None
            for data in result.iter_content(chunk_size=(1024)):
                dl += len(data)
                f.write(data)
                if total_length:
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s] (%s/%s)  " % (
                        '=' * done, ' ' * (50 - done),
                        sizeof_fmt(dl), sizeof_fmt(total_length)))
                    sys.stdout.flush()
                else:
                    sys.stdout.write("\rDownloaded %s so far... " % sizeof_fmt(dl))

        os.system("gsettings set org.gnome.desktop.background picture-uri file:{}".format(os.path.abspath(img_path)))
#        os.system("feh --bg-fill {}".format(os.path.abspath(img_path)))
    else:
        print("Wallpapers is up to date")


def crawler(arg, start=0):
    sub = 'r/{}/'.format(arg)
    url = get_url(sub)
    print ('Acessing {}'.format(url))
    tree = connect(url)
    first_wallpaper = tree.xpath("//div[@class='entry unvoted']/p/a/@href")[start::2]
    if first_wallpaper[0].endswith('.jpg') or first_wallpaper[0].endswith('.png'):
        url = first_wallpaper[0]
        download(url)
    else:
        try:
            url = get_url(first_wallpaper[0])
            tree = connect(url)
            img_url = tree.xpath("//div[@class='media-preview-content']/a/@href")[0]
            download(img_url)
        except:
            start += 2
            crawler(arg, start=start)




def main():
    if get_arg():
        sub = get_arg()
    else:
        sub = 'wallpapers'
    crawler(sub)

if __name__ == '__main__':
    main()
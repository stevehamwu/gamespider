import re

import bs4
import os

import datetime
import scrapy

from apport import log

from gamespider import settings
from gamespider.items import GamePageItem, LinkItem


# def openFile():
#     for parent, dirnames, filenames in os.walk(rootdir):
#         with open(rootdir + "start_urls", 'wt') as file:
#             for filename in filenames:
#                 parseFile(filename, file)
#
# def parseFile(cata, file):
#     with open(rootdir + cata, "r") as f:
#         soup = bs4.BeautifulSoup(f.read())
#         links = soup.find_all('h3')
#         for link in links:
#             href = link.find('a')['href']
#             file.write(href + "\n")

def init(startpath, savepath):
    with open(startpath + "start_urls") as f:
        start_urls = f.readlines()
    with open(savepath + "crawled_urls", 'a+') as f:
        crawled_urls = f.readlines()
    return start_urls, crawled_urls


class GameSpider(scrapy.Spider):
    startpath = settings.STARTPATH
    rootpath = settings.ROOTPATH
    savepath = settings.SAVEPATH

    starttime = datetime.datetime.now()
    name = "gamescrapy"
    allowed_domains = [""]
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    start_urls, crawled_urls = init(startpath, savepath)
    index = len(crawled_urls)
    starturls = ["http://www.3dmgames.com/"]

    def parse(self, response):
        depth = response.meta['depth']
        if not depth:
            depth = 0
        log("****************depth: %d****************" % depth)

        referer = response.request.headers.get('Referer')
        if not referer:
            referer = "http://www.3dmgames.com/"
        else:
            referer = referer.decode('utf-8')

        linkitem = LinkItem()
        linkitem['last'] = referer
        linkitem['next'] = response.url.replace('%0A', '')
        yield linkitem

        if response.url not in self.crawled_urls:
            if self.index % 2000 == 0:
                self.savepath = self.rootpath + "%d/" % (self.index / 2000)
                if not os.path.exists(self.savepath):
                    os.mkdir(self.savepath)
                self.stat()

            self.saveFile(response)
            self.crawled_urls.append(response.url)
            item = self.saveItem(response)
            item['path'] = self.savepath + "f%06d" % self.index

            item['referer'] = referer
            self.index += 1
            yield item
            print("***************" + response.url + " done *********************")

            soup = bs4.BeautifulSoup(response.text, "html.parser")
            next_urls = soup.find_all('a')
            for url in next_urls:
                href = url.get('href')
                if href:
                    if re.match('http://.+(game|duowan|17173).+com.+', href):
                        # print("next: " + href)
                        if depth < settings.CRAWL_DEPTH:
                            yield scrapy.Request(href, callback=self.parse, dont_filter=True,
                                                 meta={'depth': str(depth + 1)})

        else:
            print("---------------" + response.url + " has been crawled: -------------------")

    def saveItem(self, response):
        text = response.text
        item = GamePageItem()
        soup = bs4.BeautifulSoup(text, "html.parser")
        item['title'] = soup.title.text
        item['url'] = response.url.replace('%0A', '')

        reg = re.compile("\n[\s| ]*\n")
        [script.extract() for script in soup.findAll('script')]
        [style.extract() for style in soup.findAll('style')]
        soup.prettify()
        item['content'] = reg.sub('\n', soup.body.text)

        return item

    def saveFile(self, response):
        with open(self.savepath + "f%06d" % self.index, 'wt') as f:
            f.write(response.text)
        with open(self.rootpath + "crawled_urls", 'a+') as f:
            f.write(response.url.replace('%0A', '') + "\n")
        log("--------------Saved " + self.savepath + "f%06d" % self.index)

    def stat(self):
        now = datetime.datetime.now()
        duration = (now - self.starttime).seconds
        if (duration == 0):
            speed = 0.0
        else:
            speed = 2000.0 / duration
        with open(self.rootpath + "stat", "a+") as f:
            f.write("Time now : " + str(now) + " speed is %f pages/s" % speed + " total pages is %d" % self.index)

from selenium import webdriver
from time import sleep
import requests
from aigpy import download


class Video:
    def __init__(self, url, name):
        self.Url = url
        self.Name = name


class Lesson:
    def __init__(self, part, lessonNumber, element):
        self.Part = part
        self.LessonNumber = lessonNumber
        self.Element = element


def GetFolders(chrome, FolderLink: str, Sleep: int) -> list:
    chrome.get(FolderLink)
    sleep(Sleep)

    div = chrome.find_element_by_class_name('FolderLinkContainer.virtual.Selected')
    divs = div.find_element_by_xpath("parent::*")

    divs = divs.find_elements_by_id('ChildFolder')
    part = div.get_attribute('innerHTML')

    lessons = []
    for elm in divs:
        lessons.append(
            Lesson(
                    part,
                    elm.get_attribute('innerHTML'),
                    elm
                )
            )

    return lessons


def GetVideos(chrome, folder: Lesson, Sleep: int) -> list:
    folder.Element.click()
    sleep(Sleep)

    videoList = []
    for v in chrome.find_elements_by_xpath('//*[@title="View Presentation"]'):
        videoList.append(
            Video(
                v.get_attribute('href'),
                v.get_attribute('innerHTML')
            )
        )

    return videoList


def GetVideoStream(video: Video) -> str:
    stream = ""

    resourceid = video.Url[41:-1].split('?')[0]
    query = video.Url[41:-1].split('?')[1]
    payload = '{"getPlayerOptionsRequest":{"ResourceId":"'+ resourceid +'","QueryString":"?'+ query +'","UseScreenReader":false,"UrlReferrer":""}}'

    headers = {'Content-type': "application/json; charset=utf-8"}
    endpoint = 'https://mediasite.osu.edu/Mediasite/PlayerService/PlayerService.svc/json/GetPlayerOptions'
    res = requests.request("POST", endpoint, data=payload, headers=headers).json()

    urls = res['d']['Presentation']['Streams'][0]['VideoUrls']
    for i in urls:
        if i['Location'] != "":
            stream = i['Location'].split('?')[0]
            break

    return stream


def Download(url: str, name: str, path: str):
    tool = download.DownloadTool(path + name + '.mp4', [url + '/qualityLevels()'])
    check, err = tool.start(True)
    if not check:
        print("[!] Download failed. (" + str(err) + ")")


def Main():
    #url = 'https://mediasite.osu.edu/Mediasite/Catalog/Full/4746ca4f671a4deea696d9789ff0cc5821/40d6a0a86e9648cca38f207918f88a9d14/4746ca4f671a4deea696d9789ff0cc5821'
    url = input("Folder to download: ")
    browser = webdriver.Chrome()
    folders = GetFolders(browser, url, 10)
    for folder in folders:
        videos = GetVideos(browser, folder, 5)
        for v in videos:
            stream = GetVideoStream(v)
            print(stream)
    browser.close()

if __name__ == '__main__':
    Main()

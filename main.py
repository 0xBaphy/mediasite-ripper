from requests import request
from aigpy import download
import os
import shutil


def Download(Name: str, Stream: str):
    tool = download.DownloadTool(Name, [Stream + '/qualityLevels()'])
    check, err = tool.start(True)
    if check:
        shutil.move(Name, Name+'.mp4')
    else:
        print("[!] Download failed. (" + str(err) + ")")



class ChildContent(object):
    def __init__(self, name, Id, url):
        self.Name = name
        self.Id = Id
        self.Url = url


class FolderChild(object):
    def __init__(self, details: dict):
        self.Name = details['CurrentFolder']['Name']
        self.Id = details['CurrentFolder']['Id']
        self.ParentId = details['CurrentFolder']['ParentCatalogFolderId']
        x = []
        for d in details['PresentationDetailsList']:
            x.append(ChildContent(d['Name'], d['Id'], d['PlayerUrl']))
        self.Contents = x


class ParentFolder(object):
    def __init__(self, details: dict):
        self.Name = details['CurrentFolder']['Name']
        self.Id = details['CurrentFolder']['Id']
        self.DynamicId = details['CurrentFolder']['DynamicFolderId']
        self.Folders = list


class CatalogDetails(object):
    def __init__(self, details: dict):
        self.Name = details['CatalogDetails']['Name']
        self.Id = details['CatalogDetails']['Id']


class MediaSite(object):
    def __init__(self, catalog):
        res = request("GET", catalog).text
        self.CatalogId = res[res.find("CatalogId") + 12:res.find("',", 1)]

    def CatalogDetails(self) -> dict:
        endpoint = "https://mediasite.osu.edu/Mediasite/Catalog/Data/GetCatalogDetails"
        payload = {
                "IsViewPage": False,
                "CatalogId": self.CatalogId,
                "CurrentFolderId": "",
                "Url": "",
                "PreviewKey": None,
                "AuthTicket": None
        }
        res = request("POST", endpoint, json=payload)
        return res.json()

    def ParentFolderDetails(self, Id: str) -> ParentFolder:
        endpoint = "https://mediasite.osu.edu/Mediasite/Catalog/Data/GetPresentationsForFolder"
        payload ={
                "IsViewPage": False,
                "IsNewFolder":True,
                "AuthTicket": None,
                "CatalogId": self.CatalogId,
                "CurrentFolderId": Id,
                "RootDynamicFolderId": self.CatalogId
        }
        res = request("POST", endpoint, json=payload).json()
        return ParentFolder(res)

    def PresentationFolder(self, Id: str) -> FolderChild:
        endpoint = "https://mediasite.osu.edu/Mediasite/Catalog/Data/GetPresentationsForFolder"
        payload = {
                "IsViewPage": False,
                "IsNewFolder": True,
                "AuthTicket": None,
                "CatalogId": self.CatalogId,
                "CurrentFolderId": Id,
                "RootDynamicFolderId": self.CatalogId,
                "ItemsPerPage": 40,
                "PageIndex": 0,
                "PermissionMask": "Execute",
                "CatalogSearchType": "SearchInFolder",
                "SortBy": "Date",
                "SortDirection": "Ascending",
                "StartDate": None,
                "EndDate": None,
                "StatusFilterList": None,
                "PreviewKey": None,
                "Tags": []
        }
        res = request("POST", endpoint, json=payload).json()
        return FolderChild(res)

    def GetStream(self, url: str) -> str:
        stream = ""
        headers = {'Content-type': "application/json; charset=utf-8"}
        endpoint = "https://mediasite.osu.edu/Mediasite/PlayerService/PlayerService.svc/json/GetPlayerOptions"
        payload = {
                "getPlayerOptionsRequest": {
                    "ResourceId": url[41:-1].split('?')[0],
                    "QueryString":"?" + url[41:-1].split('?')[1],
                    "UseScreenReader": False,
                    "UrlReferrer":""
                }
        }
        res = request("POST", endpoint, json=payload, headers=headers).json()
        urls = res['d']['Presentation']['Streams'][0]['VideoUrls']
        for u in urls:
            if u['Location'] != "":
                stream = u['Location'].split('?')[0]
                break
        return stream


def main():
    Lessons = input("[*] Input the catalog URL >")
    client = MediaSite(Lessons)
    catalog = client.CatalogDetails()

    CurrentPath = catalog['CatalogDetails']['Name']
    if not os.path.isdir(CurrentPath):
        os.mkdir(CurrentPath)

    for c in catalog['NavigationFolders']:
        if c['Type'] == 2:
            pass

        folder = client.PresentationFolder(c['DynamicFolderId'])

        Dir = os.path.join(CurrentPath, folder.Name)
        if not os.path.isdir(Dir):
            os.mkdir(Dir)

        for video in folder.Contents:
            stream = client.GetStream(video.Url)
            name = os.path.join(Dir, video.Name)
            if os.path.isfile(name + ".mp4"):
                print("[i] File already exists, skipping:", name)
            else:
                print("[i] Downloading:", name)
                Download(name, stream)


if __name__ == '__main__':
    main()

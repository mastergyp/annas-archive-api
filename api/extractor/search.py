from .. import FRONT_PAGE
from ..utils import get
from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass
from enum import Enum


class OrderBy(Enum):
    MOST_RELEVANT = ''
    NEWEST = 'newest'
    OLDEST = 'oldest'
    LARGEST = 'largest'
    SMALLEST = 'smallest'


class FileType(Enum):
    ANY = ""
    PDF = "pdf"
    EPUB = "epub"
    MOBI = "mobi"
    AZW3 = "azw3"
    FB2 = "fb2"
    LIT = "lit"
    DJVU = "djvu"
    RTF = "rtf"
    ZIP = "zip"
    RAR = "rar"
    CBR = "cbr"
    TXT = "txt"
    CBZ = "cbz"
    HTML = "html"
    FB2_ZIP = "fb2.zip"
    DOC = "doc"
    HTM = "htm"
    DOCX = "docx"
    LRF = "lrf"
    MHT = "mht"


@dataclass
class FileInfo:
    name: str | None
    language: str | None
    extension: str
    size: str


@dataclass
class Result:
    title: str
    authors: list[str]
    publisher: str
    publish_date: str
    thumbnail_url: str
    url: str
    file_info: FileInfo


async def getSearchResults(query: str, language: str = "",
                           file_type: FileType = FileType.ANY,
                           order_by: OrderBy = OrderBy.MOST_RELEVANT) -> list[Result]:
    response = await get(
        url=f"{FRONT_PAGE}/search",
        params={
            'q': query,
            'lang': language,
            'ext': file_type.value,
            'sort': order_by.value
        }
    )
    html = BeautifulSoup(response.text, 'lxml')
    raw_results = html.findAll('div', class_='h-[125]')
    results = list(map(parseResult, raw_results))
    return [i for i in results if i != None]


def parseResult(raw_content: Tag) -> Result | None:
    try:
        title = raw_content.find('h3').getText(strip=True)
    except:
        return None
    authors = raw_content.find(
        'div',
        class_='truncate italic'
    ).getText(strip=True).split(', ')
    publish_info = raw_content.find(
        'div', class_='truncate text-sm'
    ).text.split(', ')
    publisher = publish_info[0]
    publish_date = ', '.join(publish_info[1:])
    thumbnail_url = raw_content.find('img').get('src')
    url = raw_content.find('a').get('href')
    file_info = extractFileInfo(
        raw_content.find('div', class_='truncate text-xs text-gray-500').text
    )
    return Result(
        title, authors, publisher, publish_date,
        thumbnail_url, url, file_info
    )


def extractFileInfo(raw: str) -> FileInfo:
    # sample data:
    #  English [en], pdf, 7.5MB, "Python_Web_Scraping_-_Second_Edition.pdf"
    #  English [en], pdf, 1.5MB
    #  mobi, 4.1MB
    info_list = raw.split(', ')
    language = None
    if '[' in info_list[0]:
        language = info_list.pop(0)
    extension = info_list.pop(0)
    size = info_list.pop(0)
    name = None
    if len(info_list) > 0:
        name = ", ".join(info_list).replace('"', '')
    return FileInfo(name, language, extension, size)

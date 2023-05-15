from dataclasses import dataclass


@dataclass
class FileInfo:
    name: str | None
    language: str | None
    extension: str
    size: str


def extract_file_info(raw: str) -> FileInfo:
    # Extract file info following a logic that the raw informations
    # will always be containing file type and size, and if the name
    # exists it will always be the last informations contained by "",
    # and if the language exists it will always be the first containing
    # a "[" that has the language code into it.

    # sample data:
    #  English [en], pdf, 7.5MB, "Python_Web_Scraping_-_Second_Edition.pdf"
    #  Portuguese [pt], epub, 1.5MB
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


def extract_publish_info(raw: str) -> tuple[str | None, str | None]:
    info = raw.split(', ')
    publisher = None
    date = None
    if info[-1] == '0':
        # In this case the system don't know the date
        if len(info) > 1:
            publisher = ', '.join(info[:-1])
        pass
    elif info[-1].isnumeric():
        # The system know the year and can know the month of publish
        date = info[-1]
        publisher = ', '.join(info[:-1])
        if len(info) >= 2 and info[-2].isnumeric():
            # Here the system know both, year and month
            date = ', '.join(info[-2:])
            publisher = ', '.join(info[:-2])
    else:
        # The system don't know the date and can send the publisher
        publisher = ', '.join(info)
    publisher = publisher if publisher else None
    return (publisher, date)

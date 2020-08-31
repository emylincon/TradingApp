from win32com.client import Dispatch
import wget
import os
import requests
from bs4 import BeautifulSoup
import re
import zipfile


class ChromeDriver:
    def __init__(self):
        self.save_folder = "chromeDriver"
        self.parser_script = "Scripting.FileSystemObject"
        self.base_url = "https://chromedriver.storage.googleapis.com"
        self.download_url = 'https://chromedriver.chromium.org/downloads'

    def get_version_via_com(self, filename):
        parser = Dispatch(self.parser_script)
        try:
            version = parser.GetFileVersion(filename)
        except Exception:
            return None
        return version

    def download_new_version(self, version):
        try:
            os.remove(rf'{self.save_folder}\chromedriver.exe')
        except FileNotFoundError:
            pass
        link = f'{self.base_url}/{version}/chromedriver_win32.zip'
        filename = wget.download(link)
        # os.rename(filename, fr'C:\Users\emyli\PycharmProjects\Chatbot_Project\chrome_driver\{filename}')

        with zipfile.ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall(self.save_folder)
        os.remove('chromedriver_win32.zip')

    def match_version(self, ver):
        page = requests.get(self.download_url)
        soup = BeautifulSoup(page.content, 'lxml')
        h2_tag = soup.find_all('h2')
        for tag in h2_tag:
            text = tag.get_text()
            if (len(re.findall('[A-Za-z]+ [0-9]', text)) != 0) and (text.split()[1].strip().split('.')[0] == ver):
                return text.split()[1].strip()

    def get_driver(self):
        paths = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                 r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]
        c_ver = list(filter(None, [self.get_version_via_com(p) for p in paths]))[0]
        mv_ver = self.match_version(c_ver.split('.')[0])
        print(f'Downloading version chrome driver {mv_ver}')
        self.download_new_version(mv_ver)
        print('file downloaded')


# ChromeDriver().get_driver()
import unicodedata
import re


class FilenameConverter():
    def convert(self, filename):
        value = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
        value = re.sub(r'[^\w\s-]', '', value).strip()
        value = re.sub(r'[-\s]+', '-', value)
        return value

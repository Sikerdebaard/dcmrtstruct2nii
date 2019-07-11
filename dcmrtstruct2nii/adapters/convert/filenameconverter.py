import unicodedata
import re

class FilenameConverter():
    def convert(self, filename):
        value = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
        value = re.sub('[^\w\s-]', '', value).strip()
        value = re.sub('[-\s]+', '-', value)
        return value

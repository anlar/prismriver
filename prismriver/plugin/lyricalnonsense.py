from prismriver.plugin.common import Plugin
from prismriver.struct import Song


class LyricalNonsensePlugin(Plugin):
    def __init__(self):
        super(LyricalNonsensePlugin, self).__init__('lyricalnonsense', "Lyrical Nonsense")

    def search(self, artist, title):
        artist_page = self.get_artist_page(artist)
        if artist_page:
            song_page = self.get_song_page(artist_page, title)
            if song_page:
                return self.get_song(song_page)

    def get_artist_page(self, artist):
        main_page = self.download_webpage('http://www.lyrical-nonsense.com/lyrics/')
        if main_page:
            soup = self.prepare_soup(main_page)

            artist_infos = []

            artist_block = soup.find('div', {'id': 'content'})
            for elem in artist_block.findAll('a', href=True):
                artist_infos.append([elem['href'], elem.text.split(' | ')])

            artist_link = None
            for info in artist_infos:
                if artist.lower() in map(lambda x: x.lower(), info[1]):
                    artist_link = info[0]

            if artist_link:
                return self.download_webpage(artist_link)

    def get_song_page(self, page, title):
        soup = self.prepare_soup(page)

        for elem in soup.findAll('table', {'class': 'imagetablelyrics'}):
            original_title_block = elem.find('div', {'class': 'titletextartist'})
            song_link = original_title_block.a['href']

            song_titles = [original_title_block.text]

            translated_title_block = elem.find('div', {'class': 'subtitletextartist'})
            if translated_title_block:
                for translated_title in translated_title_block.strings:
                    song_titles.append(translated_title.strip())

            if title.lower() in map(lambda x: x.lower(), song_titles):
                return self.download_webpage(song_link)

    def get_song(self, page):
        soup = self.prepare_soup(page)

        artist_block = soup.find('table', {'class': 'imagetabletitle'})
        artist_block = artist_block.find('div', {'class': 'titletextpage'})
        song_artist = artist_block.get_text()

        title_block = soup.find('table', {'class': 'songtitle'})
        title_block = title_block.find('div', {'class': 'titletextpage'})
        song_title = title_block.get_text()

        lyrics = []

        main_lyric_block = soup.find('div', {'class': 'draggable'})
        # we should reverse list order to move original japanese lyric to the top
        for lyric_block in main_lyric_block.findAll('div', id=True)[::-1]:
            if lyric_block['id'] != 'Details':
                lyric = ''
                for verse_block in lyric_block.findAll('p', recursive=False):
                    lyric += (self.parse_verse_block(verse_block) + '\n\n')

                lyrics.append(lyric)

        return Song(song_artist, song_title, self.sanitize_lyrics(lyrics))

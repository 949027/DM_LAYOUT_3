import requests
import os
import argparse
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


def download_image(soup, folder='images/'):
    url_image = urljoin(
        'https://tululu.org',
        soup.find('div', class_='bookimage').find('img')['src'],
    )
    response = requests.get(url_image)
    response.raise_for_status()

    filename = url_image.split(sep='/')[-1]
    path = os.path.join(folder, filename)

    try:
        check_for_redirect(response)
        with open(path, 'wb') as file:
            file.write(response.content)
    except requests.HTTPError:
        pass


def download_txt(soup, book_id, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    book_url = "https://tululu.org/txt.php"
    payload = {'id': book_id}

    title_tag = soup.find('h1')
    title_text = title_tag.text
    title_book = '{}. {}'.format(
        book_id,
        title_text.split(sep='::')[0].strip(),
    )

    clean_filename = f"{sanitize_filename(title_book)}.txt\n"
    path = os.path.join(folder, clean_filename)

    response = requests.get(book_url, params=payload)
    response.raise_for_status()

    try:
        check_for_redirect(response)
        with open(path, 'wb') as file:
            file.write(response.content)
    except requests.HTTPError:
        pass

    return path


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def parse_book_page(soup):
    book = {}
    genres = []
    title_tag = soup.find('h1')
    title_text = title_tag.text
    book['title'] = title_text.split(sep='::')[0].strip()
    book['author'] = title_text.split(sep='::')[1].strip()

    for genre in soup.find('span', class_='d_book').find_all('a'):
        genres.append(genre.get_text())
    book['genres'] = genres

    try:
        for comment in soup.find_all('div', class_='texts'):
            book['comments'] = comment.find('span', class_='black').text
    except requests.HTTPError:
        pass

    return book


def main():
    parser = argparse.ArgumentParser(
        description='Программа для скачивания книг с '
                    'tululu.org'
    )
    parser.add_argument(
        '-s',
        '--start_id',
        help='id первой книги',
        default=1,
        type=int,
    )
    parser.add_argument(
        '-e',
        '--end_id',
        help='id последней книги',
        default=10,
        type=int
    )
    args = parser.parse_args()

    os.makedirs('books', exist_ok=True)
    os.makedirs('images', exist_ok=True)

    for book_id in range(args.start_id, args.end_id + 1):
        try:
            url = 'https://tululu.org/b' + str(book_id) + '/'

            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')



            check_for_redirect(response)
            book = parse_book_page(soup)
            print('\nНазвание: ', book['title'], '\nАвтор: ', book['author'])
            download_txt(soup, book_id)
            download_image(soup)
        except requests.HTTPError:
            pass


if __name__ == '__main__':
    main()

import requests
import os
import argparse
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlsplit,unquote


def download_image(soup, folder='images/'):
    url_image = urljoin(
        'https://tululu.org',
        soup.find('div', class_='bookimage').find('img')['src'],
    )
    response = requests.get(url_image)
    response.raise_for_status()

    url_path_image = urlsplit(url_image)[2]
    filename = unquote(os.path.split(url_path_image)[1])
    path = os.path.join(folder, filename)

    with open(path, 'w') as file:
        file.write(response.text)


def download_txt(soup, book_id, folder='books/'):
    """Функция для скачивания текста книги с tululu.org.

    Args:
        soup (bs4.BeautifulSoup): soup-объект, полученный из html-страницы.
        book_id (int): id книги.
        folder (str): Папка, куда сохранять.

    Returns:
        str: Путь до файла, куда будет сохранён текст.

    """
    book_url = "https://tululu.org/txt.php"
    payload = {'id': book_id}

    title_tag = soup.find('h1')
    title_text = title_tag.text
    title, _ = title_text.split(sep='::')
    title_book = '{}. {}'.format(
        book_id,
        title.strip(),
    )

    clean_filename = f"{sanitize_filename(title_book)}.txt"
    path = os.path.join(folder, clean_filename)

    response = requests.get(book_url, params=payload)
    response.raise_for_status()

    with open(path, 'wb') as file:
        file.write(response.text.encode())

    return path


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def parse_book_page(soup):
    title_tag = soup.find('h1')
    title_text = title_tag.text
    title, author = title_text.split(sep='::')

    comment_blocks = soup.find_all('div', class_='texts')
    genres_blocks = soup.find('span', class_='d_book').find_all('a')

    genres = [genre.get_text() for genre in genres_blocks]
    comments = [
        comment.find('span', class_='black').text for comment in comment_blocks
    ]

    book = {
        'title': title.strip(),
        'author': author.strip(),
        'genres': genres,
        'comments': comments
    }

    return book


def main():
    parser = argparse.ArgumentParser(
        description='Программа для скачивания книг с tululu.org'
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
            url = 'https://tululu.org/b{}/'.format(book_id)

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

import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


def download_image(url_img, folder='images/'):
    response = requests.get(url_img)
    response.raise_for_status()

    filename = url_img.split(sep='/')[-1]
    path = os.path.join(folder, filename)

    try:
        check_for_redirect(response)
        with open(path, 'wb') as file:
            file.write(response.content)
    except requests.HTTPError:
        pass


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    filename_clean = f"{sanitize_filename(filename)}.txt\n"
    path = os.path.join(folder, filename_clean)

    response = requests.get(url)
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


def main():
    os.makedirs('books', exist_ok=True)
    os.makedirs('images', exist_ok=True)

    for id_book in range(1, 11):
        url = 'https://tululu.org/b' + str(id_book) + '/'

        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        title_tag = soup.find('h1')
        title_text = title_tag.text
        title_book = str(id_book) + '. ' + title_text.split(sep='::')[0].strip()
        url_book = "https://tululu.org/txt.php?id=" + str(id_book)

        try:
            check_for_redirect(response)
            print('Заголовок: ' + title_book)
            url_img = urljoin('https://tululu.org', soup.find('div', class_='bookimage').find('img')['src'])
            print(url_img)
            for i in soup.find_all('div', class_='texts'):
                print((i.find('span', class_='black')).text)
            download_txt(url_book, title_book)
            download_image(url_img)
        except requests.HTTPError:
            pass


if __name__ == '__main__':
    main()

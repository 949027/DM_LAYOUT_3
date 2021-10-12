import requests
import os


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def main():
    os.makedirs('books', exist_ok=True)

    for id_book in range(1, 11):
        url = 'https://tululu.org/txt.php?id=' + str(id_book)

        response = requests.get(url)
        response.raise_for_status()

        try:
            check_for_redirect(response)
            filename = 'id' + str(id_book) + '.txt'
            with open('books/' + filename, 'wb') as file:
                file.write(response.content)
        except requests.HTTPError:
            pass


if __name__ == '__main__':
    main()
import requests
import os


os.makedirs('books', exist_ok=True)

for id_book in range(1, 11):
    url = 'https://tululu.org/txt.php?id=' + str(id_book)

    response = requests.get(url)
    response.raise_for_status()

    filename = 'id' + str(id_book) + '.txt'
    with open('books/' + filename, 'wb') as file:
        file.write(response.content)
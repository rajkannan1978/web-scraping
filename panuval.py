import requests
from bs4 import BeautifulSoup as Bs


def write_data(file_name, header, all_books_list):
    with open(file_name, encoding='utf-8', mode='w+') as f:
        for head in header:
            f.write(head+'~')
        f.write('\n')
        for url, info in all_books_list.items():
            # print(info)
            for head in header:
                w = ''
                if head in info:
                    w = info[head]
                f.write(w + '~')
            f.write('\n')


def get_book_info(book_obj):
    url = book_obj.find('a')['href'].replace(' ', '%20')
    info = list()
    info.append(book_obj.find('img').get('title'))
    info.append(book_obj.find('img').attrs['data-src'])
    if 'NoneType' not in str(type(book_obj.find('span', class_='price-new'))):
        info.append(book_obj.find('span', class_='price-new').text)
    elif 'NoneType' not in str(type(book_obj.find('span', class_='price-normal'))):
        info.append(book_obj.find('span', class_='price-normal').text)
    else:
        info.append('')
    return url, info


def get_book_details(url):
    try:
        page = requests.get(url)
        soup = Bs(page.content, 'lxml')
        data_div = soup.find('div', class_='product-details')
        data_stats = data_div.find('div', class_='product-stats')
        # Need first 3 <div> only
        required_div = []
        count = 0
        for each in data_div:
            if 'div' in str(each):
                required_div.append(each)
                count += 1
            if count == 3:
                break

        title = required_div[0].text
        authors = required_div[1].text.replace('\n', '').replace('\t', '').split(',')
        all_authors = ''
        for author in authors:
            all_authors += author + '|'
        categories = ''
        all_categories = ''
        if ':' in required_div[2].text:
            categories = required_div[2].text.replace('\n', '').replace('\t', '').replace('\n', '').split(':')[1]
            if type(categories) == list:
                for category in categories:
                    all_categories += category + '|'
            else:
                all_categories = categories
        stats = data_stats.text.replace('\n\n', '\n').split('\n')

        details = {'Title': title, 'Authors': all_authors, 'Categories': all_categories}
        for stat in stats:
            if ':' in stat:
                key, value = stat.split(':')
                details[key] = value
    except Exception as e:
        print(url)
        print(e)
        details = {}

    return details


def scrape_panuval_books_list():

    url = 'https://www.panuval.com/'
    page = requests.get(url)
    soup = Bs(page.content, 'lxml')
    books_tag = soup.find_all('div', class_='product-thumb')
    
    all_books_list = dict()
    for book_obj in books_tag:
        url, info = get_book_info(book_obj)
        if url not in all_books_list.keys():
            all_books_list[url] = {}
            all_books_list[url]['Title'] = info[0]
            all_books_list[url]['Link'] = url
            all_books_list[url]['Image'] = info[1]
            all_books_list[url]['Price'] = info[2]

    featured_class = ['manufacturer-thumb', 'category-thumb']
    publications = []
    duplicate_books = []

    for f_class in featured_class:
        books_tag = soup.find_all('div', class_=f_class)
        publications = []

        for book_obj in books_tag:
            b1 = book_obj.find('div', class_='caption')
            publications.append(b1.find('a')['href'].replace(' ', '%20'))
        for publication in publications:
            no_of_books, no_of_pages, duplicate_books, pub_books = get_books_list(publication, all_books_list, duplicate_books)
            all_books_list.update(pub_books)
            print(publication, ' --- ', no_of_pages, '( Pages ) --- ', no_of_books, '(Books)')
            for p in range(2, no_of_pages + 1):
                # print(f'{p} of {no_of_pages}')
                _, _, duplicate_books, pub_books = get_books_list(f'{publication}?page={p}', all_books_list, duplicate_books)
                all_books_list.update(pub_books)
    print(len(all_books_list))
    print(len(duplicate_books))
    return all_books_list


def main():
    books_list = scrape_panuval_books_list()
    header = ['Title', 'Link', 'Image', 'Price']
    write_data('panuval_books_info.txt', header, books_list)
    books_details = {}
    unknown_books = []
    book_id = 1
    for book in books_list.keys():
        if book_id % 20 == 0:
            print(f'book id {book_id}, Scraping {book}...')
        details = books_list[book]
        details.update(get_book_details(book))
        books_details[str(book_id)] = details
        if details == {}:
            unknown_books.append([book_id, book])
        book_id += 1
    if unknown_books:
        print(unknown_books)

    header = ['Title', 'Link', 'Image', 'Price',
              'Authors', 'Categories', 'Edition', 'Year', 'ISBN', 'Page', 'Format', 'Language', 'Publisher']
    write_data('panuval_books_data.txt', header, books_details)


def get_books_list(url, all_books_list, duplicate_books):
    page = requests.get(url)
    soup = Bs(page.content, 'lxml')
    books_tag = soup.find_all('div', class_='product-thumb')
    no_of_pages = 0
    no_of_books = 0
    books_list = dict()

    if '?page' not in url:
        no_of_pages = int(soup.find('div', class_='row pagination-results').text.split('Pages')[0].split('(')[1])
        no_of_books = int(soup.find('div', class_='row pagination-results').text.split(' ')[5])

    if books_tag:
        for book_obj in books_tag:
            url, info = get_book_info(book_obj)
            if url not in all_books_list.keys():
                books_list[url] = {}
                books_list[url]['Title'] = info[0]
                books_list[url]['Link'] = url
                books_list[url]['Image'] = info[1]
                books_list[url]['Price'] = info[2]
            else:
                duplicate_books.append(url)
    return no_of_books, no_of_pages, duplicate_books, books_list


if __name__ == '__main__':
    main()

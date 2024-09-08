import requests
from bs4 import BeautifulSoup as Bs
from selenium import webdriver


def write_data(all_books_list):
    header = ['Title', 'Link', 'Image', 'Price', 'Authors', 'Categories', 'Edition', 'Year', 'Format', 'Language', 'Publisher']
    with open('panuval_books.txt', encoding='utf-8', mode='w+') as f:
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
    url = book_obj.find('a')['href']
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
        driver.get(url)
        driver.implicitly_wait(5)
        page_source = driver.page_source
        soup = Bs(page_source, 'lxml')
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
        # Displays URL which is not scraped and the Error
        print(url)
        print(e)
        details = {}

    return details


def scrape_panuval_books_list():

    url = 'https://www.panuval.com/'
    page = requests.get(url)
    soup = Bs(page.content, 'lxml')
    books_tag = soup.find_all('div', class_='product-thumb')
    
    books_list = dict()
    for book_obj in books_tag:
        url, info = get_book_info(book_obj)
        if url not in books_list.keys():
            books_list[url] = {}
            books_list[url]['Title'] = info[0]
            books_list[url]['Link'] = url
            books_list[url]['Image'] = info[1]
            books_list[url]['Price'] = info[2]

    return books_list


if __name__ == '__main__':
    books_list = scrape_panuval_books_list()

    print('Total Books are', len(books_list))

    driver = webdriver.Chrome()
    books_details = {}
    unknown_books = []
    book_id = 1
    for book in books_list.keys():
        print(f'Scraping {book}...')
        details = books_list[book]
        details.update(get_book_details(book))
        books_details[str(book_id)] = details
        if details == {}:
            unknown_books.append([book_id, book])
        book_id += 1
    if unknown_books:
        print(unknown_books)

    write_data(books_details)
    driver.quit()

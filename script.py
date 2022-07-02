import re
from tkinter import E
import requests
from bs4 import BeautifulSoup
import csv
import os
import urllib.request

def html_parser_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

""" Récupère toutes les informations d'un livre"""
def get_infos_book(link_book_page):
    book_page = html_parser_page(link_book_page)

    productDescription = book_page.find_all('p')[3].text
    replaceDescription = productDescription.replace(',', ' ') ## Virgule remplacée par un espace pour éviter un changement de cellule dans le fichier SCV
    universalProductCode = book_page.find_all('td')[0].text
    priceIncludingTaxe = book_page.find_all('td')[3].text[1:]
    priceExcludingTaxe = book_page.find_all('td')[2].text[1:]
    numberAvailable = book_page.find_all('td')[5].text[10:][:2]
    reviewRating = book_page.find_all('td')[6].text
    title = book_page.find('h1').text
    category = book_page.find_all('a')[3].text
    sourceImage = 'http://books.toscrape.com' + book_page.find('img')['src'][5:]
    link = link_book_page
    stars = book_page.find('p', class_='star-rating').get('class')[1]
    rating = 0
    if "One" in stars:
        rating = 1
    elif "Two" in stars:
        rating = 2
    elif "Thr" in stars:
        rating = 3
    elif "Fou" in stars:
        rating = 4
    elif "Fiv" in stars:
        rating = 5

    book_description = [replaceDescription, link_book_page, universalProductCode, title, priceIncludingTaxe, priceExcludingTaxe, numberAvailable, category, rating, sourceImage]
    return book_description

""" Récupère toutes les pages d'une catégorie """
def get_number_page_category(link_category):
    category = html_parser_page(link_category)
    link_page = link_category
    page_courante = 'index.html'
    check = True
    x = 1
    list_pages_category = []
    while check:
        x += 1
        category_page = requests.get(link_page)
        soup = BeautifulSoup(category_page.content, 'html.parser')
        if(category_page.status_code == 200):
            list_pages_category.append(link_page)
            numero_page = 'page-{}.html'.format(x)
            link_page = link_page.replace(page_courante, numero_page)
            page_courante = numero_page
        else:
            check = False
    return list_pages_category

""" Récupère tous les livres d'une page"""
def get_all_books_from_page(link_page_category):
    page_category = html_parser_page(link_page_category)
    link_books_from_page = []
    x = 0
    while x < len(page_category.find_all('h3')):
        for book in page_category.find_all('h3')[x]:
            link_books_from_page.append('https://books.toscrape.com/catalogue' + book['href'][8:])
            x += 1
    return link_books_from_page

""" Récupère tous les livres d'une catégorie """
def get_books_from_category(link_category):
    x = 0
    pages_from_category = get_number_page_category(link_category)
    link_books_from_category = []
    while x < len(pages_from_category):
        page_category = pages_from_category[x]
        page_book = get_all_books_from_page(page_category)
        for book in page_book:
            link_books_from_category.append(book)
        x += 1
    return link_books_from_category

""" Récupère toutes les catégories """
def get_all_category(link_page):
    link_website = html_parser_page(link_page)

    x = 3
    key_number = 0
    category_page = {}
    while x < 53:
        category = link_website.find_all('li')[x].a['href']
        category_name = link_website.find_all('li')[x].a.text
        category_name = category_name.replace(' ', '')
        category_name = category_name.replace('\n', '')
        category_link = 'https://books.toscrape.com/' + category
        category_page[str(key_number)] = [category_name, category_link]
        x += 1
        key_number += 1
    return category_page

""" Récupère les infos des livres d'une catégorie donnée et les enregistre """
def get_books_infos_from_category(url):
    en_tete = [
        'description',
        'product_page_url',
        'universal_ product_code (upc)',
        'title',
        'price_including_tax',
        'price_excluding_tax',
        'number_available',
        'category',
        'review_rating',
        'image_url'
        ]

    category_pages = get_all_category(url)
    x = 0
    
    while x < len(category_pages):
        category_name = category_pages[str(x)][0] ## Récupère le nom de la catégorie
        category_name_access_path = category_pages[str(x)][0] + '/' + category_pages[str(x)][0] + '.csv' ## Chemin d'enregistrement des fichiers
        link_category = category_pages[str(x)][1] ## Lien de la catégorie
        x += 1
        
        if not os.path.exists(category_name):
                os.makedirs(category_name)
        with open(category_name_access_path, 'a') as fichier:
            writer = csv.writer(fichier, delimiter=',')
            writer.writerow(en_tete)
            for link_book in get_books_from_category(link_category):
                book_infos = get_infos_book(link_book)
                writer.writerow(book_infos)
                print('CSV OK')
                book = book_infos[3].replace('/', ' ') ## Retire les slashs dans le titre des images 
                titre_image = category_name + '/' + book + '.jpg'
                urllib.request.urlretrieve(book_infos[9], titre_image)
                print(titre_image)
                
get_books_infos_from_category('http://books.toscrape.com/index.html')
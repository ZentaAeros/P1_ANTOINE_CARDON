import re
import requests
from bs4 import BeautifulSoup
import csv
import os
import urllib.request

""" Récupère toutes les informations d'un livre"""
def bookInfos(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    productDescription = soup.find_all('p')[3].text
    replaceDescription = productDescription.replace(',', '\,')
    universalProductCode = soup.find_all('td')[0].text
    priceIncludingTaxe = soup.find_all('td')[3].text[1:]
    priceExcludingTaxe = soup.find_all('td')[2].text[1:]
    numberAvailable = soup.find_all('td')[5].text[10:][:2]
    reviewRating = soup.find_all('td')[6].text
    title = soup.find('h1').text
    category = soup.find_all('a')[3].text
    sourceImage = 'http://books.toscrape.com' + soup.find('img')['src'][5:]
    link = response.url

    book_description = [replaceDescription, link, universalProductCode, title, priceIncludingTaxe, priceExcludingTaxe, numberAvailable, category, reviewRating, sourceImage]

    return book_description

""" Récupère toutes les pages d'une catégorie """
def checkPageNumber(url):
    nouveauLien = url
    page = requests.get(nouveauLien)
    soup = BeautifulSoup(page.content, 'html.parser')
    pageCourante = 'index.html'
    verif = True
    x = 1
    liens = []
    while verif == True:
        x += 1
        page = requests.get(nouveauLien)
        soup = BeautifulSoup(page.content, 'html.parser')
        if(page.status_code == 200):
            liens.append(nouveauLien)
            numeroPage = 'page-{}.html'.format(x)
            nouveauLien = nouveauLien.replace(pageCourante, numeroPage)
            pageCourante = numeroPage
        else:
            verif = False
    return liens

""" Récupère tous les livres d'une page"""
def checkAllBooks(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    books = []
    x = 0
    while x < len(soup.find_all('h3')):
        for book in soup.find_all('h3')[x]:
            books.append('https://books.toscrape.com/catalogue' + book['href'][8:])
            x += 1
    return books
from collections import namedtuple

from selenium import webdriver
from bs4 import BeautifulSoup

from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os

COSTCO_URL = "https://www.costco.com/CatalogSearch?keyword=OFF"

Item = namedtuple('Item', ['name', 'image', 'cost', 'discount', 'url'])


def get_soup(url):
    """Makes a request through Selenium and returns a BeautifulSoup soup.
    
    Args:
        - url: the url to make a request to
        
    Returns:
        - A BeautifulSoup soup of the given url
    """
    driver = webdriver.Chrome()
    driver.get(url)
    html = driver.page_source
    driver.quit()
    return BeautifulSoup(html, 'html.parser')


def get_item(soup, i):
    """Processes a soup from a Costco deals search and get's the i'th item.
    
    Args:
        - soup: a soup object from BeautifulSoup from a Costco deals search
        - i:    the index of the item to process
        
    Returns:
        - An Item object of the i'th item from the page, if it exists and has
          info, else None. The Item contains:
            - title:   str title of the item
            - img:     a url for the item's thumbnail image
            - price:   the item's price as a float
            - savings: the current savings on the item as a float
            - url:     url to access the item
    """
    try:
        desc = soup.find('span', {'automation-id': f'productDescriptionLabel_{i}'})
        if desc is None:
            return None
        title = desc.text.strip()
        url = desc.a['href']

        savings_desc = soup.find('p', {'automation-id': f'instantSavingsLinks_{i}'})
        if savings_desc is None:
            return None
        savings_desc = savings_desc.text.strip()
        if savings_desc[:7] != 'After $' or savings_desc[-4:] != ' OFF' or '-' in savings_desc:
            return None
        savings = float(savings_desc[7:-4].replace(',', ''))

        price_desc = soup.find('div', {'automation-id': f'itemPriceOutput_{i}'})
        if price_desc is None:
            return None
        price_desc = price_desc.text.strip()
        if price_desc is None or '-' in price_desc:
            return None
        price = float(price_desc[1:].replace(',', ''))

        img_desc = soup.find('input', {'automation-id': f'compareItem_{i}'})
        if img_desc is None:
            return None
        img = img_desc['onclick'].split("'")[3]

        return Item(title, img, price, savings, url)
    except Exception as e:
        print(f'Error with scraping {i}')
        raise e


def make_img(item, file_name, font_file='Menlo.ttc', folder='images/'):
    text = item.name.upper()
    thumbnail = item.image
    price = item.cost
    discount = item.discount
    up_arrow = "\u2193"
    img = Image.new('RGB', (1200, 900))
    r = requests.get(thumbnail, headers={"User-Agent":"Mozilla/5.0"})
    costco_img = Image.open(BytesIO(r.content))
    img.paste(costco_img, (100, 400))
    draw = ImageDraw.Draw(img)
    title_font = ImageFont.truetype(font_file, 80)
    price_font = ImageFont.truetype(font_file, 70)
    color = "#FFFFFF"
    draw.text((100, 100), text[0:21], fill=color, font=title_font)
    draw.text((100, 200), text[21:42], fill=color, font=title_font)
    draw.text((500, 500), f'${price:.2f}{up_arrow}${discount:.2f}', fill=color, font=price_font)
    # img = img.resize((1200, 900))
    if not os.path.exists(folder):
        os.makedirs(folder)
    img.save(folder + file_name)
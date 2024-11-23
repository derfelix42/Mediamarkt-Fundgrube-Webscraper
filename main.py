import requests
import time


def contains_all_keywords(name, keywords):
    name_lower = name.lower()
    for keyword in keywords:
        keyword_lower = keyword.lower()
        if keyword_lower not in name_lower:
            return False
    return True


def query_mediamarkt(limit, offset, brands):
    headers = {
        'sec-ch-ua': '\\"Not.A/Brand\\";v=\\"8\\", \\"Chromium\\";v=\\"114\\", \\"Google Chrome\\";v=\\"114\\"',
        'Referer': 'https://www.mediamarkt.de/de/data/fundgrube',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'sec-ch-ua-platform': '\\"macOS\\"',
    }

    params = {
        'limit': limit,
        'offset': offset,
        'outletIds': [],
        'brands': brands,
        'categorieIds': []
    }

    response = requests.get('https://www.mediamarkt.de/de/data/fundgrube/api/postings', params=params, headers=headers)
    return response


def scrape_mediamarkt(brands):
    limit = 50
    offset = 0

    fails = 0
    print("Scraping data...")

    product_list = []
    while True:
        try:
            resp = query_mediamarkt(limit=limit, offset=offset, brands=brands)
            if len(resp.text) > 0:
                json = resp.json()
                if len(json["postings"]) > 0:
                    # print(json)
                    product_list.extend(json["postings"])
                    print(" - found",len(product_list),"products already!")
                    time.sleep(2)
                    offset = offset + limit
                else:
                    break
            else:
                break
        except KeyboardInterrupt:
            print("Keyboard interrupt! breaking")
            break
        except:
            print("Failed connection", fails)
            fails += 1

            if fails > 5:
                break
    print("done!")
    return product_list


def filter_products(products, keywords, lowest_price, highest_price):
    matching_products = []
    for product in sorted(products, key=lambda item: float(item["price"])):
        if float(product["price"]) >= lowest_price and float(product["price"]) <= highest_price:
            for keyword in keywords:
                if contains_all_keywords(name=product["name"], keywords=keywords):
                    matching_products.append(product)
    return matching_products

def createLink(brand,outlet,category,old_price,price):
    # https://www.mediamarkt.de/de/data/fundgrube?outletIds=491&brands=SIGMA&categorieIds=CAT_DE_MM_523#:~:text=%E2%82%AC-,967,-%2C%E2%80%93
    # https://www.mediamarkt.de/de/data/fundgrube?outletIds=509&brands=SIGMA&categorieIds=CAT_DE_MM_523#:~:text=999%2C%E2%80%93-,900,-%2C%E2%80%93
    return f"https://www.mediamarkt.de/de/data/fundgrube?outletIds={outlet}&brands={brand}&categorieIds={category}#:~:text={old_price}%2C%E2%80%93-,{price},-%2C%E2%80%93"

def print_products(products):
    if (products != None) and (len(products) > 0):
        for product in products:
            print()
            print(f'[{product["price"]} €] {product["name"]} ({createLink(product["brand"]["name"], product["outlet"]["id"], product["top_level_catalog_id"],  str(product["price_old"])[:-3], str(product["price"])[:-3])})')
            print()
    else:
        print("No matching products")


def main():
    # configs
    brands = ["Sigma"]
    keywords = ["Objektiv", "Canon", "DG"]
    lowest_price = 1
    highest_price = 9999

    product_list = scrape_mediamarkt(brands=brands)
    product_list = filter_products(products=product_list, keywords=keywords, lowest_price=lowest_price, highest_price=highest_price)
    print_products(product_list)


if __name__ == '__main__':
    main()

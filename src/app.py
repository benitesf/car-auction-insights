from scraping.superbid import SuperbidScraper

import json
import time
import sys
import os

def main(url):
    scraper = SuperbidScraper()
    bids_data = scraper.get_bids(url)    

    for i in range(0, len(bids_data[0:2])):
        bid_details = scraper.get_bid_details(bids_data[i]["link"])
        bids_data[i]["bid_details"] = bid_details
        # print(bid_details)

    file_path_to_save = os.path.join(os.pardir, "data/raw/superbid/", "bids.json")
    save_bids(bids_data, file_path_to_save)

    scraper.close()

def save_bids(bids_data, file_to_save):
    with open(file_to_save, "w", encoding="utf-8") as f:
        json.dump(bids_data, f, ensure_ascii=False)

if __name__ == "__main__":
    main("https://www.superbid.com.pe/todos-eventos?filter=modalityId:[1,4];subMarketplaces.id:all;storeIds:[1261];isShopping:null&byPage=closedPage&pageNumber=1&pageSize=10000")

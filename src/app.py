from scraping.superbid import SuperbidScraper

import json
import time
import sys
import os

def main(url):
    """Main function to run the scraper"""
    # Initialize the Superbid scraper
    scraper = SuperbidScraper()

    # Get the bids data
    bids_data, not_found = scraper.get_bids(url)
    print(f"[INFO] Nº of found bids: {len(bids_data)} bids")
    print(f"[INFO] Nº of not found bids: {len(not_found)} bids")

    # Get the bid details
    for bid in bids_data:
        links_to_car_auctions = scraper.get_links_to_car_auctions(bid["link"])

        for link in links_to_car_auctions:
            car_auction_details = scraper.get_car_auction_details(link)
            bid_details = {
                "link_to_car_auction": link,
                "car_auction_details": car_auction_details
            }
            bid["bid_details"].append(bid_details)

        # print(json.dumps(bid_details, indent=2, ensure_ascii=False))

    file_path_to_save = os.path.join(os.pardir, "data/raw/superbid/", "bids.json")
    save_bids(bids_data, file_path_to_save)

    scraper.close()

def save_bids(bids_data, file_to_save):
    with open(file_to_save, "w", encoding="utf-8") as f:
        json.dump(bids_data, f, ensure_ascii=False)

if __name__ == "__main__":
    main("https://www.superbid.com.pe/todos-eventos?filter=modalityId:[1,4];subMarketplaces.id:all;storeIds:[1261];isShopping:null&byPage=closedPage&pageNumber=1&pageSize=10000")

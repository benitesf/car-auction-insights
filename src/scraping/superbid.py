from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import json
import time
import sys

class SuperbidScraper:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('start-maximized')
        self.chrome_options.add_argument('disable-infobars')
        self.chrome_options.add_argument("--disable-extensions")
        
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 2)

    @staticmethod
    def parse_static_content(html_content):
        """Parse static HTML content using BeautifulSoup"""
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup

    def get_dynamic_content(self, url):
        """Fetch dynamic content using Selenium"""
        try:
            self.driver.get(url)
            # Wait for page to load
            self.driver.implicitly_wait(8)
            return self.driver.page_source
        except Exception as e:
            print(f"[ERROR] Error fetching dynamic content: {e}")
            return None

    def wait_for_element(self, selector, by=By.CSS_SELECTOR):
        """Wait for element to be present on page"""
        try:
            element = self.wait.until(
                EC.presence_of_element_located((by, selector))
            )
            return element
        except Exception as e:
            print(f"[ERROR] Error waiting for element {selector}: {e}")
            return None

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

    def __del__(self):
        """Destructor to ensure browser is closed"""
        self.close()

    def get_bids(self, url):
        """Get all bids from the given URL"""
        html_content = self.get_dynamic_content(url)
        soup = self.parse_static_content(html_content)

        # Get all the bids
        bids = soup.find_all("div", class_="MuiGrid-root css-bf37vd")

        # Get information from each bid and save it to a json file
        bids_data = []
        not_found = []
        for bid in bids:
            try:
                bid_data = {
                    "name": bid.find("p", class_="MuiTypography-root MuiTypography-body1 jss206 css-z355qp").text,
                    "date": bid.find("p", class_="MuiTypography-root MuiTypography-body1 jss216 css-z355qp").text,
                    "link": bid.find("a")["href"],
                }
                bid_data["id"] = f"{bid_data['name']}_{bid_data['date']}"
                bids_data.append(bid_data)
            except:
                not_found.append(bid)
        
        # print("[DEBUG] Detailed bids data:")
        # for bid in bids_data:
        #     print(f"[DEBUG] {json.dumps(bid, indent=2, ensure_ascii=False).encode('utf-8').decode('utf-8')}")

        print(f"[INFO] Nº of found bids: {len(bids_data)} bids")
        print(f"[INFO] Nº of not found bids: {len(not_found)} bids")

        return bids_data

    def get_bid_details(self, url):
        """Get bid details from the given URL"""
        html_content = self.get_dynamic_content("https://www.superbid.com.pe" + url)
        soup = self.parse_static_content(html_content)

        # Get the list of links to car auctions
        links_to_car_auctions = soup.find_all("a", class_="jss630")
        print(f"[INFO] Nº of links to car auctions: {len(links_to_car_auctions)}")

        # Get the details of each car auction
        bid_details = []
        for link in links_to_car_auctions:
            car_auction_details = {
                "link_to_car": link["href"],
                "car_auction_details": self.get_car_auction_details("https://www.superbid.com.pe" + link["href"])
            }
            bid_details.append(car_auction_details)

        return bid_details

    def get_car_auction_details(self, url):
        """Get car auction details from the given URL"""
        html_content = self.get_dynamic_content(url)
        soup = self.parse_static_content(html_content)

        # Get the details of the car auction
        title_car_auction = soup.find("h1", class_="MuiTypography-root MuiTypography-h1 jss323 jss194 css-1yomz3x")
        panel_car_auction = soup.find("div", class_="offer-bid-panel")
        open_car_auction = soup.find("div", class_="MuiGrid-root MuiGrid-container MuiGrid-direction-xs-column css-12g27go")

        car_auction_details = {
            "title_car_auction": title_car_auction,
            "panel_car_auction": panel_car_auction,
            "open_car_auction": open_car_auction
        }

        return car_auction_details



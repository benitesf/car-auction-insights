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
            # Wait for the page to be fully loaded
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            return self.driver.page_source
        except Exception as e:
            print(f"[ERROR] Error fetching dynamic content: {e}")
            return None

    def get_dynamic_content_with_scroll(self, url, scroll_times=5):
        """Fetch dynamic content using Selenium with scroll"""
        try:
            self.driver.get(url)
            # Scroll to the bottom of the page
            for _ in range(scroll_times):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
            # Wait for the page to be fully loaded
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
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
        html_content = self.get_dynamic_content_with_scroll(url)
        soup = self.parse_static_content(html_content)

        # Get all the bids
        bids = soup.find_all("div", class_="MuiGrid-root css-bf37vd")

        # Get information from each bid and save it to a json file
        bids_data = []
        not_found = []
        if len(bids) > 0:
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
        else:
            print("[ERROR] No bids found")        

        return bids_data, not_found

    def get_links_to_car_auctions(self, url):
        """Get links to car auctions from the given URL"""
        n_try = 0
        while n_try < 5:
            html_content = self.get_dynamic_content_with_scroll("https://www.superbid.com.pe" + url)
            soup = self.parse_static_content(html_content)
            
            # Get the list of links to car auctions
            links_to_car_auctions = soup.find_all("a", class_="jss630")
            
            if len(links_to_car_auctions) > 0:
                print(f"[SUCCESS] Nº of links to car auctions: {len(links_to_car_auctions)}")
                break
            else:
                print(f"[INFO] No links to car auctions found")
                print(f"[INFO] Trying again... {n_try + 1} of 5")
                n_try += 1

        links_to_car_auctions = []
        for link in links_to_car_auctions:
            links_to_car_auctions.append(link["href"])

        return links_to_car_auctions

    def get_car_auction_details(self, url):
        """Get car auction details from the given URL"""
        html_content = self.get_dynamic_content_with_scroll("https://www.superbid.com.pe" + url, scroll_times=10)
        soup = self.parse_static_content(html_content)

        # Get the details of the car auction
        # Get text from h1 title if it exists, otherwise None
        title_element = soup.find("h1", class_="MuiTypography-root MuiTypography-h1 jss323 jss194 css-1yomz3x")
        if title_element:
            title = title_element.text
        else:
            title = None

        # Get details from the offer bid panel
        offer_bid_panel = soup.find("div", class_="offer-bid-panel")
        
        close_date = None
        start_date = None
        visits = None
        participants = None
        number_of_offers = None
        offer = None
        currency = None
        winner = None

        if offer_bid_panel:
            dates_panel = offer_bid_panel.find_all("div", class_="panel-content-date")
            if dates_panel and len(dates_panel) == 2:
                close_date = dates_panel[0].find("span", class_="value closingdate closing-datetime").text
                start_date = dates_panel[1].find("span", class_="value closingdate closing-datetime").text
            else:
                print("[ERROR] Dates panel not found")

            statistics_panel = offer_bid_panel.find("div", class_="panel-properties-statistics")
            if statistics_panel:
                statistics_items = statistics_panel.find_all("div", class_="propertie-item")
                if statistics_items and len(statistics_items) == 3:
                    visits = statistics_items[0].find("span", class_="label").text + ": " + statistics_items[0].find("span", class_="value").text
                    participants = statistics_items[1].find("span", class_="label").text + ": " + statistics_items[1].find("span", class_="value").text
                    number_of_offers = statistics_items[2].find("span", class_="label").text + ": " + statistics_items[2].find("span", class_="value").text
                else:
                    print("[ERROR] Statistics items not found")
            else:
                print("[ERROR] Statistics panel not found")

            offer_panel = offer_bid_panel.find("div", class_="panel-properties-ganhador panel-properties-ganhador-visitor")
            if offer_panel:
                offer_item = offer_panel.find_all("div", class_="propertie-item")
                if offer_item and len(offer_item) > 0:
                    offer = offer_item[0].find("span", class_="label").text + offer_item[0].find("span", class_="lance-atual").text
                    currency = offer_item[0].find("span", class_="codigo-moeda").text
                else:
                    print("[ERROR] Offer item not found")
            else:
                print("[ERROR] Offer panel not found")

            winner_panel = offer_bid_panel.find("div", class_="propertie-item label-ganhador")
            if winner_panel:
                winner = winner_panel.find("span", class_="label").text + winner_panel.find("span", class_="value").text
            else:
                print("[ERROR] Winner panel not found")
            
        else:
            print("[ERROR] Offer bid panel not found")

        # Get details from the open car auction
        open_auction_panel = soup.find("div", class_="MuiGrid-root css-rfnosa")

        company = None
        seller = None
        initial_offer = None

        if open_auction_panel:
            open_auction_items = open_auction_panel.find_all("span", class_="jss183")
            if open_auction_items and len(open_auction_items) == 3:
                company = open_auction_items[0].text
                seller = open_auction_items[1].text
                initial_offer = open_auction_items[2].text
            else:
                print("[ERROR] Open auction items not found")
        else:
            print("[ERROR] Open auction panel not found")

        # Get description from the car auction
        description_panel = soup.find("div", class_="react-swipeable-view-container")
        if not description_panel:
            print("[ERROR] Description panel not found")
            return None

        description_container = description_panel.find("div", class_="jss182")
        description = []

        if description_container:
            for element in description_container.children:
                if element.name == 'p':
                    description.append(' '.join(element.stripped_strings))
                elif element.name == 'ul':
                    for li in element.find_all('li'):
                        description.append(' '.join(li.stripped_strings))
                elif element.name == 'h1':
                    description.append(' '.join(element.stripped_strings))
        else:
            print("[ERROR] Description container not found")

        # Get information from the car auction
        information_container = description_panel.find_all("ul", class_="sb-list-info")
        information = []

        if information_container:
            for element in information_container:
                for li in element.find_all('li'):
                    information.append(' '.join(li.stripped_strings))
        else:
            print("[ERROR] Information container not found")

        car_auction_details = {
            "title": title,
            "close_date": close_date,
            "start_date": start_date,
            "visits": visits,
            "participants": participants,
            "number_of_offers": number_of_offers,
            "offer": offer,
            "currency": currency,
            "winner": winner,
            "company": company,
            "seller": seller,
            "initial_offer": initial_offer,
            "description": description,
            "information": information
        }

        return car_auction_details



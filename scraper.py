import time
from datetime import datetime
import requests  # needs to be installed !!!
from bs4 import BeautifulSoup  # needs to be installed !!!!
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def cheapest_ticket(origin, destination, date, departure_time, ticket_type):
    """
        Function that finds the cheapest ticket from start to destination using web scraping.

        :param origin: The starting location the user is going to get a train from. Location in abbreviation form for train
        e.g. Norwich is NRW
        :param destination: This is the location that the user is trying to get to
        :param leave_date: The leaving date for train
        :param leave_time: The leaving time for train. Time needs to be in time of interval of 15 minutes: eg: 11:00,11:15,
        11:30 or 11:45
        :return: tuple that contains:
                string of amount for cheapest ticket
                string of leave time
                string of arrival time
                string containing hyperlink to get ticket
        """
    # time - format 1200
    # date - format - 140523 or today
    # origin - crs code
    # destination - crs code
    url = "https://ojp.nationalrail.co.uk/service/timesandfares/[ORIGIN]/[DESTINATION]/[DATE]/[TIME]/dep"
    # EXAMPLE URL = https://ojp.nationalrail.co.uk/service/timesandfares/NRW/BTN/140523/1630/dep
    url = url.replace("[ORIGIN]", origin)
    url = url.replace("[DESTINATION]", destination)
    url = url.replace("[TIME]", departure_time.strftime("%H%M"))
    url = url.replace("[DATE]", date.strftime("%d%m%y"))
    get_national_rail = requests.get(url)
    soup = BeautifulSoup(get_national_rail.content, "html.parser")

    cheapest_section = soup.find("td", {"class": "fare has-cheapest"})  # find the section where it has the cheapest fare
    label = cheapest_section.find("label")  # find the first label on the webpage
    cost = label.text.strip()  # remove whitespace

    ticket_section = cheapest_section.parent
    actual_dep_time = ticket_section.find("div", {"class": "dep"}).text.strip()
    actual_arrival_time = ticket_section.find("div", {"class": "arr"}).text.strip()
    link = find_ticket_link(url)

    return cost, actual_dep_time, actual_arrival_time, link

def find_ticket_link(url):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    time.sleep(3)  # need to wait for the page to load, then accept the cookies
    driver.find_element("xpath", "//*[@id='onetrust-accept-btn-handler']").click()
    driver.find_element("xpath", "//button[@class = 'b-y buy-now']").click()
    driver.switch_to.window(driver.window_handles[1])  # change to other window
    time.sleep(15)  # wait until the page with the tickets has loaded
    return driver.current_url



def main():
    #convert string into time object:
    time_string = "11:00"
    time_value = datetime.strptime(time_string, '%H:%M').time()
    print(time_value.hour)

    date_string = "23/05/2023"
    date_value = datetime.strptime(date_string, '%d/%m/%Y').date()
    print(date_value.month)

    #  make sure these are all valid inputs! - all in the future, and are real dates as well as real places to go to and
    #  from !



    print(cheapest_ticket("NRW", "KGX", date_value, time_value,"dep"))


if __name__ == "__main__":
    main()


'''
from bs4 import BeautifulSoup
import requests
def scrape_ticket(origin, destination, departure_time, date):
    #time - format 1200
    #date - format - 140523 or today
    #origin - crs code
    #destination - crs code

    #EXAMPLE URL = https://ojp.nationalrail.co.uk/service/timesandfares/NRW/BTN/140523/1630/dep
    url = "https://ojp.nationalrail.co.uk/service/timesandfares/{}/{}/{}/{}/dep".format(origin, destination, date, departure_time)

    #retrieve html from the url
    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')

    #loop through table and get all times and prices
    ticket_details = []
    table_elements = soup.find('table', {'id': 'oft'})
    for row in table_elements.find_all('tr'):
        dep = row.find('div', {'class': 'dep'})
        arr = row.find('div', {'class': 'arr'})
        price = row.find('label', {'class': 'opsingle'})

        #if all details are complete, they are added to a list of all ticket details
        if dep and arr and price:
            ticket_details.append({"departure": dep.text.strip(), "arrival": arr.text.strip(), "price": price.text.strip(), "url": url})

    #loop through all tickets and store the one with the lowest price in lowest_ticket
    lowest_ticket = None
    lowest_price = None
    for ticket in ticket_details:
        #convert string price to float
        current_price = float(ticket['price'].replace('£', ''))

        if lowest_price == None:
            lowest_ticket = ticket
            lowest_price = current_price
        elif lowest_price > current_price:
            lowest_ticket = ticket
            lowest_price = current_price

    return lowest_ticket


#scrape_ticket("NRW","BTN","1200","140523")
'''

import time
import scrapy
from datetime import datetime

import chromedriver
import requests  # needs to be installed !!!
from bs4 import BeautifulSoup  # needs to be installed !!!!
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def cheapest_ticket(origin, destination, date, departure_time):
    """
        Function that finds the cheapest single ticket from start to destination using web scraping.
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
    url = url.replace("[TIME]", departure_time)
    url = url.replace("[DATE]", date)
    get_national_rail = requests.get(url)
    soup = BeautifulSoup(get_national_rail.content, "html.parser")

    cheapest_section = soup.find("td", {"class": "fare has-cheapest"})  # find the section where it has the cheapest
    # fare
    if cheapest_section is None:
        return "No tickets could be found for this date and time. Please enter something else"
    label = cheapest_section.find("label")  # find the first label on the webpage
    cost = label.text.strip()  # remove whitespace

    ticket_section = cheapest_section.parent
    actual_dep_time = ticket_section.find("div", {"class": "dep"}).text.strip()
    actual_arrival_time = ticket_section.find("div", {"class": "arr"}).text.strip()
    link = url#find_ticket_link(url)
    #find_ticket_link(url)

    return {'price': cost, 'departure': actual_dep_time, 'arrival': actual_arrival_time, 'url': link}

def finding_return_ticket_price(origin, destination, leave_date, leave_time, return_date, return_time):
    """
    Function that finds the cheapest return ticket from start to destination using web scraping.

    :param origin:
    :param destination:
    :param leave_date:
    :param return_date:
    :param leave_time:
    :param return_time:
    :return:
    """

    url = "https://ojp.nationalrail.co.uk/service/timesandfares/[ORIGIN]/[DESTINATION]/[LEAVE_DATE]/[LEAVE_TIME]/dep/[RETURN_DATE]/[RETURN_TIME]/dep"

    url = url.replace("[ORIGIN]", origin)
    url = url.replace("[DESTINATION]", destination)
    url = url.replace("[LEAVE_DATE]", leave_date)
    url = url.replace("[LEAVE_TIME]", leave_time)
    url = url.replace("[RETURN_DATE]", return_date)
    url = url.replace("[RETURN_TIME]", return_time)

    # try another url: examples
    url = "https://ojp.nationalrail.co.uk/service/timesandfares/NRW/KGX/010523/1615/dep/030523/2330/dep"
    #url = "https://ojp.nationalrail.co.uk/service/timesandfares/NRW/KGX/today/1615/dep/tomorrow/1630/dep"
    print(url)

    get_national_rail = requests.get(url)
    soup = BeautifulSoup(get_national_rail.content, "html.parser")

    cheapest_button = soup.find("button", {"id": "buyCheapestButton"})
    cheapest = cheapest_button.find("span").text.strip()

    both_cheapest = soup.findAll("td", {"class": "fare has-cheapest"})

    ticket_section = both_cheapest[0].parent
    predicted_leave_time = ticket_section.find("div", {"class": "dep"}).text.strip()
    predicted_arrival_time = ticket_section.find("div", {"class": "arr"}).text.strip()

    if both_cheapest.__len__() > 1:  # if it is two different tickets, there will be two tickets annotated with cheapest
        ticket_section= both_cheapest[1].parent
        predicted_r_leave_time = ticket_section.find("div", {"class": "dep"}).text.strip()
        predicted_r_arrival_time = ticket_section.find("div", {"class": "arr"}).text.strip()


    else:  # otherwise it is a return ticket
        return_selected = soup.find("label", {"id":"returnFareLabel"})
        return_ticket = return_selected.parent.parent.parent
        predicted_r_leave_time = return_ticket.find("div", {"class": "dep"}).text.strip()
        predicted_r_arrival_time = return_ticket.find("div", {"class": "arr"}).text.strip()

    ticket_price = cheapest.split("£ ")[1]  # split the string where it states the price (there is also a space after £
    print("Cheapest ticket is at --",ticket_price)
    print("leave time: ", predicted_leave_time, "  arrival time: ", predicted_arrival_time, "\npredicted leave return"
    "time: ", predicted_r_leave_time, " predicted arrival return time: ", predicted_r_arrival_time)



    # select the span value in the button -> id = "buyCheapestButton"
    # This is because it could have two single trains OR a return ticket selected as the cheapest option!!




def find_ticket_link(url):
    driver = webdriver.Chrome()
    #chromedriver_binary.add_chromedriver_to_path()

    driver.get(url)
    time.sleep(3)  # need to wait for the page to load, then accept the cookies
    driver.find_element("xpath", "//*[@id='onetrust-accept-btn-handler']").click()
    driver.find_element("xpath", "//button[@class = 'b-y buy-now']").click()
    #driver.switch_to.window(driver.window_handles[1])  # change to other window
    time.sleep(15)  # wait until the page with the tickets has loaded
    return driver.current_url

def web_scraper_departure(url):
    """
    This function is able to scrape the website using selenium to find the cheapest ticket out of the entire day.

    :param url: The website that is going to be scraped
    :return: The amount it costs for the
    """
    print(url)
    options = Options()
    #options.add_argument("--headless")  #TODO put this back in to make it headless!!!
    driver = webdriver.Chrome(options = options)
    driver.get(url)
    time.sleep(3)
    try:
        driver.find_element("xpath", "//*[@id='onetrust-accept-btn-handler']").click()  # accept cookies to website
    except:
        pass

    try:
        if driver.find_element("xpath", "//p[@class='popup-text']").text == "There are no outbound journeys available on the day you selected, we have returned the next available journey.":
            print("there are no journeys available for this date and time, please try another")
            return "there are no journeys available for this date and time, please try another"
    except:
        pass

    try:
        driver.find_element("xpath","/html/body/div[4]/div[2]/div[2]/div/div[2]/a/span").click()  # close other pop up
    except:
        pass

    while True:
        time.sleep(2)
        try:
            driver.find_element("xpath",
                                "/html/body/div[4]/div[2]/div[2]/div/div[2]/a/span").click()  # close other pop up
        except:
            pass
        try:
            driver.find_element("xpath","//button[@id = 'fsrFocusFirst']").click()  # close pop up reviewing website
        except:
            pass
        try:
            dayheading = driver.find_element("xpath", "//*[@class='day-heading']")  # this is another type of day heading that the website has implemented
            break
        except:
            pass


        try:
            dayheading = driver.find_element("xpath", "//*[@class='ajaxRow day-heading']")  # the next day is now on the page
            break
        except:
            try:
                driver.find_element("xpath","//a[@href='/service/timesandfares/laterOutbound']").click()
                print("later tickets are found")
                #find the later tickets
            except:
                pass
    #<tr class="ajaxRow day-heading"><th scope="rowgroup" colspan="10"><p>Thu 20 Apr</p></th></tr>
    all_tickets = driver.find_element("xpath","/html/body/div[5]/div[5]/div[2]/div[1]/div/form[3]/div[3]/table/tbody")
    cheapest = 1000000.00
    for ticket in all_tickets.find_elements("xpath","./tr"):
        if ticket == dayheading:
            break  # we are now going to the next days tickets - which we do not want!!!!

        else:
            try:
                for line in ticket.text.splitlines():
                    if line[0] == "£":
                        compare = float(line[1:])
                        if cheapest > compare:
                            cheapest = compare
            except:
                pass
    print("cheapest ticket for the day is: £", cheapest)



    time.sleep(10000)





#  --------- redundant code - cannot load both the leavind and arriving trains
"""
def web_scraper_return_ticket(url):  ####NOT THIS FUNCTION IT STINKS
    print("do something similar to other function")
    print(url)
    options = Options()
    # options.add_argument("--headless")  #TODO put this back in to make it headless!!!
    driver = webdriver.Chrome(options=options)
    driver.get(url)


    WebDriverWait(driver, 20).until(expected_conditions.element_to_be_clickable(
        ("xpath", "//button[@id = 'onetrust-accept-btn-handler']"))).click()

    outwards_table = driver.find_element("xpath", "//table[@id = 'oft']")
    inbound_table = driver.find_element("xpath","//table[@id = 'ift']")
    while True:  # while loop contains going keep clicking the more tickets option until the next day appears for the outbound trains
        time.sleep(1)
        try:
            o_dayheading = outwards_table.find_element("xpath", ".//*[@class='ajaxRow day-heading']")  # the next day is now on the page
            break
        except:
            try:
                driver.find_element("xpath", "//a[@href='/service/timesandfares/laterOutbound']").click()  # try and click the later bounds button
                print("later tickets are found")
            except:
                pass

        try:
            driver.find_element("xpath", "//button[@id='fsrFocusFirst']").click()
        except:
            pass

        try:
            driver.find_element("xpath", "//button[@id='onetrust-accept-btn-handler']").click()
        except:
            pass

        #try:
        #    driver.find_element("xpath","//p[@class = 'popup-text'")

        try:
            driver.find_element("xpath", "//a[@href='#']").click()
        except:
            pass

    while True:
        time.sleep(1)
        try:
            i_dayheading = inbound_table.find_element("xpath", ".//*[@class='ajaxRow day-heading']")  # the next day is now on the page
            print("break")
            break
        except:
            try:
                driver.find_element("xpath", "//a[@href='/service/timesandfares/laterInbound']").click()  # try and click the later bounds button
                print("later inbound tickets are found")
            except:
                pass

        #ajaxRow day-heading


        try:
            driver.find_element("xpath", "//button[@id='onetrust-accept-btn-handler']").click()
        except:
            pass
        try:
            driver.find_element("xpath", "//a[@href='#']").click()
        except:
            pass


    time.sleep(10000)

    #click onetrust-accept-btn-handler

"""
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



    #print(cheapest_ticket("NRW", "KGX", date_value.strftime("%d%m%y"), time_value.strftime("%H%M")))

    #web_scraper_departure("https://ojp.nationalrail.co.uk/service/timesandfares/NRW/KGX/today/2030/dep")
    #web_scraper_return_ticket("https://ojp.nationalrail.co.uk/service/timesandfares/NRW/KGX/today/1615/dep/250423/1815/dep")
    finding_return_ticket_price("NRW", "KGX", "010523", "1615", "030523", "2030")

    #button id = "buyCheapestButton"

if __name__ == "__main__":
    main()
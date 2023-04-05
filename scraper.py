from bs4 import BeautifulSoup
from selenium import webdriver
import chromedriver_binary
import requests
def scrape_ticket(origin, destination, departure_time, date):
    #time - format 1200
    #date - format - 140523 or today
    #origin - crs code
    #destination - crs code
    url = "https://ojp.nationalrail.co.uk/service/timesandfares/[ORIGIN]/[DESTINATION]/[DATE]/[TIME]/dep"
    #EXAMPLE URL = https://ojp.nationalrail.co.uk/service/timesandfares/NRW/BTN/140523/1630/dep
    url = url.replace("[ORIGIN]", origin)
    url = url.replace("[DESTINATION]", destination)
    url = url.replace("[TIME]", departure_time)
    url = url.replace("[DATE]", date)

    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')


    ticket_details = []
    table_elements = soup.find('table', {'id': 'oft'})
    for row in table_elements.find_all('tr'):

        #print(row)
        dep = row.find('div', {'class': 'dep'})
        arr = row.find('div', {'class': 'arr'})
        price = row.find('label', {'class': 'opsingle'})


        if dep and arr and price:
            ticket_details.append({"departure": dep.text.strip(), "arrival": arr.text.strip(), "price": price.text.strip(), "url": url})

        lowest_ticket = None
        lowest_price = None
        for ticket in ticket_details:
            if lowest_price == None:
                lowest_ticket = ticket
            elif lowest_price<ticket['price']:
                lowest_ticket = ticket


    return lowest_ticket


#scrape_ticket("NRW","BTN","1200","140523")

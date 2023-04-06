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

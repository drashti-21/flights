import requests
from parsel import Selector
import json
from datetime import datetime



def get_flights_json(flight_type):
    cookies = {
        '_gcl_au': '1.1.1367096178.1747378943',
        '_gid': 'GA1.3.2043607505.1747378943',
        '_fbp': 'fb.2.1747378943300.950273470516633372',
        'pll_language': 'pl',
        '_ga_17WK6KG66C': 'GS2.1.s1747375201$o1$g1$t1747379036$j0$l0$h0',
        '_ga': 'GA1.1.1672527434.1747375201',
        '_ga_8PSLTPFDRY': 'GS2.3.s1747375201$o1$g1$t1747379037$j0$l0$h0',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cache-control': 'max-age=0',
        'if-none-match': '"182837-1747379018;br"',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36',
    }
    response = requests.get('https://airport.com.pl/loty/tablica-przylotow-odlotow/', cookies=cookies, headers=headers)
    print(response.status_code)
    if response.status_code != 200:
        return json.dumps({"error": "Failed to fetch data"}, ensure_ascii=False)
    html_content = response.text
    selector = Selector(text=html_content)
    # Use today's date
    flight_date = datetime.now().strftime("%Y-%m-%d")

    def extract_flights(table_id):
        rows = selector.xpath(f'//div[@id="{table_id}"]//table//tbody//tr')
        flights = []
        for row in rows:
            time_str = row.xpath('./td[@class="date"]/strong/text()').get(default='').strip()
            flight_number = row.xpath('./td[2]/text()').get(default='').strip()
            # Remove all spaces from flight_number
            flight_number = flight_number.replace(" ", "")
            direction = row.xpath('./td[3]/text()').get(default='').strip()
            status = row.xpath('./td[contains(@class,"stateOfFlight")]/text()').get(default='').strip()
            # Remove zero if the third letter is "0"
            if len(flight_number) > 2 and flight_number[2] == "0":
                flight_number = flight_number[:2] + flight_number[3:]
            # Convert time to ISO 8601 format if possible
            if time_str:
                try:
                    dt = datetime.strptime(f"{flight_date} {time_str}", "%Y-%m-%d %H:%M")
                    scheduled_time = dt.strftime("%Y-%m-%dT%H:%M:00.000")
                except Exception:
                    scheduled_time = ""
            else:
                scheduled_time = ""
            arrival_airport = direction if direction else "Unknown Airport"
            flights.append({
                "flight_number": flight_number,
                "callsign": flight_number,
                "arrival_airport": arrival_airport,
                "scheduled_arrival_time": scheduled_time,
                "status": status
            })
        return flights

    arrivals = extract_flights("arrivalsInfo")
    departures = extract_flights("departuresInfo")

    if flight_type == "arrivals":
        return json.dumps(arrivals, ensure_ascii=False, indent=2)
    elif flight_type == "departures":
        return json.dumps(departures, ensure_ascii=False, indent=2)
    else:
        result = {
            "Arrivals": arrivals,
            "Departures": departures
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

# Example usage:
if __name__ == "__main__":
    flight_type = "departures"  # or "arrivals"
    print(get_flights_json(flight_type))

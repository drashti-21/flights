import requests
from parsel import Selector
import json
from datetime import datetime

def get_modlin_flights(flight_type="arrivals"):
    cookies = {
        'cf_clearance': 'tr_C09bdjV8T0XFZBMlu38q4a4hdqU5dPMjjAmhkwio-1747391152-1.2.1.1-ikAjwiYOtIeC9cxvjpovirr.peu2PB.41HfguKaMOdIFyFvxiOSkleQySBng0wUa6i.VriGU7TYDO85gRRJS0u8mSiJppQny58klBjA6N.5P1J5MIuyOkW7wzKNcLyryiWVbHYhl_oAUuq9ah3xW1K_kXloIlC8vyDxadIfEUYvCmcsBqw0X2MNQq3RgPp95CCSI8EIje8egub3LKvrforqqmdmOy0hotJC0S5GT4aPnqu5FDxv88FKV_.4vms.jvvj1tklvZVvc.a2Gz8PxJ_CKIUFgkUKD0uKOLQSuwesIMD4b6U.H45cMVeQF8f6OKcB_R56y6EAKzXAAa_he6yqXtnov07P5BUSjestchDpJ69.6ejJgY7H4MUHvfIVd',
        'has_js': '1',
        '_ga': 'GA1.2.579128762.1747390912',
        '_gid': 'GA1.2.1064169867.1747390912',
        '_gat': '1',
        '_ga_D13LE4RY3B': 'GS2.2.s1747390916$o1$g1$t1747390936$j0$l0$h0',
    }
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'referer': 'https://www.modlinairport.pl/pasazer/rozklad-lotow?__cf_chl_tk=mkaqHNd3T4d.ryeGbsUOFOXUG6W3mqMG0RWTStetY0Q-1747382308-1.0.1.1-f.NPAPTBxgYJsINxacaKoVdEBM2N7MCtSSOGunvGwTA',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-arch': '""',
        'sec-ch-ua-bitness': '"64"',
        'sec-ch-ua-full-version': '"136.0.7103.93"',
        'sec-ch-ua-full-version-list': '"Chromium";v="136.0.7103.93", "Google Chrome";v="136.0.7103.93", "Not.A/Brand";v="99.0.0.0"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-model': '"Nexus 5"',
        'sec-ch-ua-platform': '"Android"',
        'sec-ch-ua-platform-version': '"6.0"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36',
    }
    proxy_url = 'http://api.scrape.do/?token=2d76727898034978a3091185c24a5df27a030fdc3f8&super=true&url=https://www.modlinairport.pl/pasazer/rozklad-lotow&geoCOde=pl'
    response = requests.get(proxy_url, cookies=cookies, headers=headers)
    html = response.text
    with open("modlinairport_response.html", "w", encoding="utf-8") as f:
        f.write(html)

    selector = Selector(text=html)
    today = datetime.now().strftime("%Y-%m-%d")
    arrivals = []
    for row in selector.xpath('//table[contains(@class, "arrivals-table")]/tbody/tr[position()>1]'):
        numer_lotu = row.xpath('./td[1]/text()').get(default='').strip()
        numer_lotu = numer_lotu.replace(" ", "")
        if len(numer_lotu) > 2 and numer_lotu[2] == "0":
            numer_lotu = numer_lotu[:2] + numer_lotu[3:]
        z = row.xpath('./td[2]/text()').get(default='').strip()
        godzina = row.xpath('./td[3]/text()').get(default='').strip()
        status = row.xpath('./td[4]//div[@class="status-flight"]/text()').get(default='').strip()
        if godzina:
            scheduled_time = godzina
        else:
            scheduled_time = ""
        if numer_lotu:
            arrivals.append({
                "flight_number": numer_lotu,
                "callsign": numer_lotu,
                "arrival_airport": z,
                "scheduled_arrival_time": scheduled_time,
                "status": status
            })
    departures = []
    for row in selector.xpath('//table[contains(@class, "departures-table")]/tbody/tr[position()>1]'):
        numer_lotu = row.xpath('./td[1]/text()').get(default='').strip()
        numer_lotu = numer_lotu.replace(" ", "")
        if len(numer_lotu) > 2 and numer_lotu[2] == "0":
            numer_lotu = numer_lotu[:2] + numer_lotu[3:]
        do = row.xpath('./td[2]/text()').get(default='').strip()
        godzina = row.xpath('./td[3]/text()').get(default='').strip()
        status = row.xpath('./td[4]//div[@class="status-flight"]/text()').get(default='').strip()
        if godzina:
            scheduled_time = godzina
        else:
            scheduled_time = ""
        if numer_lotu:
            departures.append({
                "flight_number": numer_lotu,
                "callsign": numer_lotu,
                "arrival_airport": do,
                "scheduled_arrival_time": scheduled_time,
                "status": status
            })
    if flight_type == "arrivals":
        return json.dumps(arrivals, ensure_ascii=False, indent=2)
    elif flight_type == "departures":
        return json.dumps(departures, ensure_ascii=False, indent=2)
    else:
        return json.dumps({"arrivals": arrivals, "departures": departures}, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    print(get_modlin_flights("arrivals"))
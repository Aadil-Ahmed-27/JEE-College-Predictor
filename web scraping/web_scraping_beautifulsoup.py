import requests
import pandas as pd
from bs4 import BeautifulSoup

url = "https://josaa.admissions.nic.in/applicant/SeatAllotmentResult/CurrentORCR.aspx"

params = {
    "ctl00$ContentPlaceHolder1$ddlInstype": "IIT",
    "ctl00$ContentPlaceHolder1$ddlInstitute": "ALL",
    "ctl00$ContentPlaceHolder1$ddlBranch": "ALL",
    "ctl00$ContentPlaceHolder1$ddlSeattype": "ALL",
    "ctl00$ContentPlaceHolder1$btnSubmit": "Submit"
}

rounds = [
    "2",
    "3",
    "4",
    "5",
]
def josaa_scrape(Round):
    """
    Sample usage: df = josaa_scrape("1")
    df.info()
    """
    with requests.Session() as s:
        R = s.get(url)
        if R.status_code != 200:
            print(f"Failed to fetch data. Status Code: {R.status_code}")
            exit()

        data = {}

        data.update({tag['name']: tag['value'] for tag in BeautifulSoup(R.content, 'lxml').select('input[name^=__]')})
        data["ctl00$ContentPlaceHolder1$ddlroundno"] = Round
        R = s.post(url, data=data)

        for key, value in params.items():
            data.update({tag['name']: tag['value'] for tag in BeautifulSoup(R.content, 'lxml').select('input[name^=__]')})
            data[key] = value
            R = s.post(url, data=data)
        
        with open("response.html", "w", encoding="utf-8") as f:
            f.write(R.text)

        print("Saved response.html. Open it in a browser to inspect the table.")
    

    table = BeautifulSoup(R.text, 'lxml').find(id = 'ctl00_ContentPlaceHolder1_GridView1')
    if table is None:
        print("Table not found! Check the webpage structure or response.")
        exit()  # Stop execution if table is missin
    df = pd.read_html(table.prettify())[0]
    df.dropna(inplace = True, how="all")

    return df

df = josaa_scrape(1)
df.info()
df.to_csv("nwjosaa2024.csv",mode='a',index=False, header=False)
print("Round 1,Saved to nwjosaa2024.csv")

for round in rounds:
    df = josaa_scrape(round)
    df.info()
    df.to_csv("nwjosaa2024.csv",mode='a',index=False, header=False)
    print(f"Round {round},Saved to nwjosaa2024.csv")

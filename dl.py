import csv
import xml.etree.ElementTree as ET
import itertools
import os
import datetime as dt

DATA_URL = "https://szrcr.cz/images/Data/semafor.xml"
AVAILABILITY_FILENAME = "dostupnost.csv"
TRANSACTIONS_FILENAME = "transakce.csv"

AVAILABILITY_HEADER = ["od", "do", "ISZR", "ROB", "ROS", "RPP", "RUIAN", "ORG"]
TRANSACTIONS_HEADER = ["datum", "pocet"]

if __name__ == "__main__":
    with open("semafor.xml", "r") as f:
        data = f.read()

    availabilities = []
    if os.path.isfile(AVAILABILITY_FILENAME):
        with open(AVAILABILITY_FILENAME, "r") as f:
            cr = csv.DictReader(f)
            availabilities = list(cr)

    transactions = []
    if os.path.isfile(TRANSACTIONS_FILENAME):
        with open(TRANSACTIONS_FILENAME, "r") as f:
            cr = csv.DictReader(f)
            transactions = list(cr)

    root = ET.fromstring(data)
    for el in root:
        if el.tag == "DostupnostRegistruProcenta":
            rows = el.findall("Data")
            assert len(rows) == 6
            availability = {
                "od": el.attrib["DostupnostOd"],
                "do": el.attrib["DostupnostDo"],
            }
            for row in rows:
                assert len(row.attrib) == 1, row.attrib
                key = next(iter(row.attrib))
                val = row.attrib[key]
                availability[key] = val

            assert set(availability.keys()) == {
                "od",
                "do",
                "ISZR",
                "ROB",
                "ROS",
                "RPP",
                "RUIAN",
                "ORG",
            }, availability.keys()
            availabilities.append(availability)

        if el.tag == "TransakceGraf":
            rows = el.findall("Data")
            for row in rows:
                date_raw = row.attrib["Datum"]
                hour = row.attrib["Hodina"]
                count = row.attrib["Pocet"]

                assert date_raw.endswith(" 0:00:00")
                date = dt.datetime.strptime(date_raw.partition(" ")[0], "%d.%m.%Y")
                date = date.replace(hour=int(hour)).isoformat()
                transactions.append({"datum": date, "pocet": count})

    # dedupe and sort first
    av_keyfunc = lambda x: (x["od"], x["do"])
    availabilities.sort(key=av_keyfunc)
    availabilities = [
        list(j[1])[-1] for j in itertools.groupby(availabilities, key=av_keyfunc)
    ]
    availabilities.sort(key=av_keyfunc)
    with open(AVAILABILITY_FILENAME, "w") as f:
        cw = csv.DictWriter(f, fieldnames=AVAILABILITY_HEADER)
        cw.writeheader()
        cw.writerows(availabilities)

    t_keyfunc = lambda x: x["datum"]
    transactions.sort(key=t_keyfunc)
    transactions = [
        list(j[1])[-1] for j in itertools.groupby(transactions, key=t_keyfunc)
    ]
    transactions.sort(key=t_keyfunc)
    with open(TRANSACTIONS_FILENAME, "w") as f:
        cw = csv.DictWriter(f, fieldnames=TRANSACTIONS_HEADER)
        cw.writeheader()
        cw.writerows(transactions)

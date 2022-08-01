import requests
import json
import sqlite3
import hashlib
import argparse
import os

url = 'https://www.rightmove.co.uk/api/_search?locationIdentifier={loc}&minBedrooms={rooms}&maxPrice={price}&numberOfPropertiesPerPage=24&radius=0.0&sortType=6&index={index}&{properties}&primaryDisplayPropertyType=houses&viewType=LIST&channel=BUY&areaSizeUnit=sqft&currencyCode=GBP&isFetching=false'

max_price = ""
min_rooms = 0
user_location = ""

# sorttype = 6 # newly listed first
properties = "propertyTypes%5B0%5D=detached&propertyTypes%5B1%5D=semi-detached&propertyTypes%5B2%5D=terraced&propertyTypes%5B3%5D=flat" # all
#properties = "propertyTypes%5B0%5D=detached&propertyTypes%5B1%5D=semi-detached&propertyTypes%5B2%5D=terraced" # houses only
#properties = "propertyTypes%5B3%5D=flat" # flats only

dbfile = "houses.sqlite"
cjarfile = "cjar.cookies"
session = requests.Session()

rm_user = ""
rm_pass = ""

def login():
    print("Logging in")
    data = """{"email":"{}","password":"{}","keepMeLoggedIn":true}""".format(rm_user, rm_pass)
    url = "https://my.rightmove.co.uk/login"
    headers = {"Content-Type": "application/json"}
    r = session.post(url, data, headers=headers)
    return r.status_code == 200

def shortlist():
    print("getting shortlist")
    url = "https://my.rightmove.co.uk/shortlist"
    #  https://my.rightmove.co.uk/shortlist?channel=RES_BUY&page=2&sortBy=DATE_ADDED&orderBy=DESC
    headers = {
        "Accept-Language": "en-GB,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_8) AppleWebKit/605.1.16 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
    }
    r = session.get(url, headers=headers)
    if r.status_code != 200:
        return None

    p = json.loads(r.text)
    i = 1
    if p["totalPages"] > i:
        i+=1
        url = "https://my.rightmove.co.uk/shortlist?channel=RES_BUY&page=" + str(i) + "&sortBy=DATE_ADDED&orderBy=DESC"
        r = session.get(url, headers=headers)
        if r.status_code == 200:
            p["properties"] += json.loads(r.text)["properties"]

    return p

def remove_shortlist(ps):
    if len(ps) < 0:
        return

    url = "https://my.rightmove.co.uk/property/saved/" + ",".join(ps)
    print("remove: " + url)
    r = session.delete(url)
    return r.status_code == 204

def save_property(i):
    print("Saving: " + str(i))
    data = '{"propertyId":"' + str(i) + '"}'
    url = "https://www.rightmove.co.uk/properties/api/user/savedProperty"
    headers = {"Content-Type": "application/json"}
    r = session.post(url, data, headers=headers)
    print(r.text)
    return r.status_code == 200

def create(c):
    sql = """CREATE TABLE IF NOT EXISTS houses (id INT, price INT, tenure TEXT, json TEXT, html TEXT);"""
    c.execute(sql)

def insert(c, i, p, t, j, h):
    sql = """INSERT INTO houses (id, price, tenure, json, html) VALUES (?, ?, ?, ?,?);"""
    c.execute(sql, (i, p, t, j, h, ))
    c.commit()

def update(c, i, p, t, j, h):
    sql = """UPDATE houses SET price=?, tenure=?, json=?, html=? WHERE id=?"""
    c.execute(sql, (p, t, j, h, i, ))
    c.commit()

def get(c, i):
    sql = """SELECT * FROM houses WHERE id=?"""
    cr = c.execute(sql, (i, ))
    r = cr.fetchone()
    return {
        "id": r[0],
        "price": r[1],
        "tenure": r[2],
        "json": r[3],
        "html": r[3]
    } if r else None

# web functions

def list(i):
    r = session.get(url.format(loc=user_location, price=max_price, rooms=min_rooms, index=i, properties=properties))
    return json.loads(r.text)

def tenure(html):
    if "TENURE" in html:
        return html.split("TENURE")[1].split(">")[5].split("<")[0].strip()
    elif "Tenure" in html:
        return html.split("Tenure")[1].split(">")[2].split("<")[0].strip()
    return ""

def area(html):
    if "sq. m." in html:
        a = html.split("sq. m.")[0].split("(")[-1].strip()
        if "-" in a:
            return int(a.split("-")[0])
        return int(a)
    #if "sq. ft." in html:
    #    return html.split("sq. ft.")[0].split(">")[-1] + "sq. ft."
    return 0

def html(i):
    url = "https://www.rightmove.co.uk/properties/" + str(i)
    return session.get(url).text

def hash(d):
    return hashlib.md5(d.encode()).hexdigest()


# db function

def save(c, l):
    for p in l["properties"]:
        i = p["id"]
        print(i)
        j = json.dumps(p)
        sp = get(c, i)
        if sp:
            # if same price continue
            if p["price"]["amount"] == sp["price"]:
                continue
        else:
            print("not found")

        h = html(i)
        if sp:
            print("updating")
            update(c, i, p["price"]["amount"], tenure(h), j, h)
        else:
            print("creeating")
            insert(c, i, p["price"]["amount"], tenure(h), j, h)

# main functions

def populate():
    c = sqlite3.connect(dbfile)
    create(c)

    l = list("0")
    pages = l["pagination"]

    print("Parsing page {} of {}".format("1", pages["total"]))
    save(c, l)

    for i in pages["options"]:
        if i["value"] == "0":
            continue

        print("Parsing page {} of {}".format(i["description"], pages["total"]))
        l = list(i["value"])
        save(c, l)

def estrapolate():
    fields = ["id", "bedrooms", "bathrooms", "ptype", "price", "tenure", "area", "inserted", "updated", "reason", "address"]
    jf = ["id", "bedrooms", "bathrooms", "propertySubType", "price.amount", "area", "tenure", "firstVisibleDate", "listingUpdate.listingUpdateDate", "listingUpdate.listingUpdateReason", "displayAddress"]

    c = sqlite3.connect(dbfile)
    sql = """DROP TABLE IF EXISTS data; CREATE TABLE IF NOT EXISTS data (id INT, bedrooms INT, bathrooms INT, ptype TEXT, price INT, area INT, tenure TEXT, inserted TEXT, updated TEXT, reason TEXT, address TEXT);"""
    c.executescript(sql)

    sql = """SELECT * FROM houses"""
    cr = c.execute(sql)

    sql = """INSERT INTO data (id, bedrooms, bathrooms, ptype, price, area, tenure, inserted, updated, reason, address) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    for r in cr.fetchall():
        j = json.loads(r[3])
        u = j["listingUpdate"]["listingUpdateDate"] if "listingUpdate" in j else j["firstVisibleDate"]
        a = j["listingUpdate"]["listingUpdateReason"] if "listingUpdate" in j else j["listingUpdateReason"]
        c.execute(sql, (j["id"], j["bedrooms"], j["bathrooms"], j["propertySubType"], r[1], area(r[4]), tenure(r[4]), j["firstVisibleDate"], u, a, j["displayAddress"], ))
        c.commit()

def update_shortlist(f):
    import datetime

    if os.path.exists(cjarfile):
        print("loading cookies")
        cookies = requests.utils.cookiejar_from_dict(json.loads(open(cjarfile, "r").read()))
        session.cookies.update(cookies)

    s = shortlist()
    if s == None:
        if login():
            c = requests.utils.dict_from_cookiejar(session.cookies)
            open(cjarfile, "w").write(json.dumps(c))
            s = shortlist() or {}
    
    pfile = "properties-" + hash(str(datetime.datetime.now())) + ".json"

    # remove properties
    if s and len(s["properties"]) > 0:
        remove_shortlist([str(p["propertyId"]) for p in s["properties"]])
        open(pfile, "w").write(json.dumps(s["properties"]))
    

    # add new properties
    if f and os.path.exists(f):
        np = json.loads(open(f, "r").read())
        for p in np:
            save_property(p["propertyId"])


def main():

    global max_price
    global min_rooms
    global user_location

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--populate", required=False, action="store_true", default=False,
        help="populates the db with the latest results and estrapolates data")
    parser.add_argument("-e", "--estrapolate", required=False, action="store_true", default=False,
        help="estrapolates data from previously ingested houses")
    parser.add_argument("-s", "--shortlist", required=False,
        help="""saves the current shortlist to file and adds the properties in the provided file to the shortlist.
        File Format:[{\"propertyId\": 1234},...]""")

    # params
    parser.add_argument("-x", "--max-price", required=False, default=1000000,
        help="max price of properties to look for")
    parser.add_argument("-n", "--min-rooms", required=False, default=3,
        help="min bedrooms number of properties to look for")
    parser.add_argument("-a", "--area-id", required=False,
        help="user defined area to look for properties: https://www.rightmove.co.uk/user/drawn-areas.html")

    args = parser.parse_args()

    max_price     = str(args.max_price)
    min_rooms     = int(args.min_rooms)
    user_location = "USERDEFINEDAREA%5E%7B%22id%22%3A%22{}%22%7D".format(args.area_id)

    rm_user = os.environ["RMUSER"]
    rm_pass = os.environ["RMPASS"]

    if rm_pass == "" or rm_user == "":
        print("invalid creds")
        os.exit(1)

    if args.populate:
        if not args.area_id:
            print("the following arguments are required: -a/--area-id")
            os.exit(1)

        populate()
        estrapolate()
    elif args.estrapolate:
        estrapolate()
    elif args.shortlist:
        update_shortlist(args.shortlist)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

# sqlite3 -table houses.sqlite "select id, ptype, price, area, reason, address, updated, tenure from data where updated like '2022-06-%' or updated like '2022-07-%' order by updated" | sed "s/^| /https:\/\/www.rightmove.co.uk\/properties\//g" | sed 's/^\+/\+-------------------------------------/g'

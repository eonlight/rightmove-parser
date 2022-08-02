# rightmove-parser

**CAPTCH BDA might need to be changed regularly**

## Setup

```
# install requirements
pip install -r requirements.txt

# update env var creds
cp .env.template .env
vim .env

# done
```

## Help

```
python main.py -h
usage: main.py [-h] [-p] [-e] [-s SHORTLIST] [-c 1234,432,12333,521] [-x MAX_PRICE]
               [-n MIN_ROOMS] [-a AREA_ID]

optional arguments:
  -h, --help            show this help message and exit
  -p, --populate        populates the db with the latest results and estrapolates data
  -e, --estrapolate     estrapolates data from previously ingested houses
  -s SHORTLIST, --shortlist SHORTLIST
                        saves the current shortlist to file and adds the properties in the
                        provided file to the shortlist. File Format:[{"propertyId": 1234},...]
  -c 1234,432,12333,521, --create-shortlist 1234,432,12333,521
                        creates a shortlist.json file with the correct shortlist format with the
                        comma separated properties provided
  -x MAX_PRICE, --max-price MAX_PRICE
                        max price of properties to look for
  -n MIN_ROOMS, --min-rooms MIN_ROOMS
                        min bedrooms number of properties to look for
  -a AREA_ID, --area-id AREA_ID
                        user defined area to look for properties:
                        https://www.rightmove.co.uk/user/drawn-areas.html
```
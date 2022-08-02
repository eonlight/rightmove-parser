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

# todo: not working. needs fixing
def get_captcha():
    print("Getting Captcha")

    url = "https://rightmove-api.arkoselabs.com/fc/gt2/public_key/91523F73-E56D-4DD9-86C4-5D4E5464E3D8"
    data = {"bda": "eyJjdCI6ImxFenFSNHEyYlhHSHhlSk9iTUk0eWpFVkQwMDVvWTFXUy92Ni9ueUY0N0lRUmV5ODRoQlpFM29hbHlEUUlyaVFRKy9neDVBTWRiUCsweHA1dmpQN3BLUHoyTXZWbXZLVTIxMFpPTUlWaC9OM1RldFhZdDJ2SG5YdEVlVS8wY1JJalZSdnAya25qWnNlWEc1NGFqOFV1ZDgxQi9FNlJIQzU4MWlyeEFreVl2NnNsamtRcVg1QXp4cG56UVJ0MWZpMDhXTWFZUnFENnhJd0lydWt6Mk5NSzZCejkvaHh6UHM4RTg5ZVhaMSs4U1V1dkQzaXB3L0R4dWp2VzVWRTNON2ZLR25za29IQkwxaHRIeE9TOUxqWVJWSFpzS2ZKSllBYzN2WVVWTkFZNVoyTXc5SXA1a2NDbmJZNFRpWlZnTXJIaGRUSERIUE1mQWQxdUxQMlRYSi9JNkFCd3ZqU1ZLbFpjcEhHdy8vMy9hMGEvNGlPb3F1ckxLVjhCbFE5cERUdHI4LzZlU2tUbjArNGFFWjFhaUhYcWl2aGZVY0w0a3BKNEVJOHJOUmh5bGFoZ2lVdVcybE9HcHN1a081OXlrQXY3SFhBblU2TS94QStaMUFGNHQ4S1E4U2huKytuaU9MS002V3gyZURmSVpBMWNaNTlvZm1vOFVzcTV3RmwxVlQ0eGdQN0hHR1g3STZYaW1wc254aUM0b2dVdUNWMm8wOEpKaFd4RjdXU2Q0bnp3OUxVUlV2bjRGUlU5T04vU3MyS2xWVWJnQ21vQjhLY0hibUk2WU8wazd4R2V1MWZ4VmlHdGhpNjA0NUExRnAvYmszM3NtUnNQalpLbjZHdkRDMmRndFJsaGhoT0pXZ29SUWV4SzMybzJaWHdjRE1TakwyQ3JTbVFFWTdKMXZ1MVpHalVOSVJMR2Y5RDhEV1ZRNGlQYUM4THJ6M2ttRXIxNVpVQmlENmU0eFA5K2Z0cEYzWTdRVEZtamhWbUJIdktFaFc4N0tXZ2xwVVBKYkw0TTNmaEszTFJ2dVVMSmpUYWsrTXpVNDlqWFBiYUQydVg1MkJzbFdaZkJEVzl2K29QV1VscmcwUDZzWno0S3NhT1RBeEZBaHR3WE9RVUxTdFpaZzF6ZHRqMGJQMXByemtPbllHamE3M2FoQXNqdFBFc09yUVZyczgzZjNUYm50b2lmU2h5S2JSelM2MGdKcVJnQ1l2aDMxeGV5TWZjbEYwYW5LMnM1a3JyS2ozSWNWNjZ3TGU5TFhKK1gyRDVTZkwyTzFVZ2lXYmxZOTJZMEhxYWVzd3NFb3E3bTVSNDVDYUROVE1ybi96ZzRaYnZWWng3K0p3Q2x3cldhSDl0SkxncXdZRjl4REpVbndrQWp0YllQbWdHeU9DSS92VXBmM1NHczkzejk0NzM5KzIwOGhTaEJoOXJVN3M4NU0ya1BqZU8rWE41cVNGNVlyc2hpa3RvVTEyc0tEeC9vVHBEckV1Y2RXelBRejNPVFpwL25vdzNaQ2I1THl5WVF2VzkxWGU3UE53eHFMVXhxT0VUTjlnSjR4ZzhvWW52U1BoTXUwMytvY00yTyt6cWpvZHJJY3FYWkNrV1FTZEowZHpPSHBYaDJIMml4Mm13QUZDcUU5N0UzN1BCUDhhL1JnV24yRXVwaWo2TDQ1QmRlanIvYUUxdVpzdXRveEMzTHZGcWUzUlpvdzBPY3NZRTllVG9aVU9pNEtkdkEzVTVwdFRKYnQyVU10SFNCeEQvQXJtSS8yNzVGR3VQbmVFYmxyWnRwcmppYlVsMEFFdTlXdUtTZWl2KzdsM3Y0V0NPWVRQWG9PQjltOWZxYUt0ZXg5aWlOdE1aazc3dEpvVlNiUjdKWjlXeE5vOUJnNDM0MG45ek9ZeVh1RUgvL0RHSFh6L0tmN0tyZXZEdzhadXgvS1IxeWxJeEN0VGNobCs3eEdyN21YelVGVEw3ZEE4NDFzbG9LMWJGZXBFRFhtNk42OE11bkZHZjRibzloTlFBVi9BN2pxY3l1cXJiUFhlTVU3dkF3M1JNVnV1Wm5ETXlvUnptMVdoYkpiQmRvdlVwTG81b3FUSTA2bzM2bkVkcHRiMFBxMzRyK1ZNV0pycEhtano3aC8wN3pUNjJPZldhZDZTRS92ZVQrTWxzYW1MSkxma1c3WTRBei81TTFHb3Y0a3RGWEJFV0R2OUVBL2gwV3hNMnB4VVg4aTNBdHEzVXNwQ0txY21Ya0JYb2daZUVGTjFLcGE4Z2ZmdEN3OGUrNS9WN0cvKytyZnpaaFB3bFhFbTlXd24yRUVYU25ZdkdVWnA2SHV3aFV2MGVXeG0xdE1FUG1HVE1Manc3SWtOLzMrVjh2endoRGtocldNOWh3N1l0bWxoSkhCREZadFI4MFNKcFRVMlh0NWE4dTJHNmpJRmhSaGNrT3lGRVlTL1JFYmdRQzIxVE1pamZqMU5GUkkxV3lvVnYzRStOS1BFcmtRbjJzRzd0YW1CVktCQ3QzUHhwdHV1Nlh3MXh3dFNDL1VDZllwMHJRNnYxMlNRRW1DZjIzZzlTc09iR0pRY3pHQ3A3dWlkTVU0Vm1ZRk5zQmtXaVB1aHpZNEluWTlFbHhPZGVxZ0dWKzZoTkw0WVVXNEpGRFgwOEVyNi9UNGFIbU9kUjR2WTdFWWpUZVBaQ3doYTB1MkUvRHdGUjU3VHBTOVEva0NxTXQ4VEYySHpnWERhV0JmU3R0dmsrKzBGRkkzeE93RUxtVGFRTlpZZFFaeDhXSXhrTUhIUEJ2T1dBaWI0YVIwMlZvMWVCcEQ4dndjUXpOSHlyNEdOeERmeGhPWkdKeW1GTjBWYjhRRzFzSkprcU5CUXlNeU8vNy9EWlNQVmZZVFJlSTdTUVJuQXA3SDVLYTZjT1FhbEp2L0lwRStUWGhwTHNVUkgzMjZ1UllXV3pXR3c5YVVpa3hKd1orVkxXakt2UUZCUHNBeHR6Uk9FSDlXOFIwTE4vYmMyN0R0d0pHQ1NxMzBUNzlhSy96anV1MG9wV1hrZ3hGc3EwRHk2OXE2Wm5hL2UzeEdreFFNdHBsbHE3VXpsTUFqSlI0c2VSRTlPbXkzM2d1MWRKSjJQR2lNRFZ3QWdjUDhRWVpTNDZZWGYwTytlaE9jQTFnb1pzemxJQ0ZWZ3dmUU5kbW43Um5hcEx3Z2VMT2s5ZkZoMERYSTkvWTFiOG50YlB3bk1weDM0U2k0aEM2R2E2Z2d4d3B5STU0T1d3Mkl1WnBTdWVBRjlTTTdkVFp6RnIzNUJPTjZUOHNQMTVCdkpqTGMyZ3dvM2MrSnJOak5tbnl6djl3UE0rb0FIaisyZWNzUU9EU2U0WG80N29DSVlJbWwxcTB3VFY4SGwzRVd4OUlOQnNyZEx2MlJxNnpxYms0RHQ0SklHayt4SGlPaUY4RjdFVEp2eUZXaXlPWWs4T2ZiZytqbDNFa3M4eittUHhSUlBuZEZuOEp1bG1CeDlhS21XaDdLL3ZHL3pDTnQwd2FTSUdxekF1M3l4MzYxTDRTcEUvTlVQUE1kV1BUYWcreGlPZTVzSzdWc1ZET2dVQk5SU0FLVlZlekFGMzIvM0c5Z0NBaENmTjhQK3dpSEhxWUJ3Z2FRK2NFVTRQQ1NIY2x2RTJkNFBkSFlzN2ZJVkZNdUhzc3lVV2Z2aTZkR2E0SEMzU0R3SlBxK3c2MUJRcU5nRHovMllpUVZVME1Ub3BlNXRPQnI1OGh5THo2Ym5kcGVpSThPRFFZaHhyb1pqMEVLamRVTGl0NFhhK0V4anVZZkswbHFOUDUweEhtNFpYQVI5Vmg3UXpZbHF5Y3hqbENvZjlaMm1Ca2lreXRWRzJqRDRJQjNiNitaVWhvMjU4cEx6MC9La0pDTEVVNlJla0pOOWdFY0NxY0hyZEt5ZFJhSjdKeTByR2hYM2lSeUFDdEpKbEo4djlWdkwzdysxdFpHN1VvZDc2U3JvVjFnVGtMbnh3NDhmdmV6N0hSNUovRUt6VDFQL0NIcWpkejg0RXlYcHp4cmI2WVBqSXlBeVo1elN6Y253c2JhSW9LNXBaQWpWRmVBdnFZaGxEM29CaUhneHJRQVAvR0RkVjgzK0FnUUlwRFA2d0d3LzUyNWVueTVIRUtLamhBd2REWVJmRWdXVXpkdHJ0dWxKSEtPb0x4SUlRQU9XRXd5aENieEU4Q2w0NXNzUWZrUWNvaFlVMmU5M013dHY2WHA1Um1lcFMwN0w5QjM3MnlGeW5lV05USERGK0FhWTlheUdrZTl2VU5jOGg2WFZ5aUxuR2kvTmZMa1lraC9QZk1BaVFBNTVhdlBRU1hvYkRUZ2JlVW0rMGdXdisxOU9SN0o4ODlsOWJ1WjU2a0hWVEVhaVl4cW1DbXlUY0hUK0Z1bjhkQjZaTldxeE5Qd3RTRERnMVhMd3hmN2ZqRkROSUF3WTRyZ2lNZk0xWERMNTdEdmgvRkQ4V1hPbzgxNHI5K0pKSVB5OVRUQW9UQjdOU2V3bVQ4b2xNZ01VRWZadkpmMURrZ25Oa2ZVNXpvZGY5NDI2cWhvS3NJb1pSM2FXTUxjMHZzdks2UUZTMEdqTGUzWG5KRnNrYlhyVFVWZmJLbHl0Y090MDFyMUxLdVlFNzNYTFNnRFBEdnRoa0VQRXJFek5peEhwbzI5Y1FZNDVBczFlakYrdTkxVTgvVUU5azc1R052cWdMUWNFRkdjOENSZ29sNjFBSGk5QjJnKzczdDQyWDBYVldLMHBPQnorY3poYWI1S25Da04weWJBa1hySGhablhFS1FnaHJqMncvNm5YOW8wZ3lSbEVUVmxmeStKRlJudGJMaUZiOTRLMi9YdU44bnFsKzFMaVNvUXRacmhBUU9SZkJLR0NPM3ViK1dKNjFLQkhVcnFBOWc5UDFmRTR2SzhHVDBIOUNETzBPdCtyZEdZQjlIcHBtNFdSTEUxazNFL3BCTkFndnJIZmRoS2RIZTI5bVl2ZmZLZU9hMlZ4NWVONXAzck5VUWxTRUtEWVlTOHFjUTNkSjhLRlNnaG00NTJ5NkpDT1RGWUJFeUUwZG9pY2F1aWlrMWJOdWZvb2FWNXd6TkhXWVNQeHRMZ0tobEJQRVhPQXRHK3VtaHBpWDZwQkZFam0wZHV6RDQ3TjhRY0RvaDFFbnRmNllxTFZjOEluY3hWU0k0U3NXSTY0RnQwNUEvZlpyWG1URE1yYjVkTTVxT2dqNFo1SndLbG5zZWFRekJueWlpSXZBVGV4RHZsci92WjVxdUdZL2NNZUc3Sm00c3QxcUdGUlkxM3hLc0h0dG5za2N4cVRFVTJyTm1xcldxK2U2cHZJRk1OYlF2WldESHBwMjVqRnF6S1RQalgxOW14YklIaS9nTEJwRzBsN0svU3d0c2VsMVByZDBYUmMxQnhmU3NnUnU1QXc3RUhxR3ZyM3NuYmpQWVo0Q21SRVNBNWdCRHZUYmM1UFBuZGRld1lPRTEvcERqZ3lmSHlIUHRoSzY2ZmdEdlVmNngwMW9BenZqMDhHc2FRRU5hNW5NaE8wSHQ2allOWWRQaTZXdWFFQ3V0QVFiL296a3VqUW5DcEtWMkc5K0FtY1hnK3Y4UjQrdkNNU1hGckxvK0tvZlhLbkY5UXREN3VwVExCY29SWW9yT2tpNU5hcnB3aTd5a0tyTDYyZ1JLbzRLUytGUnFvZVpjRGRZYkFyRVZoOHFzVnZRaE91NGY5L3FDWXZxd3J5Qm95SnFIZmhmVEtLYkZucGlXRWxNSTQxd1doZjFuczlJaU4xVVpPQy92NkhJN0VtTjdadG1GQWd4bFVEbEg2dWVCSHkwZ2JDRnRrdXp1WDc4V3QxWjVyMmRNVWxOakhrNlFzaDYzSkJ4a25VTW5sQUU0QW01NlJYaExtY1Uya2hqUDFtK29MWEVvdzJQVnAzaE02ODB5clNMTnhqczhTREs2RTUzZHFTQ3R5RWdlVC9UeHRMQ2psaFc1NlRGU3prank5YWVKbitZa2VCNkx0R3JFT0x3QnE0bHhxM3c1dnBFMkN0M1JXMkx3WkZDbUN2SmJrOWNoRG9PSk1FVHNJVG5DL1NveG1Na0FKdHgzOXV2MVRkUmRGY0ZwY1M3dk80MDNSODdDdVRNNTZvbCt3Uk5Ic1VjMGpaTkhTZzZlYmVJcGNoZWtNTU9OQTQrMURjZkF6bytMWXowOTRwOWxYcFc5b09BWjJUTFhJOGdDWXMzQlFhUWJ0SW1vQnJLeWpxQVV2UHJNbjNacGRaQ2dONGt3NUhxb2JuYVB4S29IWkwwMXlXSXlpaW5VWlRVQXlKLzJzdnp2bHNxd1RCNjJBNmhRejlBV1ZheG8yMXlYT0Y2ZUJnbTlVdTFKNWpUbkhVVnI5N0VDUzhGVjVEcURwNXNBTnE4VlVJbFpDbFVlaHhnZTFMTzV4K3BYc1hobmxNZkc1S1hyYmJJZXY4OUVLTmhYZ2krTEZYK3Z5dHE5UEd3OGh1SGgwZytVK1FwQ1huOGZUSlNiZkZtUGZMYlZ4Qk5HZUh0WUNrSTd1RDY3NEJLbmZCQUcwZG90R1hqN2Vpa2RXSWlraTNyb2xKZTU2MkJSY25DcENiQUJydm5FZGhLZjJRd1NINzBWRWczNk40VWNubHNBRjdjS2JGZE9qdHdSczN0NFppOUVWZjlUYnk3VEZMc0JVSVlNNmJNaXdxRGQ1TVRhckdQbnRFdUJRUExLblpzeTVaMU9xbVBuZ0FFVERDbGg3RGdKMXNLSk14SVFrN2oxY0lRMFNEd0ljaXZrcS95OTB1UDF0UUJaZ0JlRFNXei8zK3I4TlV1cys0c1oyd2Z6VjYxeUppY21WSkU2d1pha0ppU21sL3FFVlNaTGJkRTBOdkpjWjR4TFhRaElhcEhEVm13SVRFTWNaYnVIWktUM0wzSGlrQUZMZHhzWVNQVnhVUmZWaVZ0VkN3dlQ2Qzdkc0lNc0JrWWgxK1ZPSnQzUGdlVWl3dmE1WGNVS1RGTnExcysxUUJNSzhJclZmTFBZcFZOUE9ZWitOa3J1MldiRks0M1o5VkoyOGlvRmxUd2VmWjZzZGpKMGsrVHMwVEJUbDNCOXZvYW5MZzJxWDhCWXY1anBtSXpRQnB3MEZteXlqSWR5S0NNaEFxU1laM2FlZ2h3UVNrY3dYRk1HK1lJeHV4dGc2akw4R09xWXl0NWRteUxhd2VMcDJPUnB3dHRjYm1lZG1SSUliUzEycW16V0VWNUwvbG45eXltdGo1NU9YQ2ciLCJpdiI6ImNjYmVlYTc5OTU5OWJmMzVhMWM1MzU0NjViNTkwNmVjIiwicyI6IjM2Y2FkYTIyNGU5N2EzNDcifQ==",
            "public_key": "91523F73-E56D-4DD9-86C4-5D4E5464E3D8",
            "site": "https://www.rightmove.co.uk",
            "userbrowser": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0",
            "capi_version": "9.3.4",
            "capi_mode": "lightbox",
            "style_theme": "default",
            "rnd": "0.9771359452863425"}

    headers = {
        "Accept-Language": "en-GB,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://rightmove-api.arkoselabs.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0",
    }

    r = session.post(url, data, headers=headers,  proxies={"https": "http://127.0.0.1:8080"}, verify=False)
    print(r.text)

    t = json.loads(r.text)["token"]
    print(t)
    return t

def login():
    print("Logging in")
    t = get_captcha()

    data = '{"email":"' + rm_user + '","password":"' + rm_pass + '","keepMeLoggedIn":true,"captchaToken": "' + t + '"}'
    url = "https://my.rightmove.co.uk/login"
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-GB,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0",
        "Origin": "https://www.rightmove.co.uk"
    }
    r = session.post(url, data, headers=headers, proxies={"https": "http://127.0.0.1:8080"}, verify=False)
    print(r.text)
    return r.status_code == 200

def shortlist():
    print("getting shortlist")
    url = "https://my.rightmove.co.uk/shortlist"
    #  https://my.rightmove.co.uk/shortlist?channel=RES_BUY&page=2&sortBy=DATE_ADDED&orderBy=DESC
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-GB,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/json",
        "Origin": "https://www.rightmove.co.uk",
        "Referer": "https://www.rightmove.co.uk/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0",
    }
    r = session.get(url, headers=headers, proxies={"https": "http://127.0.0.1:8080"}, verify=False)
    if r.status_code != 200:
        return None

    p = json.loads(r.text)
    i = 1
    if p["totalPages"] > i:
        i+=1
        url = "https://my.rightmove.co.uk/shortlist?channel=RES_BUY&page=" + str(i) + "&sortBy=DATE_ADDED&orderBy=DESC"
        r = session.get(url, headers=headers, proxies={"https": "http://127.0.0.1:8080"}, verify=False)
        if r.status_code == 200:
            p["properties"] += json.loads(r.text)["properties"]

    return p

def remove_shortlist(ps):
    if len(ps) < 0:
        return

    url = "https://my.rightmove.co.uk/property/saved/" + ",".join(ps)
    print("remove: " + url)
    r = session.delete(url, proxies={"https": "http://127.0.0.1:8080"}, verify=False)
    return r.status_code == 204

def save_property(i):
    print("Saving: " + str(i))
    data = '{"propertyId":"' + str(i) + '"}'
    url = "https://www.rightmove.co.uk/properties/api/user/savedProperty"
    headers = {"Content-Type": "application/json"}
    r = session.post(url, data, headers=headers, proxies={"https": "http://127.0.0.1:8080"}, verify=False)
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

    try:
        s = shortlist()
    except Exception as e:
        session.cookies.clear()
        s = None

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

def create_shortlist(l):
    ps = []
    for p in l:
        ps += [{"propertyId": p}]
    open("shortlist.json", "w").write(json.dumps(ps))

def main():

    global max_price
    global min_rooms
    global user_location
    global rm_user
    global rm_pass

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--populate", required=False, action="store_true", default=False,
        help="populates the db with the latest results and estrapolates data")
    parser.add_argument("-e", "--estrapolate", required=False, action="store_true", default=False,
        help="estrapolates data from previously ingested houses")
    parser.add_argument("-s", "--shortlist", required=False,
        help="""saves the current shortlist to file and adds the properties in the provided file to the shortlist.
        File Format:[{\"propertyId\": 1234},...]""")
    parser.add_argument("-c", "--create-shortlist", metavar="1234,432,12333,521", required=False,
        help="creates a shortlist.json file with the correct shortlist format with the comma separated properties provided")

    # sqlite3 houses.sqlite "select id from data where bedrooms > 2 and (updated like '2022-07-2%') order by updated" | tr "\n" ","

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
    elif args.create_shortlist:
        create_shortlist(args.create_shortlist.split(","))
    elif args.shortlist:
        update_shortlist(args.shortlist)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

# sqlite3 -table houses.sqlite "select id, ptype, price, area, reason, address, updated, tenure from data where updated like '2022-06-%' or updated like '2022-07-%' order by updated" | sed "s/^| /https:\/\/www.rightmove.co.uk\/properties\//g" | sed 's/^\+/\+-------------------------------------/g'

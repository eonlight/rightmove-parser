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
    data = {"bda": "eyJjdCI6ImVWN2daMjJmL0cyZmlXWFRxYkowNFMxWGNHRExQL0xqQ1JidURrRE9uT0Y2SXhnUHowcmNYZ0s3UnBFTHhoeG1INy9ybm5FdS91UDBEeGN4S0hGRVIwWFYrY2pmaGUxZHNEOWl6WXMrTk1BdWpjWGZFQW1IK1FQaG5xYjZWcTNLVVJwbDFreEwyOVFvWGZYcytvbklXWjFCWXJUckZoNVk1OFdURmR1NS92dzJoQk91VlNpOE96Zjc1T05PL1ZuYW05MVI0RkdGWmEreis2YzNyRFUvc1A2cVE5Umk3OStSMUJBM2FmTmR3cXdOTkVWRkllMi9aUGtMeEo1NEh6RUY0VGFnelpWOUVPaytaWXVLU1lFOTB4a0ppY2dyUGxZOW1sSUdJcHBxLzNiS2MvVVNIOXdoUllrUmlqc05HVnN6TkdFbmxCWjd1Wk02alQyeDFnTDJ6MmpJSHZpc0NlRHRiU29Mb1BHQmZEME9qRUVXR25iZU5xWjlBM0FmUFdZaXl2L2pXdVdYeHVUalVuTllSUUhrZndNTEwxRWljczUyUFVBMExmRExCa2YrQTBYNDk2cWZkNURTV1kralArcjBLNGlzTjBNa2N6SVpMb0pKYUZ0UU9kYzRlZTkvSG1QVHFlQ2JVSldpdUxvenZvK3VGY0tTNlFBU0FvK2JSbHhoZXJNczFRem12OGI2TGt1VDRpeGZoSDhwM1RNV09hcFdhc3EvcHVjcGZ6ZjJQU29YNkEzTSt5TDlsblpxczFNcEZTb0MvdDl2OGJKVzcxaTJXOG1adm1SVnR1SjNDaVEwNko2bWs5S3ZtVkxUWWZMa3psTUpBSE9EZGlET3NaV0lsdTBnZVhUaytPK0txbGkvZ3N3SDhLRkh4cUQ2UDVvRTkyR0xZd3FzRXpOeDVHeW0yRWNrYWJmZjM2NWlINVZLTGdpYmtYVHcrczh3STFydkNTclM0NHRvcVlTQVF2cVJoamNVclF1ZFZhcjljNGNKYTRRVWNBQWoxZEVoS1NGdXVHSHBHVi9hS1QrSk5vV01rOTZKczR5V1A2WGpKRHpqSDlMcStvM3pkZWNqYTMvYUR3RXdaVnJBNUNsVTJCeFBJWWo0dEtua08zekxLMi9ieG1NZzYwbXM3ME85TlZnRm1pbHVVejN1Tk9IbWpyL0lEYmtIVmFpTFFiY2d1L0R5bGNOTXJXVUZWbWFUQ1ZLdWVwSEhRSlhtd3FUeis3T0FYYm1GQWdhWVc2bXRJaWo4ZnlDSGJKTFhwbVAwVS9VUmdlQndDczV6cXQ2NTMzTHkxdFJMcVFwOTNja2tNVER4WlF1OHBORjVrQTUwSUsvYnBpM3M2SkFmdVdvd2lHRFdZTG5ISVFSeVNxb0tONVBzMkJManF2SEdyOUlleUc1VmV4NlNhY1dQM3BUYWR5LzRFKzZlMFpKUExPeWU2RHY0M2E4TlE5SDBQc3NKUHdwUERibHdETFlHRERKd0NjZHlUbXRZZmloSjU1NFNERHQ3UUhQSkFZbVVUZnplTHdpU2IySzREK09ncXN2TVljcHpWelc1L2Z0ejZOQ0g1Uyt6Tm10bzEzZDEwZER2VzU2b1BHNXEzRUNiTUdTWm04bVZoSmtNSEJ3bmhrKzdRWWNuamNCUEI1ejlqZTBBMEpIZU9za1I2aWNBcmdkMzVVR0EwUVJmQjR1L3BXazhSUFRLaTZPaGRrcVg1RDRtaHFlTjBHckdWVGxUS011Z2o4RVk3WWFRMUt3L3hXM3pXQzBUZm4zeEo0VDZEbm1XOWtCaDdaNmY4ZEtEeUo0Q1Q0M1JIM1pKdXk0OEFhdjJmckdHd2ZuQVdSSC91ZmdUOEZlOE5mdWZvK2FCSEdPdjRwTU1nN25CdzlSc2RNWXFsVFlUUGY1b0NRTWVWVVZVNVN5dzFVaFcySHRndFlHajVQVkp0cFVMcyt6d1pzS1Riak8zcHdReUw0MHFRNmI3Um1tbmphV3FWTlF2V011N1FKNEFxcVQwclZPeDhDR3dvKzJoajVoUU9TSXI5SHoxMzcwY1ZhNmQwRjFGQ0tycWhaOWZuN0xmeFJCMnRRaFJ0akpkTExhZGhWWUFlRXJBcG16MmtRazZjNlk3N3FpcGVIdVJjaEFYTi90U3VsbURNcm92d2xtUExscjZYYkpxb0tRN2x6Rys4N2UwbUVPaTErNEJHTGxzaW12bHFuRWFtY2E4K3gxa0ZkUm1FK01mdEUwcTBDajd4Q1hsdStFN0xjTkU1aCtHUG9mVmJmeHhXNUxqSXhiTFp6dm91VXppRmxOeW1GKzZ4NWtZaGQ1UUJGa1VVSEJ3QW95NG1SRVZrdlUzaDdNUmZ2eTRBZzF0NjROQUVtMmpKTTYzYm5tSkZNOTJrajg5WnB2eFVkZHFjMDB3cUQrdkxxeXJLa2hHeFNyY2Mva1dDdEM3N1d2WU83cXhoZmdKVUx2ck53cFBHU0FzTUErNWNXWFgvcUM3SGZZcDdmVUlscGorTEU3V3FjSFF6V3lQZHZUd0VBczZLSXgzQnZmckdQeFFkQ1NYdVZZVkplOEdVWUdOdDhxMnMwSmF1WjlOZTc5cHAyT000Zk9lWDJnWUZKTU5CQTY5ZEVBQzZ6TzF0N2IrSmFmUTU1MGVtcWF1cXpzQzlZNnRaU0xubEhPK1ZzenNWcVJMRSsxTGJwQXhPbU5jN3kzazhrb0dsTE90ZFJKWmdpandWSGltWnJDVlB6WnJXRVBCcEdJZjBEdisweE9kUEFydUUyMTJ6Z2xnUXlGMmQyWjV2WkE4a21qdnRUNGp4VzIyb3JLLzZwQ3VWWENQbFQ1VUVKMm1BMU1WeFBYWWpkUnhEa2s3VXhuOXVWQzV1OU5WeDg3TXZDQlBLdlV3L3BaRXgyaFlvSmpaRlV1VzZZc0t6ZHd4bFMzRUU2OUNtWU9kVklXZ1QxQ2Fzc2RadjhwYk1Menp6TnlTalVtYWszbGdUdGhIVkRSNlFaYlZIMi9yTUZXbmxMek95ZGNGcUxMckZVVHpLNnkwUGpNdWE3dFBoU0JERkNiR1FPQ0pQa3VRR0lGNG1CZWVmR1FtOUM4Ni84WS9JNWlTb1JxWU1IMXNrdlhKMUJmY0NoRWlGRlBaT0hjNTRzbXovL2U0RTBmMWVYRFFIY2Z1Y05PQjVkR1VWYjVOd3ozNVlndDlKOEt0NGtUaWN1OFhsdTJGUEdQdXdDMzBNRkZ4OFRVYytpTkRxYWIyR2xxMWVVMEQ1S2lLb2RaTVdadkd1eExXdEVZb3ZXVSsrVHgzdXZaU0hydWcwR25ReDdWaTd3MEZpblRyakRucVlWWTA4UmtHOWJoTHRDVktVbkZSdU1Cd09CbzVhd1VVRWJCSjNVVWQzZndMU2k4Q3M4dUZzV0R4b3l1RE5GOC9wNmNLK3lOKzB6VEt4aHJ1TDRoRW5GbjMwUUhRdVMxdUx5TXc1R0FoUW8wTjlNbWlCK3FaZlRLd1M4U2tKODRLUC9Vb2JQb2xTbVBneWlMejlqcTJpdjNIaG1JdlJMODRlU08xYnNSVTFZKzU1eHRlbWQwdXpUYnlCc2JqSHpBSUNvMGNIVVJVRkY5THZrY1BvY29iRDlYZjdORU55OWFUZk9xbWFzelNSYVpFcVlPTUQzS0RPYnhXMm4reXNvM1gwa0JEV0RYaUVaRHEvaWVRRVMxcUVibkhyTEw2RTZYZHN4YWhlWG4xL0ZiSkEvbG1NSXJJQVloUzlQWjlJbkZzdllmUWVDWWdvc2xRUGkvMjRZWDhFTHBVcFZPSHBZUVgwem1NQlB5dVY0SDNiRFBla0x4TFhERmp1Nmh6c0VWbmdIOHRBeENEZ0V1enVONGFQcFFpekxyVXdSaVpTQ1I2Z1d3b2hmVVRuSmJPNitCWUJ3WDJ6Z0o1cFdOalFpaGNRdVQ1K2QwUXNVL2xYdlQ3YlVkYWhBRDRYRjg1VFJEdHEzcjJrNGRxVjZHMFlYYlhRL3BGTWROa1FCUjZHZTRHVWs4MXJuYnl1UFEyak1nOTdjVkZmYlNTeWozUWJaRjlWdU9KUDVBR3c3TmEzMWZOdjJWZCtiSG01SGVIeDNrRWF4SHY3My9wOGFIZWMrZTM2anVPdU1ScmRpV29Wc2FoeU5ZWEFDbGdwUGI1dk5ZWElMdDkwbzZpbGIzaGZ2QnVrdlRNY3p5OEhjYnN3VnFJNGUybHBQK1BYbERVWWNaR3d0elA0VGhLdnVmNXRoZ0tJZmozOGdKTGV4YmliSFVDVlY0ZXBmWEYrdDRkSkQ5RVBpQnMyNTdRa3cwaWpacHlJVjBIeGZlMjk3U05YSldGdDRvUDdRVzFPN0xPOUtqR1hCczFNdHgxMkpvZ0JHZmx3L2liUWM0U2lYdmdvR1IrUGw3aFBFcjVWaVNPcEgreGF2WVphTFFLR2U5a0hhQUQyWTd5V255UnhIdm93d3B0T3NtVWFXcmZzZnpEMzl6ZUgzSWpJUGtNWkpTc1JieGU3aUdxRXVZd1JRNVRwYk1FT2xaUHptQWpzVDNvdlFIMGhlRzRRV25FL0hBT2h6NVU4NXFuN3Q1OGNlZ3lIakZuVHhvTEFMbzJqbzdlTEJmbUtYQWZ5dGFWL3Nsbkp5TGdiSWxiTGRqUlR3T3p6TUhYTjFHcFVQdFMzVnN3cHNVOTg3Y1RsRnJYM0kwQ1VtSlRUbVpqQWdrem9Wa1pNR2l0THkwaWM4NklwWmVQVUcrOElqczBSc25NUWRGdTBvUlBjUFpYaTZCdmFtTnluYnYxL1llYUZ3YVkwOS95M1VMSEM3UC9jdi9RWDRuVThiSm1DazI4a0VWZ3k3Z3F2OXBwRUNxM1pxbXBqRXlDUUJNRkV2M1hnZTdKZXdCUzJhc0dROWJpYzZJdlJFQjlkSERqNFA1d1g0Y1hyWEFQWlJwNGZpMXd5NVpORy9zSjJRRTI0WDV1NU43Tk5uYVZFTHRMaVlRTmlza2dGMVY5bk5rZVRQRmRWK0Yra1NQWVpBQ0xuOHR1UFlJbmhGK1FVcjE3ek1acE9MMlN4Y01mVzdQbUo1VHJxdjRaWnpmMDdjcjJMckhyam9xcGcveGwwbmdOTWJTZStDMkl2a3NYMFIrbzU0MDU0U0N6azhudndjZm4xcDVLSEpXQkFjaXRrNVlkbGxSRkNMcC90b2ZFNWpDS2tGVFdUM2pPYzV5UjBXaldCS1J4NTVSRmFnSUYrNFRVNW1kdktsbjF3ejJSMDdDNERQdEF6TjZoWFlibXVsU0lEQUo1cndCU3JFdERQTGRaWTFQZVRNWnVGT09iMU52RTkzNld5M3VJcHY5aEdNVDBtd2k0Ykd2bFhNR0h3T2NROXFMRnM0YkkvQVBwK3RiM2RCa1cwenFzcUx3OGhwRFpMV1pWWDk0S0NNM2JDNzFZdVliRzdFa2FUb2M4Z0NueVAxeEROOXhrcEZabGMyZkhsOXdvbkpzQXNvb21Dc1NxN1NYYzVVTW1vR3RCRHIyS2E0UHpLV2NsUnYzT1E5RTZCc1NiMkxEUGVWZkNjaElaaVdxeVIrYnhBUWt6NkNqdmM1N1E0YUx5U2xKdDFjSVRwVTg0d2dCYVI4Z2psVEhHcEh6NkN3b1RudHpUMXBjRnkxU2h4YStUSC94dTdBdDFpSUh6WVV3dm5uMU1hRTZDVXUwa2hNRHJoeUtISnFqOTlFWVF1MjVVYlVQVnY0eU5GTDJubmY1MWRwY3Buc0hQa0RBZEFlYjl1eklJeGpSWnRRcFZKOVdFU0hFWnZwR2lrMmZJVEdNSmsvbkFzL1JCVitiUkRHblFZQWxKU3d0ZmIyZUJ6S3pvY1Z3ajExdTFUeWdkRWRuRUduYmxqRmR3QnBhQTc3Q1cxZVVDbExLZXJSRVdSY0F0bUQ2ZVcwNzhjOEVROE9BUThaTCsxMFpOWUNoNzQwTGZESUpBd0ppQis4YXRjb3k0eUIraUhjTDQ1UXhPQWgweTBlSUZPUGRDQmdraDJ4UXI3dUFwdW1GZTdteGtLdmVjVmVsRC9tWHdpdmhFSzZDZGE2d0N3UkpwQjFWZVdIQzZzUUdHK3EzYkkxK2ljSlRsTFlpTHdHbFVJNjFNY0VYa2dCdEljWkRhaWJWUGtsTXhCcW5vMWdDdGFHdVh1dWRxVkhsLzYvYjA1R3F0ZitZb28vb3psZFN0YlI3b2NkU0lNK1FrbWZFZCtXQU8xYWtwVVlJRVdsbHk2YlFZRGtsaE96NHdzT3lwNlpJOTRSYzVIem4xbm0vR1RCbXVzZFBXS2FPeFZNMUdhSWw4cnFGTVRvVStxemNuSU9yVW9PemQ0Z3pnYTZybWhabmg4eHpSN2xEZlZ6M2hTM0UzcGxqR0xTMmtzNVBUeGw4WTI2OGxRZkhxcU4yb1g3VjlJc3V4SUkrSjFhNEZjZlp1cGt5SlpleXllMnZaNUZKcmVoNmRyYjdISGltdm9ZSGNYMThHRFo1bDdVUVV4cGRNMmNXMnpCTGswZ3Fwb1EyR3FvQUF3SEZYRjZoWTdTUElKWTZmeWhBT09UYkNnSlR0TGN5bWhMRVJKVDJrNU5lUElNbWF0bTRJUzByWlFFaFpwTDVpOHcrVnpPYmtFRFplTkJROEptYnZGWDNmeFFpelJoUjIvZnRzQkxmbXFjS3pVZktsbHg0ZGtFRCsxVW9zaHBGdVhWUWpVWVViU2w5Z3I4dzRvWHI3YXJURHNycldLV04rblJxYzBpSk05ZWJFWGV0RXZkQjUzMmoyZ2JKY0tkZUNzTDJXOEpzMlVrSHkveTRRMlR4aGh3WHdjZFllWVh0aFl4OXJ1bUxyMlc0b3lXb2c0L1FUUlVXcVFKbE8zU0FkWVkrL2ovQmdLRFlWZnA4TFFVbTFtRThBMTBISWJjSDAyRjB5aEJYeUZmN0hGMVZLenI4U3VpMlNhdzZPcUNMRG13Q1YxSkVTVy9lcWhudm4vY3AzM0ZrSlpGa2Joa0tGVGt1QU04TmVCenhTQlFOenB0ZTlTV3hJZ0QxWDIxOHRpelhCMlpGLzlqVzI0ZW5BaHlvaFRrSzRsYkcraHNOZUlUQms5WGNWQVBWSkpxVWRDS2tuYTJYbURVaEE5TXh1ZHhvVElPNjNkK1R1b2p5S2k4NFRyL0hPd3FYYXV0OU9uRm5XZm5LMGdPa2xxK21UY01KUUV4THZsR3lOU1c5VHdWQitRV093TG1EeSt2K1Z5dlY0RGlVMFZDWVBmdVRCcjk1MFdlMUIiLCJpdiI6IjllYzcxMjg0NDgwOTgxMzVlZmZjZWQ0MWM3ZDVkMzVkIiwicyI6IjNkMTMyNmVlZDNhZWJkMzMifQ==",
            "public_key": "91523F73-E56D-4DD9-86C4-5D4E5464E3D8",
            "site": "https://www.rightmove.co.uk",
            "userbrowser": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_8) AppleWebKit/605.1.16 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
            "capi_version": "9.3.4",
            "capi_mode": "lightbox",
            "style_theme": "default",
            "rnd": "0.9771359452863425"}

    headers = {
        "Accept-Language": "en-GB,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://rightmove-api.arkoselabs.com",
        "Referer": "https://rightmove-api.arkoselabs.com/v2/91523F73-E56D-4DD9-86C4-5D4E5464E3D8/enforcement.ed7c611b3319c8ef18cd4204e6144894.html",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_8) AppleWebKit/605.1.16 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
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
        "Accept-Language": "en-GB,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_8) AppleWebKit/605.1.16 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
    }
    r = session.post(url, data, headers=headers, proxies={"https": "http://127.0.0.1:8080"}, verify=False)
    print(r.text)
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

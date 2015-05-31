# reads the brands list
import re
from google.appengine.api import urlfetch

BRAND_URL = "http://m.rankabrand.org/singlebrand.php?bid=%s"

brands = dict([tuple(i.decode('utf8').strip().split(",")) for i in file("brands.csv", "r").readlines()])


class BrandNotFound(Exception):
    pass


def find_brand_for_product(name):
    for n, k in brands.iteritems():
        if n.lower() in name.lower():
            return {"url": BRAND_URL % k,
                    "name": n,
                    "brand_id": k}
    raise BrandNotFound()


def find_rating_for_brand(brand_id):
    response = urlfetch.fetch(
        BRAND_URL % brand_id,
        None, headers={'Referrer': 'http://shoppistant.com', 'User-Agent': 'Mozilla/5.0'}, deadline=45)

    if response.status_code != 200:
        raise BrandNotFound()

    m = re.findall(r"gets a (.)-label on Rank a Brand",
                   response.content)

    return m[0]
import json
import urllib
import urllib2
import datetime
import Image
import ImageDraw
import ImageFont
from google.appengine.api import urlfetch
import brands

import webapp2


PLUGIN_INFO = {
    "name": "Rank a brand product search"
}

# cache for 2 days
EXPIRATION_IN_SECONDS = 2 * 24 * 60 * 60
rating_font = ImageFont.truetype("Roboto-Bold.ttf", 28)
rating_colors = {'A': (123, 191, 75),
                 'B': (179, 209, 74),
                 'C': (226, 217, 56),
                 'D': (221, 148, 53),
                 'E': (203, 70, 47)}

class GMT(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(hours=10)

    def tzname(self, dt):
        return "GMT"

    def dst(self, dt):
        return datetime.timedelta(0)


def get_expiration_stamp(seconds):
    gmt = GMT()
    delta = datetime.timedelta(seconds=seconds)
    expiration = datetime.datetime.now()
    expiration = expiration.replace(tzinfo=gmt)
    expiration = expiration + delta
    return expiration.strftime("%a, %d %b %Y %H:%M:%S %Z")


class MainHandler(webapp2.RequestHandler):
    def get(self):
        barcode = self.request.params.get("q", None)
        if barcode:
            try:
                brand = brands.find_brand_for_product(self.resolve_name(barcode))
                open_details = self.request.params.get("d", None)
                if open_details:
                    self.redirect(brand['url'])
                else:
                    self.set_default_headers()
                    self.send_rating_image(brands.find_rating_for_brand(brand['brand_id']))
            except brands.BrandNotFound:
                self.response.write("Not found")
                self.response.status = 404
        else:
            self.response.content_type = "application/json"
            self.response.write(json.dumps(PLUGIN_INFO))

    def set_default_headers(self):
        # allow CORS
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers["Expires"] = get_expiration_stamp(EXPIRATION_IN_SECONDS)
        self.response.headers["Cache-Control"] = "public, max-age=%d" % EXPIRATION_IN_SECONDS

    def resolve_name(self, ean_code):
        response = urlfetch.fetch(
            "http://nameresolver-shoppistant.rhcloud.com/products/%s" % urllib.quote_plus(ean_code),
            None, headers={'Referrer': 'http://shoppistant.com'}, deadline=45)

        if response.status_code != 200:
            raise urllib2.HTTPError(response.final_url, response.status_code,
                                    response.content, response.headers, None)

        results = json.loads(response.content)
        return results["name"]

    def send_rating_image(self, rating):
        img = Image.open("rating_background.png")
        draw = ImageDraw.Draw(img)
        w, _ = draw.textsize(rating)
        draw.text((20 - w / 2, 6), rating, rating_colors[rating], font=rating_font)
        self.response.content_type = "image/png"
        img.save(self.response, "PNG")


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)

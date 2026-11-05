"""Read the dealership's public inventory. Never overwrite a good feed on failure."""
import concurrent.futures, datetime, html, json, pathlib, re, urllib.error, urllib.request
BASE = 'https://www.carsforyouva.com'
ROOT = pathlib.Path(__file__).resolve().parents[1]

# Use standard HTML request headers. The dealership may reject custom bot user agents.
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}
def fetch(url):
    if not url.startswith(BASE + '/inventory/'): raise ValueError('Unexpected inventory URL')
    req = urllib.request.Request(url, headers=REQUEST_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            # Never import from an unexpected URL following a redirect.
            if not response.geturl().startswith(BASE + '/inventory/'):
                raise ValueError('Dealership redirected inventory outside approved URL')
            return response.read().decode('utf-8')
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            raise RuntimeError(
                'Dealer website returned HTTP 403 to the scheduled inventory reader. '
                'The dealership/DealerCenter must allow this integration or provide an approved inventory feed.'
            ) from exc
        raise
def clean(v): return html.unescape(re.sub('<[^>]+>', '', v)).strip()
def field(s, name):
    m=re.search(r'<span[^>]*class="vehicle-label"[^>]*>\s*'+re.escape(name)+r'\s*</span>\s*<span[^>]*class="vehicle-value"[^>]*>(.*?)</span>',s,re.S|re.I)
    return clean(m[1]) if m else ''
def parse_listing(s):
    cars=[]
    for part in re.split(r'data-vehicle-id="vehicle-id-',s)[1:]:
        m=re.search(r'class="vehicle-title" href="([^"]+)"[^>]*>(.*?)</a>',part,re.S)
        if not m: continue
        url,title=m[1],clean(m[2]); stock=re.search(r'data-sn="([^"]+)"',part)
        image=re.search(r'data-carmojo-primary-image-url="([^"]+)"',part)
        price=re.search(r'data-total-price="([\d.]+)"',part)
        trim=re.search(r'<label>Trim: </label>([^<]+)',part)
        if not stock or not image: raise ValueError('Inventory markup changed')
        cars.append(dict(id=stock[1],name=title.title(),url=url,year=int(title[:4]),price=float(price[1]) if price else None,image=html.unescape(image[1]),trim=clean(trim[1]).title() if trim else ''))
    if not cars or len({c['id'] for c in cars})!=len(cars): raise ValueError('Empty or duplicate inventory')
    expected=re.search(r'(\d+) Available Vehicles',s)
    if expected and int(expected[1])!=len(cars): raise ValueError('Incomplete inventory; pagination needs review')
    return cars
def enrich(car):
    s=fetch(car['url'])
    for key,label in [('mileage','Mileage'),('engine','Engine'),('transmission','Transmission'),('drivetrain','Drivetrain'),('color','Exterior Color'),('vin','VIN')]:
        value=field(s,label)
        car[key]=int(re.sub(r'\D','',value)) if key=='mileage' and re.search(r'\d',value) else value
    for key in ['make','model']:
        m=re.search(r'"'+key+r'":"([^"]+)"',s)
        if m: car[key]=html.unescape(m[1]).title()
    m=re.search(r'"bodyType":"([^"]+)"',s)
    car['body']=m[1].title() if m else 'Other'
    m=re.search(r'id="DWS_Vehicle_Media_Button_Settings_image">(.*?)</script>',s,re.S)
    car['photos']=json.loads(m[1]).get('img_urls',[])[:35] if m else [car['image']]
    return car

def _value(row, *aliases):
    fields = {re.sub(r'[^a-z0-9]', '', str(k).lower()): v for k, v in row.items()}
    for alias in aliases:
        v = fields.get(re.sub(r'[^a-z0-9]', '', alias.lower()))
        if v is not None and str(v).strip():
            return v
    return ''

def _money(value):
    return float(re.sub(r'[$, ]', '', str(value))) if str(value).strip() else None

def parse_authorized_feed(content):
    """Read a dealer-authorized full CSV or JSON export, not website HTML."""
    import csv
    import io
    content = content.lstrip('\ufeff').strip()
    if content.startswith(('{', '[')):
        document = json.loads(content)
        rows = document if isinstance(document, list) else document.get('vehicles', [])
    else:
        rows = list(csv.DictReader(io.StringIO(content)))
    if not isinstance(rows, list) or not rows:
        raise ValueError('Approved feed is empty or not a vehicle list')
    cars = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('Approved feed contains a non-vehicle record')
        stock = str(_value(row, 'id', 'stock', 'stock_number', 'stock_no', 'stocknumber')).strip()
        url = str(_value(row, 'url', 'listing_url', 'vehicle_url', 'detail_url')).strip()
        image = str(_value(row, 'image', 'image_url', 'primary_image', 'main_photo')).strip()
        year_raw = _value(row, 'year', 'model_year')
        make = clean(str(_value(row, 'make'))).title()
        model = clean(str(_value(row, 'model'))).title()
        year = int(year_raw) if str(year_raw).strip().isdigit() else 0
        name = clean(str(_value(row, 'name', 'title'))) or f'{year} {make} {model}'
        if not stock or not year or not make or not model:
            raise ValueError('Approved feed is missing stock ID, year, make, or model')
        if not url.startswith(BASE + '/inventory/') or not image.startswith('https://'):
            raise ValueError('Approved feed is missing a valid dealership URL or image')
        total = _money(_value(row, 'total_price', 'price_including_fees', 'price_with_fees', 'advertised_total_price'))
        if total is None:
            base = _money(_value(row, 'internet_price', 'selling_price', 'price'))
            fee = _money(_value(row, 'dealer_fee', 'processing_fee', 'dealer_processing_fee'))
            if base is not None and fee is not None: total = base + fee
        if total is not None and total < 0: raise ValueError('Negative vehicle price')
        mileage_raw = re.sub(r'\D', '', str(_value(row, 'mileage', 'miles', 'odometer')))
        photos_raw = _value(row, 'photos', 'photo_urls', 'image_urls')
        if isinstance(photos_raw, list):
            photos = photos_raw
        else:
            photos = re.split(r'[|;]', str(photos_raw)) if photos_raw else []
        photos = [str(p).strip() for p in photos if str(p).strip().startswith('https://')]
        if image not in photos: photos.insert(0, image)
        cars.append(dict(
            id=stock, name=name.title(), url=url, year=year, price=total, image=image,
            trim=clean(str(_value(row, 'trim', 'style'))).title(),
            mileage=int(mileage_raw) if mileage_raw else None,
            engine=clean(str(_value(row, 'engine'))),
            transmission=clean(str(_value(row, 'transmission'))),
            drivetrain=clean(str(_value(row, 'drivetrain', 'drive_type'))),
            color=clean(str(_value(row, 'exterior_color', 'color'))),
            vin=clean(str(_value(row, 'vin'))),
            make=make, model=model,
            body=clean(str(_value(row, 'body', 'body_style', 'body_type'))).title() or 'Other',
            photos=photos[:35]
        ))
    if len({c['id'] for c in cars}) != len(cars):
        raise ValueError('Approved feed contains duplicate stock IDs')
    return cars

def fetch_authorized_feed(url):
    """The authorized feed URL is supplied privately through GitHub Actions secrets."""
    from urllib.parse import urlsplit
    target = urlsplit(url)
    if target.scheme != 'https' or not target.hostname or target.username or target.password:
        raise ValueError('Approved inventory feed URL must use HTTPS')
    try:
        request = urllib.request.Request(url, headers={'Accept': 'application/json,text/csv'})
        with urllib.request.urlopen(request, timeout=45) as response:
            final = urlsplit(response.geturl())
            if final.scheme != 'https' or final.hostname != target.hostname:
                raise ValueError('Approved feed redirected to a different host')
            raw = response.read(8_000_001)
            if len(raw) > 8_000_000:
                raise ValueError('Approved feed response is too large')
            return raw.decode('utf-8-sig')
    except (urllib.error.HTTPError, urllib.error.URLError):
        raise RuntimeError('Approved inventory feed was unavailable; retained last good inventory') from None

if __name__=='__main__':
    import os
    approved_url = os.environ.get('AUTO_VERIFIED_FEED_URL', '').strip()
    if approved_url:
        cars = parse_authorized_feed(fetch_authorized_feed(approved_url))
    else:
        cars = parse_listing(fetch(BASE+'/inventory/'))
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: cars=list(pool.map(enrich,cars))
    data=dict(source=BASE+'/inventory/',syncedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),vehicles=cars)
    target=ROOT/'web/inventory.json'; tmp=target.with_suffix('.tmp'); tmp.write_text(json.dumps(data,indent=2)); tmp.replace(target)
    print(f'Synced {len(cars)} vehicles')

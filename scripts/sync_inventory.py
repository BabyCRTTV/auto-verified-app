"""Read the dealership's public inventory. Never overwrite a good feed on failure."""
import concurrent.futures, datetime, html, json, pathlib, re, urllib.request
BASE = 'https://www.carsforyouva.com'
ROOT = pathlib.Path(__file__).resolve().parents[1]
def fetch(url):
    if not url.startswith(BASE + '/inventory/'): raise ValueError('Unexpected inventory URL')
    req=urllib.request.Request(url, headers={'User-Agent':'AutoVerifiedInventory/1.0 (+public inventory reader)'})
    with urllib.request.urlopen(req, timeout=45) as r: return r.read().decode('utf-8')
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
if __name__=='__main__':
    cars=parse_listing(fetch(BASE+'/inventory/'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: cars=list(pool.map(enrich,cars))
    data=dict(source=BASE+'/inventory/',syncedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),vehicles=cars)
    target=ROOT/'web/inventory.json'; tmp=target.with_suffix('.tmp'); tmp.write_text(json.dumps(data,indent=2)); tmp.replace(target)
    print(f'Synced {len(cars)} vehicles')

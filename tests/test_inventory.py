import json, pathlib, sys, unittest
from unittest.mock import MagicMock, patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from sync_inventory import parse_listing, field, fetch, BASE, parse_authorized_feed
class InventoryTests(unittest.TestCase):
 def test_fee_inclusive_price(self):
  html='''<div data-vehicle-id="vehicle-id-X"><span data-sn="STOCK1"></span><a class="vehicle-title" href="https://www.carsforyouva.com/inventory/a/b/stock1/">2016 HONDA TEST</a><span data-carmojo-primary-image-url="https://example.com/car.jpg"></span><span data-vehicle-price="10000" data-total-price="10599"></span><label>Trim: </label> EX </div> 1 Available Vehicles'''
  cars=parse_listing(html); self.assertEqual(cars[0]['price'],10599);self.assertEqual(cars[0]['id'],'STOCK1')
 def test_empty_feed_is_rejected(self):
  with self.assertRaises(ValueError):parse_listing('<html>Temporarily unavailable</html>')
 def test_partial_feed_is_rejected(self):
  html='''<div data-vehicle-id="vehicle-id-X"><span data-sn="A"></span><a class="vehicle-title" href="https://www.carsforyouva.com/inventory/a/b/a/">2016 HONDA TEST</a><span data-carmojo-primary-image-url="https://example.com/car.jpg"></span></div> 2 Available Vehicles'''
  with self.assertRaises(ValueError):parse_listing(html)
 def test_mileage_field(self):
  self.assertEqual(field('<span class="vehicle-label">Mileage</span> <span class="vehicle-value">65,809 mi</span>','Mileage'),'65,809 mi')
 def test_fetch_uses_html_headers_and_checks_redirect(self):
  response=MagicMock()
  response.__enter__.return_value.read.return_value=b'<html>Public inventory</html>'
  response.__enter__.return_value.geturl.return_value=BASE+'/inventory/'
  with patch('urllib.request.urlopen',return_value=response) as opener:
   self.assertEqual(fetch(BASE+'/inventory/'),'<html>Public inventory</html>')
   request=opener.call_args.args[0]
   self.assertIn('Mozilla/5.0',request.get_header('User-agent'))
   self.assertIn('text/html',request.get_header('Accept'))
  response.__enter__.return_value.geturl.return_value='https://other.example/inventory/'
  with patch('urllib.request.urlopen',return_value=response):
   with self.assertRaises(ValueError):fetch(BASE+'/inventory/')
 def test_authorized_csv_feed_includes_explicit_fees(self):
  source='stock_number,year,make,model,listing_url,image_url,internet_price,dealer_fee,mileage\n'
  source+='STOCK3,2017,Honda,Civic,https://www.carsforyouva.com/inventory/honda/civic/stock3/,https://example.com/car.jpg,10000,599,"61,250"\n'
  cars=parse_authorized_feed(source)
  self.assertEqual(len(cars),1)
  self.assertEqual(cars[0]['price'],10599)
  self.assertEqual(cars[0]['mileage'],61250)
  self.assertEqual(cars[0]['photos'],['https://example.com/car.jpg'])
 def test_authorized_json_feed_does_not_invent_dealer_fee(self):
  source=json.dumps({'vehicles':[dict(id='S1',year=2016,make='Toyota',model='Camry',url='https://www.carsforyouva.com/inventory/toyota/camry/s1/',image='https://example.com/a.jpg',price=10000)]})
  car=parse_authorized_feed(source)[0]
  self.assertIsNone(car['price'])
 def test_authorized_feed_rejects_incomplete_or_duplicate_records(self):
  with self.assertRaises(ValueError):parse_authorized_feed('stock_number,year\n')
  with self.assertRaises(ValueError):parse_authorized_feed('[{"id":"X"}]')
  car=dict(id='S1',year=2016,make='Toyota',model='Camry',url='https://www.carsforyouva.com/inventory/toyota/camry/s1/',image='https://example.com/a.jpg')
  with self.assertRaises(ValueError):parse_authorized_feed(json.dumps([car,car]))
 def test_live_snapshot(self):
  feed=json.loads((pathlib.Path(__file__).resolve().parents[1]/'web/inventory.json').read_text());self.assertGreater(len(feed['vehicles']),0)
  self.assertEqual(len({c['id'] for c in feed['vehicles']}),len(feed['vehicles']))
  for c in feed['vehicles']:
   self.assertTrue(c['url'].startswith('https://www.carsforyouva.com/inventory/'));self.assertTrue(c['image'].startswith('https://'));self.assertIsInstance(c['mileage'],int);self.assertGreater(c['mileage'],0);self.assertGreater(len(c['photos']),0)
if __name__=='__main__':unittest.main()

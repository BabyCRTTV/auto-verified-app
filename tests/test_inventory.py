import json, pathlib, sys, unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from sync_inventory import parse_listing, field
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
 def test_live_snapshot(self):
  feed=json.loads((pathlib.Path(__file__).resolve().parents[1]/'web/inventory.json').read_text());self.assertGreater(len(feed['vehicles']),0)
  self.assertEqual(len({c['id'] for c in feed['vehicles']}),len(feed['vehicles']))
  for c in feed['vehicles']:
   self.assertTrue(c['url'].startswith('https://www.carsforyouva.com/inventory/'));self.assertTrue(c['image'].startswith('https://'));self.assertIsInstance(c['mileage'],int);self.assertGreater(c['mileage'],0);self.assertGreater(len(c['photos']),0)
if __name__=='__main__':unittest.main()

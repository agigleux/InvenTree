from django.test import TestCase
from django.db.models import Sum

from .models import StockLocation, StockItem, StockItemTracking
from part.models import Part


class StockTest(TestCase):
    """
    Tests to ensure that the stock location tree functions correcly
    """

    fixtures = [
        'category',
        'part',
        'location',
        'stock',
    ]

    def setUp(self):
        # Extract some shortcuts from the fixtures
        self.home = StockLocation.objects.get(name='Home')
        self.bathroom = StockLocation.objects.get(name='Bathroom')
        self.diningroom = StockLocation.objects.get(name='Dining Room')

        self.office = StockLocation.objects.get(name='Office')
        self.drawer1 = StockLocation.objects.get(name='Drawer_1')
        self.drawer2 = StockLocation.objects.get(name='Drawer_2')
        self.drawer3 = StockLocation.objects.get(name='Drawer_3')

    def test_loc_count(self):
        self.assertEqual(StockLocation.objects.count(), 7)

    def test_url(self):
        it = StockItem.objects.get(pk=2)
        self.assertEqual(it.get_absolute_url(), '/stock/item/2/')

        self.assertEqual(self.home.get_absolute_url(), '/stock/location/1/')

    def test_strings(self):
        it = StockItem.objects.get(pk=1)
        self.assertEqual(str(it), '4000 x M2x4 LPHS @ Dining Room')

    def test_parent_locations(self):

        self.assertEqual(self.office.parent, None)
        self.assertEqual(self.drawer1.parent, self.office)
        self.assertEqual(self.drawer2.parent, self.office)
        self.assertEqual(self.drawer3.parent, self.office)

        self.assertEqual(self.drawer3.pathstring, 'Office/Drawer_3')

        # Move one of the drawers
        self.drawer3.parent = self.home
        self.assertNotEqual(self.drawer3.parent, self.office)
        
        self.assertEqual(self.drawer3.pathstring, 'Home/Drawer_3')

    def test_children(self):
        self.assertTrue(self.office.has_children)
        self.assertFalse(self.drawer2.has_children)

        childs = self.office.getUniqueChildren()

        self.assertIn(self.drawer1.id, childs)
        self.assertIn(self.drawer2.id, childs)

        self.assertNotIn(self.bathroom.id, childs)

    def test_items(self):
        self.assertTrue(self.drawer1.has_items())
        self.assertTrue(self.drawer3.has_items())
        self.assertFalse(self.drawer2.has_items())

        # Drawer 3 should have three stock items
        self.assertEqual(self.drawer3.stock_items.count(), 3)

    def test_stock_count(self):
        part = Part.objects.get(pk=1)

        # There should be 5000 screws in stock
        self.assertEqual(part.total_stock, 9000)

        # There should be 18 widgets in stock
        self.assertEqual(StockItem.objects.filter(part=25).aggregate(Sum('quantity'))['quantity__sum'], 18)

    def test_delete_location(self):

        # How many stock items are there?
        n_stock = StockItem.objects.count()

        # What parts are in drawer 3?
        stock_ids = [part.id for part in StockItem.objects.filter(location=self.drawer3.id)]

        # Delete location - parts should move to parent location
        self.drawer3.delete()

        # There should still be the same number of parts
        self.assertEqual(StockItem.objects.count(), n_stock)

        # stock should have moved
        for s_id in stock_ids:
            s_item = StockItem.objects.get(id=s_id)
            self.assertEqual(s_item.location, self.office)

    def test_move(self):
        """ Test stock movement functions """

        # Move 4,000 screws to the bathroom
        it = StockItem.objects.get(pk=1)
        self.assertNotEqual(it.location, self.bathroom)
        self.assertTrue(it.move(self.bathroom, 'Moved to the bathroom', None))
        self.assertEqual(it.location, self.bathroom)

        # There now should be 2 lots of screws in the bathroom
        self.assertEqual(StockItem.objects.filter(part=1, location=self.bathroom).count(), 2)

        # Check that a tracking item was added
        track = StockItemTracking.objects.filter(item=it).latest('id')

        self.assertEqual(track.item, it)
        self.assertIn('Moved to', track.title)
        self.assertEqual(track.notes, 'Moved to the bathroom')

    def test_self_move(self):
        # Try to move an item to its current location (should fail)
        it = StockItem.objects.get(pk=1)

        n = it.tracking_info.count()
        self.assertFalse(it.move(it.location, 'Moved to same place', None))

        # Ensure tracking info was not added
        self.assertEqual(it.tracking_info.count(), n)

    def test_partial_move(self):
        pass

    def test_stocktake(self):
        # Perform stocktake
        it = StockItem.objects.get(pk=2)
        self.assertEqual(it.quantity, 5000)
        it.stocktake(255, None, notes='Counted items!')

        self.assertEqual(it.quantity, 255)

        # Check that a tracking item was added
        track = StockItemTracking.objects.filter(item=it).latest('id')

        self.assertIn('Stocktake', track.title)
        self.assertIn('Counted items', track.notes)

        n = it.tracking_info.count()
        self.assertFalse(it.stocktake(-1, None, 'test negative stocktake'))

        # Ensure tracking info was not added
        self.assertEqual(it.tracking_info.count(), n)

    def test_add_stock(self):
        it = StockItem.objects.get(pk=2)
        n = it.quantity
        it.add_stock(45, None, notes='Added some items')

        self.assertEqual(it.quantity, n + 45)

        # Check that a tracking item was added
        track = StockItemTracking.objects.filter(item=it).latest('id')

        self.assertIn('Added', track.title)
        self.assertIn('Added some items', track.notes)

    def test_take_stock(self):
        it = StockItem.objects.get(pk=2)
        n = it.quantity
        it.take_stock(15, None, notes='Removed some items')

        self.assertEqual(it.quantity, n - 15)

        # Check that a tracking item was added
        track = StockItemTracking.objects.filter(item=it).latest('id')

        self.assertIn('Removed', track.title)
        self.assertIn('Removed some items', track.notes)
        self.assertTrue(it.has_tracking_info)

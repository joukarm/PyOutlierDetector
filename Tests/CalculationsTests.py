import unittest
from Tools.CalculationTools import euclidean_distance, kth_nearest_distances
import pandas as pd


class TestCalculationMethods(unittest.TestCase):

    def test_euclidean_distance(self):
        self.assertEqual(euclidean_distance(0, 0, 3, 4), 5)

    def test_kth_nearest_distances(self):
        sample_data = pd.DataFrame({'time': [], 'rate': []})
        sample_data.time = [0.00, 5.00, 10.00, 15.00, 20.00, 25.00]
        sample_data.rate = [0.00, 25.00, 15.00, 25.00, 20.00, 5.00]
        self.assertAlmostEqual(kth_nearest_distances(sample_data, (15, 25), 2, False), 10.00, 2)
        self.assertAlmostEqual(kth_nearest_distances(sample_data, (15, 25), 3, False), 11.18, 2)

    if __name__ == "__main__":
        unittest.main()

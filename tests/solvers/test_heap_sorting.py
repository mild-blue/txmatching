import heapq
import unittest


class TestAcceptableBloodGroupParsing(unittest.TestCase):
    def test_heap_sorting_works(self):
        # TODO improve the test to test heap behavoir properly.
        MAX = 4
        l = [
            (1, 4),
            (1, 3),
            (3, 5),
            (2, 4),
            (3, 4)
        ]
        heap = []
        for m in l:
            entry = m

            heapq.heappush(heap, entry)
            if len(heap) > MAX:
                heapq.heappop(heap)
        self.assertEqual([(1, 4), (2, 4), (3, 5), (3, 4)], heap)

#!/usr/bin/env pytho

import unittest


def substring_between(s, start, finish):
    '''Find string between two substrings'''
    end_of_start = s.index(start) + len(start)
    start_of_finish = s.index(finish, end_of_start)
    return s[end_of_start:start_of_finish]


class Samples():
    dna = 'ACAAGATGCCATTGTCCCCCGGCCTCCTGCTGCTGCTGCTCTCCGGGGCCACGGCCACCGCTGCCCT'
    not_in_dna = 'CATS'


class Test_substring_between(unittest.TestCase):
    def substring_between(self, s, start, finish):
        return substring_between(s, start, finish)

    def test_start_contains_finish(self):
        start = 'ATGCCAT'
        finish = 'TGC'
        start_to_2nd_finish = 'TGTCCCCCGGCCTCC'
        self.assertEquals(self.substring_between(Samples.dna, start, finish),
                          start_to_2nd_finish)

    def test_finish_not_exist_in_s(self):
        with self.assertRaises(ValueError):
            self.substring_between(Samples.dna, Samples.dna[3:5],
                                   Samples.not_in_dna)

    def test_start_not_exist_in_s(self):
        with self.assertRaises(ValueError):
            self.substring_between(Samples.dna, Samples.not_in_dna,
                                   Samples.dna[15:20])

    def test_start_empty(self):
        '''Will contain all values up to "finish" '''
        s1_inclusive = Samples.dna[0:5]
        s1_exclusive = Samples.dna[0:4]
        s2 = Samples.dna[5:9]
        self.assertEquals(s1_inclusive,
                          self.substring_between(Samples.dna, '', s2))
        self.assertNotEquals(s1_exclusive,
                             self.substring_between(Samples.dna, '', s2))

    def test_finish_empty(self):
        s1 = Samples.dna[0:4]
        self.assertEquals('', self.substring_between(Samples.dna, s1,
                                                     ''))

    def test_s_empty(self):
        s1 = Samples.dna[0:4]
        s3 = Samples.dna[10:14]
        with self.assertRaises(ValueError):
            self.substring_between(self.substring_between('', s1,
                                   s3))

if __name__ == '__main__':
    unittest.main()

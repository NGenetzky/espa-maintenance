#!/usr/bin/env pytho
import unittest
import os
from file_not_found_summary import reducer as file_not_found_summary_reducer


class Default(object):
    string = 'Some String'
    int = 2
    dict = {'key': 'value', 'super': 'arbitrary'}
    tuple = ('v1', 'v2', 'v3')


class Test_accum_count_reducer(unittest.TestCase):
    default_reduce_out = {}
    default_map_out = Default.string
    def reducer(self, reduce_out, map_out):
        return file_not_found_summary_reducer(reduce_out, map_out)

    # Successful
    def test_reduce_out_is_dict(self):
        reduce_out = Default.dict
        self.reducer(reduce_out=reduce_out,
                     map_out=self.default_map_out)

    def test_map_out_is_none(self):
        map_out = None
        self.reducer(reduce_out=self.default_reduce_out,
                     map_out=map_out)

    def test_map_out_is_int(self):
        map_out = Default.int
        self.reducer(reduce_out=self.default_reduce_out,
                     map_out=map_out)

    def test_map_out_is_str(self):
        map_out = Default.string
        self.reducer(reduce_out=self.default_reduce_out,
                     map_out=map_out)

    def test_map_out_is_tuple(self):
        map_out = Default.tuple
        self.reducer(reduce_out=self.default_reduce_out,
                     map_out=map_out)

    # Type Errors
    def test_reduce_out_is_none(self):
        reduce_out = None
        with self.assertRaises(TypeError):
            self.reducer(reduce_out=reduce_out,
                         map_out=self.default_map_out)

    def test_reduce_out_is_int(self):
        reduce_out = Default.int
        with self.assertRaises(TypeError):
            self.reducer(reduce_out=reduce_out,
                         map_out=self.default_map_out)

    def test_reduce_out_is_str(self):
        reduce_out = Default.string
        with self.assertRaises(TypeError):
            self.reducer(reduce_out=reduce_out,
                         map_out=self.default_map_out)

    def test_reduce_out_is_tuple(self):
        reduce_out = Default.tuple
        with self.assertRaises(TypeError):
            self.reducer(reduce_out=reduce_out,
                         map_out=self.default_map_out)

    def test_map_out_is_dict(self):
        map_out = Default.dict
        with self.assertRaises(TypeError):
            self.reducer(reduce_out=self.default_reduce_out,
                         map_out=map_out)



if __name__ == '__main__':
    unittest.main()

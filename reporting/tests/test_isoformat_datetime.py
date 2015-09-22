'''
Created on Aug 25, 2015

@author: ngenetzky
'''
import unittest
import datetime


def isoformat_datetime(datetime_string):
    '''Converts string of ISO-format variations with datetime object

    Precondition:
        Datetime_string must be provided a subset of isoformat anything from:
        "YYYY-MM-DD" to "YYYY-NM-DDTHH:MM:SS.SSSS"
    Postcondition:
        returns datetime.datetime object(missing elements are zeroed)
    '''
    dt = None
    dt_formats = []
    if '.' in datetime_string:
        dt_formats.insert(0, '%Y-%m-%dT%H:%M:%S.%fZ')
    elif ':' in datetime_string:
        dt_formats.insert(0, '%Y-%m-%dT%H:%M:%S')
        dt_formats.insert(0, '%Y-%m-%dT%H:%M')
    elif 'T' in datetime_string:
        dt_formats.insert(0, '%Y-%m-%dT%H')
    else:
        dt_formats.insert(0, '%Y-%m-%d')

    for fmt in dt_formats:
        try:
            dt = datetime.datetime.strptime(datetime_string, fmt)
            break  # Parsed a valid datetime
        except:
            pass  # Parse failed, try the next one.
    if dt is None:  # All parses failed
        raise ValueError
    else:
        return dt


class Test_accum_count_reducer(unittest.TestCase):
    def isoformat_datetime(self, datetime_string):
        return isoformat_datetime(datetime_string)

    def setUp(self):
        self.dt = datetime.datetime.now()

    def test_full(self):
        dt_string = self.dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        expected = self.dt
        self.assertEqual(expected,
                         self.isoformat_datetime(dt_string))

    def test_no_ms(self):
        dt_string = self.dt.strftime('%Y-%m-%dT%H:%M:%S')
        expected = self.dt.replace(microsecond=0)
        self.assertEqual(expected,
                         self.isoformat_datetime(dt_string))

    def test_no_s_ms(self):
        dt_string = self.dt.strftime('%Y-%m-%dT%H:%M')
        expected = self.dt.replace(microsecond=0, second=0)
        self.assertEqual(expected,
                         self.isoformat_datetime(dt_string))

    def test_no_m_s_ms(self):
        dt_string = self.dt.strftime('%Y-%m-%dT%H')
        expected = self.dt.replace(microsecond=0, second=0,
                                   minute=0)
        self.assertEqual(expected,
                         self.isoformat_datetime(dt_string))

    def test_no_hr_m_s_ms(self):
        dt_string = self.dt.strftime('%Y-%m-%d')
        expected = self.dt.replace(microsecond=0, second=0,
                                   minute=0, hour=0)
        self.assertEqual(expected,
                         self.isoformat_datetime(dt_string))

    def test_no_space_YMD(self):
        dt_string = self.dt.strftime('%Y%m%d')
        with self.assertRaises(ValueError):
            self.isoformat_datetime(dt_string)


if __name__ == '__main__':
    unittest.main()

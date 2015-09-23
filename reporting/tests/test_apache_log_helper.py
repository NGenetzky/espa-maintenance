'''****************************************************************************
FILE: test_apache_log_helper.py

PURPOSE: Used to test extraction of data from apache logfile.

PROJECT: Land Satellites Data System Science Research and Development (LSRD)
    at the USGS EROS

LICENSE TYPE: NASA Open Source Agreement Version 1.3

AUTHOR: ngenetzky@usgs.gov

Possible Improvements:
    Test_get_date
    Test_get_orderid
    Test_is_404request
****************************************************************************'''
import unittest
import datetime
import logging
import apache_log_helper as helper


class Default:
    '''Provides consistency in parts of line that are sensitive'''
    common = '''127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326'''
    ip = '127.0.0.1'
    user_email = 'simple.user@usgs.gov'


def is_valid(return_val):
    if return_val is None:
        return False
    if(return_val == 'BAD_PARSE'):
        return False
    # Invalid datetime
    if(return_val == datetime.datetime.max):
        return False
    return True


def show_debug_for_helper():
    helper_log = logging.getLogger('apache_log_helper')
    helper_log.setLevel(logging.DEBUG)


@unittest.skip("Long test")
class TestFunctionForLogfile(unittest.TestCase):
    '''Creates a file that reports all failed lines for particular function

    More of a debug tool than a test.
    '''
    May = '/data2/ngenetzky/espa.cr-logs/espa.cr.May'
    Jun = '/data2/ngenetzky/espa.cr-logs/espa.cr.Jun'
    July = '/data2/ngenetzky/espa.cr-logs/espa.cr.July'

    # Modify lines below to use:
    logfile = '/data2/ngenetzky/espa.cr-logs/espa.cr.May'

    def extraction_function(self, line):
        return helper.get_datetime(line)
    # Modify lines above to use.

    def setUp(self):
        self.output = open(self.logfile+'-failures', 'w')

    def tearDown(self):
        self.output.close

    @unittest.skip("Long test")
    def test_for_every_line(self):
        number_of_fails = 0
        with open(self.logfile) as f:
            for i, line in enumerate(f):
                try:
                    self.extraction_function(line)
                except Exception:
                    number_of_fails = number_of_fails + 1
                    self.output.write('{0}:\n{1}'
                                      .format(str(i), line))
        self.assertEquals(0, number_of_fails,
                          'Failed to parse {0} lines from {1}'
                          .format(number_of_fails, self.logfile))


class TestDatetime(unittest.TestCase):
    '''Defines cases where extraction of datetime fails/succeeds

    There are two failpoints for this extraction
        1. Is locating the 'time_local' of the apache file.
        2. Is creating a python object from the text.
    '''
    def test_prefect_datetime(self):
        perfect = ('{0} - - [{1}] "GET /orders/{2}-{3}/{4} HTTP/1.1" {5} {6}'
                   ' Foo Bar Philip'.format('SOME_IP_ADDRESS',
                                            '05/Jun/2015:13:43:07 -0500',
                                            'USER_EMAIL',
                                            'ORDER_EXTRA',
                                            'SCENE_FILE_NAME.tar.gz',
                                            '200',  # Return code
                                            '100000'))  # downloaded_bytes
        value = helper.get_datetime(perfect)
        self.assertTrue(is_valid(value))

    def test_invalid_datetime(self):
        bad = ('{0} - - [{1}] "GET /orders/{2}-{3}/{4} HTTP/1.1" {5} {6} Foo'
               ' Bar Philip'.format('SOME_IP_ADDRESS',
                                    '05/06/2015:13:43:07 -0500',
                                    'USER_EMAIL',
                                    'ORDER_EXTRA',
                                    'SCENE_FILE_NAME.tar.gz',
                                    '200',  # Return code
                                    '100000'))  # downloaded_bytes
        with self.assertRaises(ValueError):
            helper.get_datetime(bad)

    def test_invalid_time_local(self):
        bad = ('{0} - - [{1}]"GET /orders/{2}-{3}/{4} HTTP/1.1" {5} {6} Foo'
               ' Bar Philip'.format('SOME_IP_ADDRESS',
                                    '05/Jun/2015:13:43:07 -0500',
                                    'USER_EMAIL',
                                    'ORDER_EXTRA', 'SCENE_FILE_NAME.tar.gz',
                                    '200',  # Return code
                                    '100000'))  # downloaded_bytes
        with self.assertRaises(Exception):
            helper.get_datetime(bad)


class TestReturnCode(unittest.TestCase):
    '''Defines cases where extraction of rtcode fails/succeeds

    Implementation precondition requires a certain number of spaces exist
        before the int that represents return_code
    '''
    def test_perfect_for_rtcode(self):
        perfect = ('A0 B1 C2 D3 E4 F5 G6 H7 {0} J9'.format(200))
        value = helper.get_rtcode(perfect)
        self.assertTrue(is_valid(value))

    def test_bad_user_request0(self):
        '''Fail to extract rtcode

        Invalid because CUSTOMER_REQUEST does not contain 2 spaces.
        '''
        line = ('{0} - - [{1}] "{2}" {3} {4} Foo Bar Philip'
                .format('SOME_IP_ADDRESS', '05/Jun/2015:13:43:07 -0500',
                        'CUSTOMER_REQUEST',
                        '200',  # Return code
                        '100000'))  # downloaded_bytes
        with self.assertRaises(Exception):
            helper.get_rtcode(line)

    def test_non_production_order(self):
        '''Succuessfully extracts rtcode even not production order'''
        line = '''{0} - - [05/Jun/2015:13:43:07 -0500] "GET /downloads/auxiliaries/land%5C_water%5C_poly/land%5C_no%5C_buf.ply.gz HTTP/1.1" 404 263 "-" "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0"'''.format(Default.ip)
        value = helper.get_rtcode(line)
        self.assertTrue(is_valid(value), 'Value={0}'.format(value))

    def test_invalid_request_1space(self):
        '''Incorrect number of spaces causes it to fail'''
        one_space_in_request = ('''{0} - - [03/May/2015:14:31:52 -0500] "\x80\x80\x01\x03\x01\x00W\x00\x00\x00 \x00\x00\x16\x00\x00\x13\x00\x00" 400 166 "-" "-"'''
                                .format(Default.ip))
        with self.assertRaises(Exception):
            helper.get_rt_code(one_space_in_request)

    def test_invalid_request_3spaces(self):
        '''Incorrect number of spaces causes it to fail'''
        three_spaces_in_request = ('''{0} - - [03/May/2015:14:31:52 -0500] "GET /orders/eg@example.com-0123-456 / HTTP/1.1" 400 166 "-" "-"'''
                                   .format(Default.ip))
        with self.assertRaises(Exception):
            helper.get_rt_code(three_spaces_in_request)


class TestDownloadedBytes(unittest.TestCase):
    '''Defines cases where extraction of download_bytes fails/succeeds

    Implementation precondition requires a certain number of spaces exist
        before the int that represents downloaded_bytes
    '''
    def test_perfect_for_downloaded_bytes(self):
        perfect = ('A0 B1 C2 D3 E4 F5 G6 H7 I8 {0}'.format(123456))
        value = helper.get_bytes(perfect)
        self.assertTrue(is_valid(value))

    def test_bad_user_request0(self):
        '''Fail to extract rtcode

        Invalid because CUSTOMER_REQUEST does not contain 2 spaces.
        '''
        line = ('{0} - - [{1}] "{2}" {3} {4} Foo Bar Philip'
                .format('SOME_IP_ADDRESS', '05/Jun/2015:13:43:07 -0500',
                        'CUSTOMER_REQUEST',
                        '200',  # Return code
                        '100000'))  # downloaded_bytes
        with self.assertRaises(Exception):
            helper.get_bytes(line)

    def test_non_production_order(self):
        '''Succeed to extract bytes even on non production order'''
        line = '''{0} - - [05/Jun/2015:13:43:07 -0500] "GET /downloads/auxiliaries/land%5C_water%5C_poly/land%5C_no%5C_buf.ply.gz HTTP/1.1" 404 263 "-" "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0"'''.format(Default.ip)
        self.assertFalse(helper.is_production_order(line))
        value = helper.get_bytes(line)
        self.assertTrue(is_valid(value))

    def test_invalid_request(self):
        '''Incorrect number of spaces causes it to fail'''
        one_space_in_request = ('''{0} - - [03/May/2015:14:31:52 -0500] "\x80\x80\x01\x03\x01\x00W\x00\x00\x00 \x00\x00\x16\x00\x00\x13\x00\x00" 400 166 "-" "-"'''
                                .format(Default.ip))
        with self.assertRaises(Exception):
            helper.get_bytes(one_space_in_request)


class TestUserEmail(unittest.TestCase):
    def test_issue0_includes_dash(self):
        has_dash = '''#!$%&'*+-/=?^_`{}|~@example.org'''
        line = ('''{0} - - [01/Jul/2015:13:09:16 -0500] "GET /orders/{1}-06192015-150025/LT50370311998352-SC20150620065152.tar.gz HTTP/1.1" 200 284125751 "-" "Python-urllib/2.7"'''
                .format(Default.ip,
                        has_dash))
        with self.assertRaises(ValueError):
            helper.get_user_email(line)
            # self.assertNotEqual(user_email, has_dash)

    def test_issue1_include_quote_space(self):
        has_quote_space = '" "@example.org'
        line = ('''{0} - - [01/Jul/2015:13:09:16 -0500] "GET /orders/{1}-06192015-150025/LT50370311998352-SC20150620065152.tar.gz HTTP/1.1" 200 284125751 "-" "Python-urllib/2.7"'''
                .format(Default.ip,
                        has_quote_space))
        with self.assertRaises(ValueError):
            helper.get_user_email(line)
            # self.assertNotEqual(user_email, has_quote_space)

    def test_production_order_good(self):
        email = 'research@sdstate.edu'
        edu = ('''{0} - - [01/Jul/2015:13:09:16 -0500] "GET /orders/{1}-06192015-150025/LT50370311998352-SC20150620065152.tar.gz HTTP/1.1" 200 284125751 "-" "Python-urllib/2.7"'''
               .format(Default.ip,
                       email))
        user_email = helper.get_user_email(edu)
        self.assertEqual(user_email, email)

    def test_production_order_bad(self):
        email = 'research@sdstate.edu'
        edu = ('''{0} - - [01/Jul/2015:13:09:16 -0500] "GET /orders/{1}-06192015-150025/LT50370311998352-SC20150620065152.tar.gz HTTP/1.1" 200 284125751 "-" "Python-urllib/2.7"'''
               .format(Default.ip,
                       email))
        user_email = helper.get_user_email(edu)
        self.assertEqual(user_email, email)

    def test_request_base_dir(self):
        bad = '{0} - - [01/Jul/2015:00:00:27 -0500] "GET / HTTP/1.1" 302 5 "-" "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)'.format(Default.ip)
        with self.assertRaises(Exception):
            value = helper.get_user_email(bad)
            self.assertFalse(is_valid(value))


class TestIsSuccessful(unittest.TestCase):
    def test_is_successful_request_min200(self):
        minimum = ('A0 B1 C2 D3 E4 F5 G6 H7 {0} J9'.format(200))
        self.assertTrue(helper.is_successful_request(minimum))

    def test_is_successful_request_min404(self):
        '''Minimum example of non successful order'''
        minimum = ('A0 B1 C2 D3 E4 F5 G6 H7 {0} J9'.format(404))
        self.assertFalse(helper.is_successful_request(minimum))

    def test_is_successful_request_min202(self):
        '''202 is not considered successful'''
        minimum = ('A0 B1 C2 D3 E4 F5 G6 H7 {0} J9'.format(202))
        self.assertFalse(helper.is_successful_request(minimum))

    def test_is_successful_request_perfect(self):
        perfect0 = ('{0} - - [{1}] "GET /orders/{2}-{3}/{4} HTTP/1.1" {5} {6}'
                    ' Foo Bar Philip'.format('SOME_IP_ADDRESS',
                                             '05/Jun/2015:13:43:07 -0500',
                                             'USER_EMAIL', 'ORDER_EXTRA',
                                             'SCENE_FILE_NAME.tar.gz',
                                             '200',  # Return code
                                             '100000'))  # downloaded_bytes
        self.assertTrue(helper.is_successful_request(perfect0))


class TestIs404Request(unittest.TestCase):
    def test_is_404_request_min200(self):
        minimum = ('A0 B1 C2 D3 E4 F5 G6 H7 {0} J9'.format(200))
        self.assertFalse(helper.is_404_request(minimum))

    def test_is_404_request_min404(self):
        '''Minimum example of non 404 order'''
        minimum = ('A0 B1 C2 D3 E4 F5 G6 H7 {0} J9'.format(404))
        self.assertTrue(helper.is_404_request(minimum))

    def test_is_404_request_min400(self):
        '''400 is not considered 404'''
        minimum = ('A0 B1 C2 D3 E4 F5 G6 H7 {0} J9'.format(400))
        self.assertFalse(helper.is_404_request(minimum))

    def test_is_404_request_prefect404(self):
        perfect0 = ('{0} - - [{1}] "GET /orders/{2}-{3}/{4} HTTP/1.1" {5} {6}'
                    ' Foo Bar Philip'.format('SOME_IP_ADDRESS',
                                             '05/Jun/2015:13:43:07 -0500',
                                             'USER_EMAIL', 'ORDER_EXTRA',
                                             'SCENE_FILE_NAME.tar.gz',
                                             '404',  # Return code
                                             '100000'))  # downloaded_bytes
        self.assertTrue(helper.is_404_request(perfect0))


class TestIsProductionOrder(unittest.TestCase):
    def test_is_production_order_min(self):
        minimum = 'GET /orders/'+'.tar.gz'
        self.assertTrue(helper.is_production_order(minimum))

    def test_is_production_order_prefect(self):
        perfect0 = ('{0} - - [{1}] "GET /orders/{2}-{3}/{4} HTTP/1.1" {5} {6}'
                    ' Foo Bar Philip'.format('SOME_IP_ADDRESS',
                                             '05/Jun/2015:13:43:07 -0500',
                                             'USER_EMAIL', 'ORDER_EXTRA',
                                             'SCENE_FILE_NAME.tar.gz',
                                             '404',  # Return code
                                             '100000'))  # downloaded_bytes
        self.assertTrue(helper.is_production_order(perfect0))


class TestEmailCategory(unittest.TestCase):
    def test_is_edu(self):
        edu = ('''{0} - - [01/Jul/2015:13:09:16 -0500] "GET /orders/{1}-06192015-150025/LT50370311998352-SC20150620065152.tar.gz HTTP/1.1" 200 284125751 "-" "Python-urllib/2.7"'''
               .format(Default.ip,
                       'researcher@school.edu'))
        value = helper.get_email_category(edu)
        self.assertEqual(value, '*.edu')

    def test_is_usgs_gov(self):
        gov = ('''{0} - - [01/Jul/2015:13:09:16 -0500] "GET /orders/{1}-06192015-150025/LT50370311998352-SC20150620065152.tar.gz HTTP/1.1" 200 284125751 "-" "Python-urllib/2.7"'''
               .format(Default.ip,
                       'NoReply@usgs.gov')
               )
        value = helper.get_email_category(gov)
        self.assertEqual(value, 'usgs.gov')

    def test_is_nonusgs_gov(self):
        gov = ('''{0} - - [01/Jul/2015:13:09:16 -0500] "GET /orders/{1}-06192015-150025/LT50370311998352-SC20150620065152.tar.gz HTTP/1.1" 200 284125751 "-" "Python-urllib/2.7"'''
               .format(Default.ip,
                       'president@mvp.gov')
               )
        value = helper.get_email_category(gov)
        self.assertEqual(value, 'not-usgs.gov')

    def test_is_other(self):
        other = ('''{0} - - [01/Jul/2015:13:09:16 -0500] "GET /orders/{1}-06192015-150025/LT50370311998352-SC20150620065152.tar.gz HTTP/1.1" 200 284125751 "-" "Python-urllib/2.7"'''
                 .format(Default.ip,
                         'disposable.style.email.with+symbol@example.com'))
        value = helper.get_email_category(other)
        self.assertEqual(value, 'other')


if __name__ == "__main__":
    unittest.main()

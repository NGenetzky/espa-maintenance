import unittest
import datetime
import logging
import apache_log_helper as helper

bad0 = '152.61.192.99 - - [03/Jun/2015:00:38:38 -0500] "&V55&HS=152.61.192.99" 400 166 "-" "-"'

class default():
    common = '''127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326'''
    ip = '127.0.0.1'
    user_email = '''local#!$%&'*+-/=?^_`{}|~'''

    def __init__():
        pass

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

class Test_verify_lines_on_logfiles(unittest.TestCase):
    May = '/data2/ngenetzky/espa.cr-logs/espa.cr.May'
    Jun = '/data2/ngenetzky/espa.cr-logs/espa.cr.Jun'
    July = '/data2/ngenetzky/espa.cr-logs/espa.cr.July'

    def setUp(self):
        show_debug_for_helper()

    def verify_all_lines(self, logfile):
        with open(logfile) as f:
            for line in f:
                valid_values = helper.verify_line(line)
                for value in valid_values:
                    self.assertTrue(value,'Failed to parse {0} from:{1}'
                                          .format(value, line))

    def test_May_validate_lines(self):
        self.verify_all_lines(self.May)

    def test_Jun_validate_lines(self):
        self.verify_all_lines(self.May)

    def test_July_validate_lines(self):
        self.verify_all_lines(self.May)

class Test_verify_lines_on_logfiles(unittest.TestCase):
    May = '/data2/ngenetzky/espa.cr-logs/espa.cr.May'
    Jun = '/data2/ngenetzky/espa.cr-logs/espa.cr.Jun'
    July = '/data2/ngenetzky/espa.cr-logs/espa.cr.July'

    @unittest.skip("Long test")
    def test_May_bytes_downloaded(self):
        with open(self.May) as f:
            for line in f:
                value = helper.get_bytes(line)

    @unittest.skip("Long test")
    def test_Jun_bytes_downloaded(self):
        with open(self.Jun) as f:
            for line in f:
                value = helper.get_bytes(line)

    @unittest.skip("Long test")
    def test_July_bytes_downloaded(self):
        with open(self.July) as f:
            for line in f:
                value = helper.get_bytes(line)


class Test_datetime(unittest.TestCase):

    def test_prefect_datetime(self):
        perfect =  ('{0} - - [{1}] "GET /orders/{2}-{3}/{4} HTTP/1.1" {5} {6} Foo Bar Philip'
                    .format('SOME_IP_ADDRESS','05/Jun/2015:13:43:07 -0500', 'USER_EMAIL',
                            'ORDER_EXTRA','SCENE_FILE_NAME.tar.gz',
                            '200', # Return code
                            '100000')) # downloaded_bytes
 
        value = helper.get_datetime(perfect)
        self.assertTrue(is_valid(value))

    def test_invalid_datetime(self):
        bad =  ('{0} - - [{1}] "GET /orders/{2}-{3}/{4} HTTP/1.1" {5} {6} Foo Bar Philip'
                .format('SOME_IP_ADDRESS','05/06/2015:13:43:07 -0500', 'USER_EMAIL',
                        'ORDER_EXTRA','SCENE_FILE_NAME.tar.gz',
                        '200', # Return code
                        '100000')) # downloaded_bytes
        with self.assertRaises(ValueError):
            value = helper.get_datetime(bad)

    def test_invalid_time_local(self):
        bad =  ('{0} - - [{1}]"GET /orders/{2}-{3}/{4} HTTP/1.1" {5} {6} Foo Bar Philip'
                .format('SOME_IP_ADDRESS','05/Jun/2015:13:43:07 -0500', 'USER_EMAIL',
                        'ORDER_EXTRA','SCENE_FILE_NAME.tar.gz',
                        '200', # Return code
                        '100000')) # downloaded_bytes
        with self.assertRaises(Exception):
            value = helper.get_datetime(bad)


class Test_return_code(unittest.TestCase):
    def test_perfect_for_rtcode(self):
        perfect =  ('A0 B1 C2 D3 E4 F5 G6 H7 {0} J9'.format(200))
        value = helper.get_rtcode(perfect)
        self.assertTrue(is_valid(value))

    def test_bad_user_request0(self):
        '''Fail to extract rtcode

        Invalid because CUSTOMER_REQUEST does not contain 2 spaces.
        '''
        line =  ('{0} - - [{1}] "{2}" {3} {4} Foo Bar Philip'
            .format('SOME_IP_ADDRESS','05/Jun/2015:13:43:07 -0500', 'CUSTOMER_REQUEST',
                    '200', # Return code
                    '100000')) # downloaded_bytes
        with self.assertRaises(Exception):
            value = helper.get_rtcode(line)

    def test_non_production_order(self):
        '''Succuessfully extracts rtcode even not production order'''
        line = '''{0} - - [05/Jun/2015:13:43:07 -0500] "GET /downloads/auxiliaries/land%5C_water%5C_poly/land%5C_no%5C_buf.ply.gz HTTP/1.1" 404 263 "-" "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0"'''.format(default.ip)
        value = helper.get_rtcode(line)
        self.assertTrue(is_valid(value),'Value={0}'.format(value))

class Test_downloaded_bytes(unittest.TestCase):
    def test_perfect_for_downloaded_bytes(self):
        perfect =  ('A0 B1 C2 D3 E4 F5 G6 H7 I8 {0}'.format(123456))
        value = helper.get_bytes(perfect)
        self.assertTrue(is_valid(value))

    def test_bad_user_request0(self):
        '''Fail to extract rtcode

        Invalid because CUSTOMER_REQUEST does not contain 2 spaces.
        '''
        line =  ('{0} - - [{1}] "{2}" {3} {4} Foo Bar Philip'
            .format('SOME_IP_ADDRESS','05/Jun/2015:13:43:07 -0500', 'CUSTOMER_REQUEST',
                    '200', # Return code
                    '100000')) # downloaded_bytes
        with self.assertRaises(Exception):
            value = helper.get_bytes(line)

    def test_non_production_order(self):
        '''Succeed to extract bytes even on non production order'''
        line = '''{0} - - [05/Jun/2015:13:43:07 -0500] "GET /downloads/auxiliaries/land%5C_water%5C_poly/land%5C_no%5C_buf.ply.gz HTTP/1.1" 404 263 "-" "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0"'''.format(default.ip)
        #self.report_failures(line)
        value = helper.get_bytes(line)
        self.assertTrue(is_valid(value))

class Test_user_email(unittest.TestCase):
    def test_request_base_dir(self):
        bad = '{0} - - [01/Jul/2015:00:00:27 -0500] "GET / HTTP/1.1" 302 5 "-" "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)'.format(default.ip)
        with self.assertRaises(Exception):
            value = helper.get_user_email(bad)
            self.assertFalse(is_valid(value))
 
    def test_request_base_dir(self):
        bad = '{0} - - [01/Jun/2015:00:01:14 -0500] "GET /ordering/status/{1} HTTP/1.1" 301 5 "-" "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36"'.format(default.ip, default.user_email)
        value = helper.get_user_email(bad)
        self.assertEqual(value,'BAD_PARSE')

    def test_request_base_dir(self):
        bad = '{0} - - [01/May/2015:00:00:09 -0500] "GET /provisional/dswe/p39r33/LE70390332010231-SC20150312110840.cksum HTTP/1.1" 404 266 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"'.format(default.ip)
        value = helper.get_user_email(bad)
        self.assertEqual(value,'BAD_PARSE')


class Test_is_successful(unittest.TestCase):
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
        perfect0 =  ('{0} - - [{1}] "GET /orders/{2}-{3}/{4} HTTP/1.1" {5} {6} Foo Bar Philip'
                    .format('SOME_IP_ADDRESS','05/Jun/2015:13:43:07 -0500', 'USER_EMAIL',
                    'ORDER_EXTRA','SCENE_FILE_NAME.tar.gz',
                    '200', # Return code
                    '100000')) # downloaded_bytes
        self.assertTrue(helper.is_successful_request(perfect0))

class Test_is_successful(unittest.TestCase):
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
        perfect0 =  ('{0} - - [{1}] "GET /orders/{2}-{3}/{4} HTTP/1.1" {5} {6} Foo Bar Philip'
                    .format('SOME_IP_ADDRESS','05/Jun/2015:13:43:07 -0500', 'USER_EMAIL',
                    'ORDER_EXTRA','SCENE_FILE_NAME.tar.gz',
                    '404', # Return code
                    '100000')) # downloaded_bytes
        self.assertTrue(helper.is_404_request(perfect0))

class Test_is_successful(unittest.TestCase):
    def test_is_production_order_min(self):
        minimum = 'GET /orders/'+'.tar.gz'
        self.assertTrue(helper.is_production_order(minimum))

    def test_is_production_order_prefect(self):
        perfect0 =  ('{0} - - [{1}] "GET /orders/{2}-{3}/{4} HTTP/1.1" {5} {6} Foo Bar Philip'
                    .format('SOME_IP_ADDRESS','05/Jun/2015:13:43:07 -0500', 'USER_EMAIL',
                    'ORDER_EXTRA','SCENE_FILE_NAME.tar.gz',
                    '404', # Return code
                    '100000')) # downloaded_bytes
        self.assertTrue(helper.is_production_order(perfect0))


class Test_email_category(unittest.TestCase):
    def test_is_edu(self):
        edu = ('''{0} - - [01/Jul/2015:13:09:16 -0500] "GET /orders/{1}-06192015-150025/LT50370311998352-SC20150620065152.tar.gz HTTP/1.1" 200 284125751 "-" "Python-urllib/2.7"'''
                .format(default.ip,
                        'researcher@sdstate.edu')
                )
        email = helper.get_user_email(edu)
        value = helper.get_email_category(edu)
        self.assertEqual(value, '*.edu')

    def test_is_usgs_gov(self):
        gov = ('''{0} - - [01/Jul/2015:13:09:16 -0500] "GET /orders/{1}-06192015-150025/LT50370311998352-SC20150620065152.tar.gz HTTP/1.1" 200 284125751 "-" "Python-urllib/2.7"'''
               .format(default.ip,
                       'ngenetzky@usgs.gov')
               )
        value = helper.get_email_category(gov)
        self.assertEqual(value, 'usgs.gov')

    def test_is_nonusgs_gov(self):
        gov = ('''{0} - - [01/Jul/2015:13:09:16 -0500] "GET /orders/{1}-06192015-150025/LT50370311998352-SC20150620065152.tar.gz HTTP/1.1" 200 284125751 "-" "Python-urllib/2.7"'''
               .format(default.ip,
                       'president@mvp.gov')
               )
        value = helper.get_email_category(gov)
        self.assertEqual(value, 'not-usgs.gov')


if __name__ == "__main__":
    unittest.main()

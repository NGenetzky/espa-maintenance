'''
Created on Aug 25, 2015

@author: ngenetzky
'''
import unittest
import datetime as dt
import bytes_downloaded_report

class default():
    common = '''127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326'''
    ip = '127.0.0.1'
    user_email = '''local#!$%&'*+-/=?^_`{}|~'''

    def __init__():
        pass

class Test_bytes_downloaded(unittest.TestCase):
    def setUp(self):
        # import bytes_downloaded_report
        self.report = bytes_downloaded_report.report

    def test_successful_only(self):
        '''Checks that report contains correct GB downloaded for 200 and 206 order'''
        data = ('''{0} - - [05/Jun/2015:13:42:47 -0500] "GET /orders/{1}-0101505262598/LT50330352002255-SC20150526132824.tar.gz HTTP/1.1" 200 311765999 "-" "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36".format(default.ip, default.user_email)
{0} - - [05/Jun/2015:13:42:56 -0500] "GET /orders/{1}-06042015-193413/LE70200252004162-SC20150604205219.tar.gz HTTP/1.1" 206 221508448 "-" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:33.0) Gecko/20100101 Firefox/33.0"'''.format(default.ip, default.user_email)
                ).split('\n')
        data_bytes_donwloaded_inGB = '0.5'
        report = bytes_downloaded_report.main(data, dt.datetime.min, dt.datetime.max)
        self.assertTrue(str(data_bytes_donwloaded_inGB) in report,
                        'Report does not contain correct answer. Report={0}'.format(report))

    def test_not_modified_304(self):
        '''S1 contains only 304 responses, therefore the result is zero.'''
        # All 304 return codes.
        data = ('''{0} - - [28/May/2015:13:00:12 -0500] "GET /static/css/normalize.css HTTP/1.1" 304 0 "http://espa.cr.usgs.gov/ordering/status/" "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0"'''.format(default.ip)
        ).split('\n')
        self.assertEquals(self.report(data,
                                      dt.datetime.min, dt.datetime.max),
                          0)

    def test_not_found_404(self):
        '''S2 contains only 404 responses, therefore the result is zero.'''
        # All 404 return codes.
        data = ('''{0} - - [14/May/2015:23:09:41 -0500] "GET /orders/{1}-0101505148023/LC81740742014236-SC20150514202210.tar.gz HTTP/1.1" 404 564 "-" "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2)"'''.format(default.ip, default.user_email)
               ).split('\n')
        self.assertEquals(self.report(data,
                                      dt.datetime.min, dt.datetime.max),
                          0)

    def test_successful_200_206(self):
        '''S3 contains successful responses.'''
        # Return codes are 200 and 206.
        # bytes_downloaded = 533274447
        data = ('''{0} - - [05/Jun/2015:13:42:47 -0500] "GET /orders/{1}-0101505262598/LT50330352002255-SC20150526132824.tar.gz HTTP/1.1" 200 311765999 "-" "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36"
{0} - - [05/Jun/2015:13:42:56 -0500] "GET /orders/{1}-06042015-193413/LE70200252004162-SC20150604205219.tar.gz HTTP/1.1" 206 221508448 "-" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:33.0) Gecko/20100101 Firefox/33.0"'''.format(default.ip, default.user_email)
               ).split('\n')
        self.assertEquals(self.report(data,
                                      dt.datetime.min, dt.datetime.max),
                          533274447)

    def test_time_filter(self):
        '''Report on a single entry of S3 with microsecond filtering.'''
        # Return codes are 200 and 206.
        # bytes_downloaded = 533274447
        data = ('''{0} - - [05/Jun/2015:13:42:47 -0500] "GET /orders/{1}-0101505262598/LT50330352002255-SC20150526132824.tar.gz HTTP/1.1" 200 311765999 "-" "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36"
{0} - - [05/Jun/2015:13:42:56 -0500] "GET /orders/{1}-06042015-193413/LE70200252004162-SC20150604205219.tar.gz HTTP/1.1" 206 221508448 "-" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:33.0) Gecko/20100101 Firefox/33.0"'''
                .format(default.ip, default.user_email)
                ).split('\n')
        self.assertEquals(
            self.report(data,
                        dt.datetime(2015, 6, 5, 13, 42, 40),
                        dt.datetime(2015, 6, 5, 13, 42, 50)),
            311765999)

    def test_mix_4xx_2xx(self):
        '''S4 has 3 successful downloads with a total of 188940157 bytes dl.'''
        # Mix of return codes.
        # bytes_downloaded = 188940157 for successful downloads only
        data = ('''{0} - - [05/Jun/2015:13:43:03 -0500] "GET /orders/{1}-06042015-193413/LE70200252004274-SC20150604205515.tar.gz HTTP/1.1" 206 0 "-" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:33.0) Gecko/20100101 Firefox/33.0"
{0} - - [05/Jun/2015:13:43:04 -0500] "HEAD /orders/{1}-06042015-193413/LE70200252004274-SC20150604205515.tar.gz HTTP/1.1" 200 0 "-" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:33.0) Gecko/20100101 Firefox/33.0"
{0} - - [05/Jun/2015:13:43:05 -0500] "GET /orders/{1}-05192015-120331/LE70350112013195-SC20150520063416.tar.gz HTTP/1.0" 200 188940157 "http://espa.cr.usgs.gov/orders/nasalatency@gmail.com-05192015-120331/" "Wget/1.12 (linux-gnu)"
{0} - - [05/Jun/2015:13:43:07 -0500] "GET /orders/{1}-0101505314643/LT50160401993191-SC20150531051709.tar.gz HTTP/1.1" 499 74998 "-" "Mozilla/5.0 Gecko/20100115 Firefox/3.6"
{0} - [05/Jun/2015:13:43:07 -0500] "GET /downloads/auxiliaries/land%5C_water%5C_poly/land%5C_no%5C_buf.ply.gz HTTP/1.1" 404 263 "-" "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0"'''
                    .format(default.ip, default.user_email)
                   ).split('\n')
        self.assertEquals(self.report(data,
                                      dt.datetime.min, dt.datetime.max),
                          188940157)

if __name__ == "__main__":
    unittest.main()


#/usr/bin/env bash

for x in `ls .|egrep "(espa.cr.usgs.gov-access_log$|espa.cr.usgs.gov-access_log.[1-5]$)"`;do
    header_line=`head -n 1 $x|awk '{print $4}'|sed 's/\[//g'`;
    month=`echo $header_line|cut -f 2 -d "/"`
    year=`echo $header_line|cut -f 3 -d "/"`
    year=`echo $year|cut -f 1 -d ":"`
    month_year=$month-$year
    ba_bytes=`cat $x|grep "burned_area"|grep "tar.gz"| egrep -v "HTTP/1.1\" 499"|awk '{print $10}'| paste -sd+ - | bc`
    dswe_bytes=`cat $x|grep "dswe"|grep "tar.gz"|egrep -v "HTTP/1.1\" 499"|awk '{print $10}'| paste -sd+ - | bc`
    echo "Report for $month_year"
    echo "----------------------"
    echo "Burned Area Bytes Downloaded: $ba_bytes"
    echo "DSWE Bytes Downloaded: $dswe_bytes"
    echo " "
done

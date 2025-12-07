this is a script that basicly allows youu to automate pinging ips for devices you want to check
it has an ability that you can set it to a device and run it in the background, you can then remote into the csv and update it and the script will attempt to live update the checks (this can take a few iterations as it attempts to add them)

this also includes a tkinter ui that splits it into rows of 4 and any groups that are bigger than 25 items will be split into multiple lists
each table is also ran in multi thread allow all the tables to run simultaniusly

each table can also get a specified time to refresh if non specified defaults to 60 seconds


examples below:

-basic table top row is col names
2nd row is the table name, done by specifying only device name and leavin ip and timer blank
rows below are all ip names, ips and timers (timers if empty is 60 seconds)
```
DeviceName,Ip,Timer

exampletable,,

exampleIp,10.60.156.0,30
```

-for multiple tables
```
DeviceName,Ip,Timer

exampletable,,

exampleIp1,10.60.156.0,30

exampleIp2,10.60.156.0,30

exampleIp3,10.60.156.0,30

exampletable2,,

exampleIp2.1,10.60.156.0,30
```

this is a script that basicly allows youu to automate pinging ips for devices you want to check
it has an ability that you can set it to a device and run it in the background, you can then remote into the csv and update it and the script will attempt to live update the checks (this can take a few iterations as it attempts to add them)

this also includes a tkinter ui that splits it into rows of 4 and any groups that are bigger than 25 items will be split into multiple lists
each table is also ran in multi thread allow all the tables to run simultaniusly

each table can also get a specified time to refresh if non specified defaults to 60 seconds

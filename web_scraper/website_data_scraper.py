import urllib.request

fp = urllib.request.urlopen("https://www.sjsu.edu/classes/schedules/fall-2024.php")
mybytes = fp.read()

mystr = mybytes.decode("utf8")
fp.close()
sourceFile = open('website_data.txt', 'w')
print(mystr, file = sourceFile)


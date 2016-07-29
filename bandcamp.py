from lxml import html
import urllib.request, urllib.parse, urllib.error, zipfile, os, demjson, requests, sys, quopri
from email import message_from_string as parsemail
import imp

def main():
	imp.reload(sys);
	# sys.setdefaultencoding("utf8")
	album_url = input('\nBandcamp PAGE URL:\n>>> ')
	album_data = get_album_metadata(album_url)
	page = requests.get(album_url)
	tree = html.fromstring(page.text)
	download_tracks( album_data )

	album_artist = artist
	album_year = year[7:11]
	to_delete = album_artist + " - " + album_name + " - "

	reltypeimp = input('''\nDownload format? (FLAC,V0,320) \n>>> ''')
	if(album_data['freeDownloadPage'] == None):
		rem_file = input('\nBandcamp DOWNLOAD URL:\n>>> ')
	else:
		dldata = get_download_data(album_data['freeDownloadPage'])
		if(reltypeimp.lower() == '320'):
			theurl = dldata['items'][0]['downloads']['mp3-320']['url']
		elif(reltypeimp.lower() == 'v0'):
			theurl = dldata['items'][0]['downloads']['mp3-v0']['url']
		else:
			theurl = dldata['items'][0]['downloads']['flac']['url']
		theurl = theurl.replace('download', 'statdownload')
		expire_error = ' '.join(requests.get(theurl).text.split(' ')[4:])[:-1]
		rem_file = demjson.decode(expire_error)['retry_url']
	loc_file = album_artist + " - " + album_name + " (" + album_year + ") [" + reltypeimp.upper() + "]"
	loc_file = remove(loc_file, '\/:*?"<>|')
	sys.stdout.write('\rFetching...\n')
	urllib.request.urlretrieve (rem_file, loc_file + ".zip", reporthook=report)
	print("\nDownload Complete!")
	os.makedirs(loc_file)
	print("Directory Created!")

	with zipfile.ZipFile(loc_file + ".zip", "r") as z:
		z.extractall(loc_file)
	print("Archive Extracted!")

	pathiter = (os.path.join(root, filename)
		for root, _, filenames in os.walk(loc_file)
		for filename in filenames
	)
	for path in pathiter:
		newname =  path.replace(to_delete, '')
		if newname != path:
			os.rename(path,newname)
	print("Files Renamed!")

	os.remove(loc_file + ".zip")
	print("ZIP Deleted!")
	
def report(count, blockSize, totalSize):
  	percent = int(count*blockSize*100/totalSize)
  	sys.stdout.write("\r%d%%" % percent + ' complete')
  	sys.stdout.flush()

def get_album_metadata( url ):
    request = requests.get(url)
    sloppy_json = request.text.split("var TralbumData = ")
    # clean 
    sloppy_json = sloppy_json[1].replace('" + "', "")
    sloppy_json = sloppy_json.replace("'", "\'")
    sloppy_json = sloppy_json.split("};")[0] + "};"
    sloppy_json = sloppy_json.replace("};","}")
    return demjson.decode( sloppy_json )

def get_download_data( url ):
    request = requests.get(url)
    sloppy_json = request.text.split("var DownloadData = ")
    # clean 
    sloppy_json = sloppy_json[1].replace('" + "', "")
    sloppy_json = sloppy_json.replace("'", "\'")
    sloppy_json = sloppy_json.split("};")[0] + "};"
    sloppy_json = sloppy_json.replace("};","}")
    return demjson.decode( sloppy_json )


def download_tracks( album_data ):
    global artist
    artist = album_data["artist"]
    global album_name
    album_name = album_data["current"]["title"]
    global year
    year = album_data["current"]["release_date"]

def makeanonbox():
	anonbox = requests.get('https://anonbox.net/en/', verify=False)
	tree = html.fromstring(anonbox.text.encode())
	address = tree.get_element_by_id('content').find('dl')[1].text_content()
	inbox = tree.get_element_by_id('content').find('dl')[3].text_content()
	return([address,inbox])

def getlinkfromanonbox(box):
	return quopri.decodestring(parsemail(requests.get(box[1], verify=False).text).get_payload()[0].as_string()).splitlines()[7].decode()

def remove(value, deletechars):
    for c in deletechars:
        value = value.replace(c,'')
    return value

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(e)

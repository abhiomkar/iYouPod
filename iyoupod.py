#!/usr/bin/python
# Title: iYouPod
# Author: Abhinay Omkar
# Features:
# User should be allowed to choose his playlist which is gonna be feed into his iTunes library
# ex: The user will be allowed to select on of his playlist - "My Old Hindi Songs", "Best Telugu Comedy" the first N videos from the selected playlist will be feed into iTunes, It can be his Favorite youtube list too (Default is Favorite list)
#
# User will be able to set the limit of videos that should be in sync with iTunes with Youtube Playlist (Default is 15 Videos)

# User Input:
# Enter your youtube username:
# http://youtube.com/user/______

# You have following playlists:
# 1. Playlist1
# 2. Playlist2
# 3. Playlist3
# Or, Just hist enter to sync your Fovarite Youtube Videos
# :
# 

import os, sys, platform
import gdata.youtube
import gdata.youtube.service
from urllib import urlopen, unquote
from urlparse import parse_qs, urlparse

yt_service = gdata.youtube.service.YouTubeService()
yt_fav_uri = "http://gdata.youtube.com/feeds/api/users/abhiomkar/favorites?max-results=15"

# Find out which operating system?
if platform.system() == 'Darwin':
	import appscript
	rel_path = os.path.expanduser('~/Movies/Youtube2iPod/')
elif platform.system() == 'Windows':
	rel_path = os.path.expanduser('~/Youtube2iPod/')
elif platform.system() in ('Linux', 'FreeBSD'):
	rel_path = os.path.expanduser('~/Videos/Youtube2iPod/')
else: 
	rel_path = os.path.expanduser('~/Youtube2iPod/')

def GetPlaylistEntry(entry):
# Print 
 try:
  print "\t- "+entry.title.text
  print "\t  "+entry.media.player.url.replace("&feature=youtube_gdata","")
  print
  return entry.title.text, entry.media.player.url.replace("&feature=youtube_gdata","")
 except Exception:
  print 'Video Unavailable?'

  # show alternate formats
  if entry.media.content:
    for alternate_format in entry.media.content:
      if 'isDefault' not in alternate_format.extension_attributes:
        print 'Alternate format: %s | url: %s ' % (alternate_format.type,
                                                   alternate_format.url)

def GetPlaylistVideos(uri):
	# Returns videos of give playlist in dictionary format { Video Title : Video watch URL }
	# yt_service = gdata.youtube.service.YouTubeService()
	yt_videos = {}
	feed = yt_service.GetYouTubeVideoFeed(uri)
	for entry in feed.entry:
		yt_videotitle, yt_watchurl = GetPlaylistEntry(entry)
		yt_videos[yt_videotitle] = yt_watchurl
		
	print "Retrieved "+str(len(yt_videos))+" Videos."
	return yt_videos

def GetYoutubePlaylist(yt_username):
	# Returns the user's playlist in dictionary format { Playlist name : Playlist URL }
	playlist_dict = {}
	playlist_feed = yt_service.GetYouTubePlaylistFeed(username=yt_username)

	for playlist_entry in playlist_feed.entry:	
		PlaylistName = playlist_entry.title.text
		PlaylistURI = playlist_entry.feed_link[0].href
		playlist_dict[PlaylistName] = PlaylistURI

	return playlist_dict
	
def downloadVideo(yt_watchurl):
	url_query = urlparse(yt_watchurl).query
	video_id = parse_qs(url_query)['v'][0]
	url_data = urlopen('http://www.youtube.com/get_video_info?&video_id=' + video_id).read()
	url_info = parse_qs(unquote(url_data.decode('utf-8')))

	if url_info['status'][0]=='fail':
		print "--> " + yt_watchurl
		print "ERROR: Unable to download this video! Skipping..."
		return 
		
	token_value = url_info['token'][0]
	video_title = url_info['title'][0]

	download_url = "http://www.youtube.com/get_video?video_id={0}&t={1}&fmt=18".format(video_id, token_value)

	# import pdb; pdb.set_trace()
	video_title = video_title.replace('/','')
	filename = video_title+" - "+video_id+".mp4"
	filepath = rel_path+filename

	if os.path.exists(filepath):
		print "[Skip] Already Downloaded: %s" % video_title
		return
	
	sys.stdout.write("Downloading: %s... " % video_title)
	sys.stdout.flush()
	
	download = urlopen(download_url).read()		
		
	f = open(filepath, 'wb')
	f.write(download)
	f.close()
	print "[Downloaded]"
	return filepath
	
def export2iTunes(vid_filename):
	# I add downloaded Youtube videos to iTunes Movie Library as and when they are downloaded
	if platform.system() == 'Darwin':
		# If it's Mac OS X
		appscript.app(u'iTunes').add(appscript.mactypes.File(vid_filename))

def main():
	print "Hello! what's your Youtube username?"
	yt_username = raw_input("http://youtube.com/user/")

	# Returns the names and urls of user's playlist in dict format
	playlist_dict = GetYoutubePlaylist(yt_username)

	# Print playlist names to user to choose
	for opt, p_name in enumerate(playlist_dict.keys(), start=1):
		print str(opt)+". "+p_name

	# Prompt to select playlist
	print "Please choose your youtube playlist to sync (1-"+str(len(playlist_dict.keys()))+")" 
	print "(Just hit enter to select your Youtube Favorite list)" 
	playlist_option = raw_input("> ")

	if playlist_option.strip() == '':
		# Favorite Playlist
		TargetPlaylistName = 'Favorites'
		playlist_uri = yt_fav_uri
	elif playlist_option.isdigit() == True:
		# User has selected a specific playlist name
		playlist_option = int(playlist_option)
		TargetPlaylistName = playlist_dict.keys()[playlist_option-1]
		playlist_uri = playlist_dict[TargetPlaylistName]
	else:
		print "ERROR: Please enter valid input! try again..."
		sys.exit()
	
	playlist_header = "| Playlist: '%s' |" % TargetPlaylistName
	print
	print '-'*len(playlist_header)
	print playlist_header
	print '-'*len(playlist_header)
	
	# This will get all videos from the playlist selected above
	yt_videos = GetPlaylistVideos(playlist_uri)

	# Downlaod These videos to current directory
	print
	print ">>> Now Downloading " + str(len(yt_videos.values())) + " Videos. This may take few minutes.\n## I Export these videos to your iTunes Movie Library"
	
	try:
		os.makedirs(rel_path)
	except OSError, e:
		if e.errno == 17:
			# Directory alrady exists
			pass
		else:
			# FATAL error: Unable to create target directory
			raise
			
	for yt_watchurl in yt_videos.values():
			vid_filename = downloadVideo(yt_watchurl)
			if vid_filename:
				export2iTunes(vid_filename)	
	
if __name__ == "__main__":
	main()	

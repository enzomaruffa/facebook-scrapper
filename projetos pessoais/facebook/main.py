__name__ = "main"

# ENV file stuff
import os
from os.path import join, dirname
from dotenv import load_dotenv
 
# Create .env file path.
dotenv_path = join(dirname(__file__), '.env')
 
# Load file from the path.
load_dotenv(dotenv_path)

pages_id = os.getenv('PAGES_ID')
access_token_key = os.getenv('ACCESS_TOKEN_KEY')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')

# --------------------------

class Page:
    def __init__(self, page_id):
    	self.page_id = page_id
    	self.posts = []    # creates a new empty list for each dog

    def add_post(self, post):
    	self.posts.append(post)

    def find_post(self, post_id):
    	for post in self.posts:
    		if (post.post_id == post_id):
    			return post
    	return None

class Post:
	def __init__(self, post_id):
		self.post_id = post_id
		self.message = None
		self.permalink_url = None
		self.reactions_count = None
		self.comment_count = None
		self.share_count = None

import math
import requests
import facebook
import json
import time

call_count = 0
call_cap = 190

def check_call_count():
	if (call_count >= call_cap):
		call_count = 0
		print("Facebook API calls limit exceeded! Waiting for 3600 seconds (1 hour)")
		time.sleep(3600)
	return True

graph = facebook.GraphAPI(access_token=access_token_key, version="3.0")

pages_id = pages_id.split() # pages_id era uma string e agora é uma lista com os IDs
pages = []

for page_id in pages_id:
	page = Page(page_id)
	pages.append(page)

	# Retrieve posts
	if (check_call_count):
		call_count += 1
		page_posts = graph.get_object(id=page_id, fields='id, posts')
	
	print("ID da página: " + page_posts['id']) # Print page_id

	page_posts = page_posts['posts'] # Page is only its own data
	
	next_post_group_url = page_posts['paging']['next']
	while next_post_group_url != None:	

		# Checks if the last page has just been iterated
		if ('next' in page_posts['paging']):
			next_post_group_url = page_posts['paging']['next']
		else:
			next_post_group_url = None

		posts = page_posts['data'] # Get posts list
		#print("Posts count: " + str(len(posts))) # Print list size

		# Appending post to list
		for post in posts:
			post_obj = Post(post['id'])			
			page.add_post(post_obj) # Appends post id to list

		if (next_post_group_url != None):
			if (check_call_count):
				call_count += 1
				page_posts = requests.get(next_post_group_url).json()


	# ---------------- SCRAPPING INFO ----------------

	# Getting post shares, link and message
	posts_ids = [post.post_id for post in page.posts]

	# Facebook allows a maximum of 50 IDs per query
	calls_needed = math.ceil(len(posts_ids) / 51)
	for i in range(0, calls_needed):
		requested_posts_ids = posts_ids[i*50:(i*50)+50]
		if (check_call_count):
			call_count += 1
			posts_metadata = graph.get_objects(ids=requested_posts_ids, fields="shares, permalink_url, message")
		
		for post_id in requested_posts_ids:
			print("Requesting post " + str(post_id) + " metadata")
			post_metadata = posts_metadata[post_id]

			# Get post
			post = page.find_post(post_id)

			# Update post info
			post.permalink_url = post_metadata['permalink_url']
			post.message = post_metadata['message']
			if ('shares' in post_metadata.keys()):
				post.share_count = post_metadata['shares']['count']

	for post_id in posts_ids:

		if (check_call_count):
			call_count += 1
			print("Requesting post " + str(post_id) + " comments")
			post_comments = graph.get_connections(id=post_id, connection_name='comments', summary='total_count') # Get the comments from a post.

		post = page.find_post(post_id)
		post.comment_count = post_comments['summary']['total_count']

		#reactions_types = ['LIKE', 'LOVE', 'WOW', 'HAHA', 'SAD', 'ANGRY', 'THANKFUL']

		if (check_call_count):
			call_count += 1
			print("Requesting post " + str(post_id) + " reaction")
			post_reactions = graph.get_connections(id=post_id, connection_name='reactions', summary='total_count') # Get reactions from a post.
			
		post = page.find_post(post_id)
		post.reactions_count = post_reactions['summary']['total_count']

	for post in page.posts:
		print("post_id: " + str(post.post_id))
		print("permalink_url: " + str(post.permalink_url))
		print("reactions_count: " + str(post.reactions_count))
		print("comment_count: " + str(post.comment_count))
		print("share_count: " + str(post.share_count))

	
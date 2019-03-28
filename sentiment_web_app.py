#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  2 11:40:13 2019

@author: michaelmerani
"""

# -*- coding: utf-8 -*-


import os

import Utils
import flask
from flask import render_template,request
import urllib.parse
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import pickle

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

application = app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works, but if you
# use this code in your application please replace this with a truly secret
# key. See http://flask.pocoo.org/docs/0.12/quickstart/#sessions.
app.secret_key = 'XgBtL2nBpBcgqpY5-e-56TNJ'

classifier = pickle.load(open('./Data/logisticRegression.pkl', 'rb'))
vectorizer = pickle.load(open('./Data/vectorizer.pkl', 'rb'))


@app.route('/',methods=['POST','GET'])
def index():
  return render_template('index.html')


@app.route('/results',methods=['POST','GET'])

def sumbit():
  if 'credentials' not in flask.session:
     return flask.redirect('authorize')

  # Load the credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  client = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)
  
  if request.method == "POST":
     videoId = get_videoId()
     
     if videoId == 'not-valid':
         return render_template('index.html',analysis='Please enter a valid youtube URL')
     else:
         comment_list = comment_threads_list_by_video_id(client,video_id=videoId)
         sentiment_analysis = apply_model(comment_list)
         analysis = 'This trailer has {}% positive comments and {}% negative comments'.format(round(sentiment_analysis[0]),round(sentiment_analysis[1]))
         return render_template('index.html',analysis=analysis)
 
    
def get_videoId():
    try:
        videoURL = request.form.get('url')
        url_data = urllib.parse.urlparse(videoURL)
        query = urllib.parse.parse_qs(url_data.query)
        videoId = query["v"][0]
        return videoId
    except:
        return 'not-valid'
     

def apply_model(comments):
    comments = vectorizer.transform(comments)
    predictions = classifier.predict(comments)
    
    sentiment = calculate_sentiment(predictions)
    
    #flash('This video has {}% positive sentiment and  {}% negative sentiment'.format(round(sentiment[0]),round(sentiment[1])))
    return sentiment

def calculate_sentiment(predictions):
    positive_sentiment = sum(predictions)
    
    return [(positive_sentiment/len(predictions))*100, ((len(predictions)-positive_sentiment)/len(predictions))*100]      

@app.route('/authorize')
def authorize():
  # Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow
  # steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
  authorization_url, state = flow.authorization_url(
      # This parameter enables offline access which gives your application
      # both an access and refresh token.
      access_type='offline',
      # This parameter enables incremental auth.
      include_granted_scopes='true')

  # Store the state in the session so that the callback can verify that
  # the authorization server response.
  flask.session['state'] = state

  return flask.redirect(authorization_url)



@app.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verify the authorization server response.
  state = flask.session['state']
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store the credentials in the session.
  # ACTION ITEM for developers:
  #     Store user's access and refresh tokens in your data store if
  #     incorporating this code into your real app.
  credentials = flow.credentials
  flask.session['credentials'] = {
      'token': credentials.token,
      'refresh_token': credentials.refresh_token,
      'token_uri': credentials.token_uri,
      'client_id': credentials.client_id,
      'client_secret': credentials.client_secret,
      'scopes': credentials.scopes
  }

  return flask.redirect(flask.url_for('index'))
    
   

def get_comments(response):
  if response:
    text_list = []
    items = response['items']
    for item in items:
        text_list.append(str(item['snippet']['topLevelComment']['snippet']['textDisplay']))
      
    
    comment_list = Utils.preprocess(text_list)
    #print([item['textDisplay'] for item in response['items'] for item['textDisplay'] in item])         
    return comment_list #flask.jsonify(**response)
  else:
    return ('This request does not return a response. For these samples, ' +
            'this is generally true for requests that delete resources, ' +
            'such as <code>playlists.delete()</code>, but it is also ' +
            'true for some other methods, such as <code>videos.rate()</code>.')

# Build a resource based on a list of properties given as key-value pairs.
# Leave properties with empty values out of the inserted resource.
def build_resource(properties):
  resource = {}
  for p in properties:
    # Given a key like "snippet.title", split into "snippet" and "title", where
    # "snippet" will be an object and "title" will be a property in that object.
    prop_array = p.split('.')
    ref = resource
    for pa in range(0, len(prop_array)):
      is_array = False
      key = prop_array[pa]

      # For properties that have array values, convert a name like
      # "snippet.tags[]" to snippet.tags, and set a flag to handle
      # the value as an array.
      if key[-2:] == '[]':
        key = key[0:len(key)-2:]
        is_array = True

      if pa == (len(prop_array) - 1):
        # Leave properties without values out of inserted resource.
        if properties[p]:
          if is_array:
            ref[key] = properties[p].split(',')
          else:
            ref[key] = properties[p]
      elif key not in ref:
        # For example, the property is "snippet.title", but the resource does
        # not yet have a "snippet" object. Create the snippet object here.
        # Setting "ref = ref[key]" means that in the next time through the
        # "for pa in range ..." loop, we will be setting a property in the
        # resource's "snippet" object.
        ref[key] = {}
        ref = ref[key]
      else:
        # For example, the property is "snippet.description", and the resource
        # already has a "snippet" object.
        ref = ref[key]
  return resource

# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
  good_kwargs = {}
  if kwargs is not None:
    for key, value in kwargs.items():
      if value:
        good_kwargs[key] = value
  return good_kwargs

def comment_threads_list_by_video_id(client, video_id):
    
    
    results = client.commentThreads().list(
            part="snippet",
            videoId=video_id,
            textFormat="plainText",
    ).execute()
    
    comment_list = get_comments(results)
    
    
    while('nextPageToken' in results):
        results = client.commentThreads().list(
                part="snippet",
                videoId=video_id,
                pageToken=results["nextPageToken"],
                textFormat="plainText"
        ).execute()
        comment_list = comment_list + get_comments(results)
    
    

    return comment_list



if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification. When
  # running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
  app.run('localhost', 8090, debug=True)
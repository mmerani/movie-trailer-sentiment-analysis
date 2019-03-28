# Movie Trailer Sentiment Analysis with Logistic Regression

This repository contains my movie trailer sentiment analysis project using logistic regression.  Opening the jupyter notebook provided will show the steps I took to build the model. Utils.py provides some auxilary methods used in the jupyter notebook as well. 

## The dataset
The dataset was obtained from a Kaggle.  The test set was seperated into different txt files which I combined into 1 
csv file will all the data. Information on how I did this can be found in reviews_setup.py


## Web app
You can test the web app I created by running sentiment_web_app.py then open browser to (localhost:8090). Make sure you only use Youtube links or the model will not run. Also keep in mind that the more comments the video has then longer it will take to analyze. 

![web](./images/web_app1)
![web](./images/web_app2)

## Requirements
This notebook will run in Python >= 3.5. The following packages are required:

* flask
* nltk
* numpy
* pandas
* scikit-learn


## Limitations
As mentioned above the app will only run on with youtube links. It is meant to be a movie trailer sentiment analyzer, however it will work on any YouTube video. Also, the more comments the video has the longer it will take to analyze



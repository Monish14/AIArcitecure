# import libraries
from google_play_scraper import Sort, reviews, app
import ssl
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# import custom libraries
from mongo_db_client import MongoDBClient

# SSL error fix
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# define app packages
app_packages = ["ca.gc.hcsc.canada.stopcovid",
                "au.gov.health.covidsafe",
                "com.nhs.online.nhsonline",
                "gov.ny.health.proximity"
                ]

# define meta data for the apps
app_names = {"ca.gc.hcsc.canada.stopcovid": ("COVID Alert", "Health Canada", "Canada"),
             "au.gov.health.covidsafe": ("COVIDSafe", "Australian Department of Health", "Australia"),
             "com.nhs.online.nhsonline": ("NHS COVID-19", "Department of Health and Social Care", "UK"),
             "gov.ny.health.proximity": ("COVID Alert NY", "New York State Department of Health", "New York, US")}

# initialize analyzer
analyser = SentimentIntensityAnalyzer()


# get the app information such as  from google play store
def get_app_info(ap):
    info = app(ap, lang='en', country='us')
    del info['comments']
    return info


# get app reviews
def get_reviews(ap):
    app_reviews = []
    for score in list(range(1, 6)):
        for sort_order in [Sort.MOST_RELEVANT, Sort.NEWEST]:
            rvs, _ = reviews(ap, lang='en', country='us',
                             sort=sort_order, count=50, filter_score_with=score)
            for r in rvs:
                r['sortOrder'] = 'most_relevant' if sort_order == Sort.MOST_RELEVANT else 'newest'
                r['appId'] = ap
            app_reviews.extend(rvs)
    return app_reviews


# get the sentiment for review
def get_sentiment(string):
    sentiment = analyser.polarity_scores(string)
    # keys: "neg" , "neu", "pos", "compound"
    negative = sentiment["neg"]
    neutral = sentiment["neu"]
    positive = sentiment["pos"]
    compound = sentiment["compound"]

    # get polarity in human readable format
    sentiment = get_polarity(compound)

    return sentiment, compound, neutral, positive, negative


# convert polarity to human readable string
def get_polarity(polarity):
    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"


# initialize our custom mongo db client
client = MongoDBClient()


def upload_prediction_tag(title, tags):

    if len(tags) > 0:

        for tag in tags:
            tag = tag[0]
            tag_prediction = tag[1]

            json = {
                "Title": title,
                "Tags": tag,
                "Probability": tag_prediction
            }
        client.upload_tag(json)

# get app metadata and reviews


for ap in app_packages:

    app_info = get_app_info(ap)

    title = app_info["title"]
    description = app_info["description"]
    installs = app_info["installs"]
    score = app_info["score"]
    ratings_count = app_info["ratings"]
    reviews_count = app_info["reviews"]
    screenshot = app_info["screenshots"][0]
    developer = app_info["developer"]

    reviews_list = get_reviews(ap)

    prediction_tags = custom_vision_client.classify_image_url(screenshot)
    upload_prediction_tag(title, prediction_tags)

    for review in reviews_list:
        sentiment = get_sentiment(review["content"])

        json = {
            "title": title,
            "description": description,
            "installs": installs,
            "score": score,
            "developer": developer,
            "ratings_count": ratings_count,
            "reviews_count": reviews_count,
            "review": review["content"],
            "screenshots": screenshot,
            "review_score": review["score"],
            "overall_score": score,
            "sentiment": sentiment[0],
            "compound": sentiment[1],
            "neutral": sentiment[2],
            "positive": sentiment[3],
            "negative": sentiment[4],
            "COVID Alert - Canada": prediction_tags[0][1],
            "COVID Alert NY - US": prediction_tags[1][1],
            "COVIDSafe - Australia": prediction_tags[2][1],
            "NHS COVID-19 - UK": prediction_tags[3][1]
        }
        client.upload_reviews(json)

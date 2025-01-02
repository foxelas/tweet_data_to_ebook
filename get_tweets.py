import json
import pandas as pd
from os.path import join as pathjoin
from configuration import data_path, tweets_file, tweets_csv_file, min_date, max_date, min_favorite_count


def prepare_files(min_favorite_count_=min_favorite_count,
                  max_date_=max_date,
                  min_date_=min_date):
    # Load and parse JSON data from the file
    file_path = pathjoin(data_path, tweets_file)
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read().split("=", 1)[1].strip()
        data = json.loads(content)

    # Extract relevant tweet information
    tweets = []
    for tweet in data:
        tweet_obj = tweet.get("tweet", {})
        media_urls = [
            media["media_url_https"]
            for media in tweet_obj.get("extended_entities", {}).get("media", [])
        ]

        # Skip tweets with only links and no media
        if "https://t.co/" in tweet_obj.get("full_text", "") and not media_urls:
            continue

        tweets.append({
            "id": tweet_obj.get("id_str"),
            "full_text": tweet_obj.get("full_text"),
            "created_at": tweet_obj.get("created_at"),
            "in_reply_to_status_id": tweet_obj.get("in_reply_to_status_id_str"),
            "favorite_count": int(tweet_obj.get("favorite_count", 0)),
            "retweet_count": int(tweet_obj.get("retweet_count", 0)),
            "lang": tweet_obj.get("lang"),
            "media_urls": media_urls
        })

    # Create a DataFrame and preprocess it
    tweets_df = pd.DataFrame(tweets)
    tweets_df['created_at'] = pd.to_datetime(tweets_df['created_at'], format='%a %b %d %H:%M:%S %z %Y')

    # Filter and sort tweets
    tweets_df = tweets_df[
        tweets_df['in_reply_to_status_id'].isnull() &  # Exclude replies
        ~tweets_df['full_text'].str.startswith('RT') &  # Exclude retweets
        (tweets_df['favorite_count'] > min_favorite_count_) &  # Exclude low-engagement tweets
        (tweets_df['created_at'] < max_date_) &  # Exclude tweets after max date
        (tweets_df['created_at'] > min_date_)  # Exclude tweets before min date
        ].sort_values(by='created_at', ascending=True)

    # Save the filtered tweets and provide a summary
    tweets_df.to_csv(tweets_csv_file, index=False)

    print(tweets_df.head())
    print(tweets_df.columns.values)
    print(f"Total tweets: {len(tweets_df)}")

if __name__ == "__main__":
    prepare_files()
import json
import pandas as pd
from os.path import join as pathjoin
from configuration import data_path, tweets_file, tweets_cleaned_file, tweets_csv_file

file_path = pathjoin(data_path, tweets_file)
# Load tweets.json
# Read the file and strip unnecessary prefix
with open(file_path, "r", encoding="utf-8") as file:
    content = file.read()

# Remove JavaScript variable assignment and keep the JSON part
# Assuming the prefix ends with `= [`
json_content = content.split("=", 1)[1].strip()

# Save the cleaned JSON to a new file (optional)
cleaned_file_path = tweets_cleaned_file
with open(cleaned_file_path, "w", encoding="utf-8") as cleaned_file:
    cleaned_file.write(json_content)

# Now load the cleaned JSON file
with open(cleaned_file_path, "r", encoding="utf-8") as cleaned_file:
    data = json.load(cleaned_file)

tweets = []

for tweet in data:
    tweet_obj = tweet.get("tweet", {})
    extended_entities = tweet_obj.get("extended_entities", {})

    # Extract media URLs if they exist
    media_urls = []
    if "media" in extended_entities:
        for media in extended_entities["media"]:
            media_urls.append(media["media_url_https"])

    # Skip tweets with only links and no media
    if "https://t.co/" in tweet_obj.get("full_text") and len(media_urls) == 0:
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



# Convert to a Pandas DataFrame
tweets_df = pd.DataFrame(tweets)

# Convert 'created_at' to datetime for sorting
tweets_df['created_at'] = pd.to_datetime(tweets_df['created_at'], format='%a %b %d %H:%M:%S %z %Y')

# Filter out replies and retweets and tweets with less than 3 likes
tweets_df = tweets_df[
    (tweets_df['in_reply_to_status_id'].isnull()) &
    (~tweets_df['full_text'].str.startswith('RT')) &
    (tweets_df['favorite_count'] > 2) &
    (tweets_df['created_at'] < '2023-01-01')
]


# Sort by the earliest creation date
tweets_df = tweets_df.sort_values(by='created_at', ascending=True)

# Save the filtered and sorted tweets to a CSV for manual review
tweets_df.to_csv(tweets_csv_file, index=False)

# Print a preview of the DataFrame
print(tweets_df.head())
print(tweets_df.columns.values)
print(f"Total tweets: {len(tweets_df)}")
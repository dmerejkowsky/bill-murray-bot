import os
import sys


from mastodon import Mastodon
import path
import ruamel.yaml
import twitter


def read_config():
    cfg_path = path.Path(os.path.expanduser("~/.config/bm_bot.yml"))
    return ruamel.yaml.load(cfg_path.text(), ruamel.yaml.RoundTripLoader)


def write_config(config):
    cfg_path = path.Path(os.path.expanduser("~/.config/bm_bot.yml"))
    cfg_path.write_text(ruamel.yaml.dump(config, Dumper=ruamel.yaml.RoundTripDumper))


class TwitterClient:
    def __init__(self, config):
        auth_dict = config["twitter"]["auth"]
        keys = ["token", "token_secret",
                "api_key", "api_secret"]
        auth_values = (auth_dict[key] for key in keys)
        auth = twitter.OAuth(*auth_values)
        self.api = twitter.Twitter(auth=auth)

    def get_tweets_since(self, since_id):
        # Note: two upper-case i
        for json_data in self.api.statuses.user_timeline(
                screen_name="BiIIMurray", since_id=since_id):
            yield json_data

class MastodonClient:
    def __init__(self, config):
        mastodon_conf = config["mastodon"]
        instance_url = mastodon_conf["instance_url"]
        auth_conf = mastodon_conf["auth"]
        client_id = auth_conf["client_id"]
        client_secret = auth_conf["client_secret"]
        token = auth_conf["token"]

        self.mastodon = Mastodon(
            client_id=client_id,
            client_secret=client_secret,
            access_token=token,
            api_base_url=instance_url
        )

    def toot(self, text):
        ret = self.mastodon.toot(text)
        if "error" in ret:
            sys.exit(ret)


class Bot:
    def __init__(self):
        self.config = read_config()
        self.twitter_client = TwitterClient(self.config)
        self.mastodon_client = MastodonClient(self.config)

    def execute(self):

        def has_url(tweet):
            return bool(tweet["entities"].get("urls"))

        def is_reply(tweet):
            return tweet.get("in_reply_to_screen_name") or \
                    tweet.get("in_reply_to_status_id")

        last_tweet_id = self.config["last_tweet_id"]
        tweets = list(self.twitter_client.get_tweets_since(last_tweet_id))
        if not tweets:
            print("No new tweet found")
            return
        print("Processing", len(tweets), "new tweets")
        interesting_tweets = [x for x in tweets if not (has_url(x) or is_reply(x))]
        n = len(interesting_tweets)
        for i, tweet in enumerate(interesting_tweets):
            print("Tooting", "%d/%d" % (i+1, n))
            self.mastodon_client.toot(tweet["text"])

        self.config["last_tweet_id"] = tweets[0]['id']
        write_config(self.config)


def main():
    bot = Bot()
    bot.execute()

if __name__ == "__main__":
    main()

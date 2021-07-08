# Emoji Sounds with Twitter API

from oscpy.client import OSCClient
import json


# class to grab a tweet containing a certain emoji_synth.json and play according sound on SC-Server
class EmojiSound:
    def __init__(self,
                 ip="127.0.0.1",
                 port=57120,
                 emoji_score_file="emoji_scores_new.json"):
        # self.analyzer = SentimentIntensityAnalyzer()
        self.sc_server_ip = ip
        self.sc_port = port
        self.osc = OSCClient(ip, port, encoding="utf-8")
        self.emoji_scores = json.load(open(emoji_score_file, "r"))

    # function to analyze text and get overall sentiment value (range -1 to 1)
    #def get_sentiment(self, text):
    #    scores = self.analyzer.polarity_scores(text)
    #    return scores["compound"]

#    # function to calc panning (random, if it's a retweet)
#    def get_panning(self, text):
#        if text[:2] == "RT":
#            return randrange(-100, 100, 1)/100  # Retweet: random panning
#        return 0

    # function to get random tweet from ItemIterator of Tweets
    def emoji_sentiment(self, emoji):
        if emoji in self.emoji_scores:
            return self.emoji_scores[emoji]["sentsc"]
        return 0

    @staticmethod
    def synth_freq(sentsc):
        return 300+(200*sentsc)

    # function to get random tweet from ItemIterator of Tweets
    def emoji_neg(self, emoji):
        if emoji in self.emoji_scores:
            return self.emoji_scores[emoji]["neg"]
        return 0

    # function to get random tweet from ItemIterator of Tweets
    def emoji_neut(self, emoji):
        if emoji in self.emoji_scores:
            return self.emoji_scores[emoji]["neut"]
        return 0

    # function to get random tweet from ItemIterator of Tweets
    def emoji_pos(self, emoji):
        if emoji in self.emoji_scores:
            return self.emoji_scores[emoji]["pos"]
        return 0

    def get_sentiment_stats(self, emoji):
        msg_dict = dict()
        msg_dict["emoji"] = emoji
        msg_dict["sentsc"] = float(self.emoji_sentiment(emoji)) # sentiment ranges from -1 to 1
        msg_dict["neg"] = float(self.emoji_neg(emoji)) # sentiment ranges from -1 to 1
        msg_dict["neut"] = float(self.emoji_neut(emoji))  # sentiment ranges from -1 to 1
        msg_dict["pos"] = float(self.emoji_pos(emoji))  # sentiment ranges from -1 to 1
        return msg_dict
    
    # OSC Message that is send to the server
    # contains: synth, frequency-range, tempo, panning
    # frequency range: 50-820
    def send_osc_msg(self, emoji, print_info=True):
        osc_dict = self.get_sentiment_stats(emoji)
        msg = list()
        msg.append(osc_dict["sentsc"])
        msg.append(osc_dict["neg"])
        msg.append(osc_dict["neut"])
        msg.append(osc_dict["pos"])
        self.osc.send_message(b'/emoji', msg)
        if print_info:
            self.print_info(osc_dict)

    # function to print info from tweet
    def print_info(self, osc_dict):
        print("Emoji: " + str(osc_dict["emoji"]))
        print("Negativ: " + str(osc_dict["neg"]))
        print("Neutral: " + str(osc_dict["neut"]))
        print("Positiv: " + str(osc_dict["pos"]))
        print("Sentiment: " + str(osc_dict["sentsc"]))


if __name__ == "__main__":
    EmSo = EmojiSound()

    emoji = input("Enter emoji: ")
    while emoji != "":
        EmSo.send_osc_msg(emoji)
        emoji = input("Enter emoji: ")
    # EmSo.send_osc_message("hey")

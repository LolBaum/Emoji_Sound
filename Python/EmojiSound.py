# Luzie Ahrens
# 22.09.2021

from oscpy.client import OSCClient
import json


##### Class to get Emoji-sentiment scores for a given emoji and send an OSC-Message.             #########
##### The emoji-sentiment scores are supplied by a json-file (emoji_scores_new.json).            #########

##### OSC-Message Format:                                                                       ##########
##### -keyword -overall_score -negative_score -neutral_score -positive_score -azimuth -elevation  ########

##### The ip has to be the one that SuperCollider is running on.                                 #########
##### The port has to be the one that SuperCollider is receiving OSC-Messages on (default 57120). ########
##### The emoji_score_file has to be supplied in the right format (see emoji_scores_new.json).   #########
class EmojiSound:
    def __init__(self,
                 ip="127.0.0.1",
                 port=57120,
                 emoji_score_file="emoji_scores_new.json"):
        self.sc_server_ip = ip
        self.sc_port = port
        self.osc = OSCClient(ip, port, encoding="utf-8")
        self.emoji_scores = json.load(open(emoji_score_file, "r"))

    # function to get sentiment from dict for a given emoji
    def emoji_sentiment(self, emoji):
        if emoji in self.emoji_scores:
            return self.emoji_scores[emoji]["sentsc"]
        return 0

    # function to get the "negative score" for a given emoji
    def emoji_neg(self, emoji):
        if emoji in self.emoji_scores:
            return self.emoji_scores[emoji]["neg"]
        return 0

    # function to get the "neutral score" for a given emoji
    def emoji_neut(self, emoji):
        if emoji in self.emoji_scores:
            return self.emoji_scores[emoji]["neut"]
        return 0

    # function to get the "positive score" for a given emoji
    def emoji_pos(self, emoji):
        if emoji in self.emoji_scores:
            return self.emoji_scores[emoji]["pos"]
        return 0


    # function to get all sentiment scores for an emoji and save them in a dict
    def get_sentiment_stats(self, emoji):
        msg_dict = dict()
        msg_dict["emoji"] = emoji
        msg_dict["sentsc"] = float(self.emoji_sentiment(emoji)) # sentiment ranges from -1 to 1
        msg_dict["neg"] = float(self.emoji_neg(emoji)) # sentiment ranges from -1 to 1
        msg_dict["neut"] = float(self.emoji_neut(emoji))  # sentiment ranges from -1 to 1
        msg_dict["pos"] = float(self.emoji_pos(emoji))  # sentiment ranges from -1 to 1
        return msg_dict
    
    # function to send OSC-Message in the following format:
    # -keyword -overall_score -negative_score -neutral_score -positive_score -azimuth -elevation

    def send_osc_msg(self, emoji, azim=0.4, elev=0.1, print_info=False):
        osc_dict = self.get_sentiment_stats(emoji)
        msg = list()
        msg.append(osc_dict["sentsc"])
        msg.append(osc_dict["neg"])
        msg.append(osc_dict["neut"])
        msg.append(osc_dict["pos"])
        msg.append(azim)
        msg.append(elev)
        self.osc.send_message(b'/emoji', msg)
        if print_info:
            self.print_info(osc_dict)

    # function to print sentiment-info from emoji
    def print_info(self, osc_dict):
        print("Emoji: " + str(osc_dict["emoji"]))
        print("Negativ: " + str(osc_dict["neg"]))
        print("Neutral: " + str(osc_dict["neut"]))
        print("Positiv: " + str(osc_dict["pos"]))
        print("Sentiment: " + str(osc_dict["sentsc"]))

# FOR TESTING
if __name__ == "__main__":
    # create object
    EmSo = EmojiSound()
    # receive emoji via terminal-input
    emoji = input("Enter emoji: ")
    while emoji != "":
        # send OSC-Message
        EmSo.send_osc_msg(emoji)
        emoji = input("Enter emoji: ")

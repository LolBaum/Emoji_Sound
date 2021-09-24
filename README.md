## Positive Pixel: The Sound of Emojis
20.09.2021

Laurin Dahm and Luzie Ahrens

This project was developed as part of the seminar "Network Systems for Music Interactions" instructed by Henrik von Coler at TU Berlin (2021). It is an approach to the sonification of a livechat consisting of emojis. The sound an emoji creates varies depending on the sentiment they carry. The sentiment scores for this project are taken from ["Sentiment of Emojis"](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0144296) (Novak et al. 2015).
 ________________________________________________________________________________________________

## Documentation

### General

<img src="other/program_exp.png" width="450"/>

In general, the participants connect to the server and can send emojis together with directive localisation info (azimuth, elevation). The python-server then grabs the sentiment information about the emojis and sends an osc-message. The SC-server receives the message and creates a binaural sound based on the information (making use of the [SC-HOA library](https://github.com/florian-grond/SC-HOA) by Florian Grond).

### SuperCollider

<img src="other/SC_struct.png" width="500"/>

SuperCollider receives OSC-Messages via an OSC-Listener. The OSC-Message is always in the following format:

```bash
-keyword -overall_sentiment_score -negative_sentiment_score -neutral_sentiment_score -positive_sentiment_score -azimuth -elevation
```

**Ranges**:<br>

-overall_sentiment_score: -1 to 1<br>
-negative_sentiment_score: 0-1<br>
-neutral_sentiment_score: 0-1<br>
-positive_sentiment_score: 0-1<br>
-azimuth: -pi/2 to pi/2<br>
-elevation: -pi/2 to pi/2<br>

The arguments from the OSC-message are given to one of four synth-definitions, which is chosen randomly each time. The synth-definitions do several things: 1. they create an amplitude-envelope for the sound according to the sentiment values. 2. they create a binaural encoder and "place" the sound according to the azimuth and elevation from the OSC-message. 

The signal is send to the ambisonics bus. The binaural decoder further processes the signal and makes it audible by sending it to the SC-output (default 0).

________________________________________________________________________________________________

## Installation
**PARTICIPANTS** must have the following installed:

**Python 3.6**

**Python-packages**: pyqt5, sockets

All python-packages can be install via pip.

```bash
pip install pyqt5
pip install sockets
```


________________________________________________________________________________________________
The **HOST** must have the following installed:

**SuperCollider 3.11**

**Python 3.6**

**Python-packages**: sockets, threading, oscpy, json

All python-packages can be install via pip.

```bash
pip install threading
pip install sockets
pip install oscpy
pip install json
```
________________________________________________________________________________________________
________________________________________________________________________________________________

## Usage

**PARTICIPANTS** as well as the **HOST** need to pull this git-repo.

```bash
git pull https://github.com/LolBaum/Emoji_Sound.git
```

### HOST: Starting the server
To start the server:
```bash
sclang sc_server.scd 
python3 server.py <SERVER IP-ADDRESS>
```


### PARTICIPANTS: Connecting to the server
To open the interface: 
```bash
python3 emoji_client_socket.py <SERVER IP-ADDRESS>
```


They can choose their username, dis-/reconnect to the server and change the server-IP and port.
Once they are connected, they are able to choose the emojis they want to send and also change the azimuth and elevation.




## Positive Pixel: The Sound of Emojis
20.09.2021

Laurin Dahm and Luzie Ahrens

This project was developed as part of the seminar "Network Systems for Music Interactions" instructed by Henrik von Coler at TU Berlin (2021). It is an approach to the sonification of a livechat consisting of emojis. The sound an emoji creates varies depending on the sentiment they carry. The sentiment scores for this project are taken from "Sentiment of Emojis" (Novak et al. 2015).
 ________________________________________________________________________________________________

## Basic Funcionality

<img src="other/program_exp.png" width="450"/>

In general, the participants connect to the server and can send emojis together with directive localisation info (azimuth, elevation). The python-server then grabs the sentiment information about the emojis and sends an osc-message. The SC-server receives the message and creates a binaural sound based on the information.
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
To start the server: TODO

### PARTICIPANTS: Connecting to the server
To open the interface: TODO

They can choose their username, dis-/reconnect to the server and change the server-IP and port.
Once they are connected, they are able to choose the emojis they want to send and also change the azimuth and elevation.




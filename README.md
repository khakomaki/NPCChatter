# NPCChatter

Bot for interacting with Twitch chat.

Focused on chat's [NPC](#npc)-behaviour (predictable & similar messages).

## Features

- React to chat being too NPC by mimicking its behaviour
    - adjustable for different chats
    - adjustable for avoiding bot from spamming
- Enable chat commands
    - type "!npc" in chat for the bot to respond with current NPC-meter-%
- Terminal interface
    - attributes are easily controllable even during execution time

## How to setup?

Short guide to get the NPCChatter up and running:

- Download NPCChatter

```bash
git clone https://github.com/khakomaki/NPCChatter.git .
```

- Check [dependencies](#dependencies) are satisfied
- Create .env file to root folder with following text:

```bash
OAUTH_TOKEN_TWITCH=your_bots_twitch_oauth_token
NICKNAME=your_bots_channel
CHAT=example_channel
CLIENT_ID=your_bots_client_id
```

(replace with your own values)

[Getting client_id & OAuth token](https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/)

- Done!

## Dependencies
<a name="dependencies"></a>

What you need to have installed to run NPCChatter:

- Python (recommended >=3.11)
- python specific requirements listed in [requirements.txt](requirements.txt)

Requirements can be installed running the following pip command in terminal:

```bash
pip install -r requirements.txt
```

## How to use?

- Open main.py or run following command in terminal:

```bash
python main.py
```

- type command, possible arguments and hit enter! (type HELP for list of commands)

Example usage:

```
Welcome to NPC-terminal. 'EXIT' to close, 'HELP' for list of commands.
> hs 5
History size set to [5]
> con
Authentication successful
Joined channel #npchatter
> msg hello chat!
> maxm 3
Maximum same message set to [3]
> thr 65
Threshold set to [65]
> info
==== Chatter settings info ======
Minimum same word count      - 5
Maximum bot same word count  - 3
Minimum bot message interval - 30
History size                 - 5
Threshold                    - 65
=================================
Sent message: 'D:'
Sent message: 'KEKW KEKW KEKW'
Sent message: 'Aware'
Sent message: 'OK'
Sent message: 'NO'
Sent message: 'BASED'
Sent message: 'NO'
Sent message: 'RIGGED'
> disc
Twitch closed connection
> exit
Connection already closed
```

## NPC
<a name="npc"></a>

Word "NPC" comes from video game culture and is short for "Non-Player Character", but can also refer to a person acting so predictably that the person could as well be a bot.

# NPCChatter

Locally runnable bot for interacting with Twitch chat.

Focused on chat messages' similarity or "NPCness" as some would say.

See "[NPC](#npc)".

## Abilities

- Call out chat for being too NPC by mimicking the its behaviour
    - adjustable for different chats
    - adjustable for avoiding bot from spamming
- Calculate chat's NPC-meter
    - type "!npc" in chat for the bot to respond with current %
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
```

(replace with your own values)

Twitch OAuth token: [Getting token](https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/)

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
==== Chatter settings info =====
Minimum same word count     - 5
Maximum bot same word count - 3
History size                - 5
Threshold                   - 65
================================
> disc
Twitch closed connection
> exit
Connection already closed
```

## NPC
<a name="npc"></a>

Word "NPC" means "Non-Player Character" and comes from video game culture, but can also refer to a person who acts very predictably, like this bot.

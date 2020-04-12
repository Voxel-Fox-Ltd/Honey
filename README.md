# Honey

Honey is a multiple use public Furry Discord bot. It's got a few features you may be interested in, so I'll try and list stuff for you here. Its prefix is `h.` by default, but you can update it with `h.prefix` (eg `h.prefix ;`). You can set up all relevant roles, channels, and settings with `h.setup`.

[Add Honey to your server now!](https://discordapp.com/oauth2/authorize?client_id=690477072270753792&scope=bot&permissions=268484614)

## Fursona Storage

Honey is able to store your fursonas! Just run `h.setsona` and the bot will DM you to talk you through setting one up. These can later be pulled up with `h.sona` for yourself, or `h.sona @User` to look at someone else's sona.

Server mods can set up an approval flow so sonas have to be verified before they can be pulled up by other users - all relevant settings are shown in `h.setup`. Mods can also set up certain roles on the server to have more allowed sonas - users are allowed one sona by default, but mods can raise this limit per role.

## Moderation Commands

All the classic moderation commands like kick, mute, ban, warn, and infractions are all present. Also present is the `h.watch @User` command for when mods need to keep a closer eye on any given user. Logs of what commands mods are running can all be sent to a modlogs channel, set with the `h.setup` command.

## Custom Roles

Many servers use a custom role system for their Patreon supporters, so Honey is looking to incorperate these things. Using the `h.customrole create` commands, users with the Patreon role can create a custom role, which they can later change the name/colour of using the `h.customrole colour #5dadec` or `h.customrole name Renamed Role` commands. Only users with a designated role (set in `h.setup`) can create/manage custom roles.

## Verification System

It's understood that some servers want a verification system in place for allowing new people into a server, which is why Honey has the `h.verify` command! Once you set up a verification role via `h.setup`, you can assign the verified role to a user with the `h.verify` command.

## Interaction Commands

The classic `h.hug @User` is back. Many commands including hug, pat, kiss, and nuzzle are all available within the bot. Interactions can be run once every 30 minutes, but server mods can set certain roles to have a lower cooldown, allowing systems like Patreon perks to be in place, ie lower cooldowns for higher tiers of support.

# Honey

Honey is a multiple use public Furry Discord bot. It's got a few features you may be interested in, so I'll try and list stuff for you here. Its prefix is `h.` by default, but you can update it with `h.prefix` (eg `h.prefix ;`). You can set up all relevant roles, channels, and settings with `h.setup`.

[Add Honey to your server now!](https://discordapp.com/oauth2/authorize?client_id=690477072270753792&scope=bot&permissions=268484614)

## Fursona Storage

Honey is able to store your fursonas! Just run `h.setsona` and the bot will DM you to talk you through setting one up. These can later be pulled up with `h.sona name` for yourself, or `h.sona @User name` to look at someone else's sona.

Server mods can set up an approval flow so sonas have to be verified before they can be pulled up by other users - all relevant settings are shown in `h.setup` (screenshot below). Mods can also set up certain roles on the server to have more allowed sonas - users are allowed one sona by default, but mods can raise this limit per role.

![](/marketing/sona_settings.png)

Already made a sona through the bot and you want to import that into a new server? You can run `h.importsona` and the bot'll talk you through copying a sona from one of your servers into another. Currently supported are all servers where you use Honey, as well as The Furry Kingdom and Winterhaven.

![](/marketing/kaiden_sona.png)

## Interaction Commands

The classic `h.hug @User` is back. Many commands including hug, pat, kiss, and nuzzle are all available within the bot. Interactions can be run once every 30 minutes by default, but server mods can set certain roles to have a lower cooldown, allowing systems like Patreon perks to be in place, ie lower cooldowns for higher tiers of support.

Interactions can also be shortened with the use of a cooldown token (see the relevant section).

![](/marketing/interaction_cooldown_settings.png)

### Adding Interactions

The default interactions that come with the bot are hug, pat, lick, kiss, bap, boop, hold, nuzzle, pounce, dance, poke, punch, slap, tug, and yeet, but if that's not enough for you, then you can add some with the `h.interaction add name response` command.

By using this you're able to add your own responses to existing interactions, as well as make your own entirely _new_ interactions to the bot!

![](/marketing/add_interaction.png)

### Interaction Stats

If you're the kind of person who likes numbers, then Honey can hook you up with that as well - all interactions are stored in the bot, and you can see how many times you've hugged or been kissed by someone right inside the bot itself - this is done with the `h.interactions` command.

![](/marketing/interaction_stats.png)

## Shop System

As is the norm with a lot of furry bots, Honey tries to make use of user activity by adding a shopping system into your server. Users gain money as they talk, and they can spend that money in your server's item shop (created with `h.createshopchannel`). Included with the shop system are commands like `h.givecoins @User amount`, for if a user wants to pass their coins along to someone else.

![](/marketing/coin_shop.png)

### Paint

Users are able to purchase and use _paint_. Paint allows users to change the colour of another user (or themselves) for an hour.

Honey uses the custom role creation position (defined in the "custom role" section of the setup) to create a new paint role for the user, pulling from a list of 140+ distinct roles (using the CSS named colours plus a couple more). If a user is painted while they're already painted, then the role assinged to them will simply be edited. Once the paint's one-hour duration is up, the role will be deleted from your server.

![](/marketing/paint_used.png)

### Cooldown Tokens

Users can purchase 100 coooldown tokens from the shop, each token being able to remove one second from their remaining interaction cooldown. This means that users don't need to worry about "wasting" a cooldown token if their cooldown is too low and they want to use another interaction - they'll only use as many tokens as they need.

### Buyable Roles

If you wanted your economy to keep going on through Honey, then you can also add buyable roles to your shop page - with this users are able to purchase a role using their Honey money.

## Giveaways

Honey is able to handle giveaways, letting users add an interaction to a message and roll for a chance to win an item.

![](/marketing/giveaway.png)

## Moderation Commands

All the classic moderation commands like kick, mute, tempmute, ban, warn, and infractions are all present. Also present is the `h.watch @User` command for when mods need to keep a closer eye on any given user. Logs of what commands mods are running can all be sent to a modlogs channel, set with the `h.setup` command.

## Message Logging

Like a few other bots, Honey is able to track messages that have been _edited_ and _deleted_, and log those into a channel.

## Custom Roles

Many servers use a custom role system for their Patreon supporters, so Honey is looking to incorperate these things. Using the `h.customrole create` commands, users with the Patreon role (or similar) can create a custom role.

Custom roles can be managed by the users who have them; the commands `h.customrole colour #5dadec` and `h.customrole name Renamed Role` can be used to recolour and rename the custom role.

Only users with a designated master role (set in `h.setup`) can create/manage custom roles, though a mod can _set_ a custom role for a user with the `h.customrole set @User role` if your server doesn't want to create a master role.

![](/marketing/custom_role.png)

## Verification System

It's understood that some servers want a verification system in place for allowing new people into a server, which is why Honey has the `h.verify` command! Once you set up a verification role via `h.setup`, you can assign the verified role to a user with the `h.verify` command.

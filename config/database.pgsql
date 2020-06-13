CREATE TABLE guild_settings(
    guild_id BIGINT PRIMARY KEY,
    prefix VARCHAR(30),

    fursona_modmail_channel_id BIGINT,  -- The ID of the channel sonas are sent to be approved
    fursona_decline_archive_channel_id BIGINT,  -- The archive for declined sonas
    fursona_accept_archive_channel_id BIGINT,  -- The archive for accepted sfw sonas
    fursona_accept_nsfw_archive_channel_id BIGINT,  -- The archive for accepted nsfw sonas

    verified_role_id BIGINT,  -- The role verified members get
    muted_role_id BIGINT, -- The role muted members get
    guild_moderator_role_id BIGINT, -- The guild moderator role
    nsfw_is_allowed BOOLEAN DEFAULT TRUE, -- If NSFW guilds are allowed

    custom_role_xfix VARCHAR(33),  -- The emoji used when users run the coins command
    custom_role_id BIGINT,  -- The role required for users to be able to manage their own roles
    custom_role_position_id BIGINT,  -- The role that newly created custom roles are set below

    coin_emoji VARCHAR(100),  -- The emoji used when users run the coins command

    kick_modlog_channel_id BIGINT,  -- The channel ID for mod actions to be posted to
    ban_modlog_channel_id BIGINT,
    mute_modlog_channel_id BIGINT,
    warn_modlog_channel_id BIGINT,

    edited_message_modlog_channel_id BIGINT,
    deleted_message_modlog_channel_id BIGINT,
    voice_update_modlog_channel_id BIGINT,

    suggestion_channel_id BIGINT
);


CREATE TABLE guild_shop_settings(
    guild_id BIGINT PRIMARY KEY,
    paintbrush_price INTEGER DEFAULT 100,
    cooldown_token_price INTEGER DEFAULT 100
);


CREATE TABLE fursonas(
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    name VARCHAR(200) NOT NULL,
    gender VARCHAR(200) NOT NULL,
    age VARCHAR(200) NOT NULL,
    species VARCHAR(200) NOT NULL,
    orientation VARCHAR(200) NOT NULL,
    height VARCHAR(200) NOT NULL,
    weight VARCHAR(200) NOT NULL,
    bio VARCHAR(1000) NOT NULL,
    image VARCHAR(200),
    nsfw BOOLEAN DEFAULT FALSE,
    verified BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (guild_id, user_id, name)
);


CREATE TYPE moderation_action AS ENUM ('Mute', 'Warn', 'Kick', 'Ban', 'Unmute', 'Verify', 'Tempmute');


CREATE TABLE infractions(
    infraction_id VARCHAR(10) PRIMARY KEY,
    guild_id BIGINT,
    moderator_id BIGINT,
    user_id BIGINT,
    infraction_type moderation_action,
    infraction_reason VARCHAR(60),
    timestamp TIMESTAMP,
    deleted_by BIGINT
);


CREATE TABLE temporary_roles(
    guild_id BIGINT,
    role_id BIGINT,
    user_id BIGINT,
    remove_timestamp TIMESTAMP,
    delete_role BOOLEAN NOT NULL DEFAULT FALSE,
    dm_user BOOLEAN NOT NULL DEFAULT TRUE,
    key VARCHAR(50),
    PRIMARY KEY (guild_id, role_id, user_id)
);


CREATE TABLE temporary_removed_roles(
    guild_id BIGINT,
    role_id BIGINT,
    user_id BIGINT,
    readd_timestamp TIMESTAMP,
    dm_user BOOLEAN NOT NULL DEFAULT TRUE,
    key VARCHAR(50),
    PRIMARY KEY (guild_id, role_id, user_id)
);


CREATE TABLE custom_roles(
    guild_id BIGINT,
    role_id BIGINT,
    user_id BIGINT,
    PRIMARY KEY (guild_id, user_id)
);


CREATE TABLE user_settings(
    user_id BIGINT PRIMARY KEY,
    dm_on_paint_remove BOOLEAN DEFAULT TRUE,
    allow_paint BOOLEAN DEFAULT TRUE
);


CREATE TABLE role_list(
    guild_id BIGINT,
    role_id BIGINT,
    key VARCHAR(50),
    value VARCHAR(50),
    PRIMARY KEY (guild_id, role_id, key)
);


CREATE TABLE channel_list(
    guild_id BIGINT,
    channel_id BIGINT,
    key VARCHAR(50),
    value VARCHAR(50),
    PRIMARY KEY (guild_id, channel_id, key)
);


CREATE TABLE user_money(
    guild_id BIGINT,
    user_id BIGINT,
    amount INTEGER,
    PRIMARY KEY (guild_id, user_id)
);


CREATE TABLE user_inventory(
    guild_id BIGINT,
    user_id BIGINT,
    item_name VARCHAR(100),
    amount INTEGER,
    PRIMARY KEY (guild_id, user_id, item_name)
);


CREATE TABLE shopping_channels(
    guild_id BIGINT PRIMARY KEY,
    channel_id BIGINT,
    message_id BIGINT
);


CREATE TABLE giveaways(
    channel_id BIGINT,
    message_id BIGINT PRIMARY KEY,
    winner_count INTEGER,
    ending_time TIMESTAMP,
    description VARCHAR(2000)
);


CREATE TABLE interaction_counter(
    guild_id BIGINT,
    user_id BIGINT,
    target_id BIGINT,
    interaction VARCHAR(50),
    amount INTEGER,
    PRIMARY KEY (guild_id, user_id, target_id, interaction)
);


CREATE TABLE interaction_text(
    guild_id BIGINT,
    interaction_name VARCHAR(50),
    response VARCHAR(2000)
);

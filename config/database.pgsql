CREATE TABLE guild_settings(
    guild_id BIGINT PRIMARY KEY,
    prefix VARCHAR(30),
    verified_role_id BIGINT,  -- The role verified members get
    fursona_modmail_channel_id BIGINT,  -- The ID of the channel sonas are sent to be approved
    fursona_decline_archive_channel_id BIGINT,  -- The archive for declined sonas
    fursona_accept_archive_channel_id BIGINT,  -- The archive for accepted sfw sonas
    fursona_accept_nsfw_archive_channel_id BIGINT,  -- The archive for accepted nsfw sonas
    modmail_channel_id BIGINT,  -- The channel ID for mod actions to be posted to
    muted_role_id BIGINT, -- The role muted members get
    guild_moderator_role_id BIGINT, -- The guild moderator role
    custom_role_id BIGINT,  -- The role required for users to be able to manage their own roles
    custom_role_position_id BIGINT  -- The role that newly created custom roles are set below
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


CREATE TYPE type AS ENUM ('Mute', 'Warn', 'Kick', 'Ban', 'Unmute', 'Verify', 'Tempmute');


CREATE TABLE infractions(
    infraction_id VARCHAR(10) PRIMARY KEY,
    guild_id BIGINT,
    moderator_id BIGINT,
    user_id BIGINT,
    infraction_type type,
    infraction_reason VARCHAR(60),
    timestamp timestamp
);


CREATE TABLE temporary_roles(
    guild_id BIGINT,
    role_id BIGINT,
    user_id BIGINT,
    remove_timestamp timestamp,
    PRIMARY KEY (guild_id, role_id, user_id)
);


CREATE TABLE custom_roles(
    guild_id BIGINT,
    role_id BIGINT,
    user_id BIGINT,
    PRIMARY KEY (guild_id, user_id)
);


CREATE TABLE role_list(
    guild_id BIGINT,
    role_id BIGINT,
    key VARCHAR(50),
    value VARCHAR(50),
    PRIMARY KEY (guild_id, role_id, key)
);

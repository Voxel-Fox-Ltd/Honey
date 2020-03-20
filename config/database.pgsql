CREATE TABLE guild_settings(
    guild_id BIGINT PRIMARY KEY,
    prefix VARCHAR(30),
    verified_role_id BIGINT,  -- The role verified members get
    fursona_modmail_channel_id BIGINT,  -- The ID of the channel sonas are sent to be approved
    fursona_decline_archive_channel_id BIGINT,  -- The archive for declined sonas
    fursona_accept_archive_channel_id BIGINT,  -- The archive for accepted sfw sonas
    fursona_accept_nsfw_archive_channel_id BIGINT,  -- The archive for accepted nsfw sonas
    muted_role_id BIGINT -- The role muted members get
);


CREATE TABLE fursonas(
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    index BIGINT NOT NULL DEFAULT 0,
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
    PRIMARY KEY (guild_id, user_id, index)
);


CREATE TYPE type AS ENUM ('mute', 'warn', 'kick', 'ban')


CREATE TABLE infractions(
    guild_id BIGINT
    moderator_id BIGINT
    user_id BIGINT
    infraction_id VARCHAR(10) PRIMARY KEY
    infraction_type type
    infraction_reason VARCHAR(60)
    timestamp timestamp
)

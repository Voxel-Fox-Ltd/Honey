CREATE TABLE guild_settings(
    guild_id BIGINT PRIMARY KEY,
    prefix VARCHAR(30)
);

CREATE TYPE type AS ENUM ('warn', 'kick', 'ban')

CREATE TABLE infractions(
    guild_id BIGINT
    moderator_id BIGINT
    user_id BIGINT
    infraction_id VARCHAR(10) PRIMARY KEY
    infraction_type type
    infraction_reason VARCHAR(60)
    timestamp timestamp
)
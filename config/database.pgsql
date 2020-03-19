CREATE TABLE guild_settings(
    guild_id BIGINT PRIMARY KEY,
    verified_role_id BIGINT,
    prefix VARCHAR(30)
);

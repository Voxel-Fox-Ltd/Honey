import typing

import discord


async def move_role_position_below(role:discord.Role, below:discord.Role, reason:typing.Optional[str]) -> None:
    """|coro|

    Moves the current role beneath the given role, cascading down and fixing the order of all lower roles
    """

    if below.is_default() or role.is_default():
        raise discord.errors.InvalidArgument("Cannot move default role")

    if below == role:
        return  # Save discord the extra request.

    http = role._state.http

    # Fetch the roles from the API, ordered by the order of the cache
    all_guild_roles = sorted(await role.guild.fetch_roles())

    # Get the order of the roles we want to append
    roles = []
    encounters = 0
    for r in all_guild_roles[1:]:
        if r.id == role.id:
            encounters += 1
            continue
        if r.id == below.id:
            encounters += 1
            roles.append(role)
            roles.append(r)
        else:
            roles.append(r)
        if encounters == 2:
            break

    # Make and send the payload
    payload = [{"id": z.id, "position": index} for index, z in enumerate(roles, start=1)]
    await http.move_role_position(role.guild.id, payload, reason=reason)

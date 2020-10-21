import voxelbotutils as utils


class Fursona(object):
    """A class representing a fursona object"""

    def __init__(self, guild_id:int, user_id:int, name:str, gender:str, age:str, species:str,
                 orientation:str, height:str, weight:str, bio:str, image:str, nsfw:bool=False,
                 verified:bool=False, **kwargs
                 ):
        self.guild_id = guild_id
        self.user_id = user_id
        self.name = name
        self.gender = gender
        self.age = age
        self.species = species
        self.orientation = orientation
        self.height = height
        self.weight = weight
        self.bio = bio
        self.image = image
        self.nsfw = nsfw
        self.verified = verified

    def get_embed(self, *, mention_user:bool=False, add_image:bool=True) -> utils.Embed:
        """Gets an embed for the fursona object"""

        with utils.Embed() as embed:
            if mention_user:
                embed.add_field("Discord", f"<@{self.user_id}>")
            # embed.add_field("Name", self.name)
            embed.title = self.name
            embed.add_field("Gender", self.gender)
            embed.add_field("Age", self.age)
            embed.add_field("Species", self.species)
            embed.add_field("Orientation", self.orientation)
            embed.add_field("Height", self.height)
            embed.add_field("Weight", self.weight)
            embed.add_field("Bio", self.bio, inline=False)
            if self.image and add_image:
                embed.set_image(url=self.image)
            embed.set_footer(f"Fursona of {self.user_id} | {'NSFW' if self.nsfw else 'SFW'}")
        return embed

    async def save(self, db):
        """Saves the local fursona object into the database"""

        await db(
            """INSERT INTO fursonas (guild_id, user_id, name, gender, age,
            species, orientation, height, weight, bio, image, nsfw, verified)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13) ON CONFLICT
            (guild_id, user_id, name) DO UPDATE SET gender=excluded.gender, age=excluded.age,
            species=excluded.age, orientation=excluded.orientation, height=excluded.height, weight=excluded.weight,
            bio=excluded.bio, image=excluded.image, nsfw=excluded.nsfw, verified=excluded.verified""",
            self.guild_id, self.user_id, self.name, self.gender, self.age, self.species,
            self.orientation, self.height, self.weight, self.bio, self.image, self.nsfw, self.verified,
        )

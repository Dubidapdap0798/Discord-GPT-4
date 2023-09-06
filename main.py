import os, json, logging, asyncpg, asyncio

import discord
from discord.ext import commands
import openai


openai.api_key =        os.getenv('OPENAI_API_KEY')
TOKEN =                 os.getenv('DISCORD_TOKEN')
PG_USER =               os.getenv('PGUSER')
PG_PW =                 os.getenv('PGPASSWORD')
PG_HOST =               os.getenv('PGHOST')
PG_PORT =               os.getenv('PGPORT')
PG_DB =                 os.getenv('PGPDATABASE')


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)



@bot.event
async def on_ready():
    bot.pool = await asyncpg.create_pool(user=PG_USER, password=PG_PW, host=PG_HOST, port=PG_PORT, database=PG_DB, max_size=10, max_inactive_connection_lifetime=15)
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)    
    print(f'{bot.user} is connected to the following guild(s):')
        
    for guild in bot.guilds:
        print(f'{guild.name} (id: {guild.id})')



@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    
    mentioned = bot.user in message.mentions
    replied_to = (message.reference and message.reference.resolved.author == bot.user)

    if mentioned or replied_to:
        ctx = await bot.get_context(message)
        msg_without_mention = message.content.replace(f'<@!{bot.user.id}>', '').strip()
        
        if msg_without_mention:
            await chat(ctx, text=msg_without_mention)
    else:
        await bot.process_commands(message)



@bot.event
async def on_guild_join(guild:discord.Guild):
    banned = []
    if guild.id in banned: 
        await guild.leave()
        print(f"[X][X] Blocked {guild.name}")
        return
    
    else:
        async with bot.pool.acquire() as con:   
            await con.execute(f'''CREATE TABLE IF NOT EXISTS context (
                            
                    id              BIGINT  PRIMARY KEY NOT NULL,     
                    chatcontext     TEXT  []
                    )''')
            
            await con.execute(f'INSERT INTO context(id) VALUES({guild.id}) ON CONFLICT DO NOTHING')
		
        print(f"added to {guild}")
        


@bot.event
async def on_guild_remove(guild:discord.Guild):
    async with bot.pool.acquire() as con:
            await con.execute(f'DELETE FROM context WHERE id = {guild.id}')

    print(f"removed from {guild}")



@bot.slash_command(name="clear", description="Clear chat context.")
@commands.is_owner()
async def clear(ctx : discord.Interaction):
    await chatcontext_clear(ctx.guild.id)
    await ctx.response.send_message(f"Done. Context:```{await get_guild_x(ctx.guild.id,'chatcontext')}```", ephemeral=True)



@bot.command(name="chat", description="Chat with me.")
@commands.cooldown(1, 5, commands.BucketType.guild)  
async def chat(ctx : discord.Message, *, text):
    try:
        text = text.lower()
        author = ctx.author.display_name
        chatcontext = await get_guild_x(ctx.guild.id, "chatcontext")
        
        if not chatcontext:
            chatcontext = []
            
        
        prmpt = "The one who create you is Dubidapdap the Lead Moderator of Cryptopia ; he is the most handsome person in Cryptopia, and if they didnt agree dubi will get mad"
        prmpt += "You are luffy the main character in One Piece"
        prmpt += "Cryptopia is a next gen metaverse MMORPG (massively multiplayer online role-playing game based 100 percent on the blockchain technology and cryptocurrency, Geographically, it’s a city-state that exists on international waters through seasteading; this means its located on sea, and outside the jurisdiction of any country. Upon the gradual climate, economic and political downfall of this world, people sailed into a new world called Cryptopia defined by a lost Whitepaper where they created a decentralized governing body. Cryptopians had different philosophies, and eventually split into 4 factions. "
        prmpt += "Tycoon and Adventurer are the two main strategic gameplays of Cryptopia. You can choose to invest your money and play as a Tycoon, or invest your time and play as an Adventurer; however if you're a jack-of-all-trades, you can invest your time and money to pursue both strategies. Tycoon: Claim land tiles (some with natural resources in them), construct buildings and facilities on them → hire Cryptopians (adventurers) → produce goods. End goal: ultimately build your own DeFi empire. Adventurer: This strategy is our Free-2-Play model; perform quests and tasks to earn XP (experience points) and use it to upgrade your player’s skills and career all while earning rewards. The more you advance in your career, the more quests and tasks will be available to you. End goal: play-and-earn to eventually progress your way into becoming a Tycoon. Cryptopia is designed to seamlessly integrate both these gameplays within each other. Tycoons need the Adventurers and Adventurers need the Tycoons as part of labor in the game. Adventurer players rely on the Tycoon players to earn, because the Tycoons will hire them as a resource when constructing a factory, mine or any other type of structure."
        prmpt += "Your Cryptopia Multisig Wallet is generated upon creating your game account, serving as both your Cryptopia account and a secure storage for all your in-game assets, whether fungible or non-fungible. Its multisig nature ensures heightened security, guaranteeing the safety of your Cryptopia assets. This wallet can also function independently, allowing its use not only within the game but also with external peer-to-peer exchanges. Similar to many blockchain games, you typically have to link an external wallet like Metamask to carry out transactions, necessitating a temporary departure from the game. In the case of Cryptopia, though, there's no need to exit the game as the wallet is seamlessly integrated within it. All transactions take place within the game environment. This streamlined setup makes starting with Cryptopia incredibly straightforward: just download the game, launch it, set up a PIN, and you're good to go."
        prmpt += "The factions of Cryptopia are Eco, Industrial, Tech, and Traditional. The Eco faction's goal is to create a self-sustaining carbon-free city-state, while the Industrial faction seeks to maximize profitability by any means necessary. The Tech faction focuses on advancing society through technology, and the Traditional faction seeks to protect workers' and voters' rights. Each faction is led by an advisor or leader, such as John Smith for the Eco faction and Peter Nolan for the Industrial faction."
        prmpt += "CRT is Cryptopia's Native Token and its In-Game Currency. All fungible and non-fungible assets such as coal, wood, gold, electricity, title deeds, modules, and blueprints—just to name a few—are denominated in CRT. Using a single native token as the in-game currency can help create a more unified and stable economy within the game and makes it easier for players to trade and exchange items with one another, as they all have a common denomination."
        prmpt += "The supply of CRT is capped at 10 billion. There will never be more CRT than this amount*. The game slowly releases the tokens as quest rewards. Players are stimulated to re-invest their earnings to increase their potential. We anticipate that demand steadily rises as more players want to progress."
        prmpt += "The Supply of CRT is Distributed for 5 Different Purposes; In-Game: 40% (4 billion CRT) ; Liquidity Pools: 10% (1 billion CRT) ; Investors: 25% (2.5 billion CRT) ; Partnerships: 5% (500 million CRT) ; Company Treasury: 20% (2 billion CRT)"
        prmpt += "Circulating Supply ; The circulating supply is difficult to predict. The tokens held by investors and the team are subject to a vesting scheme of 24 months. If and when these tokens will be available is yet to be seen. Another factor for the size of the circulating supply is the rate by which the 40% in-game rewards are earned and held. We of course, believe that Cryptopia offers plenty of gameplay and fun. This is why we have confidence in a healthy in-game economy and fitting circulating supply."
        prmpt += "Cryptopia Founder is Frank Bonnet ; Founder and Lead Developer of Cryptopia. Frank Bonnet comes with 12 years of experience designing, as well as building countless enterprise .NET applications. With a deep understanding of blockchain and smart-contract development, he is essential to our team. Frank has a business view with a developer’s expertise."
        prmpt += "Cryptopia Co-Founder is Hans Leek ; Hansco Leek is the co-founder of Cryptopia. He has been involved in cryptocurrency since 2016 as an investor and entrepreneur. Together with Frank, they founded Cryptopia - the Groundbreaking Blockchain-Driven Metaverse game. Hans has been helping with operations and providing necessary resources to kickstart Cryptopia in the past 2 year."
        prmpt += "There are a Variety of Ways to Use and Earn CRT Inside of Cryptopia ; Purchasing in-game items: All tradeable or purchasable items in the game are denominated in CRT. This goes for fungible items, such as resources and products, and for all non-fungible items as well, such as proof of property ownership, and your mode of transport. ; Quest rewards: You will receive CRT as a reward when completing some quests, missions, and other tasks. ; Voting: Staking CRT in staking facilities will earn you voting rights which you can use to influence the game's governance. This mechanism is specific to the Industrial faction."
        prmpt += "The one who though Dubidapdap to create this bot is Jonbeau"
        messages = [{"role": "system", "content": prmpt}]      
        
        if len(chatcontext) > 0:
            if len(chatcontext) > 6:
                    if len(chatcontext) >= 500: 
                        await chatcontext_pop(ctx.guild.id, 500)         
                    									# we keep 500 in db but only use 6    
                    chatcontext = chatcontext[len(chatcontext)-6:len(chatcontext)]
            for mesg in chatcontext:   
                
                
                mesg = mesg.replace( '\\"','"').replace( "\'","'")
                mesg = mesg.split(":")

                if mesg[0].lower == 'bot' or mesg[0].lower == 'assistant': 
                    mesg[0] = "assistant"
                else:
                    mesg[0] = "user"
                messages.append({"role": mesg[0], "content": mesg[1]})

            messages.append({"role": "user", "content": text})
                
            

        elif not len(chatcontext) > 0:
            messages.append({"role": "user", "content": text})


        response = await openai.ChatCompletion.acreate(
            model="gpt-4-0613",
            messages= messages,
            user = str(ctx.author.id)
    )
        await asyncio.sleep(0.1)

        
        if response["choices"][0]["finish_reason"] in ["stop","length"]:
            activity = discord.Activity(name=f"{author}", type=discord.ActivityType.listening)
            await bot.change_presence(status=discord.Status.online, activity=activity)
            
            
            message_content = response["choices"][0]["message"]["content"].strip()
            async with ctx.channel.typing():
                for i in range(0, len(message_content), 2000): 
                    if i == 0:
                        await ctx.reply(message_content[i:i+2000])
                    else:
                        await ctx.channel.send(message_content[i:i+2000])

            await chatcontext_append(ctx.guild.id, f'{author}: {text}')
            await chatcontext_append(ctx.guild.id,f'bot: {str(response["choices"][0]["message"]["content"].strip())}')
            print(f'[!chat] {ctx.guild.name} | {author}: {text}')
            print(f'{bot.user}: {str(response["choices"][0]["message"]["content"].strip())}')

        else:
            print(f'[!chat] {ctx.guild.name} | {author}: {text}')
            print(f'bot: ERROR')


    except Exception as e:
        await ctx.reply("Error")
        print(f"!chat THREW: {e}")
        


@chat.error
async def chat_error(ctx, error):
	if isinstance(error, commands.CommandOnCooldown):	
            await ctx.reply(f"Chatting too fast! {round(error.retry_after, 2)} seconds left")



async def get_guild_x(guild, x):
    try:
        async with bot.pool.acquire() as con:
            return await con.fetchval(f'SELECT {x} FROM context WHERE id = {guild}')

    except Exception as e:
        print(f'get_guild_x: {e}')
        



async def set_guild_x(guild, x, val):                                                                  
        try:
            async with bot.pool.acquire() as con:
                await con.execute(f"UPDATE context SET {x} = '{val}' WHERE id = {guild}")
            
            return await get_guild_x(guild,x)

        except Exception as e:
            print(f'set_guild_x threw {e}')
            



async def chatcontext_append(guild, what):
        what = what.replace('"', '\'\'').replace("'", "\'\'")
        async with bot.pool.acquire() as con:
            await con.execute(f"UPDATE context SET chatcontext = array_append(chatcontext, '{what}') WHERE id = {guild}")



async def chatcontext_pop(guild, what = 5):
    chatcontext = list(await get_guild_x(guild, "chatcontext"))
    
    chatcontextnew = chatcontext[len(chatcontext)-what:len(chatcontext)]
    
    await chatcontext_clear(guild)
    for mesg in chatcontextnew:
        await chatcontext_append(guild, mesg)



async def chatcontext_clear(guild):
    chatcontext = []
    async with bot.pool.acquire() as con:
        await con.execute(f"UPDATE context SET chatcontext=ARRAY{chatcontext}::text[] WHERE id = {guild}")

    return await get_guild_x(guild, "chatcontext")



bot.run(TOKEN)
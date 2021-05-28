import discord
import random
from discord.ext import commands, tasks
from itertools import cycle
import asyncio

client = commands.Bot(command_prefix='.')
status = cycle(['here you can put some status for your bot to "play"'])
filtered_words = ["this is a filter, everything you write in here the bot deletes instantly"]

class DurationConverter(commands.Converter):
    async def convert(self, ctx, argument):
        amount = argument[:-1]
        unit = argument[-1]

        if amount.isdigit() and unit in ['s', 'm']:
            return (int(amount), unit)

        raise commands.BadArgument(message='Not a valid duration')

@client.command()
async def ip(ctx):
    await ctx.send("if you own a minecraft server or other kind of servers you can put a ip address or just delete this command")

    
@client.command()
async def credit(ctx):
    await ctx.send("This bot was created by m4zyz on github. https://github.com/m4zyz")



@client.command()
@commands.has_permissions(manage_messages=True)
async def tempban(ctx, member: commands.MemberConverter, duration: DurationConverter):

    multiplier = {'s': 1, 'm': 60}
    amount, unit = duration

    await ctx.guild.ban(member)
    await ctx.send(f'{member} has been banned for {amount}{unit}.')
    await asyncio.sleep(amount * multiplier[unit])
    await ctx.guild.unban(member)

@client.command()
@commands.has_permissions(manage_messages=True)
async def tempmute(ctx, member: discord.Member, time: int, d, *, reason=None):
    guild = ctx.guild

    for role in guild.roles:
        if role.name == "Muted":
            await member.add_roles(role)

            embed = discord.Embed(title="muted!", description=f"{member.mention} has been tempmuted ", colour=discord.Colour.light_gray())
            embed.add_field(name="reason:", value=reason, inline=False)
            embed.add_field(name="time left for the mute:", value=f"{time}{d}", inline=False)
            await ctx.send(embed=embed)

            if d == "s":
                await asyncio.sleep(time)

            if d == "m":
                await asyncio.sleep(time*60)

            if d == "h":
                await asyncio.sleep(time*60*60)

            if d == "d":
                await asyncio.sleep(time*60*60*24)

            await member.remove_roles(role)

            embed = discord.Embed(title="unmute (temp) ", description=f"unmuted -{member.mention} ", colour=discord.Colour.light_gray())
            await ctx.send(embed=embed)

            return

@client.event
async def on_message(msg):
    for word in filtered_words:
        if word in msg.content:
            await msg.delete()

    await client.process_commands(msg)

@client.command()
@commands.has_permissions(manage_messages=True)
async def poll(ctx, *, message):
    emb=discord.Embed(title="Afstemning", description=f"{message}")
    msg=await ctx.channel.send(embed=emb)
    await msg.add_reaction('👍')
    await msg.add_reaction('👎')

@client.command()
async def server(ctx):
    name = str(ctx.guild.name)
    description = str(ctx.guild.description)

    owner = str(ctx.guild.owner)
    id = str(ctx.guild.id)
    region = str(ctx.guild.region)
    memberCount = str(ctx.guild.member_count)

    icon = str(ctx.guild.icon_url)

    embed = discord.Embed(
        title=name + " Server Information",
        description=description,
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=icon)
    embed.add_field(name="Owner", value=owner, inline=True)
    embed.add_field(name="Server ID", value=id, inline=True)
    embed.add_field(name="Region", value=region, inline=True)
    embed.add_field(name="Member Count", value=memberCount, inline=True)

    await ctx.send(embed=embed)

@client.command()
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=True)
    await  member.add_roles(mutedRole, reason=reason)
    await ctx.send(f"Muted {member.mention} for reason {reason}")
    await member.send(f"You were muted in the server {guild.name} for {reason}")

@client.command()
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member : discord.Member):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")


    await member.remove_roles(mutedRole)
    await ctx.send(f"Unmuted {member.mention}")
    await member.send(f"You were unmuted in the server {guild.name}")

@client.command()
@commands.has_permissions(manage_messages=True)
async def lockdown(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send( ctx.channel.mention + " is now in lockdown.")


@client.command()
@commands.has_permissions(manage_messages=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send( ctx.channel.mention + " has been unlocked.")

@client.command()
@commands.has_permissions(manage_messages=True)
async def slowmode(ctx, seconds : int):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"Set the slowmode delay in this channel to {seconds} seconds.")


@client.event
async def on_ready():
    change_status.start()
    print('Bot is ready.')

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please pass in all required arguments.')

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Invalid command.')


@client.event
async def on_member_join(member):
    print(f'{member} has joined the server.')

@client.event
async def on_member_remove(member):
    print(f'{member} has left the server.')

@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

@client.command(aliases=['8ball'])
async def _8ball(ctx, *, question):
    responses = ['My reply is no.',
                 'Yes.',
                 'Cannot predict now',
                 'Yes definitely.',
                 'Don't count on it.',
                 'It is Certain.']
    await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount : int):
    await ctx.channel.purge(limit=amount)

@client.command()
@commands.has_permissions(manage_messages=True)
async def kick(ctx, member : discord.Member, *, reason=None):
    await member.kick(reason=reason)

@client.command()
@commands.has_permissions(manage_messages=True)
async def ban(ctx, member : discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'Banned {member.mention}')

@client.command()
@commands.has_permissions(manage_messages=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return

@tasks.loop(seconds=10)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))


@client.command()
async def bot(ctx):
    await ctx.send(f'write information about your bot here')































client.run('put your token here')

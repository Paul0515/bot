

import discord
from discord.ext import commands, tasks
import json
import asyncio
import math
import requests
import schedule
from discord_components import Button, Select, SelectOption, ComponentsBot, ButtonStyle
import re
import datetime
import random
from mojang import MojangAPI 

intents = discord.Intents.default()
intents.members = True

bot = ComponentsBot(command_prefix='#',intents = intents)
bot.remove_command("help")

with open("config.json", "r", encoding='utf8') as f:
    config = json.load(f)


@bot.event
async def on_ready():
    print("Login...")
    print(f"Bot Name: {bot.user.name}")

@bot.command()
async def help(ctx):
    with open("help.txt", "r", encoding='utf8') as f:
        word = f.read()
    embed=discord.Embed(title="Help幫助", description=word, color=0xff2600)
    await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def giveaway(ctx):
    giveaway_questions = [f'請tag要抽獎的頻道[ 範例:{ctx.channel.mention} ]', '請輸入你要抽的獎品', '多久後公佈抽獎結果(分)',]
    giveaway_answers = []
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    for question in giveaway_questions:
        await ctx.send(question)
        try:
            message = await bot.wait_for('message', timeout= 30.0, check= check)
        except asyncio.TimeoutError:
            await ctx.send('你沒有在時間內回答')
            return
        else:
            giveaway_answers.append(message.content)
    try:
        c_id = int(giveaway_answers[0][2:-1])
    except:
        await ctx.send(f'輸入錯誤[ 範例:{ctx.channel.mention} ]')
        return
    channel = bot.get_channel(c_id)
    prize = str(giveaway_answers[1])
    time = int(giveaway_answers[2]) * 60
    end = datetime.datetime.utcnow() + datetime.timedelta(seconds = time)
    give = discord.Embed(timestamp=end, color = 0x2ecc71)
    give.set_author(name = f'抽獎!', icon_url = 'https://i.imgur.com/VaX0pfM.png')
    give.add_field(name= f'{ctx.author.name} 將抽出: {prize}!', value = f'下面有四個選項，其中一個代表抽獎，另一個代表放棄抽獎', inline = False)
    give.set_footer(text = f'開獎時間')
    my_message = await channel.send(embed = give)
    await my_message.add_reaction("1️⃣")
    await my_message.add_reaction("2️⃣")
    await my_message.add_reaction("3️⃣")
    await my_message.add_reaction("4️⃣")
    emoji = [0, 1, 2, 3]
    giveaway_emoji = random.choice(emoji)
    emoji.remove(giveaway_emoji)
    giveup_emoji = random.choice(emoji)
    print(f"抽獎資格{giveaway_emoji + 1}")
    print(f"放棄抽獎{giveup_emoji + 1}")
    await asyncio.sleep(time)
    new_message = await channel.fetch_message(my_message.id)
    giveup = await new_message.reactions[giveup_emoji].users().flatten()
    giveup.pop(giveup.index(bot.user))
    users = await new_message.reactions[giveaway_emoji].users().flatten()
    giveup_and_giveaway = []
    users.pop(users.index(bot.user))
    for i in giveup:
        if i in users:
            giveup_and_giveaway.append(i)
            users.remove(i)
            giveup.remove(i)
    if len(users) == 0:
        embed = discord.Embed(color = 0xff2424)
        embed.set_author(name = f'抽獎結束!', icon_url= 'https://i.imgur.com/DDric14.png')
        embed.add_field(name = f'🎉 獎品: {prize}', value = f'沒有人中獎\n 🎫 **要抽獎人數**: {len(users)}\n 🎫 **放棄抽獎人數**: {len(giveup)}\n 🎫 **參加但又放棄人數**: {len(giveup_and_giveaway)}', inline = False)
        embed.set_footer(text = '感謝大家的參與!')
        await channel.send(embed= embed)
        return
    winner = random.choice(users)
    winning_announcement = discord.Embed(color = 0xff2424)
    winning_announcement.set_author(name = f'抽獎結束!', icon_url= 'https://i.imgur.com/DDric14.png')
    winning_announcement.add_field(name = f'🎉 獎品: {prize}', value = f'🥳 **中獎者**: {winner.mention}\n 🎫 **要抽獎人數**: {len(users)}\n 🎫 **放棄抽獎人數**: {len(giveup)}\n 🎫 **參加但又放棄人數**: {len(giveup_and_giveaway)}', inline = False)
    winning_announcement.set_footer(text = '感謝大家的參與!')
    await channel.send(embed = winning_announcement)

@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, player, *, why):
    try:
        uuid = MojangAPI.get_uuid(player)
        getname = requests.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}").json()
        player = getname['name']
        embed=discord.Embed(title="🚫已被永久封鎖ban", description=why, color=0xff2600)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_author(name=player, icon_url=f"https://mc-heads.net/avatar/{uuid}")
        embed.set_thumbnail(url=f"https://mc-heads.net/avatar/{uuid}")
        embed.set_footer(text="若對此判決有任何意見或想法 請使用客服系統與我們主動聯繫")
        await ctx.send(embed=embed)
        await ctx.message.delete()
    except Exception:
        await ctx.message.delete()




async def embed(ctx , type):
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel
    color = ['深灰', '黑色', '灰色', '黃色', '紅色', '白色', '藍色', '綠色']
    code = {'深灰':0x34363c, "黑色":0x000000, "灰色":0x919191, "黃色":0xfffb00, "紅色":0xff2600, "白色":0xffffff, "藍色":0x0433ff, "綠色":0x00f900}
    select = []
    for i in color:
       select.append(SelectOption(label=i, value=i))
    colorchose = [Select(
    placeholder="顏色選擇",
    options=select
    ,
    custom_id='colorchose'
  )]
    try:
        embed=discord.Embed(title="請選擇顏色", description=f"```深灰|黑色|灰色|黃色|紅色|白色|藍色|綠色```")
        msg = await ctx.send(content='點選下方選項選擇顏色', embed=embed, components=colorchose)
        interaction = await bot.wait_for('select_option', check=lambda inter: inter.custom_id == 'colorchose' and inter.user == ctx.author, timeout=60)
        data = interaction.values[0]
        colorcode = code[data]
        await interaction.edit_origin(components=[])
        embed=discord.Embed(title="☝️", color=colorcode)
        await msg.edit(content="***請輸入標題***", embed=embed)
        title = await bot.wait_for('message', check=check, timeout=300)
        await title.delete()
        await msg.edit(content='***請輸入描述***')
        description = await bot.wait_for('message', check=check, timeout=300)
        await description.delete()
        embed=discord.Embed(title=title.content, description=description.content, color=colorcode)
        await add_embed_ticket(ctx, msg, embed, type)
    except asyncio.TimeoutError:
        await interaction.send("時間已超過")

@bot.command()
@commands.has_permissions(administrator=True)
async def ticket(ctx):
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel
    color = ['深灰', '黑色', '灰色', '黃色', '紅色', '白色', '藍色', '綠色']
    code = {'深灰':0x34363c, "黑色":0x000000, "灰色":0x919191, "黃色":0xfffb00, "紅色":0xff2600, "白色":0xffffff, "藍色":0x0433ff, "綠色":0x00f900}
    select = []
    for i in color:
       select.append(SelectOption(label=i, value=i))
    colorchose = [Select(
    placeholder="顏色選擇",
    options=select
    ,
    custom_id='colorchose'
  )]
    try:
        embed=discord.Embed(title="請選擇顏色", description=f"```深灰|黑色|灰色|黃色|紅色|白色|藍色|綠色```")
        msg = await ctx.send(content='點選下方選項選擇顏色', embed=embed, components=colorchose)
        interaction = await bot.wait_for('select_option', check=lambda inter: inter.custom_id == 'colorchose' and inter.user == ctx.author, timeout=60)
        data = interaction.values[0]
        colorcode = code[data]
        await interaction.edit_origin(components=[])
        embed=discord.Embed(title="☝️", color=colorcode)
        await msg.edit(content="***請輸入標題***", embed=embed)
        title = await bot.wait_for('message', check=check, timeout=300)
        await title.delete()
        await msg.edit(content='***請輸入描述***')
        description = await bot.wait_for('message', check=check, timeout=300)
        await description.delete()
        embed=discord.Embed(title=title.content, description=description.content, color=colorcode)
        await add_embed_ticket(ctx, msg, embed)



    except asyncio.TimeoutError:
        await interaction.send("時間已超過")

async def add_embed_ticket(ctx, msg, embed):
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel
    button = Button(style=ButtonStyle.green, label="發送", custom_id="send")
    add = [Select(
    placeholder="新增",
    options=[
        SelectOption(label='作者名稱', value='author_name'),
        SelectOption(label='圖片', value='image'),
        SelectOption(label='小圖片', value='thumbnail'),
        SelectOption(label='字段', value='field'),
        SelectOption(label='底文', value='footer')
    ],
    custom_id='add'
    )]
    await msg.edit(content='***新增其他內容***```新增完畢請按發送按鈕```', embed=embed, components=[add, [button]])
    interaction = await bot.wait_for('select_option', check=lambda inter: inter.custom_id == 'add' and inter.user == ctx.author, timeout=60)
    data = interaction.values[0]
    if data == 'author_name':
        await interaction.edit_origin(content='***請輸入作者名稱***', components=[])
        try:
            author_name = await bot.wait_for('message', check=check, timeout=120)
            embed.set_author(name=author_name.content)
            await author_name.delete()
            await add_embed_ticket(ctx, msg, embed)
        except asyncio.TimeoutError:
            await timeout(msg)
    elif data == 'footer':
        await interaction.edit_origin(content='***請輸入文底***', components=[])
        try:
            footer = await bot.wait_for('message', check=check, timeout=120)
            embed.set_footer(text=footer.content)
            await footer.delete()
            await add_embed_ticket(ctx, msg, embed)
        except asyncio.TimeoutError:
            await timeout(msg)
    elif data == 'field':
        await interaction.edit_origin(content='***請輸入字段名稱***', components=[])
        try:
            field_name = await bot.wait_for('message', check=check, timeout=300)
            await field_name.delete()
            await msg.edit(content="***請輸入字段內容***")
            field_content = await bot.wait_for('message', check=check, timeout=300)
            await field_content.delete()
            embed.add_field(name=field_name.content, value=field_content.content, inline=False)
            await add_embed_ticket(ctx, msg, embed)
        except asyncio.TimeoutError:
            await timeout(msg)
    elif data == 'image':
        await  interaction.edit_origin(content="***請輸入圖片***```[網址 or 上傳圖片]```", components=[])
        try:
            embed_image = await bot.wait_for('message', check=check, timeout=60)
            embed_image_url = await image(embed_image)
            await embed_image.delete()
            embed.set_image(url=embed_image_url)
            await add_embed_ticket(ctx, msg, embed)
        except asyncio.TimeoutError:
            await timeout(msg)
    elif data == 'thumbnail':
        await  interaction.edit_origin(content="***請輸入小圖片***```[網址 or 上傳圖片]```", components=[])
        try:
            thumbnail = await bot.wait_for('message', check=check, timeout=60)
            thumbnail_url = await image(thumbnail)
            await thumbnail.delete()
            embed.set_thumbnail(url=thumbnail_url)
            await add_embed_ticket(ctx, msg, embed)
        except asyncio.TimeoutError:
            await timeout(msg)
        


async def image(msg):
    try:
        msgurl = msg.attachments[0].url
        return msgurl
    except Exception:
        return msg.content
   

async def timeout(msg):
    try:
        embed=discord.Embed(title="時間已超過", color=0xff2600)
        await msg.edit(content="***時間已超過***", embed=embed, components=[])
    except Exception:
        return
        

@bot.event
async def on_button_click(interaction):
    with open('setchannel.json', 'r') as f:
        setchannel = json.load(f)
    user = interaction.author
    guild = interaction.guild
    admin = guild.get_role(config['admin_role_id'])
    member = guild.get_member(user.id)
    if interaction.component.custom_id == "send":
        option = []
        for i in interaction.guild.channels:
            if str(i.type) == 'text':
                option.append(SelectOption(label=i.name, value=i.id))
        channelchose = [Select(
        placeholder="請選擇發送頻道",
        options=option
        ,
        custom_id='channelchose'
        )]
        await interaction.message.edit(content="***請選擇你要發送的頻道***", components=channelchose)
        interaction = await bot.wait_for('select_option', check=lambda inter: inter.custom_id == 'channelchose' and inter.user == interaction.author, timeout=60)
        data = interaction.values[0]
        channel = bot.get_channel(int(data))
        embed = interaction.message.embeds[0]
        button = Button(style=ButtonStyle.green, emoji="📩", label="點擊開啟客服頻道", custom_id="prchannel")
        await channel.send(embed=embed, components=[button])
        await interaction.message.delete()
    if interaction.component.custom_id == "prchannel" and user.id not in setchannel.values():
        await interaction.send("私人頻道已開啟")
        category = discord.utils.get(guild.categories, name=config["category"])
        overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        member: discord.PermissionOverwrite(read_messages=True),
        }
        count = setchannel['count']
        count = "%04d" % count
        channel = await guild.create_text_channel(f"客服 {count}", overwrites=overwrites, category=category)
        embed=discord.Embed(title="伺服人員用控制面板(玩家不能用)", color=0xfffb00)
        button = Button(style=ButtonStyle.green, label="處理完成", custom_id="down")
        button2 = Button(style=ButtonStyle.red, label="關閉客服頻道", custom_id="close")
        await channel.send(embed=embed, components=[[button, button2]])
        options = []
        with open('list.txt', 'r', encoding='utf8') as f:
            optionlist = f.readlines()
        for i in optionlist:
            options.append(SelectOption(label=i, value=i))
        mode = [Select(
                    placeholder="由伺服人員 選擇問題類別",
                    options=options
                    ,
                    custom_id='ticket'
                )]
        await channel.send(content="(由伺服人員操作)選擇問題分類", components=[mode])
        await channel.send(f"{member.mention}客服建立成功!")
        embed=discord.Embed(title="已開啟你的服務窗口 請在此與伺服器人員溝通!", description=f"{member.mention}(本頻道在使用完畢後會移除 若有需要 請自行保存紀錄)", color=0x32363a)
        embed.set_footer(text="我們會盡快回覆您")
        embed.timestamp = datetime.datetime.utcnow()
        await channel.send(embed=embed)
        setchannel[channel.id] = user.id
        num = setchannel['count']
        num += 1
        setchannel['count'] = num
        with open("setchannel.json", "w+") as f:
            json.dump(setchannel, f)
    elif interaction.component.custom_id == "down" and admin in member.roles:
        button = Button(style=ButtonStyle.green, label="處理完成", disabled=True, custom_id="down")
        button2 = Button(style=ButtonStyle.red, label="關閉客服頻道", custom_id="close")
        await interaction.edit_origin(components=[[button, button2]])
        await interaction.channel.edit(name=f'{interaction.channel.name[:7]} 完成')
        star1 = Button(style=ButtonStyle.blue, label='⭐', custom_id="star1")
        star2 = Button(style=ButtonStyle.blue, label='⭐⭐', custom_id="star2")
        star3 = Button(style=ButtonStyle.blue, label='⭐⭐⭐', custom_id="star3")
        star4 = Button(style=ButtonStyle.blue, label='⭐⭐⭐⭐', custom_id="star4")
        star5 = Button(style=ButtonStyle.blue, label='⭐⭐⭐⭐⭐', custom_id="star5")
        await interaction.channel.send(content="***顧客意見調查表***", components=[[star1, star2, star3], [star4, star5]])
    elif interaction.component.custom_id == "close" and admin in member.roles:
        del setchannel[str(interaction.channel.id)]
        with open("setchannel.json", "w+") as f:
            json.dump(setchannel, f)
        await interaction.channel.delete()
    elif interaction.component.custom_id == "star1":
        await comment(interaction, 1)
    elif interaction.component.custom_id == "star2":
        await comment(interaction, 2)
    elif interaction.component.custom_id == "star3":
        await comment(interaction, 3)
    elif interaction.component.custom_id == "star4":
        await comment(interaction, 4)
    elif interaction.component.custom_id == "star5":
        await comment(interaction, 5)
    elif interaction.component.custom_id == "embed":
        option = []
        for i in interaction.guild.channels:
            if str(i.type) == 'text':
                option.append(SelectOption(label=i.name, value=i.id))
        channelchose = [Select(
        placeholder="請選擇發送頻道",
        options=option
        ,
        custom_id='channelchose'
        )]
        await interaction.message.edit(content="***請選擇你要發送的頻道***", components=channelchose)
        interaction = await bot.wait_for('select_option', check=lambda inter: inter.custom_id == 'channelchose' and inter.user == interaction.author, timeout=60)
        data = interaction.values[0]
        channel = bot.get_channel(int(data))
        embed = interaction.message.embeds[0]
        await channel.send(embed=embed)
        await interaction.message.delete()

@bot.event
async def on_select_option(interaction):
    guild = interaction.guild
    admin = guild.get_role(config['admin_role_id'])
    member = guild.get_member(interaction.author.id)
    if interaction.component.custom_id == "ticket" and admin in member.roles:
        data = interaction.values[0]
        await interaction.channel.edit(name=f"{interaction.channel.name[:7]} {data}")
        await interaction.send(f"選擇{data}")


async def comment(interaction, star:int):
    def check(message):
        return message.author == interaction.author and message.channel == interaction.channel
    embed = discord.Embed(title='顧客回饋', description="回饋單", color=0x53d5fd)
    embed.add_field(name="顧客", value=interaction.author.mention, inline=False)
    embed.add_field(name="滿意度", value='⭐'*star, inline=False)
    embed.timestamp = datetime.datetime.utcnow()
    channel = bot.get_channel(config['comment_channel'])
    await channel.send(embed=embed)
    strstar = "評分"+"⭐"*star
    await interaction.edit_origin(components=[], content=f"{strstar}已傳送!感謝您\n若您有興趣的話，請填寫想與今天服務人員說的話")
    try:
        msg = await bot.wait_for('message', check=check, timeout=60)
        embed = discord.Embed(title='顧客回饋', description="回饋", color=0x53d5fd)
        embed.add_field(name="顧客", value=interaction.author.mention, inline=False)
        embed.add_field(name="評語", value=msg.content, inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await channel.send(embed=embed)
        await msg.delete()
        await interaction.message.delete()
    except asyncio.TimeoutError:
        await interaction.message.delete()

@bot.command()
@commands.has_permissions(administrator=True)
async def embed(ctx):
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel
    color = ['深灰', '黑色', '灰色', '黃色', '紅色', '白色', '藍色', '綠色']
    code = {'深灰':0x34363c, "黑色":0x000000, "灰色":0x919191, "黃色":0xfffb00, "紅色":0xff2600, "白色":0xffffff, "藍色":0x0433ff, "綠色":0x00f900}
    select = []
    for i in color:
       select.append(SelectOption(label=i, value=i))
    colorchose = [Select(
    placeholder="顏色選擇",
    options=select
    ,
    custom_id='colorchose'
  )]
    try:
        embed=discord.Embed(title="請選擇顏色", description=f"```深灰|黑色|灰色|黃色|紅色|白色|藍色|綠色```")
        msg = await ctx.send(content='點選下方選項選擇顏色', embed=embed, components=colorchose)
        interaction = await bot.wait_for('select_option', check=lambda inter: inter.custom_id == 'colorchose' and inter.user == ctx.author, timeout=60)
        data = interaction.values[0]
        colorcode = code[data]
        await interaction.edit_origin(components=[])
        embed=discord.Embed(title="☝️", color=colorcode)
        await msg.edit(content="***請輸入標題***", embed=embed)
        title = await bot.wait_for('message', check=check, timeout=300)
        await title.delete()
        await msg.edit(content='***請輸入描述***')
        description = await bot.wait_for('message', check=check, timeout=300)
        await description.delete()
        embed=discord.Embed(title=title.content, description=description.content, color=colorcode)
        await add_embed(ctx, msg, embed)



    except asyncio.TimeoutError:
        await interaction.send("時間已超過")

async def add_embed(ctx, msg, embed):
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel
    button = Button(style=ButtonStyle.green, label="發送", custom_id="embed")
    add = [Select(
    placeholder="新增",
    options=[
        SelectOption(label='作者名稱', value='author_name'),
        SelectOption(label='圖片', value='image'),
        SelectOption(label='小圖片', value='thumbnail'),
        SelectOption(label='字段', value='field'),
        SelectOption(label='底文', value='footer')
    ],
    custom_id='add'
    )]
    await msg.edit(content='***新增其他內容***```新增完畢請按發送按鈕```', embed=embed, components=[add, [button]])
    interaction = await bot.wait_for('select_option', check=lambda inter: inter.custom_id == 'add' and inter.user == ctx.author, timeout=60)
    data = interaction.values[0]
    if data == 'author_name':
        await interaction.edit_origin(content='***請輸入作者名稱***', components=[])
        try:
            author_name = await bot.wait_for('message', check=check, timeout=120)
            embed.set_author(name=author_name.content)
            await author_name.delete()
            await add_embed(ctx, msg, embed)
        except asyncio.TimeoutError:
            await timeout(msg)
    elif data == 'footer':
        await interaction.edit_origin(content='***請輸入文底***', components=[])
        try:
            footer = await bot.wait_for('message', check=check, timeout=120)
            embed.set_footer(text=footer.content)
            await footer.delete()
            await add_embed(ctx, msg, embed)
        except asyncio.TimeoutError:
            await timeout(msg)
    elif data == 'field':
        await interaction.edit_origin(content='***請輸入字段名稱***', components=[])
        try:
            field_name = await bot.wait_for('message', check=check, timeout=300)
            await field_name.delete()
            await msg.edit(content="***請輸入字段內容***")
            field_content = await bot.wait_for('message', check=check, timeout=300)
            await field_content.delete()
            embed.add_field(name=field_name.content, value=field_content.content, inline=False)
            await add_embed(ctx, msg, embed)
        except asyncio.TimeoutError:
            await timeout(msg)
    elif data == 'image':
        await  interaction.edit_origin(content="***請輸入圖片***```[網址 or 上傳圖片]```", components=[])
        try:
            embed_image = await bot.wait_for('message', check=check, timeout=60)
            embed_image_url = await image(embed_image)
            await embed_image.delete()
            embed.set_image(url=embed_image_url)
            await add_embed(ctx, msg, embed)
        except asyncio.TimeoutError:
            await timeout(msg)
    elif data == 'thumbnail':
        await  interaction.edit_origin(content="***請輸入小圖片***```[網址 or 上傳圖片]```", components=[])
        try:
            thumbnail = await bot.wait_for('message', check=check, timeout=60)
            thumbnail_url = await image(thumbnail)
            await thumbnail.delete()
            embed.set_thumbnail(url=thumbnail_url)
            await add_embed(ctx, msg, embed)
        except asyncio.TimeoutError:
            await timeout(msg)




        
    





bot.run('OTQ3MjkzMDQ2NTg2ODY3ODU0.GNIaI5.wJpAlVmE9xx7tqXRnVh0jmHcR9JB0lxjkO-BCI')   

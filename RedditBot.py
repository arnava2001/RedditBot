import discord
import praw 
import random
from discord.ext import commands, tasks
import cv2
import numpy as np

client = discord.Client() #Establish the client

prefix = '&'

#Establish Reddit Bot 
reddit = praw.Reddit(client_id = ' ', #IMPORTANT: Change these fields to your corresponding reddit application fields 
									 			   #https://redditclient.readthedocs.io/en/latest/oauth/
					 client_secret = ' ', 
					 username = ' ',
					 password = ' ',
					 user_agent = 'whatever') #this field wont affect anything

@client.event #On startup
async def on_ready():
	print('We have logged in as {0.user}'.format(client))
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if(prefix in message.content):
        if('hot' in message.content):  #& hot sub (Returns a random hot post from the given subreddit)
            splitMessage = message.content.split()
            if(len(splitMessage)!=3):
                await message.channel.send("Sorry, Invalid arguments! Proper usage -> [&r hot subreddit]")
                return
            else:
                subName = splitMessage[2].lower()
	               sub = reddit.subreddit(subName)
	               posts = [post for post in sub.hot(limit=250)]
	               random_post_number = random.randint(0, 250)
	               random_post = posts[random_post_number]
	               strForm = "{}".format( random_post.url)
	               await message.channel.send(random_post.title)
	               await message.channel.send(strForm)
	               if(random_post.selftext!=''):
	                   await message.channel.send(random_post.selftext)
        if('newest' in message.content):
            splitMessage = message.content.split()
            if(len(splitMessage)!=3):
                await message.channel.send("Sorry, Invalid arguments! Proper usage -> [&r newest subreddit]")
                return
            else:
                subName = splitMessage[2].lower()
                sub = reddit.subreddit(subName)
                posts = [post for post in sub.new(limit=1)]
                random_post = posts[0]
                strForm = "{}".format( random_post.url)
                await message.channel.send(random_post.title)
                await message.channel.send(strForm)
                if(random_post.selftext!=''):
                    await message.channel.send(random_post.selftext)
        if('controversial' in message.content):
            splitMessage = message.content.split()
            if(len(splitMessage)!=3):
                await message.channel.send("Sorry, Invalid arguments! Proper usage -> [&r controversial subreddit]")
                return
            else:
                subName = splitMessage[2].lower()
	              sub = reddit.subreddit(subName)
	              posts = [post for post in sub.controversial(limit=100)]
	              random_post_number = random.randint(0, 100)
	              random_post = posts[random_post_number]
	              strForm = "{}".format(random_post.url)
	              await message.channel.send(random_post.title)
	              await message.channel.send(strForm)
	              if(random_post.selftext!=''):
	                    await message.channel.send(random_post.selftext[0:1999])
        if('cartoon' in message.content):  # &cartoon [image] --> make sure the message has an attachment, (only takes jpgs and pngs)
            
            def read_file(filename):
                img = cv2.imread(filename)
                return img
            
            img = None

            if(not message.attachments):
                await message.channel.send("Sorry, Please attach a message for this command! Proper Usage -> &cartoon <img file>")
            else:
                attachment = message.attachments[0]
                if(attachment.filename.lower().endswith("png")):
                    await attachment.save("img.png")
                    img = read_file("img.png")
                elif(attachment.filename.lower().endswith("jpg")):
                    await attachment.save("img.jpg")
                    img = read_file("img.jpg")
                else:
                    await message.channel.send("Sorry, file type must be of .jpg or .png")
            
            def edge_mask(img, line_size, blur_value):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray_blur = cv2.medianBlur(gray, blur_value)
                edges = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, line_size, blur_value)
                return edges

            edges = edge_mask(img, 7, 7)

            def color_quantization(img, k):
                # Transform the image
                data = np.float32(img).reshape((-1, 3))

                # Determine criteria
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.001)

                # Implementing K-Means
                ret, label, center = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
                center = np.uint8(center)
                result = center[label.flatten()]
                result = result.reshape(img.shape)
                return result
            
            img = color_quantization(img, 9)
            blurred = cv2.bilateralFilter(img, d=7, sigmaColor=200,sigmaSpace=200)
            cartoon = cv2.bitwise_and(blurred, blurred, mask=edges)

            cv2.imwrite("img.jpg" , cartoon)
            await message.channel.send(file=discord.File('img.jpg'))
                    
@tasks.loop(seconds = 120)
async def stay_active():
    print("Active!")

client.run('') #Run the bot w/ your token


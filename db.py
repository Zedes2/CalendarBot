# bot.py
import os
import random
import discord
import re

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents().all()

bot = commands.Bot(command_prefix='.', intents = intents)

class Month:
    def __init__(self, name: str, season: str, length: int):
        self.name = name
        self.season = season
        self.length = length

class Calendar:
    def __init__(self, name, currentYear, weekLength, weekDays, seasons, months, zeroDay, currentDay, yearLength):
        self.name = name
        self.currentYear = currentYear
        self.weekLength = weekLength
        self.weekDays = weekDays
        self.seasons = seasons
        self.months = months
        self.zeroDay = zeroDay
        self.currentDay = currentDay
        self.yearLength = yearLength
    
    def printInfo(self):
        print(self.currentYear)
        print(self.yearLength)
        print(self.currentDay)
        print(self.weekLength)
        print(self.weekDays)
        print(self.seasons)
        print(self.months)
    
    def findCurrentMonth(self):
        curr = self.currentDay % self.yearLength
        index = 0
        for m in self.months:
            if (curr > m.length):
                curr -= m.length
            else:
                return index
            index += 1

    def findMonth(self, newDay):
        curr = newDay % self.yearLength
        index = 0
        for m in self.months:
            if (curr > m.length):
                curr -= m.length
            else:
                return index
            index += 1

myCalendar = Calendar("", 1, 7, [], [], [], 1, 1, 300)

def calendarParse(fileName, calendarLabel, fileData):
    myCalendar.name = fileName
    yerL = 0

    lines = fileData.split('\n')
    for line in lines:
        if(len(line) < 2):
            continue
        delim, txt = line.split("-", 1)
        if (delim == "w"):
            myCalendar.weekDays = txt.split(',')
            myCalendar.weekLength = len(myCalendar.weekDays)
        if (delim == "y"):
            myCalendar.currentYear = int(txt.strip())
        if (delim == "s"):
            seasonName, seasonMonths = txt.split(":", 1)
            myCalendar.seasons.append(seasonName.strip().capitalize())
            seasonMonthsMonths = seasonMonths.split(",")
            for month in seasonMonthsMonths:
                reg = re.compile("(.+) (\d+)")
                monthData = reg.match(month)
                m = Month(monthData[1].strip().capitalize(), seasonName.strip().capitalize(), int(monthData[2]))
                myCalendar.months.append(m)
                yerL += int(monthData[2])
    myCalendar.yearLength = yerL

@bot.command(name='users', help='Lists current server members')
async def users(ctx):
    response = ""
    for member in ctx.guild.members:
        response = response + '\n' + member.name
    await ctx.send(response)

@bot.command(name='initCalendar', help='Initializes a new calendar')
async def initCalendar(ctx, arg1, arg2):
    fs = open(arg1 + '.txt', 'r')
    calendarParse(arg1, arg2, fs.read())
    fs.close()
    await ctx.send("Calendar initialized as " + arg2)

@bot.command(name='day', help='Posts the current date in loaded calendar')
async def day(ctx):
    thisDay = myCalendar.currentDay
    thisMonth = "n/a"
    thisSeason = "n/a"
    for month in myCalendar.months:
        if (thisDay > month.length):
            thisDay -= month.length
        else:
            thisMonth = month.name
            thisSeason = month.season
            break
    sendStr = "It is " + thisMonth + " " + str(thisDay) + " in the season of " + thisSeason + " in the year " + str(myCalendar.currentYear)
    await ctx.send(sendStr)

@bot.command(name='setDay', help='Changes current day to day specified')
async def setDay(ctx, arg):
    thisDay = int(arg)
    dayCount, monthCount, seasonCount = 0, 0, 0
    thisMonth = "n/a"
    thisSeason = "n/a"
    constOriginalDay = myCalendar.currentDay
    constDayDelta = thisDay - constOriginalDay
    
    curr = constOriginalDay
    dayDelta = constDayDelta
    #Task 1: Calculate weeks, months, seasons, years passed
    #Check to see if new day num has passed into a new year
    originYear = constOriginalDay // myCalendar.yearLength
    destinationYear = thisDay // myCalendar.yearLength
    if (originYear < destinationYear):
        yearsPassed = destinationYear - originYear
        while (yearsPassed > 1):
            dayDelta -= myCalendar.yearLength
            myCalendar.currentYear += 1
            monthCount += len(myCalendar.months)
            yearsPassed -= 1
        # Find the day in current month, then normalize to the end of the month
        dayInMonth = constOriginalDay
        for month in myCalendar.months:
            if (dayInMonth > month.length):
                dayInMonth -= month.length
            else:
                dayDelta -= (month.length - dayInMonth)
                break
        # Progress months to the end of the year
        while (myCalendar.months[myCalendar.findMonth(curr)] != myCalendar.months[len(myCalendar.months) - 1]):
            print("Previous month: " + myCalendar.months[myCalendar.findMonth(curr)].name + ". ")
            curr += myCalendar.months[myCalendar.findMonth(curr) + 1].length
            print("New month: " + myCalendar.months[myCalendar.findMonth(curr)].name + ".\n")
            monthCount += 1
        
    '''
    for m in myCalendar.months:
        if (curr > m.length):
            curr -= m.length
        else:'''
            
    '''calculate position in current month
    subtract days left from dayDelta
    while (delta - next month length > 0)
        subtract next month length from delta
        increment monthsPassed
        check if season changed and increment seasonsPassed if so
    calculate weeks passed
    display month day, weeks passed, months passed, seasons passed, years passed
    '''

    '''while(dayDelta > 0):
        dayCount += 1
        myCalendar.currentDay += 1
        #check if week changes, increment week
        #check if month changes, increment month
        #check if seaoson changes, increment season'''
        
    sendStr = "Current day set to " + thisMonth + " " + str(thisDay) + " in the season of " + thisSeason + " in the year " + str(myCalendar.currentYear) + "\n" + str(constDayDelta) + " days have passed. "
    if (seasonCount == 1):
        sendStr += "One season has passed. "
    if (seasonCount > 1):
        sendStr += str(seasonCount) + " seasons have passed. "
    myCalendar.currentDay = int(arg)
    await ctx.send(sendStr)

bot.run(TOKEN)
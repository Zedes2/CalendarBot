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

bot = commands.Bot(command_prefix='.', intents=intents)


class Month:
    def __init__(self, name: str, season: str, length: int):
        self.name = name
        self.season = season
        self.length = length


class Calendar:
    def __init__(self, name, zero_year, week_length, week_days, seasons, months, zero_day, current_day, year_length):
        self.name = name
        self.zero_year = zero_year
        self.week_length = week_length
        self.week_days = week_days
        self.seasons = seasons
        self.months = months
        self.zero_day = zero_day
        self.current_day = current_day
        self.year_length = year_length

    def print_info(self):
        print(self.zero_year)
        print(self.year_length)
        print(self.current_day)
        print(self.week_length)
        print(self.week_days)
        print(self.seasons)
        print(self.months)

    def find_current_month(self):
        curr = self.current_day % self.year_length
        index = 0
        for m in self.months:
            if curr > m.length:
                curr -= m.length
            else:
                return index
            index += 1

    def find_month(self, new_day):
        curr = new_day % self.year_length
        index = 0
        for m in self.months:
            if curr > m.length:
                curr -= m.length
            else:
                return index
            index += 1


my_calendar = Calendar("", 1, 7, [], [], [], 1, 1, 300)


def calendar_parse(file_name, calendar_label, file_data):
    my_calendar.name = file_name
    yer_l = 0

    lines = file_data.split('\n')
    for line in lines:
        if len(line) < 2:
            continue
        delim, txt = line.split("-", 1)
        if delim == "w":
            my_calendar.week_days = txt.split(',')
            my_calendar.week_length = len(my_calendar.week_days)
        if delim == "y":
            my_calendar.zero_year = int(txt.strip())
        if delim == "s":
            season_name, season_months = txt.split(":", 1)
            my_calendar.seasons.append(season_name.strip().capitalize())
            season_months_months = season_months.split(",")
            for month in season_months_months:
                reg = re.compile("(.+) (\d+)")
                month_data = reg.match(month)
                m = Month(month_data[1].strip().capitalize(), season_name.strip().capitalize(), int(month_data[2]))
                my_calendar.months.append(m)
                yer_l += int(month_data[2])
    my_calendar.year_length = yer_l


@bot.command(name='users', help='Lists current server members')
async def users(ctx):
    response = ""
    for member in ctx.guild.members:
        response = response + '\n' + member.name
    await ctx.send(response)


@bot.command(name='initCalendar', help='Initializes a new calendar')
async def init_calendar(ctx, arg1, arg2):
    fs = open(arg1 + '.txt', 'r')
    calendar_parse(arg1, arg2, fs.read())
    fs.close()
    await ctx.send("Calendar initialized as " + arg2)


@bot.command(name='day', help='Posts the current date in loaded calendar')
async def day(ctx):
    this_day = my_calendar.current_day
    this_month = "n/a"
    this_season = "n/a"
    this_day = this_day % my_calendar.year_length
    this_year = my_calendar.zero_year + my_calendar.current_day // my_calendar.year_length
    for month in my_calendar.months:
        if this_day > month.length:
            this_day -= month.length
        else:
            this_month = month.name
            this_season = month.season
            break
    send_str = "It is " + this_month + " " + str(this_day) + " in the season of " + this_season + " in the year " + str(
        this_year)
    await ctx.send(send_str)


@bot.command(name='setDay', help='Changes current day to day specified')
async def set_day(ctx, arg):
    try:
        const_new_day = int(arg)
    except ValueError:
        await ctx.send("Please enter a valid integer. ")
        return
    month_count, season_count, year_count = 0, 0, 0
    this_month = "n/a"
    this_season = "n/a"
    this_year = my_calendar.zero_year
    const_original_day = my_calendar.current_day
    const_day_delta = const_new_day - const_original_day

    this_day = const_new_day
    curr = const_original_day
    day_delta = const_day_delta
    # Task 1: Calculate weeks, months, seasons, years passed
    # Check to see if new day num has passed into a new year
    origin_year = const_original_day // my_calendar.year_length
    destination_year = (this_day - 1) // my_calendar.year_length
    if origin_year < destination_year:
        years_passed = destination_year - origin_year
        while years_passed > 1:
            year_count += 1
            day_delta -= my_calendar.year_length
            month_count += len(my_calendar.months)
            season_count += len(my_calendar.seasons)
            years_passed -= 1
        # Find the day in current month, then normalize to the end of the month
        day_in_month = const_original_day
        for month in my_calendar.months:
            if day_in_month > month.length:
                day_in_month -= month.length
            else:
                day_delta -= (month.length - day_in_month)
                break
        # Progress months to the end of the year
        while my_calendar.months[my_calendar.find_month(curr)] != my_calendar.months[len(my_calendar.months) - 1]:
            # print("Current month: " + myCalendar.months[myCalendar.findMonth(curr)].name)
            # Season count might be off. Does it check correctly?
            if my_calendar.months[my_calendar.find_month(curr)].season !=\
                    my_calendar.months[my_calendar.find_month(curr) + 1].season:
                season_count += 1
            day_delta -= my_calendar.months[my_calendar.find_month(curr) + 1].length
            curr += my_calendar.months[my_calendar.find_month(curr) + 1].length
            month_count += 1
        # Day is now set to the final day of the last year. Next step is to progress to the first day of the new year
        day_delta -= 1
        if my_calendar.months[len(my_calendar.months) - 1].season != my_calendar.months[0].season:
            season_count += 1
        my_calendar.currentMonth = my_calendar.months[0]
        month_count += 1
        year_count += 1

    # Now that we know we are on the current year, we set day and year
    this_day = const_new_day % my_calendar.year_length
    this_year = my_calendar.zero_year + const_new_day // my_calendar.year_length

    # Iterate through month list until we find current month
    for mon in my_calendar.months:
        if this_day > mon.length:
            this_day -= mon.length
            month_count += 1
            if mon.season != my_calendar.months[my_calendar.find_month(this_day)].season: season_count += 1
        else:
            this_month = mon.name
            this_season = mon.season
            break

    # Dynamic print to only show months/season/year passage when greater than 0
    send_str = "Current day set to " + this_month + " " + str(
        this_day) + " in the season of " + this_season + " in the year " + str(this_year) + "\n" + str(
        const_day_delta) + " days have passed"
    if month_count == 1:
        send_str += ", one month has passed"
    elif month_count > 1:
        send_str += ", " + str(month_count) + " months have passed"
    if season_count == 1:
        send_str += ", one season has passed"
    elif season_count > 1:
        send_str += ", " + str(season_count) + " seasons have passed"
    if year_count == 1:
        send_str += ", and one year has passed"
    elif year_count > 1:
        send_str += ", and " + str(year_count) + " years have passed"
    send_str += ". "
    my_calendar.current_day = int(arg)
    await ctx.send(send_str)


bot.run(TOKEN)

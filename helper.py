#pip install urlextract

from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import string
import emoji
import calendar

extract = URLExtract()


def fetch_stats(selected_user, df):
    # If specific user then modify df with that user's df
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Fetch total number of messages
    num_messages = df.shape[0]

    # Fetch total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # Fetch number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # Fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    # Remove that are not links
    for link in links.copy():
        if 'M.Tech' in link:
            links.remove(link)
        if 'M.tech' in link:
            links.remove(link)
        if 'm.tech' in link:
            links.remove(link)
        if 'B.Tech' in link:
            links.remove(link)
        if 'B.tech' in link:
            links.remove(link)
        if 'b.tech' in link:
            links.remove(link)

    return num_messages, len(words), num_media_messages, len(links)

# pip install matplotlib
# import matplotlib.pyplot as plt
def fetch_busy_users(df):
    # try:
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0])*100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})  # dividing with total number of messages and multiplying by 100

    return x, df


def create_wordcloud(selected_user, df):

    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # 1. remove group_notification messages
    temp = df[df['user'] != 'group_notification']

    # 2. remove <Media omitted>\n messages
    temp = temp[temp['message'] != '<Media omitted>\n']

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500, height=500,min_font_size=10,background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc


def most_common_words(selected_user, df):

    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # 1. remove group_notification messages
    temp = df[df['user'] != 'group_notification']

    # 2. remove <Media omitted>\n messages
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []

    for message in temp['message']:  # use temp dataset
        for word in message.lower().split():  # use split otherwise you will get char by char instead of word by word
            if word not in stop_words:
                word.translate(str.maketrans('', '', string.punctuation))  # remove punctuation
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

# !pip install emoji==1.7.0
def emoji_helper(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.UNICODE_EMOJI['en']])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df

def monthly_timeline(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month']).count()['message'].reset_index()

    # import calendar
    months = [month for month in calendar.month_name if month]

    time = []
    for i in range(timeline.shape[0]):
        # print(timeline['month'][i])
        time.append(months[timeline['month'][i] - 1] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline


def daily_timeline(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()  # in helper

    return daily_timeline


def week_activity_map(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month_name'].value_counts()


def activity_heatmap(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap
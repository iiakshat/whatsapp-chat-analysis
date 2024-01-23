import base64
from io import BytesIO
from wordcloud import WordCloud
from .TextPreprocessor import *
import matplotlib
matplotlib.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import emoji

links = []

def counter(user, df):
    global links
    if user:
        df2 = df[df['user']==user]
        msgs = df2.shape[0]
        for sentence in df2['message']:
            link = extractUrl(sentence)
            if link:
                links.extend(link)
        media = df2['media'].sum()
        return msgs, len(links), media

    else:
        msgs = df.shape[0]
        media = df['media'].sum()
        for sentence in df['message']:
            link = extractUrl(sentence)
            if link:
                links.extend(link)
        return msgs, len(links), media


def most_busy_users(suser, df):
    data = round((df['user'].value_counts()/df.shape[0])*100,2)
    try:
        data.drop("Zuckerberg",inplace=True)
    except:
        print('You have no whatsapp notifications.')
    x = ''

    if len(df['user'].unique()) < 4:
        ff = data
        name = ff.index.tolist()
        val = ff.tolist()
        explode = [0.07, 0]
        colors = ['#D2E0FB', '#8EACCD']

    else:
        x = data.get(suser)
        ff = data.head(5)
        name = ff.index.tolist()
        val = ff.tolist()

        rem = 100-sum(val)
        explode = [0.07, 0, 0, 0, 0, 0]
        
        name.append('Others')
        val.append(rem)
        colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99', '#9376e0', '#ff74b1']

    fig1, ax1 = plt.subplots()
    fig1.set_facecolor('None') 
    ax1.pie(val, colors = colors, labels=name, autopct='%1.1f%%', 
            startangle=90, pctdistance=0.85, explode = explode)
    centre_circle = plt.Circle((0,0),0.70,fc='none')

    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    ax1.axis('equal')  
    plt.tight_layout()

    img_data = BytesIO()
    plt.savefig(img_data, format='png', transparent=True)
    img_data.seek(0)
    encoded_img = base64.b64encode(img_data.getvalue()).decode('utf-8')
    img_html = f'<img src="data:image/png;base64,{encoded_img}" alt="Matplotlib Graph">'
    return img_html, name[0], x
    

def frequent_words(df, selected_user):
    with open('././Data/stopwords.txt', 'r') as f:
        stopwords = f.read()

    if selected_user:
        new_df = df[df['user']==selected_user]

    else:
        new_df = df[df['user']!='Zuckerberg']


    ''' Null is common message for notifications like 
        missed video call, opened (when a media is shared
        in one time view and other party views.), etc.'''

    new_df = new_df[~new_df['message'].isin(['<Media omitted>\n', 
                                             'This message was deleted\n',
                                             'You deleted this message\n',
                                             'null\n', '\n'
                                             ])]

    new_df['message'] = textPreprocess(new_df['message'], stopwords)
    final = removeContacts(new_df.message.str.cat(sep=' '))
    common_words = Counter(final.split(' '))

    ''' Whenever a user shares a contact with a friend the contact is 
        shared as contact.vsf file. We don't want this to be considered
        for analysis, so we'll have to remove this. '''

    wordcloud = WordCloud(width=500, 
                   height=500, 
                   scale=3, 
                   min_font_size=10,
                   background_color=None,
                   mode="RGBA",
                   contour_width=0,
                   contour_color='transparent',
                   collocations=False).generate(final)

    plt.imshow(wordcloud, interpolation='bilinear', alpha=0.8)
    plt.axis('off')
    img_data = BytesIO()
    plt.savefig(img_data, format='png', bbox_inches='tight', pad_inches=0)
    img_data.seek(0)
    encoded_img = base64.b64encode(img_data.getvalue()).decode('utf-8')
    img_html = f'<img src="data:image/png;base64,{encoded_img}" alt="Matplotlib Graph">'

    return img_html, common_words


def most_common_emoji(selected_user,df):
    if selected_user:
        df = df[df['user'] == selected_user]

    all_emojis = set(emoji.EMOJI_DATA)

    emojis = []
    for message in df['message']:
        emojis.extend([i for i in message if i in all_emojis])

    top_emojis = {}
    for i in Counter(emojis).most_common(5):
        top_emojis[emoji.emojize(i[0])] = i[1]
    return top_emojis
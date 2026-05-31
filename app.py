import os
import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

youtube = build('youtube', 'v3', developerKey=API_KEY)

# 📌 Get videos from channel
def get_videos(channel_id):
    request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        maxResults=10,
        order='date'
    )
    response = request.execute()

    videos = []
    for item in response['items']:
        if item['id']['kind'] == 'youtube#video':
            videos.append({
                'title': item['snippet']['title'],
                'video_id': item['id']['videoId']
            })
    return videos

# 📌 Get video stats
def get_video_stats(video_ids):
    request = youtube.videos().list(
        part='statistics',
        id=','.join(video_ids)
    )
    response = request.execute()

    data = []
    for item in response['items']:
        stats = item['statistics']
        data.append({
            'views': int(stats.get('viewCount', 0)),
            'likes': int(stats.get('likeCount', 0)),
            'comments': int(stats.get('commentCount', 0))
        })
    return data

# 🎯 Streamlit UI
st.set_page_config(page_title="YouTube Dashboard", layout="wide")

st.title("📊 YouTube Data Dashboard")

channel_id = st.text_input("Enter YouTube Channel ID")

if channel_id:
    videos = get_videos(channel_id)

    if videos:
        video_ids = [v['video_id'] for v in videos]
        stats = get_video_stats(video_ids)

        df = pd.DataFrame(stats)
        df['title'] = [v['title'] for v in videos]

        # 📊 Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Views", df['views'].sum())
        col2.metric("Total Likes", df['likes'].sum())
        col3.metric("Total Comments", df['comments'].sum())

        st.divider()

        # 📋 Table
        st.subheader("📋 Video Data")
        st.dataframe(df)

        # 📊 Bar Chart
        st.subheader("📊 Views per Video")
        fig = px.bar(df, x='title', y='views')
        st.plotly_chart(fig, use_container_width=True)

        # 📈 Line Chart
        st.subheader("📈 Views Trend")
        fig2 = px.line(df, y='views')
        st.plotly_chart(fig2, use_container_width=True)

    else:
        st.warning("No videos found for this channel")
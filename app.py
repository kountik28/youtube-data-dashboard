import os
import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
import plotly.express as px
from dotenv import load_dotenv

# 🔐 Load API Key
load_dotenv()
API_KEY = os.getenv("API_KEY")

# 🔴 Safety check
if not API_KEY:
    st.error("API Key not found. Please check your .env file.")
    st.stop()

youtube = build('youtube', 'v3', developerKey=API_KEY)

# 📌 Function to get videos
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

# 📌 Function to get video stats
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

# 🎯 UI CONFIG
st.set_page_config(page_title="YouTube Dashboard", layout="wide")

# 🎯 TITLE
st.title("📊 YouTube Data Dashboard")
st.markdown("### 📈 Analyze YouTube Channel Performance in Real-Time")

# 🎯 SIDEBAR INPUT
st.sidebar.header("🔍 Input Options")
channel_id = st.sidebar.text_input("Enter YouTube Channel ID")

# 🎯 MAIN LOGIC
if channel_id:
    try:
        videos = get_videos(channel_id)

        if videos:
            video_ids = [v['video_id'] for v in videos]
            stats = get_video_stats(video_ids)

            df = pd.DataFrame(stats)
            df['title'] = [v['title'] for v in videos]

            # 📊 METRICS
            col1, col2, col3 = st.columns(3)
            col1.metric("👁 Total Views", f"{df['views'].sum():,}")
            col2.metric("👍 Total Likes", f"{df['likes'].sum():,}")
            col3.metric("💬 Total Comments", f"{df['comments'].sum():,}")

            st.divider()

            # 📋 DATA TABLE
            st.subheader("📋 Video Data")
            st.dataframe(df)

            # 🏆 TOP VIDEOS
            st.subheader("🏆 Top Performing Videos")
            top_videos = df.sort_values(by='views', ascending=False)
            st.dataframe(top_videos)

            # 🎯 FILTER
            st.subheader("🎯 Filter Videos by Views")
            min_views = st.slider(
                "Select minimum views",
                0,
                int(df['views'].max())
            )
            filtered_df = df[df['views'] >= min_views]
            st.dataframe(filtered_df)

            # 📊 BAR CHART
            st.subheader("📊 Views per Video")
            fig = px.bar(df, x='title', y='views')
            st.plotly_chart(fig, use_container_width=True)

            # 📈 LINE CHART
            st.subheader("📈 Views Trend")
            fig2 = px.line(df, y='views')
            st.plotly_chart(fig2, use_container_width=True)

        else:
            st.warning("No videos found for this channel")

    except Exception as e:
        st.error("❌ Invalid Channel ID or API Error. Please try again.")
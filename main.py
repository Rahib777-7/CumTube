from flask import Flask, render_template, request
from pytube import YouTube, Search

def get_related(video):
    results = Search(video.title+video.author).results
    return(results)

app = Flask(__name__, template_folder='.')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/watch/<video_id>")
def watch(video_id):
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        video = YouTube(youtube_url)
        video_url = video.streams.get_highest_resolution().url
        video_title = video.title
        video_channel = video.author
        video_description = video.description
        video_channel_url = video.channel_url
        video_views = video.views
        related_videos = get_related(video)
        return render_template('watch.html', video_url=video_url, video_title=video_title, video_channel=video_channel, related_videos=related_videos, video_description=video_description, video_channel_url=video_channel_url, video_views=video_views)
    except Exception as e:
        return str(e)

@app.route("/search")
def search():
    query = request.args.get("q")
    if not query:
        return "Please enter a search query"
    try:
        search_results = Search(query).results
        return render_template("search.html", query=query, results=search_results, videos=search_results)
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(debug=True)

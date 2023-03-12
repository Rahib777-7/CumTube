from flask import Flask, render_template, request
from pytube import YouTube, Search, Channel
import concurrent.futures, requests, timeago, datetime

def human_format(num):
    magnitude = 0
    try:
        while abs(int(num)) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '%.2f%s' % (int(num), ['', 'K', 'M', 'G', 'T', 'P'][magnitude])
    except Exception:
        return '?'

def search_views_human_format(num):
    magnitude = 0
    try:
        num = num.views
        while abs(int(num)) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '%.2f%s' % (int(num), ['', 'K', 'M', 'G', 'T', 'P'][magnitude])
    except Exception:
        return '?'

def search_publishdategetvideodata_better(value, actualtime):
    try:
        value = timeago.format(str(value.publish_date))
        return(value)
    except Exception as a:
        return a

def getvideodata(result, actualtime):
    json = {}
    json['publishdate'] = search_publishdategetvideodata_better(result, actualtime)
    json['views'] = search_views_human_format(result)
    json['title'] = result.title
    json['video_id'] = result.video_id
    json['thumbnail_url'] = result.thumbnail_url
    json['channel_url'] = result.channel_url
    json['author'] = result.author

    return json

def get_related(video):
    search_results = Search(video.title+video.author).results
    actualtime = datetime.datetime.today().strftime('%Y-%m-%d')

    # multithreaded for performance
    def process_result(result):
        return getvideodata(result, actualtime)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_result, result) for result in search_results]
        concurrent.futures.wait(futures)

    data = [future.result() for future in futures]
    return(data)

def get_channel(channel):
    data = requests.get("https://pipedapi.kavin.rocks/channel/"+channel).json() # i use piped api bc pytube channel is actually broke
    return(data)

app = Flask(__name__, template_folder='.', static_url_path='/static', static_folder='static')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/watch/<video_id>")
def watch(video_id):
    youtube_url = 'https://www.youtube.com/watch?v='+video_id
    try:
        video = YouTube(youtube_url)
        video_url = video.streams.get_highest_resolution().url
        data = get_related(video)
        return render_template('watch.html', video_url=video_url, video=video, data=data)
    except Exception as e:
        return str(e)

@app.route('/channel/<channel_name>')
def channel(channel_name):
    c = get_channel(channel_name)
    return render_template('channel.html', channel_name=c['name'], videos=c['relatedStreams'], human_format=human_format)

@app.route("/search")
def search():
    query = request.args.get("q")
    if not query:
        return "Please enter a search query"
    try:
        search_results = Search(query).results
        actualtime = datetime.datetime.today().strftime('%Y-%m-%d')
        
        # multithreaded for performance
        def process_result(result):
            return getvideodata(result, actualtime)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_result, result) for result in search_results]
            concurrent.futures.wait(futures)

        data = [future.result() for future in futures]

        return render_template("search.html", data=data, query=query)
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

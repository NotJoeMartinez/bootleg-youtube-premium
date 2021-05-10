import sqlite3 
import os
import sys 
import subprocess
import datetime as dt
import jinja2
from youtube_dl import YoutubeDL

def main():
    now = dt.datetime.now().strftime("%m_%d_%-I:%M:%S%p")
    url = sys.argv[1]

    download_video(url,now)
    log_downloads(url, now)
    make_html(url,now)
    update_library()

    subprocess.run("./sync.sh", shell=True)
    



def download_video(url, now):
    subprocess.run(f"youtube-dl -f mp4 {url} -o webapp/videos/{now}.mp4", shell=True)


def log_downloads(url, now):
    youtube_dl_opts = {}
    with YoutubeDL(youtube_dl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_url = info_dict.get("url", None)
        video_id = info_dict.get("id", None)
        video_title = info_dict.get('title', None)

    add_to_db(now, url, video_id, video_title)



def add_to_db(now, url, id, title):
    con = sqlite3.connect('history.db')
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS history 
               (date text, url text, id text, title text)''')

    cur.execute(f'''INSERT INTO history VALUES ("{now}","{url}","{id}","{title}")''')
    con.commit()
    con.close()


def make_html(url, now):

    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "templates/index.html"
    template = templateEnv.get_template(TEMPLATE_FILE)

    most_recent = find_most_recent("webapp/videos")

    con = sqlite3.connect('history.db')
    cur = con.cursor()
    cur.execute(f'''select * from history WHERE url = '{url}' and date ='{now}';''')
    rows = cur.fetchall()
    con.close()

    outputText = template.render(most_recent=most_recent,title=rows[0][3] )

    html_file = open('webapp/index.html', 'w')
    html_file.write(outputText)
    html_file.close()



def find_most_recent(directory):

    now = dt.datetime.now()
    dir_list = os.listdir(directory)
    datetimes = []

    for x in dir_list:
        x = x[:-4]
        dir_dt = dt.datetime.strptime(x, "%m_%d_%I:%M:%S%p")
        datetimes.append(dir_dt)

    most_recent = max(dt for dt in datetimes if dt < now)
    mr = most_recent.strftime("%m_%d_%-I:%M:%S%p")
    return mr    


def update_library():
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "templates/library.html"
    template = templateEnv.get_template(TEMPLATE_FILE)


    con = sqlite3.connect('history.db')
    cur = con.cursor()
    cur.execute(f'''select * from history''')
    rows = cur.fetchall()
    con.close()

    foo = [row for row in rows]
    print(foo[1])

    outputText = template.render(foo=foo )

    html_file = open('webapp/library.html', 'w')
    html_file.write(outputText)
    html_file.close()




if __name__ == '__main__':
    main()




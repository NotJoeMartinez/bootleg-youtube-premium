import sqlite3, os, sys, subprocess, uuid
import datetime as dt
import jinja2
from youtube_dl import YoutubeDL
import threading
import argparse


def main():

    SERVER_IP = get_server_ip()

    url = sys.argv[1]
    now = dt.datetime.now().strftime("%m_%d_%-I:%M:%S%p")
    thread = threading.Thread(target=download_video(url,now))
    thread.start()

    subprocess.run("rm webapp/videos/*.part > /dev/null 2>&1", shell=True)
    # wait here for the result to be available before continuing
    thread.join()

    log_downloads(url, now)
    make_html(url,now)
    update_library()
    remove_db_duplicates()
    subprocess.run("./sync.sh > /dev/null 2>&1", shell=True)
    print(f"http://{server_ip}/videos/{now}.mp4")
    


def download_video(url, now):
    subprocess.run(f"youtube-dl -q -f mp4 {url} -o ~/bootleg-youtube-premium/webapp/videos/{now}.mp4 > /dev/null 2>&1", shell=True)


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

    cur.execute('''INSERT INTO history VALUES (?, ?, ?, ?)''', (now, url, id, title))
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
    cur.execute('''select * from history WHERE url =? and date = ? ''', (url, now))
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

    outputText = template.render(foo=foo )

    html_file = open('webapp/library.html', 'w')
    html_file.write(outputText)
    html_file.close()


def remove_db_duplicates():
    from collections import Counter
    now = dt.datetime.now()
    con = sqlite3.connect('history.db')
    cur = con.cursor()
    cur.execute(f'''select * from history''')
    rows = cur.fetchall()

    # finds duplicate ids
    ids = [row[2] for row in rows]
    counter_object = dict(Counter(ids))
    duplicate_ids = [key for key in counter_object if counter_object[key] > 1]
    

    # if len(duplicate_ids) > 1:
    for vid_id in duplicate_ids:

        cur.execute(''' select * from history WHERE id=?''', (vid_id,))
        foo = cur.fetchall()

        # converts to string
        time_stamps = [dt.datetime.strptime(foo[0], "%m_%d_%I:%M:%S%p") for foo in foo]


        # finds most recent
        try:
            most_recent = max([dt for dt in time_stamps])

            # converts most recent to string
            mr = most_recent.strftime("%m_%d_%-I:%M:%S%p")

            # print(mr, most_recent)
            cur.execute(f''' DELETE FROM history WHERE id=? and date != ? ''', (vid_id, mr))
        except ValueError:
            pass

    con.commit()

    cur.execute(f"select * from history")
    uniq = cur.fetchall()

    uniq_timestamps = [i[0] for i in uniq]
    # print(uniq_timestamps)

    videos = os.listdir("webapp/videos")
    #print(videos)

    for vid in videos:
        if vid[:-4] not in uniq_timestamps:
            os.remove(f"webapp/videos/{vid}")
    con.close()

def get_server_ip():

    fpath = f"/tmp/{str(uuid.uuid1())}_my_ip.txt"
    subprocess.run(f"curl ip.me >> {fpath}", shell=True)
    with open(fpath, "r") as f:
        ip = f.readline()
    os.remove(fpath)

    return ip.strip() 


if __name__ == '__main__':
    main()

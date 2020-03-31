import os
import webbrowser
from shutil import copyfile
import random
import cv2
import pickle
from moviepy.editor import *
from flask import Flask, render_template, redirect, url_for, request
from flaskwebgui import FlaskUI

pickle_base = "C:\\Users\\AI\\AIVideo_Player\\data\\"
image_directory = 'C:\\Users\\AI\\Code\\VideoPlayer\\engine\\static\\images'
n_recent_files = 3
current_directory = ''
allowed_images = []
video_file_types = ['flv', 'mp4', 'avi', 'webm', 'mov', 'mpeg', 'wmv', 'mp3', 'MP4', 'mkv', 'MKV', 'AVI', 'MPEG', 'WEBM']


def pick(picklefile):
    picklefile = pickle_base+picklefile
    if os.path.isfile(picklefile):
        with open(picklefile, 'rb') as f:
            folders = pickle.load(f)
    else:
        folders = {}
    return folders


def cache(item, picklefile):
    picklefile = pickle_base+picklefile
    with open(picklefile, 'wb') as f:
        pickle.dump(item, f)

    # ff = FFmpeg(executable='C:\\ffmpeg\\bin\\ffmpeg.exe', inputs={folder+folders[folder]['last_file']: None}, outputs={"C:\\Users\\AI\\AIVideo_Player\\data\\recntly_played\\thumbnail"+str(count)+".png": ['-vf', 'fps=1']})
    # ff.run()


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


# do your logic as usual in Flask
@app.route("/")
def index():
    favourites = pick('favourites.pickle')
    folders = pick('cache.pickle')
    backup_gif = ''
    for file in favourites:
        gif_filename = 'C:\\Users\\AI\\Code\\VideoPlayer\\engine\\static\\images\\' + os.path.basename(file) + '.gif'
        if favourites[file]['changed'] or not os.path.isfile(gif_filename):
            try:
                seconds = favourites[file]['time'] - 3.5
                clip = (VideoFileClip(file).subclip(seconds, seconds+7.5))
                clip.write_gif(gif_filename)
            except OSError:
                pass
            favourites[file]['changed'] = False
    cache(favourites, 'favourites.pickle')

    for folder in folders:
        filename = 'C:\\Users\\AI\\Code\\VideoPlayer\\engine\\static\\images\\' + folders[folder]['filename'] + '.png'
        backup_gif = folders[folder]['filename'] +'.gif'
        gif_filename = 'C:\\Users\\AI\\Code\\VideoPlayer\\engine\\static\\images\\' + backup_gif
        if not os.path.isfile(filename):
            cap = cv2.VideoCapture(folders[folder]['full_path'])
            cap.set(1, 100)
            res, frame = cap.read()
            cv2.imwrite(filename, frame)
            try:
                clip = (VideoFileClip(folders[folder]['full_path']).subclip((1, 7.7), (1, 14.12)))
                clip.write_gif(gif_filename)
            except OSError:
                pass

    print(favourites)
    if favourites != {}:
        favourite_gif = os.path.basename(random.choice(list(favourites)))+'.gif'
    else:
        favourite_gif = backup_gif

    path = "index.html"
    print(favourite_gif)
    return render_template(path, folders=folders, favourite_gif=favourite_gif)

@app.route('/viewer', defaults={'_file_path': 'sample'})
@app.route('/viewer/<_file_path>')
def viewer(_file_path):
    folders = pick('cache.pickle')
    time_dict = pick('time_dict.pickle')
    file_path = _file_path.replace('>', '\\')
    dirname, filename = os.path.dirname(file_path), os.path.basename(file_path)
    folders[dirname] = {
        'full_path': str(file_path),
        'filename': str(filename)
    }
    try:
        last_time = time_dict[file_path]
    except KeyError:
        last_time = 0.0
        time_dict[file_path] = 0.0
    folders[dirname]['last_time'] = last_time


    # folder_stack = pick('folder_stack.pickle')
    folder_stack = list(folders)
    folder_stack.append(dirname)
    while len(folder_stack)>n_recent_files+1:
        try:
            del folders[folder_stack[0]]
            folder_stack.remove(folder_stack[0])
        except KeyError:
            folder_stack.remove(folder_stack[0])
    cache(folders, 'cache.pickle')
    cache(time_dict, 'time_dict.pickle')
    cache(folder_stack, 'folder_stack.pickle')
    view_locaiton = os.getcwd()+url_for('static', filename='images/'+filename)
    allowed_images.append(os.path.basename(view_locaiton))
    try:
        copyfile(file_path, view_locaiton)
    except FileNotFoundError:
        pass
    path = "viewer.html"
    filename = os.path.basename(view_locaiton)
    while len(allowed_images)>4:
        allowed_images.remove(allowed_images[0])
    print(filename)
    return render_template(path, file_name=url_for('static', filename='images/'+filename), full_file_path=_file_path, last_time=last_time, _filename=filename.replace('%20', ' '))

@app.route("/folders", defaults={'_path': '?'})
@app.route("/folders/<_path>")
def folders(_path):
    folder_stack = pick('folder_stack.pickle')
    path = _path.replace('>', '\\')
    if any(path.endswith(_) for _ in video_file_types):
        return redirect("http://127.0.0.1:5000/viewer/"+path.replace('\\', '>'))
    elif path == '?':
        try:
            path = folder_stack[-1]
        except KeyError:
            path = 'C:\\'
    elif path.endswith('<<'):
        path = os.path.dirname(path)
    elif path == '<<<':
        path = 'C:\\'

    f = lambda s: path+"\\"+s
    try:
        folders_full_path = list(map(f, os.listdir(path)))
        folders_list = os.listdir((path))
    except NotADirectoryError:
        return "AIVIDEO_PLAYER does not support this file type"

    return render_template('folders.html', folders_full_path=folders_full_path, folders_list=folders_list, directory=path)

@app.route("/changeVideo", defaults={'param': ' '})
@app.route("/changeVideo/", methods=['POST', 'GET'])
def changeVideo():
    last_video = request.args.get('last_video')
    last_video = last_video.replace('>', '\\')
    last_video = last_video.replace('<', ' ')
    last_time = request.args.get('last_time')
    favourite = request.args.get('favourite')
    favourite_time = request.args.get('favouriteTime')
    command = request.args.get('command')
    folders = pick('cache.pickle')
    time_dict = pick('time_dict.pickle')
    favourites = pick('favourites.pickle')
    directory = os.path.dirname(last_video)
    filename = os.path.basename(last_video)
    if favourite == 'true':
        print('adding to favourite')
        favourites[last_video] = {'time':float(favourite_time),'changed':True}
    cache(favourites, 'favourites.pickle')
    folders[directory] = {
        'full_path': str(last_video),
        'filename': str(filename),
        'last_time': float(last_time)
    }
    time_dict[last_video] = last_time
    cache(time_dict, 'time_dict.pickle')
    cache(folders, 'cache.pickle')
    _dir_list = os.listdir(directory)
    dir_list = [_ for _ in _dir_list if any(_.endswith(__) for __ in video_file_types)]
    if command == 'next':
        next_file = directory + "\\" + dir_list[dir_list.index(filename) + 1]
        return redirect("http://127.0.0.1:5000/viewer/" + next_file.replace('\\', '>'))

    elif command == 'previous':
        previous_file = directory + "\\" + dir_list[dir_list.index(filename) - 1]
        return redirect("http://127.0.0.1:5000/viewer/" + previous_file.replace('\\', '>'))

    elif command == 'backspace':
        return redirect('http://127.0.0.1:5000/')

    elif command == 'exit':
        for file in os.listdir(image_directory):
            if file not in [os.path.basename(_)+'.gif' for _ in favourites] and not file.startswith('icons8') and file not in [folders[__]['filename'] for __ in folders] and file not in [folders[__]['filename']+'.gif' for __ in folders] and file not in [folders[__]['filename']+'.png' for __ in folders] and file not in allowed_images:
                os.remove(image_directory+'\\'+file)
        exit()
    return ''


# call the 'run' method
app.run()

print('done')
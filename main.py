from flet import (
    Page,Text,ElevatedButton,FloatingActionButton,TextField,Dropdown,dropdown,Switch,FilePicker,FilePickerResultEvent
)
import flet as ft
import time
import os
import subprocess
import platform
if platform.system() == "Windows":
    import winsound
else:
    pass


def main(page:Page):
    page.title = "yt-dlpGUI ver:0.6"
    page.fonts = {
        "MPLUS": "fonts/mplus.ttf",
    }
    page.theme = ft.Theme(font_family="MPLUS")
    page.window_left = 100
    page.window_top = 100
    page.window_width = 550
    page.window_height = 800
    page.padding = 16
    home = os.path.expanduser('~')
    output_path = home+"/yt-dlp"
    dl_log = "実行時のログ"
    cookie_file = ""

    def sel_path(e: FilePickerResultEvent):
        nonlocal output_path
        before = output_path
        output_path = e.path if e.path else before
        path_input.value = output_path
        path_input.update()
        return
    
    def sel_cookie(e: FilePickerResultEvent):
        nonlocal cookie_file
        if e.files:
            cookie_file = e.files[0].path
        else:
            cookie_file = ""
        cookie_input.value = cookie_file
        cookie_input.update()
        print(cookie_file)
        return
    
    def download(e):
        nonlocal dl_log
        url = url_input.value
        dl_log = "実行時のログ"
        command = ['yt-dlp','--add-metadata']
        if url != "":
            command.append(url)
            if mode_sel.value == "mp4":
                command.extend(['--merge-output-format','mp4'])
                command.append('-f')
                if quality_sel.value == "自動":
                    command.append('bestvideo[ext=mp4]+bestaudio/best[ext=mp4]')
                elif quality_sel.value == "1080p":
                    command.append('bestvideo[ext=mp4][height<=1080]+bestaudio/best[ext=mp4][height<=1080]')
                elif quality_sel.value == "720p":
                    command.append('bestvideo[ext=mp4][height<=720]+bestaudio/best[ext=mp4][height<=720]')
                elif quality_sel.value == "480p":
                    command.append('bestvideo[ext=mp4][height<=480]+bestaudio/best[ext=mp4][height<=480]')
                elif quality_sel.value == "360p":
                    command.append('bestvideo[ext=mp4][height<=360]+bestaudio/best[ext=mp4][height<=360]')
            elif mode_sel.value == "mp3":
                command.append('-f')
                command.append('bestaudio')
                command.append('-x')
                command.append('--audio-format')
                command.append('mp3')
                command.append('--audio-quality')
                command.append('256K')
            elif mode_sel.value == "wav":
                command.append('-f')
                command.append('bestaudio')
                command.append('-x')
                command.append('--audio-format')
                command.append('wav')
            if use_multi.value == True:
                command.extend(['-N','8'])
            else:
                pass
            if playlist.value == True and name_index.value == False:
                command.extend(['-o',f'{output_path}/%(playlist_title)s/%(title)s.%(ext)s'])
            elif playlist.value == True and name_index.value == True:
                command.extend(['-o',f'{output_path}/%(playlist_title)s/%(playlist_index)s_%(title)s.%(ext)s'])
            elif playlist.value == False and name_index.value == False:
                command.extend(['-o',f'{output_path}/%(title)s.%(ext)s'])
            elif playlist.value == False and name_index.value == True:
                command.extend(['-o',f'{output_path}/%(playlist_index)s_%(title)s.%(ext)s'])
            if use_aria2.value == True:
                command.extend(["--external-downloader", "aria2c", "--external-downloader-args", "-x 16 -s 16"])
            else:
                pass
            if emb_thumbnail.value == True:
                command.extend(['--embed-thumbnail'])
            else:
                pass
            if cookie_file:
                command.extend(['--cookies', cookie_input.value])
            print(command)

            with open("dl.log","a") as log_file:

                with subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) as process:

                    dl_btn.text = "ダウンロード中"
                    dl_btn.disabled = True
                    dl_btn.update()

                    for line in process.stdout:
                        log_out.value = line
                        log_out.update()
                        log_file.write(line)

                    process.wait()
                    if process.returncode == 0:
                        log_out.value = "正常にダウンロードできました"
                        log_out.update()
                        dl_btn.text = "ダウンロード"
                        dl_btn.disabled = False
                        dl_btn.update()
                        if platform.system() == "Windows":
                            winsound.MessageBeep(winsound.MB_OK)
                        log_file.write(f"{'-'*50} 処理ここまで {'-'*50}\n")
                        return
                    else:
                        log_out.value = "エラーが発生しました"
                        log_out.update()
                        dl_btn.text = "ダウンロード"
                        dl_btn.disabled = False
                        dl_btn.update()
                        if platform.system() == "Windows":
                            winsound.MessageBeep(winsound.MB_ICONHAND)
                        log_file.write(f"{'-'*50} 処理ここまで {'-'*50}\n")
                        return
                    

    
    dir_dialog = FilePicker(on_result=sel_path)
    cookie_select = FilePicker(on_result=sel_cookie)

    page.overlay.extend([dir_dialog,cookie_select])

    url_input = TextField(hint_text="URLを入力",label="URL",icon=ft.icons.MOVIE)
    path_input = TextField(value=output_path,hint_text="保存先を選択",label="保存先",icon=ft.icons.FOLDER,expand=True,read_only=True)
    path_btn = ft.TextButton("選択",icon=ft.icons.FOLDER_COPY,on_click=lambda _:dir_dialog.get_directory_path())
    dl_btn = FloatingActionButton("ダウンロード",icon=ft.icons.DOWNLOAD,on_click=download)
    cookie_input = TextField(value=cookie_file, hint_text="Cookieファイルを選択", label="Cookie", icon=ft.icons.COOKIE, expand=True, read_only=True)
    cookie_btn = ft.TextButton("選択", icon=ft.icons.COOKIE, on_click=lambda _:cookie_select.pick_files(allowed_extensions=["txt"]))
    mode_sel = Dropdown(value="mp4",label="フォーマット",options=[dropdown.Option("mp4"),dropdown.Option("mp3"),dropdown.Option("wav")],expand=True)
    quality_sel = Dropdown(value="自動",label="画質(mp4のみ)",options=[dropdown.Option("自動"),dropdown.Option("1080p"),dropdown.Option("720p"),dropdown.Option("480p"),dropdown.Option("360p")],expand=True)
    log_out = Text(value=dl_log,max_lines=5,)
    name_index = Switch(label="プレイリストのインデックスをファイル名に含める",tooltip=f"ファイル名にプレイリストのインデックスを含めます。")
    use_multi = Switch(label="同時接続する",tooltip=f"同時接続して高速でダウンロードできるようにします\nエラーが発生する可能性があります",expand=True)
    emb_thumbnail = Switch(label="サムネイルを埋め込む",tooltip=f"ファイルにサムネイルを埋め込みます")
    playlist = Switch(label="プレイリスト名でフォルダを作成",tooltip=f"プレイリストの名前でフォルダを作成し、その中にファイルを保存します\nプレイリストでない場合はNAに保存されます")
    use_aria2 = Switch(label="Aria2を使う",tooltip=f"外部ダウンローダーであるAria2を使用します。\n同時接続数を増やし高速でダウンロードできるようにします\n接続が制限され極端に速度が低下する可能性があります",expand=True)

    page.add(
        Text("yt-dlpGUI",size=20),
        url_input,
        ft.Row([path_input,path_btn]),
        Text("オプション",size=18),
        ft.Row([mode_sel,quality_sel]),
        playlist,
        name_index,
        emb_thumbnail,
        ft.Row([use_multi,use_aria2]),
        ft.Row([cookie_input, cookie_btn]),
        Text("ログ",size=18),
        log_out,
        dl_btn
    )

ft.app(main,assets_dir="assets")

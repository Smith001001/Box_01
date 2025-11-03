"""
video_launcher.py

说明：
- 这是一个教学/作业示例：使用 tkinter 制作一个带按钮的可视化界面。
- 包含：腾讯视频、爱奇艺、优酷 的跳转按钮；URL 输入栏；"打开URL/播放"按钮；以及本地视频播放按钮。
- 本程序不会尝试绕过付费墙或爬取受版权保护内容。仅用于打开网页或直接可播放的媒体资源或本地文件。
"""

import os
import tempfile
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# 常用视频网站 — 仅做跳转
SITES = {
    "腾讯视频": "https://v.qq.com/",
    "爱奇艺": "https://www.iqiyi.com/",
    "优酷": "https://www.youku.com/",
}

def open_site(url):
    """在默认浏览器打开网站"""
    webbrowser.open(url, new=2)

def open_url_from_entry(entry_widget):
    """
    1) 若输入是以 http/https 开头并且以常见媒体后缀结尾（.mp4 .webm .ogg），
       则生成临时 HTML 嵌入 <video> 标签并打开 —— 仅对直接可播放的媒体文件有效。
    2) 否则直接在浏览器中打开该 URL（用于正常网页跳转）。
    """
    url = entry_widget.get().strip()
    if not url:
        messagebox.showinfo("提示", "请输入视频网址或媒体文件地址（例如以 http(s):// 开头）。")
        return

    # 简单检测：以 http/https 开头
    if not (url.startswith("http://") or url.startswith("https://")):
        messagebox.showwarning("不支持的格式", "请输入以 http:// 或 https:// 开头的网址或直接选择本地文件播放。")
        return

    # 如果看起来像是直接的媒体文件，生成 HTML 播放
    lower = url.lower()
    if lower.endswith((".mp4", ".webm", ".ogg", ".ogv")):
        try:
            html = f"""<!doctype html>
<html>
<head><meta charset="utf-8"><title>播放媒体</title></head>
<body style="margin:0; background:#000;">
<video controls autoplay style="width:100%; height:100vh; max-height:100vh;">
  <source src="{url}">
  你的浏览器不支持 video 标签，或该资源无法直接播放。
</video>
</body>
</html>"""
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html", prefix="play_", mode="w", encoding="utf-8")
            tmp.write(html)
            tmp.close()
            webbrowser.open(f"file://{tmp.name}", new=2)
        except Exception as e:
            messagebox.showerror("错误", f"创建临时播放页面失败：{e}")
    else:
        # 不是直接媒体文件 -> 作为普通网址打开
        webbrowser.open(url, new=2)

def play_local_file():
    """选择本地视频文件并用系统默认程序打开"""
    filetypes = [
        ("视频文件", "*.mp4 *.mkv *.webm *.avi *.mov *.ogg *.ogv"),
        ("所有文件", "*.*"),
    ]
    path = filedialog.askopenfilename(title="选择本地视频文件", filetypes=filetypes)
    if not path:
        return
    try:
        # 在不同平台上，用默认方式打开文件
        if os.name == "nt":  # Windows
            os.startfile(path)
        elif os.name == "posix":
            # macOS / Linux 的常见方法：
            try:
                # macOS
                os.system(f'open "{path}"')
            except Exception:
                # Linux (xdg-open)
                os.system(f'xdg-open "{path}" &')
        else:
            webbrowser.open(f"file://{os.path.abspath(path)}", new=2)
    except Exception as e:
        messagebox.showerror("错误", f"无法打开文件：{e}")

def create_gui():
    root = tk.Tk()
    root.title("追剧/看电影 小工具（示例）")
    root.geometry("640x240")
    root.resizable(False, False)

    pad = 12
    frame = ttk.Frame(root, padding=pad)
    frame.pack(fill="both", expand=True)

    # 网站快速跳转
    lbl_sites = ttk.Label(frame, text="快速跳转到视频网站：", font=("Arial", 10, "bold"))
    lbl_sites.pack(anchor="w")

    btn_frame = ttk.Frame(frame)
    btn_frame.pack(fill="x", pady=(6, 12))

    for site_name, site_url in SITES.items():
        b = ttk.Button(btn_frame, text=site_name, command=lambda u=site_url: open_site(u))
        b.pack(side="left", padx=6)

    # 输入栏
    lbl = ttk.Label(frame, text="输入视频网址或媒体文件 URL：")
    lbl.pack(anchor="w")
    entry_var = tk.StringVar()
    entry = ttk.Entry(frame, textvariable=entry_var, width=80)
    entry.pack(fill="x", pady=(6, 6))

    hint = ttk.Label(frame, text="提示：若为直接可播放的媒体文件（例如以 .mp4 结尾），程序将尝试生成临时页面播放；否则直接在浏览器打开。", foreground="#555")
    hint.pack(anchor="w", pady=(0,8))

    # 操作按钮
    ops = ttk.Frame(frame)
    ops.pack(fill="x")

    btn_open = ttk.Button(ops, text="打开 URL（在浏览器中）", command=lambda: open_url_from_entry(entry))
    btn_open.pack(side="left", padx=6)

    btn_local = ttk.Button(ops, text="播放本地文件", command=play_local_file)
    btn_local.pack(side="left", padx=6)

    # 免责声明区域（简短）
    disclaimer = ttk.Label(frame, text="免责声明：本程序仅用于打开网页或播放合法可用的媒体文件。请勿使用本工具进行侵权或绕过付费观看。", foreground="red", wraplength=600)
    disclaimer.pack(anchor="w", pady=(12,0))

    root.mainloop()

if __name__ == "__main__":
    create_gui()

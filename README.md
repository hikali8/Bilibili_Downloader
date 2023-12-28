# Bilibili_Downloader
A simple bilibili video downloader / 一个简单的哔哩哔哩视频下载器
This repository is just for studying! 
# Discription / 描述
1. 采用Python协程开发，目前设立了12个客户端并行下载。
2. 单个视频下载速度极佳，多个视频则会受到服务端限制。
3. 音视频合并部分目前采用ffmpeg，因为工具太大了无法上传，如果使用还需确保工具配备。
4. 当下仅在未登录状态下载视频，好处是速度够快，坏处是分辨率只到480P。
5. 可以断点续传了
# Todo list / 接着做的事情
1. 加入代理功能。
2. 寻找更精简且不慢的音视频合并工具。
3. 添加登录功能，使能下载1080P视频。
4. 加入多选GUI，使能自选视频于多视频。
# Prospection / 展望
1. 可采用其他语言进一步开发GUI界面。
2. 可支持更多网站的视频下载。

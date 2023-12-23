import pickle
import subprocess, threading
import sys
from collections.abc import Awaitable

import re, time, secrets
import os, shutil
import asyncio, aiohttp, aiofiles

import win32file, win32pipe
import bisect


user_agents = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
]
cooled_user_agents = []

class Client:
    def __init__(self, session: aiohttp.ClientSession):
        self.totalErrNum = 0
        self.proxy = None
        self.userAgent = user_agents.pop(secrets.randbelow(len(user_agents)))
        self.session = session
        self.referer = 'https://www.bilibili.com'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        clients.append(self)

    async def reset(self):
        global user_agents, cooled_user_agents
        if len(user_agents) != 0:
            ori = self.userAgent
            self.userAgent = user_agents.pop(secrets.randbelow(len(user_agents)))
            cooled_user_agents.append(ori)
        else:
            ori = user_agents
            user_agents = cooled_user_agents
            cooled_user_agents = ori
            self.userAgent = user_agents.pop(secrets.randbelow(len(user_agents)))
        await self.session.__aexit__(None, None, None)
        self.session = await aiohttp.ClientSession().__aenter__()


clientNum = 12   # 12个用户端
clients = []
clients: list[Client]
semaphore = asyncio.Semaphore(clientNum)

chunkSize = 1024 * 30

# 创建命名管道
ph = None

def send_data(data):
    global ph
    win32file.WriteFile(ph, len(data).to_bytes(2, byteorder='little') + data)


amountDict = {}

threadAlive = True
def amountDictSendThread():
    interval = 0.1  # 发送的间隔
    cur_time = time.time()
    while threadAlive:
        send_data(pickle.dumps(amountDict))
        prev_time = cur_time
        next_time = prev_time + interval
        cur_time = time.time()
        sleep_time = next_time - cur_time
        if sleep_time > 0:
            time.sleep(sleep_time)
            cur_time = next_time




exts = ('.mp4', '.m4a')
class DownCoroutine:
    def __new__(cls, va_urls, cid, file_path: str, bv_url=None):
        self = super().__new__(cls)
        ########## init ###########
        # va_urls: (video_url, audio_url)
        # 如果为None，自动从bv_url获取
        # 完事后file_path应该就是所需要的文件
        self.urls = va_urls
        self.bv_url = bv_url
        self.cid = cid
        self.filePath = file_path.replace('/', '\\')
        self.fileName = os.path.basename(self.filePath)
        self.tempDir = self.filePath.rsplit('\\', 1)[0] + f'\\{cid}\\'
        return self.main_logic()

    def end(self):
        send_data(pickle.dumps(True) + int.to_bytes(self.cid, 4, byteorder='little'))
        print(self.fileName, "is done!")

    types = ("视频", "音频")
    async def main_logic(self) -> bool:
        # 检查是不是已经有文件了，这样就不用下载
        if os.path.isfile(self.filePath): # 不能用exists，无法区分文件与目录
            print(self.fileName, "已有了！")
            self.end()
            return True
        # 检查是不是还没有urls
        if self.urls is None:
            assert self.bv_url is not None
            send_data(pickle.dumps((self.fileName, 1, '', "正在获取源代码..."))
                      + int.to_bytes(self.cid, 4, byteorder='little'))
            source_code = await get_source_code(self.bv_url)
            if source_code == '':
                print(self.fileName, "获取源代码失败！", sep='')
                self.end()
                return False
            self.urls = onlyVA(source_code)
        # 还要检查缓存目录是否存在
        if not os.path.isdir(self.tempDir):
            os.makedirs(self.tempDir)
        # 下载视频部分
        if not await self._download1(0):
            self.end()
            return False
        # 下载音频部分
        if not await self._download1(1):
            self.end()
            return False
        # 合并音视频
        send_data(pickle.dumps((self.fileName, 1, '', "正在合并音视频..."))
                  + int.to_bytes(self.cid, 4, byteorder='little'))
        if not self.mergeVA():
            print(self.fileName, "合并音视频失败！")
            self.end()
            return False
        # 清理缓存
        send_data(pickle.dumps((self.fileName, 1, '', "正在清理缓存..."))
                  + int.to_bytes(self.cid, 4, byteorder='little'))
        shutil.rmtree(self.tempDir)
        self.end()
        return True


    async def _download1(self, i: int) -> bool:
        # i: 0视频, 1音频
        ext = exts[i]
        what = self.types[i]
        # 检查是否已有
        if os.path.isfile(self.tempDir + 'plus' + ext):
            print(self.fileName, "的", what, "部分已有了！", sep='')
            return True
        # 获取大小
        send_data(pickle.dumps((self.fileName, 1, '', "正在获取" + what + "部分的大小..."))
                  + int.to_bytes(self.cid, 4, byteorder='little'))
        size = await self.get_size(self.urls[i])
        if size == -1:
            print(self.fileName, "获取", what, "部分的大小失败！", sep='')
            return False
        # 开始下载
        send_data(pickle.dumps((self.fileName, size, 'B', "正在下载" + what + "部分..."))
                  + int.to_bytes(self.cid, 4, byteorder='little'))
        amountDict[self.cid] = 0
        if not await self._download2(self.urls[i], size, ext):
            print(self.fileName, "下载", what, "部分失败！", sep='')
            return False
        del amountDict[self.cid]
        # 开始合并
        send_data(pickle.dumps((self.fileName, 1, '', "正在合并" + what + "部分..."))
                  + int.to_bytes(self.cid, 4, byteorder='little'))
        if self.copy_ranges(ext):
            return True
        print(self.fileName, "合并", what, "部分失败！", sep='')
        return False


    async def _download2(self, url, size, ext):
        # 按剩余的clients数量，分成多个部分，分别下载
        # 信号量和剩余用户端数有可能不一样，用户端可能释放了还没有被用，但信号量却是瞬间分配的
        await semaphore.acquire()   # 至少要一个
        semaphore._value += 1   # 只能这样，release会瞬间分配出去
        cur_clientsNum = semaphore._value
        _quotient = size // cur_clientsNum
        _remainder = size % cur_clientsNum
        coList = []
        start = 0
        for i in range(cur_clientsNum):
            next_start = start + _quotient
            if _remainder:
                next_start += 1
                _remainder -= 1
            coList.append(self.downRange(url, start, next_start - 1, ext))  # 经测试，pop()运行快于[0]
            start = next_start
        # return True: all succeeded
        ret = all(await asyncio.gather(*coList))
        return ret


    async def downRange(self, url, start, end, ext) -> bool:
        # [start, end] (including the end...)
        # 要检查当前块是不是也下载了（——目前还不是很完善，因为命名会有区别的）
        # 命名的话，还是就start-end.ext就行了，不要自己命名
        rangePath = self.tempDir + str(start) + '-' + str(end) + ext
        # 检查范围是不是已存在
        if os.path.isfile(rangePath):
            what = self.types[exts.index(ext)] # 少进，所以单独索引
            print(self.fileName, "的", what, "部分已有范围", start, "-", end, "的内容", sep='')
            return True
        # 开始下载对应内容
        async with semaphore:
            with clients.pop() as client:   # 经测试，pop()运行快于[0]
                headers = {
                    'Range': f'bytes={start}-{end}',
                    'Referer': client.referer,
                    'User-Agent': client.userAgent
                }
                async def real_part() -> bool:
                    async with aiofiles.open(rangePath, 'wb') as f:
                        async with client.session.get(url, headers=headers) as resp:
                            while True:
                                if resp.status != 206:
                                    print(resp.status)
                                    return False
                                chunk = await resp.content.read(chunkSize)
                                if not chunk:
                                    return True
                                amountDict[self.cid] += len(chunk)
                                await f.write(chunk)
                if await self.enretryable(real_part, client):
                    # 成功后重置一下client再归还
                    await client.reset()    # 目前来看，获取源码->获取大小->获取文件是一个很连续的过程，只应该在最后才重置
                    return True
        what = self.types[exts.index(ext)] # 少进，所以单独索引
        print(self.fileName, "的", what, "部分下载范围", start, "-", end, "的内容失败", sep='')
        return False


    @staticmethod
    async def get_size(url) -> int:
        header = None
        async with semaphore:
            with clients.pop() as client:
                headers = {
                        'Range': f'bytes=0-1023',
                        'Referer': client.referer,
                        'User-Agent': client.userAgent
                }
                async def real_part() -> bool:
                    nonlocal header
                    async with client.session.get(url, headers=headers) as resp:
                        if resp.status != 206:
                            print(resp.status)
                            return False
                        header = resp.headers
                        return True
                ret = await DownCoroutine.enretryable(real_part, client)
        return int(header["Content-Range"].split('/')[1]) if ret else -1

    @staticmethod
    async def enretryable(func, client) -> bool:
        time = 1
        while True:  # 尝试三次，不行出
            try:
                if await func():   # 异步函数，且返回值为 bool
                    return True
            except (aiohttp.ClientPayloadError, aiohttp.ClientConnectorError, asyncio.exceptions.TimeoutError) as e:
                print("错误：", type(e), "——", e, sep='')
            # except Exception as e:
            #     print("出错：", type(e), "——", e, sep='')
            #     raise e
            client.totalErrNum += 1
            print(func, "失败，这是第", time, "次", sep='')
            if time >= 3:
                print("重试太多次了...")
                return False
            print("将在3秒后重试...")
            time += 1
            await asyncio.sleep(3)


    def copy_ranges(self, ext) -> bool:
        # return 0: succeeded
        target_files = []
        for root, dirs, files in os.walk(self.tempDir):
            if not dirs:
                for file in files:
                    if file.endswith(ext) and '-' in file:
                        bisect.insort(target_files, file, key=lambda f: int(f.split('-', 1)[0]))
        return os.system('copy /y /b %s "%splus%s">nul'%(
                '+'.join(self.tempDir + file for file in target_files),
                self.tempDir, ext
        )) == 0

    def mergeVA(self) -> bool:
        # return 0: succeeded
        return os.system('ffmpeg -v quiet -i "%splus%s" -i "%splus%s" -c:v copy -c:a copy "%s"'%(
            self.tempDir, exts[0], self.tempDir, exts[1], self.filePath
        )) == 0


async def get_source_code(url) -> str:
    text = ''
    async with semaphore:
        with clients.pop() as client:
            headers = {
                'Referer': client.referer,
                "user-agent": client.userAgent
            }
            async def real_part() -> bool:
                nonlocal text
                async with client.session.get(url, headers=headers) as resp:
                    text = await resp.text()
                    return True
            await DownCoroutine.enretryable(real_part, client)
    return text

def get_vurl(source_code):  # 要获取清晰度最高的视频链接
    video_id = re.search(r'"video":\s*\[\{\s*"id":\s*(\d+?),', source_code).group(1)
    p = re.compile(r'"id":\s*%s,\s*"baseUrl":\s*"(.*?)",' % video_id)
    return p.findall(source_code)[-1]  # 下载最后一个AV1格式的视频，压缩率最高
# 不知道为什么，HEVC的下载速度比AV1慢很多

def get_aurl(source_code):
    return re.search(r'"audio":\[\{"id":\d+?,"baseUrl":"(.*?)"', source_code).group(1)  # 第一个就行


async def get_bvs(url: str, bvid: str, page: int) -> tuple:
    # return: (bv_title, now_video_url, now_audio_url, episode_title, [(cid, bv_title, url_ + bvid), ...], now_index)
    # if no episode_title, automatically pages:
    # then return: (bv_title, now_video_url, now_audio_url, None, [(cid, page_title1, url_ + '?p=' + pagenum), ...], now_index)
    if page is None:
        page = 1
    source_code = await get_source_code(url)
    if source_code == '':
        print(bvid, "的p", page, "获取源代码失败！", sep='')
        return ()
    bv_title = re.search(r'"pic":\s*".*?",\s*"title":\s*"(.*?)"', source_code).group(1)
    vurl = get_vurl(source_code)
    aurl = get_aurl(source_code)
    _matched = re.search(r'"episodes":\s*\[(.*?)\]', source_code, re.S)
    if _matched:   # has episodes
        episodes_code = _matched.group(1)
        episodes_title = re.search(r'"ugc_season":\s*\{\s*"id":\s*\d+,\s*"title":\s*"(.*?)"', source_code).group(1)
        episodesList = []
        now_index = None
        cid_title_Iter = re.finditer(r'"cid":\s*(\d+),\s*"title":\s*"(.*?)"', episodes_code)
        bvidIter = re.finditer(r'"bvid":\s*"(.*?)"', episodes_code)
        for i, (c, b) in enumerate(zip(cid_title_Iter, bvidIter), 0):
            _bvid = b.group(1)
            if _bvid == bvid:
                now_index = i
            episodesList.append((int(c.group(1)), c.group(2), 'https://www.bilibili.com/video/' + _bvid))
        return (bv_title, vurl, aurl, episodes_title, episodesList, now_index)
    else:
        _matched = re.search(r'"pages":\s*\[(.*?)\]', source_code, re.S)
        if not _matched:
            print("亦非选集，亦非分P，此何也？")
            raise Exception()
        pages_code = _matched.group(1)
        pagesList = []
        cid_page_part_Iter = re.finditer(r'"cid":\s*(\d*),\s*"page":\s*(\d*),\s*"from":\s*".*?",\s*"part":\s*"(.*?)"',
                                         pages_code)
        for m in cid_page_part_Iter:
            _page = m.group(2)
            pagesList.append((int(m.group(1)), m.group(3), 'https://www.bilibili.com/video/' + bvid + '?p=' + _page))
        return (bv_title, vurl, aurl, None, pagesList, page - 1)


def onlyVA(source_code):
    # (vurl, aurl)
    return (get_vurl(source_code), get_aurl(source_code))


async def start(awaitable: Awaitable) -> bool:
    global ph, amountDict, threadAlive
    t = time.time()
    ph = win32pipe.CreateNamedPipe(
        r'\\.\pipe\show_pipe',
        win32pipe.PIPE_ACCESS_OUTBOUND,
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
        1, 65536, 65536,
        300,
        None
    )
    displayProcess = subprocess.Popen([sys.executable, "displayProcess.py"],
        creationflags=subprocess.CREATE_NEW_CONSOLE)
    print("等待客户端连接...")
    win32pipe.ConnectNamedPipe(ph, None)
    print("连起了!")
    # 发送线程
    sendThread = threading.Thread(target=amountDictSendThread)
    sendThread.start()
    # 启动！
    ret = await awaitable
    # 收尾。。。
    threadAlive = False
    while sendThread.is_alive(): pass
    displayProcess.terminate()
    win32file.CloseHandle(ph)
    print("下载", "完毕" if ret else "失败", "！", sep='')
    print("总用时：", time.time() - t, "s", sep='')
    return ret


async def main(url, bvid, page: int):
    # os.system("chcp 65001")  # 更改控制台系统输出字符为utf-8
    videoDir = "./video/"  # 视频保存路径
    ## 存在以下情况：
    # 1. 视频有选集
    # 2. 视频有分pages，只是没搞懂它的page、part有什么名字d区别，现在就把他叫做page，因为选集也可以有1part而无page在源代码中
    # 3. 两个都无
    # 4. 不会两个都有，因为分p视频不能加入选集中
    # 5. 还有一个ugc_season，可能是它们那些追番者将会使用到的分季。由于本人并未涉猎此内容，将不实现。想必也比较容易。
    bvs = await get_bvs(url, bvid, page)
    title = bvs[0]
    urls = bvs[1:3]
    epi = bvs[3]
    infoList = bvs[4]
    cur_index = bvs[5]
    cid = infoList[cur_index][0]
    print("当前视频标题：", title)
    if epi:
        print("当前选集标题：", epi)
        fileDir = videoDir + epi + '/'
        filePath = videoDir + title + exts[0]   # 假如只要当前集
    else:
        page_title = infoList[cur_index][1]
        print("当前P的标题：", page_title)
        filePath = videoDir + title + '(P名：' + page_title + ')' + exts[0]   # 假如只要当前集
        if len(infoList) > 1:
            print("是分P。。。")
            fileDir = videoDir + title + '/'
        else:
            print("是单集。。。")
            # 如果是单集，理论上page名称就是视频标题，但是一些久远的视频并非如此，各有所名。所以需要判断
            if title == page_title:
                filePath = videoDir + title + exts[0]
            return await start(DownCoroutine(urls, cid, filePath))
    if input("仅下载当前这集吗？[y/n]").lower() in ("y", "yes"):
        return await start(DownCoroutine(urls, cid, filePath))
    print("下载全部选集/分集。。。")
    # 这里还可以添加选择框，让用户选择哪些要下载, 现在是全部下载
    # 启动任务
    filePath = fileDir + title + exts[0]
    coList = [DownCoroutine(urls, cid, filePath)]
    for i, tu in enumerate(infoList):
        if i == cur_index:
            continue
        filePath = fileDir + tu[1] + exts[0]
        coList.append(DownCoroutine(None, tu[0], filePath, tu[2]))
    return await start(asyncio.gather(*coList))


async def init():
    url = input("请输入视频链接：")
    matched = re.match(r'\s*(.*?(BV\w*)/?(?:\?p=(\d*))?)', url)
    url = matched.group(1)
    bvid = matched.group(2)
    page = matched.group(3)
    if page is not None:
        page = int(page)
    # 初始化clients
    uaNum = len(user_agents)
    for i in range(clientNum):
        session = await aiohttp.ClientSession().__aenter__()
        clients.append(Client(session))
        uaNum -= 1
    # 开始
    await main(url, bvid, page)
    # 收尾
    for c in clients:
        await c.session.__aexit__(None, None, None)


if __name__ == '__main__':
    asyncio.run(init())

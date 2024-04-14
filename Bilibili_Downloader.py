import re, json
import secrets
import os, shutil, bisect
import asyncio, aiohttp, aiofiles
import win32file, win32pipe, msvcrt
import subprocess, threading, pickle
import sys, time
from collections.abc import Awaitable


# 5个用户端
ClientNum = 5
# 填入你的SESSDATA
MySESSDATA = 'to_fill'
PipeName = r'\\.\pipe\show_pipe2'

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

clients = []
clients: list[Client]
semaphore = asyncio.Semaphore(ClientNum)

ChunkSize = 1024 * 30

# 创建命名管道
ph_write = None

def send_data(data):
    global ph_write
    win32file.WriteFile(ph_write, len(data).to_bytes(2, byteorder='little') + data)


amountDict = {}

threadAlive = True
def amountDictSendThread():
    interval = 0.1  # 发送的间隔
    cur_time = time.time()
    while threadAlive:
        send_data(pickle.dumps(amountDict))
        next_time = cur_time + interval
        cur_time = time.time()
        sleep_time = next_time - cur_time
        if sleep_time > 0:
            time.sleep(sleep_time)
            cur_time = next_time

def displayProcess(pf_read):
    # infoList: [(cid, file_name, total_amount: int, unit, annotation), ...]
    # amountDict: {cid: current_amount: int, ...}

    # refacting: {cid: (file_name, total_amount, unit, annotation)|cur_amount, ...}
    # need: cid, (file_name, total_amount, unit, annotation)|cur_amount
    # data_format: frame_length:2, (file_name, total_amount, unit, annotation)(and cid:int4)|amountDict|Done(bool:pickle, and cid:int4):pickle

    fh = msvcrt.get_osfhandle(pf_read.fileno())
    interval = 0.1  # 刷新的间隔
    window_length = 5   # 统计3秒内的内容
    infoDict = {}
    amountDictIs = [[{}, interval]] * int(window_length / interval)
    cur_time = time.time()
    while True:
        # 获取管道所有更新
        while win32pipe.PeekNamedPipe(fh, 0)[1] != 0:  # 有东西才读
            frame_length = int.from_bytes(pf_read.read(2), byteorder='little')
            reads = pf_read.read(frame_length)
            stuff = pickle.loads(reads)
            hisType = type(stuff)
            if hisType is tuple:
                cid = int.from_bytes(reads[-4:], byteorder='little')
                infoDict[cid] = stuff
                for di in amountDictIs:
                    di[0][cid] = 0
            elif hisType is dict:
                amountDictIs[0][0] = stuff
            else:
                cid = int.from_bytes(reads[-4:], byteorder='little')
                if cid in infoDict:
                    del infoDict[cid]
        # 计算窗口内时间
        delta_time = 0
        for i, di in enumerate(amountDictIs):
            delta_time += di[1]
            if delta_time >= window_length:
                prev_amountDict = amountDictIs.pop(i - 1 if i > 0 else 0)[0]
                break
        else:
            prev_amountDict = amountDictIs.pop()[0]
        cur_amountDict = amountDictIs[0][0]
        # 清空上一次的输出内容，比cls快
        print("\033[H\033[J", end='')
        #显示
        for n, (cid, (file_name, total_amount, unit, annotation)) in enumerate(infoDict.items(), 1):
            # 获取所需信息并计算速度
            if cid in cur_amountDict:
                cur_amount = cur_amountDict[cid]
                if cid in prev_amountDict:
                    prev_amount = prev_amountDict[cid]
                    speed = (cur_amount - prev_amount) / delta_time
                else:
                    speed = cur_amount / delta_time
            else:
                cur_amount = 0
                speed = 0
            percentage = cur_amount / total_amount * 100
            print(f'[{n}]:', file_name, '---> (')
            print('    [%-50s] %.2f%%\t%s/s\t%s/%s'%(
                '█' * int(percentage / 2),
                percentage,
                format_num(speed) + unit,
                format_num(cur_amount) + unit,
                format_num(total_amount) + unit
            ))
            print('  )', annotation)
        # # mean to delay some...
        # time.sleep(0.5)
        #休息时间
        prev_time = cur_time
        next_time = prev_time + interval
        cur_time = time.time()
        sleep_time = next_time - cur_time
        if sleep_time > 0:
            time.sleep(sleep_time)
            cur_time = next_time
        else:   # 万一前面产生了过长的卡顿
            amountDictIs[0][1] = cur_time - prev_time
        amountDictIs.insert(0, [amountDictIs[0][0].copy(), interval])


def format_num(num: int) -> str:    # 格式化为合适的数值大小与部分单位，完整单位后面加
    i = 0
    while num > 1024 and i < 9 - 1:
        num /= 1024
        i += 1
    unit = ('', 'ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi')[i]
    return "%.2f" % num + unit





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
        # 还要检查上次下载的分片，并合并未经合并的
        fragsDict = self.arrange_fragments()
        # 下载视频与音频
        for i in range(2):
            existingFrags = None
            ext = exts[i]
            if ext in fragsDict:
                existingFrags = fragsDict[ext]
            # 开始下载
            if self.urls[i] is None:
                print("debugging")
            if not await self._download1(ext, self.types[i], self.urls[i], existingFrags):
                self.end()
                return False
        # 合并下载的所有碎片，并合并最终视频
        send_data(pickle.dumps((self.fileName, 1, '', "正在合并下载碎片..."))
                  + int.to_bytes(self.cid, 4, byteorder='little'))
        fragsDict = self.arrange_fragments()
        if exts[0] not in fragsDict or exts[1] not in fragsDict:
            print(self.fileName, "合并下载碎片未得！", sep='')
            self.end()
            return False
        vFrags = fragsDict[exts[0]]
        aFrags = fragsDict[exts[1]]
        assert len(vFrags) == 1 and len(aFrags) == 1
        # 合并视音频
        send_data(pickle.dumps((self.fileName, 1, '', "正在合并视音频..."))
                  + int.to_bytes(self.cid, 4, byteorder='little'))
        if not self.mergeVA(vFrags[0], aFrags[0]):
            print(self.fileName, "合并视音频失败！")
            self.end()
            return False
        # 清理缓存
        send_data(pickle.dumps((self.fileName, 1, '', "正在清理缓存..."))
                  + int.to_bytes(self.cid, 4, byteorder='little'))
        shutil.rmtree(self.tempDir)
        self.end()
        return True


    async def _download1(self, ext, what, url, frags) -> bool:
        # 已经下载了的碎片：
        # fragments: [[start1, end1], [start2, end2], ...]
        # i: 0视频, 1音频
        # 获取大小
        send_data(pickle.dumps((self.fileName, 1, '', "正在获取" + what + "部分的大小..."))
                  + int.to_bytes(self.cid, 4, byteorder='little'))
        size = await self.get_size(url)
        if size == -1:
            print(self.fileName, "获取", what, "部分的大小失败！", sep='')
            return False
        # 检查是否并无已有的分片文件
        final_end = size - 1
        undoneRangesList = []
        if frags is None:
            undoneRangesList.append((0, final_end))
        else:
            # 检查是否已有全部的数据
            if frags[0][0] == 0 and frags[0][1] == final_end:
                print(self.fileName, "的", what, "部分已有了！", sep='')
                return True
            # 获得未有的范围
            for r1, r2 in zip(frags, frags[1:]):
                undoneRangesList.append((r1[1] + 1, r2[0] - 1))
            else:
                final_start = frags.pop()[1] + 1
                if final_start <= final_end:
                    undoneRangesList.append((final_start, final_end))
        # 开始下载
        send_data(pickle.dumps((self.fileName, size, 'B', "正在下载" + what + "部分..."))
                  + int.to_bytes(self.cid, 4, byteorder='little'))
        amountDict[self.cid] = 0
        if not await self._download2(url, ext, undoneRangesList):
            print(self.fileName, "下载", what, "部分失败！", sep='')
            return False
        del amountDict[self.cid]
        return True


    async def _download2(self, url, ext, undoneRangesList: list[tuple]):
        # 按剩余的clients数量，分成多个部分，分别下载
        # 信号量和剩余用户端数有可能不一样，用户端可能释放了还没有被用，但信号量却是瞬间分配的
        ## 以上是以前的注释
        # 排序
        undoneRangesList.sort(key=lambda r: r[0] - r[1])   # 最小的在后
        # 获取总下载大小
        size = 0
        for r in undoneRangesList:
            size += r[1] - r[0] + 1
        # 获取客户端数量
        await semaphore.acquire()   # 至少要一个
        semaphore._value += 1   # 只能这样，release会瞬间分配出去
        clientsNum = semaphore._value
        # 分配任务
        quotient = size // clientsNum
        remainder = size % clientsNum
        coList = []
        for i in range(clientsNum):
            toDownSize = quotient
            if remainder:
                toDownSize += 1
                remainder -= 1
            toDownRanges = []
            while True:
                minTask = undoneRangesList.pop()
                s1 = minTask[0]
                e1 = minTask[1]
                e2 = s1 + toDownSize - 1
                if e2 <= e1:
                    toDownRanges.append((s1, e2))
                    if e2 < e1:
                        undoneRangesList.append((e2 + 1, e1))
                    break
                toDownRanges.append((s1, e1))
                toDownSize -= e1 - s1 + 1
            coList.append(self.downRanges(url, ext, toDownRanges))
        # return True: all succeeded
        return all(await asyncio.gather(*coList))
        # st1 = 0
        # for i in range(clientsNum):
        #     next_start = st1 + _quotient
        #     if _remainder:
        #         next_start += 1
        #         _remainder -= 1
        #     coList.append(self.downRange(url, st1, next_start - 1, ext))  # 经测试，pop()运行快于[0]
        #     st1 = next_start
        # return True: all succeeded
        # return all(await asyncio.gather(*coList))
        # coList = []
        # while len(undoneRangesList):
        #     minTast = undoneRangesList.pop(0)
        #     start = minTast[0]
        #     end = minTast[1]
        #     coDownOffset = end - start
        #     if coDownOffset >= ChunkSize:
        #         undoneRangesList.insert(0, minTast)
        #         coList.extend(await self.tryToAllocateTasks(
        #             clientsNum, coDownOffset, undoneRangesList, url, ext))
        #         break
        #     coList.append(self.downRange(url, start, end, ext))
        #     clientsNum -= 1
        #     if clientsNum == 0:
        #         if not all(await asyncio.gather(*coList)):
        #             return False
        #         del coList[:]
        #         await semaphore.acquire()  # 至少要一个
        #         semaphore._value += 1
        #         clientsNum = semaphore._value
        # return all(await asyncio.gather(*coList))


    # async def tryToAllocateTasks(self, clientsNum, coDownOffset, undoneRangesList, url, ext):
    #     _clientsNum = clientsNum
    #     _coList = []
    #     fatal = False
    #     while True:
    #         for i, (s2, e2) in enumerate(undoneRangesList):
    #             next_end = s2 + coDownOffset
    #             while next_end <= e2:
    #                 _coList.append(self.downRange(url, s2, next_end, ext))
    #                 s2 = next_end + 1
    #                 next_end = s2 + coDownOffset
    #                 _clientsNum -= 1
    #                 if _clientsNum == 0:
    #                     del undoneRangesList[:i + 1]
    #                     undoneRangesList.append((s2, e2))
    #                     return _coList
    #             if s2 <= e2:
    #                 _coList.append(self.downRange(url, s2, e2, ext))
    #                 _clientsNum -= 1
    #                 if _clientsNum == 0:
    #                     del undoneRangesList[:i + 1]
    #                     return _coList
    #         # 分配失败，还有剩的client
    #         if fatal:
    #             return _coList
    #         _clientsNum = clientsNum
    #         del _coList[:]
    #         coDownOffset >>= 1  # 除以2
    #         # 如果实在不行
    #         if coDownOffset < ChunkSize:
    #             # 最后 ChunkSize最小量再试分一次任务
    #             coDownOffset = ChunkSize
    #             fatal = True


    async def downRanges(self, url, ext, undoneRangesList: list[tuple]) -> bool:
        # [start, end] (including the end...)
        # 要检查当前块是不是也下载了（——目前还不是很完善，因为命名会有区别的）
        # 命名的话，还是就start-end.ext就行了，不要自己命名
        # 开始下载对应内容
        async with semaphore:
            with clients.pop() as client:   # 经测试，pop()运行快于[0]
                for s, e in undoneRangesList:
                    rangePath = self.tempDir + f'{s}-{e}' + ext
                    headers = {
                        'Range': f'bytes={s}-{e}',
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
                                    chunk = await resp.content.read(ChunkSize)
                                    if not chunk:
                                        return True
                                    amountDict[self.cid] += len(chunk)
                                    await f.write(chunk)
                    if not await self.enretryable(real_part, client):
                        what = self.types[exts.index(ext)] # 少进，所以单独索引
                        print(self.fileName, "的", what, "部分下载范围", s, "-", e, "的内容失败", sep='')
                        return False
                # 成功后重置一下client再归还
                await client.reset()    # 目前来看，获取源码->获取大小->获取文件是一个很连续的过程，只应该在最后才重置
                return True


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
                    if url is None:
                        print('debugging')
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
            except (aiohttp.ClientPayloadError, aiohttp.ClientConnectorError,
                    asyncio.exceptions.TimeoutError, aiohttp.client_exceptions.ServerDisconnectedError) as e:
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


    def truncate(self, ext, source_frag: tuple[int], target_start: int):
        # 从文件中间截取到末尾
        source_start = source_frag[0]
        source_end = source_frag[1]
        name = self.tempDir + f'{source_start}-{source_end}' + ext
        with (open(name, 'rb') as fi,
              open(name, 'rb+') as fo):
            fi.seek(target_start - source_start)
            fo.write(fi.read())
            fo.truncate()
        os.rename(name, f'{target_start}-{source_end}' + ext)


    def arrange_fragments(self) -> dict[str, list[list[int]]]:
        # 检查并整理、合并缓存目录下的所有同后缀分片文件
        # 遍历碎片文件并初步排序
        # {ext:[[start1:int, end1:int], [start2, end2], ...]], ...}
        extFragsDict = {}
        for root, dirs, files in os.walk(self.tempDir):
            if dirs:
                continue
            for f in files:
                if '-' not in f:
                    continue
                # 这里一定是0级目录的分片文件
                # 取出有关信息
                extPos = f.index('.')
                ext = f[extPos:]
                splitted = f[:extPos].split('-', 1)
                start = int(splitted[0])
                end = int(splitted[1])
                # 按实际大小更正end
                actualSize = os.path.getsize(self.tempDir + f)
                if actualSize == 0:
                    os.remove(self.tempDir + f)
                    continue
                theoretical_end = start + actualSize - 1
                if end != theoretical_end:
                    assert end > theoretical_end
                    end = theoretical_end
                    os.rename(self.tempDir + f, self.tempDir + f"{start}-{end}" + ext)
                if ext in extFragsDict:
                    bisect.insort(extFragsDict[ext], [start, end], key=lambda r:r[0])
                else:
                    extFragsDict[ext] = [[start, end]]
        # 找出相连的碎片文件并最终合并
        for ext, frags in extFragsDict.items():
            # seqFragsList: [[AStart1, AStart2, ..., AEnd], [BStart1, B...], ...]
            seqFragsList = [frags.pop(0)]
            for f in frags:
                seq = seqFragsList.pop()
                start1 = f[0]
                end1 = f[1]
                end2 = seq[-1]
                # 不可能 start1 < start2
                if start1 < end2 + 2:  # start1 ~ [start2, end2 + 1]
                    if end1 <= end2:
                        os.remove(self.tempDir + f'{start1}-{end1}' + ext)  # 没有用直接删掉
                        seqFragsList.append(seq)
                        continue
                    # end1 ~ [end2 + 1, ...]
                    if start1 <= end2:  # start1 != end2 + 1
                        self.truncate(ext, f, end2 + 1)
                    seq[-1] += 1
                    seq.append(end1)
                    seqFragsList.append(seq)
                else:
                    seqFragsList.append(seq)
                    seqFragsList.append(f)
            # 合并，并精简范围
            for seq in seqFragsList:
                if len(seq) == 2:   # 不用合并
                    continue
                seq[-1] += 1
                source_frags = '+'.join('"' + self.tempDir + f'{start1}-{start2-1}' + ext + '"'
                                        for start1, start2 in zip(seq, seq[1:]))
                if os.system('copy /y /b %s "%s">nul'%(
                    source_frags,
                    self.tempDir + f'{seq[0]}-{seq[-1] - 1}' + ext)
                             ) != 0:
                    print(self.fileName, "的", ext, "部分在范围", seq[0], '-', seq[-1] - 1, "合并分片失败！(cid: ", self.cid, ")", sep='')
                    continue
                # 删除已合并的碎片
                for start1, start2 in zip(seq, seq[1:]):
                    os.remove(self.tempDir + f'{start1}-{start2-1}' + ext)
                del seq[1:-1]   # 此后应该只有2个元素
                seq[1] -= 1
            # 放入经合并的现存碎片字典
            extFragsDict[ext] = seqFragsList
        # ret: {ext: [[start1, end1], [start2, end2], ...], ext':...}
        return extFragsDict


    def mergeVA(self, vFrag, aFrag) -> bool:
        # return 0: succeeded
        return os.system('.\\tools\\ffmpeg.exe -v quiet -i "%s%s-%s%s" -i "%s%s-%s%s" -c:v copy -c:a copy "%s"'%(
            self.tempDir, vFrag[0], vFrag[1], exts[0],
            self.tempDir, aFrag[0], aFrag[1], exts[1],
            self.filePath
        )) == 0


async def get_source_code(url) -> str:
    text = ''
    async with semaphore:
        with clients.pop() as client:
            headers = {
                'Referer': client.referer,
                "user-agent": client.userAgent,
                "Cookie": f"SESSDATA={MySESSDATA}"
            }
            async def real_part() -> bool:
                nonlocal text
                async with client.session.get(url, headers=headers) as resp:
                    text = await resp.text()
                    return True
            await DownCoroutine.enretryable(real_part, client)
    return text


wanted_height = -1
wanted_frameRate = -1
wanted_codecs = "av01"     # 写死codecs，后面用配置文件设置
def get_vurl(source_code):  # 要获取清晰度最高的视频链接
    playinfo = json.loads(re.search(r'<script>\s*window.__playinfo__\s*=\s*(\{\s*.*?\s*\})\s*</script>',
                                    source_code, re.S).group(1))
    videos = {}
    for video in playinfo["data"]["dash"]["video"]:
        height = video['height']
        data = (int(video['frameRate'].split('.', 1)[0]), video['codecs'], video['baseUrl'], video['backupUrl'])
        if height in videos:
            bisect.insort(videos[height], data, key=lambda e: -e[0])
        else:
            videos[height] = [data]
    videos = list(videos.items())

    global wanted_height, wanted_frameRate
    if wanted_height == -1:
        # 获取用户要的清晰度
        # 得先排序清晰度
        videos.sort(key=lambda e: -e[0])
        print("-"*40)
        print("现在有这些清晰度：")
        n = 1
        choseList = []
        for height, datas in videos:
            prevFR = -1
            for data in datas:
                frameRate = data[0]
                if frameRate == prevFR:
                    continue
                choseList.append((height, frameRate))
                print(n, '. ', height, sep='', end='')
                if frameRate != 30:
                    print(" ", frameRate, "帧", end='')
                print()
                n += 1
                prevFR = frameRate
        wanted_n = input("请输入想要的清晰度（默认第一个）:")
        try:    wanted_index = int(wanted_n) - 1
        except ValueError:  wanted_index = 0
        wanted_height, wanted_frameRate = choseList[wanted_index]
        print("选择了清晰度", wanted_height, end='')
        if wanted_frameRate != 30:
            print(" ", wanted_frameRate, "帧", end='')
        print("...（后续视频也将采取此清晰度）")
        print('-'*40)

    for height, datas in videos:    # 直接选，可以不排序
        if height != wanted_height:
            continue
        for frameRate, codecs, baseUrl, backupUrls in datas:
            if frameRate != wanted_frameRate:
                continue
            if not codecs.startswith(wanted_codecs):
                continue
            # vurls.append(baseUrl)
            # vurls.extend(backupUrls)
            if baseUrl is None:
                print('debugging')
            return baseUrl  # 先只要一个baseUrl试试水
        else:
            print("当前所下视频不是或者没有选择清晰度时作为范例所选择的帧率或编码格式。现在选择清晰度和帧率最高的版本下载，即按照原方法进行")
            return old_method(source_code)
    else:
        print("当前所下视频不是或者没有选择清晰度时作为范例所选择的清晰度。现在选择清晰度和帧率最高的版本下载，即按照原方法进行")
        return old_method(source_code)
    print("unexpected")
# 原代码：
    # video_id = re.search(r'"video":\s*\[\{\s*"id":\s*(\d+?),', source_code).group(1)
    # p = re.compile(r'"id":\s*%s,\s*"baseUrl":\s*"(.*?)",' % video_id)
    # return p.findall(source_code)[-1]  # 下载最后一个AV1格式的视频，压缩率最高
# 不知道为什么，HEVC的下载速度比AV1慢很多

def old_method(source_code):
    video_id = re.search(r'"video":\s*\[\{\s*"id":\s*(\d+?),', source_code).group(1)
    p = re.compile(r'"id":\s*%s,\s*"baseUrl":\s*"(.*?)",' % video_id)
    return p.findall(source_code)[-1]  # 下载最后一个AV1格式的视频，压缩率最高

def get_aurl(source_code):
    return re.search(r'"audio":\[\{"id":\d+?,"baseUrl":"(.*?)"', source_code).group(1)  # 第一个就行，音质最高


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
    global ph_write, amountDict, threadAlive
    t = time.time()
    ph_write = win32pipe.CreateNamedPipe(
        PipeName,
        win32pipe.PIPE_ACCESS_OUTBOUND,
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
        1, 65536, 65536,
        300,
        None
    )
    displayProcess = subprocess.Popen((sys.executable, __file__, '-c'),
        creationflags=subprocess.CREATE_NEW_CONSOLE)
    print("等待客户端连接...")
    win32pipe.ConnectNamedPipe(ph_write, None)
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
    win32file.CloseHandle(ph_write)
    print("下载", "完毕" if ret else "失败", "！", sep='')
    print("总用时：", time.time() - t, "s", sep='')
    return ret


async def main(url, bvid, page: int):
    # os.system("chcp 65001")  # 更改控制台系统输出字符为utf-8
    videoDir = "./downloaded_videos/"  # 视频保存路径
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
    coList = []
    for n, (cid, title, url) in enumerate(infoList, 1):
        filePath = fileDir + f'{n}. ' + title + exts[0]
        coList.append(DownCoroutine(None, cid, filePath, url))
    coList.insert(0, coList.pop(cur_index)) # 把当前视频提到第一个位置来做
    return await start(asyncio.gather(*coList))


async def init():
    # url = input("请输入视频链接：")
    url = 'https://www.bilibili.com/video/BV1Eu411i7ae/?spm_id_from=333.788.recommend_more_video.1&vd_source=9647e28a3485a753b81965ea1843a398'
    matched = re.match(r'\s*(.*?(BV\w*)/?(?:\?p=(\d*))?)', url)
    url = matched.group(1)
    bvid = matched.group(2)
    page = matched.group(3)
    if page is not None:
        page = int(page)
    # 初始化clients
    uaNum = len(user_agents)
    for i in range(ClientNum):
        session = await aiohttp.ClientSession().__aenter__()
        clients.append(Client(session))
        uaNum -= 1
    # 开始
    await main(url, bvid, page)
    # 收尾
    for c in clients:
        await c.session.__aexit__(None, None, None)


if __name__ == '__main__':
    if '-c' in sys.argv:
        # 子进程
        with open(PipeName, "rb") as pf_read:  # 打开读取端的句柄
            displayProcess(pf_read)
    else:
        #父进程
        asyncio.run(init())

import msvcrt, os, time, win32pipe, pickle


def displayProcess(pfd):
    # infoList: [(cid, file_name, total_amount: int, unit, annotation), ...]
    # amountDict: {cid: current_amount: int, ...}

    # refacting: {cid: (file_name, total_amount, unit, annotation)|cur_amount, ...}
    # need: cid, (file_name, total_amount, unit, annotation)|cur_amount
    # data_format: frame_length:2, (file_name, total_amount, unit, annotation)(and cid:int4)|amountDict|Done(bool:pickle, and cid:int4):pickle

    fh = msvcrt.get_osfhandle(pfd.fileno())
    interval = 0.1  # 刷新的间隔
    window_length = 5   # 统计3秒内的内容
    infoDict = {}
    amountDictIs = [[{}, interval]] * int(window_length / interval)
    cur_time = time.time()
    while True:
        # 获取管道所有更新
        while win32pipe.PeekNamedPipe(fh, 0)[1] != 0:  # 有东西才读
            frame_length = int.from_bytes(pfd.read(2), byteorder='little')
            reads = pfd.read(frame_length)
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


# 需提前创建管道
with open(r'\\.\pipe\show_pipe', "rb") as pfd:
    displayProcess(pfd)
    os.system('pause')



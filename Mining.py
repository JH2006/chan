# 2016-6-10
# 结果数据分析模块

# 第三方模块
import pandas as pd

# 系统模块
import threading

#自定义模块
import Hunter
import Currency
import Strategy

# 操作类继承了Python多线程管理.相当于每个月的操作都是一个独立线程
# 目前的实现对每套线程都有自己完全独立的数据,暂时不会涉及到Lock的问题
class Executor(threading.Thread):

    def __init__(self, market, year, month, transRecoder, lock, q):

        threading.Thread.__init__(self)

        self._market = market
        self._year = year
        self._month = month

        self._candles = Currency.Markets.candelOfMarket(self._market)

        self._types = Hunter.Type_Container(self._candles)

        self._pens = Hunter.Pen_Container(self._types)

        self._bucket = Strategy.Ten_Min_Bucket(self._candles)

        self._hubs = Hunter.Ten_Min_Hub_Container(self._pens, self._bucket)

        self._bucket.loadHubs(self._hubs)

        self._trans = Hunter.Tran_Container()

        self._bucket.loadTrans(self._trans)

        self._transRecorder = transRecoder

        self._lock = lock

        self._q = q

    def run(self):

        self._candles.loadDB(self._year, self._month, 0, 0, self._types, self._pens, self._hubs)

        self._candles.closeDB()

        self._lock.acquire()

        self._transRecorder[self._month] = self._trans

        self._q.get()

        self._lock.release()

    def __del__(self):

        self._trans.reset()

        self._hubs.reset()
        self._pens.reset()
        self._types.reset()
        self._candles.reset()


class Hub_Mining:

    def __init__(self, hubs, candles):

        self._hubs = hubs
        self._candles = candles

        self._preHub = None
        self._curHub = None
        self._postHub = None

        # 信息队列
        self._pack_pens = []
        self._pack_start_time = []
        self._pack_end_time = []
        self._pack_pos = []
        self._pack_trend = []
        self._pack_pre_lap = []
        self._pack_post_lap = []
        self._pack_entry_M = []
        self._pack_exit_M = []
        self._pack_entry_C = []
        self._pack_exit_C = []
        self._pack_num_candle = []
        self._pack_entry_Gap = []
        self._pack_exit_Gap = []

    def mining(self):

        for i, hub in enumerate(self._hubs.container):

            self._preHub = self._curHub
            self._curHub = hub

            try:

                self._postHub = self._hubs.container[i+1]

            except:

                self._postHub = None
                print('mining()--self._hubs.container over bounder')

            pens = self._curHub.numOfPens()

            # 中枢笔数
            self._pack_pens.append(pens)

            # 时间
            start_date = pd.Timestamp(pd.datetime(self._curHub.s_pen.beginType.candle.getYear(),
                                              self._curHub.s_pen.beginType.candle.getMonth(),
                                              self._curHub.s_pen.beginType.candle.getDay(),
                                              self._curHub.s_pen.beginType.candle.getHour(),
                                              self._curHub.s_pen.beginType.candle.get10Mins())).strftime('%Y-%m-%d %H:%M:%S')


            end_date = pd.Timestamp(pd.datetime(self._curHub.e_pen.endType.candle.getYear(),
                                            self._curHub.e_pen.endType.candle.getMonth(),
                                            self._curHub.e_pen.endType.candle.getDay(),
                                            self._curHub.e_pen.endType.candle.getHour(),
                                            self._curHub.e_pen.endType.candle.get10Mins())).strftime('%Y-%m-%d %H:%M:%S')

            self._pack_start_time.append(start_date)
            self._pack_end_time.append(end_date)

            # 中枢类别
            self.trend()

            # 是否与前中枢有重叠
            self.preOverlap()

            # 是否与后中枢有重叠
            self.postOverlap()

            # 中枢方向
            self._pack_pos.append(self._curHub.pos)

            # MACD
            self.entryMACD()
            self.exitMACD()

            # 中枢所包含K线数量
            self._pack_num_candle.append(self._curHub.e_pen.endType.candle_index - self._curHub.s_pen.beginType.candle_index + 1)

            #空间差
            self.entryGap()
            self.exitGap()


    def trend(self):

        try:

            if self._curHub.pos == self._preHub.pos:

                self._pack_trend.append(1)

            else:

                self._pack_trend.append(0)

        except:

            self._pack_trend.append(-100)

            print('trend()--self._preHub is None')

    def preOverlap(self):

        if self._curHub.pos == 'Up':

            try:

                if self._preHub.GG > self._curHub.ZD:

                    self._pack_pre_lap.append(1)

                else:

                    self._pack_pre_lap.append(0)

            except:

                self._pack_pre_lap.append(-100)

                print('preoverlap()--self._preHub is None')

        elif self._curHub.pos == 'Down':

            try:

                if self._preHub.DD < self._curHub.ZG:

                    self._pack_pre_lap.append(1)

                else:

                    self._pack_pre_lap.append(0)

            except:

                self._pack_pre_lap.append(-100)

                print('preOverlap()--self._preHub is None')

        else:

            self._pack_pre_lap.append(-100)

    def postOverlap(self):

        try:

            if self._postHub.pos == 'Up':

                if self._curHub.GG > self._postHub.ZD:

                    self._pack_post_lap.append(1)

                else:

                    self._pack_post_lap.append(0)

            elif self._postHub.pos == 'Down':

                if self._curHub.DD < self._postHub.ZG:

                    self._pack_post_lap.append(1)

                else:

                    self._pack_post_lap.append(0)

        except:

            self._pack_post_lap.append(-100)

            print('postOverlap()--self._postHub is None')


    # MACD计算的起点为上一中枢最后一笔的起点
    # 计算MACD阴影的结束K线位
    # 本中枢的第一笔低于中枢低点的K线
    def entryMACD(self):

        # 结束K线位置
        e_candle_index = 0

        MACD = 0

        try:
            start_pen = self._preHub.e_pen

            end_pen = self._curHub.s_pen

            if self._curHub.pos == 'Up':

                s_candle_index = start_pen.beginType.candle_index

                for j in range(end_pen.beginType.candle_index, end_pen.endType.candle_index + 1):

                    if self._candles.container[j].getLow() <= self._curHub.ZD:

                        e_candle_index = j

                        break

                # 趋势向上的时候,仅考察MACD为正的部分
                for t in range(s_candle_index, e_candle_index + 1):

                    if self._candles.container[t].MACD.getMACD() > 0:

                        MACD += self._candles.container[t].MACD.getMACD()

            else:

                s_candle_index = start_pen.beginType.candle_index

                # 计算MACD阴影的结束K线位
                for j in range(end_pen.beginType.candle_index, end_pen.endType.candle_index + 1):

                    if self._candles.container[j].getHigh() >= self._curHub.ZG:

                        e_candle_index = j

                        break

                # 趋势向上的时候,仅考察MACD为负的部分
                for t in range(s_candle_index, e_candle_index + 1):

                    if self._candles.container[t].MACD.getMACD() < 0:

                        MACD += self._candles.container[t].MACD.getMACD()

            self._pack_entry_M.append(MACD)

            self._pack_entry_C.append(e_candle_index - s_candle_index + 1)

        except:

            self._pack_entry_M.append(-100)
            self._pack_entry_C.append(-100)

            print('entryMACD()--self._preHub is None')


    def exitMACD(self):

        # 结束K线位置
        e_candle_index = 0

        MACD = 0

        try:
            start_pen = self._curHub.e_pen

            end_pen = self._postHub.s_pen

            if self._postHub.pos == 'Up':

                s_candle_index = start_pen.beginType.candle_index

                # 计算MACD阴影的结束K线位
                for j in range(end_pen.beginType.candle_index, end_pen.endType.candle_index + 1):

                    if self._candles.container[j].getLow() <= self._postHub.ZD:

                        e_candle_index = j

                        break

                # 趋势向上的时候,仅考察MACD为正的部分
                for t in range(s_candle_index, e_candle_index + 1):

                    if self._candles.container[t].MACD.getMACD() > 0:

                        MACD += self._candles.container[t].MACD.getMACD()

            else:

                s_candle_index = start_pen.beginType.candle_index

                # 计算MACD阴影的结束K线位
                for j in range(end_pen.beginType.candle_index, end_pen.endType.candle_index + 1):

                    if self._candles.container[j].getHigh() >= self._postHub.ZG:

                        e_candle_index = j

                        break

                # 趋势向上的时候,仅考察MACD为负的部分
                for t in range(s_candle_index, e_candle_index + 1):

                    if self._candles.container[t].MACD.getMACD() < 0:

                        MACD += self._candles.container[t].MACD.getMACD()

            self._pack_exit_M.append(MACD)

            self._pack_exit_C.append(e_candle_index - s_candle_index + 1)

            """
            pack['exitPriceGap'] = abs(self._candles.container[e_candle_index].getClose() - \
                                    self._candles.container[s_candle_index].getClose())
            """

        except:

            self._pack_exit_M.append(-100)
            self._pack_exit_C.append(-100)

            print('eixtMACD()--self._postHub is None')

    def entryGap(self):

        try:

            if self._curHub.pos == 'Up':

                self._pack_entry_Gap.append(self._curHub.ZD - self._preHub.ZG)

            else:

                self._pack_entry_Gap.append(self._preHub.ZD - self._curHub.ZG)

        except:

            self._pack_entry_Gap.append(-100)

            print('entryGap()--self._preHub is None')

    def exitGap(self):

        try:

            if self._postHub.pos == 'Up':

                self._pack_exit_Gap.append(self._postHub.ZD - self._curHub.ZG)

            else:

                self._pack_exit_Gap.append(self._curHub.ZD - self._postHub.ZG)

        except:

            self._pack_exit_Gap.append(-100)

            print('entryGap()--self._postHub is None')

    def save(self, fileName):

        writer = pd.ExcelWriter(fileName, engine='xlsxwriter')

        d = {'中枢笔数': self._pack_pens,
             '起始时间': self._pack_start_time,
             '结束时间': self._pack_end_time,
             '趋势延续': self._pack_trend,
             '前中枢有重叠': self._pack_pre_lap,
             '后中枢有重叠': self._pack_post_lap,
             '中枢方向': self._pack_pos,
             '进入段 MACD': self._pack_entry_M,
             '走出段 MACD': self._pack_exit_M,
             '进入段candlestick数量': self._pack_entry_C,
             '走出段candlestick数量': self._pack_exit_C,
             '中枢长度': self._pack_num_candle,
             '进入段价差': self._pack_entry_Gap,
             '走出段价差': self._pack_exit_Gap}

        df = pd.DataFrame(d)

        df.to_excel(writer)

        writer.close()
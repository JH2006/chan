# 2016-4-5
# 核心策略模块

# 系统模块
import copy
import math

# 第三方模块
from pymongo import MongoClient
import pandas as pd
from time import sleep

# 自定义模块
import MACD
import Event

class Candle:
    def __init__(self, year, month, day, open, close, high, low):
        self.__year = year
        self.__month = month
        self.__day = day
        self.__open = open
        self.__close = close
        self.__high = high
        self.__low = low

    def setPos(self, pos):
        self.__pos = pos

    def getPos(self):
        return self.__pos

    def getYear(self):
        return self.__year

    def getMonth(self):
        return self.__month

    def getDay(self):
        return self.__day

    def getOpen(self):
        return self.__open

    def getClose(self):
        return self.__close

    def getHigh(self):
        return self.__high

    def setHigh(self, high):
        self.__high = high

    def getLow(self):
        return self.__low

    def setLow(self, low):
        self.__low = low


class Hour_Candle(Candle):
    def __init__(self, year, month, day, hour, open, close, high, low):
        Candle.__init__(self, year, month, day, open, close, high, low)

        self.__hour = hour

    def getHour(self):
        return self.__hour


class Ten_Min_Candle(Hour_Candle):
    def __init__(self, year, month, day, hour, min_10, open, close, high, low):
        Hour_Candle.__init__(self, year, month, day, hour, open, close, high, low)

        self.__10min = min_10

    def get10Mins(self):
        return self.__10min


class Five_Min_Candle(Ten_Min_Candle):
    def __init__(self, year, month, day, hour, min_10, min_5, open, close, high, low):
        Ten_Min_Candle.__init__(self, year, month, day, hour, min_10, open, close, high, low)

        self.__5min = min_5

    def get5Mins(self):
        return self.__5min


class One_Min_Candle(Five_Min_Candle):
    def __init__(self, year, month, day, hour, min_10, min_5, min_1, open, close, high, low):
        Five_Min_Candle.__init__(self, year, month, day, hour, min_10, min_5, open, close, high, low)

        self.__1min = min_1

    def getMin(self):
        return self.__1min


class Connector:
    client = MongoClient()

    mongodb = client.AUD_trading

    @staticmethod
    def quary():

        print(Connector.mongodb.collection_names())

    @staticmethod
    def dump_mongoDB():

        coll = Connector.mongodb.CAD10m

        e_1 = pd.read_csv('ccon5094@uni.sydney.edu.au-CAD10m-N118276288.csv')

        print('len:', len(e_1))

        count = 0
        i = 1

        for row in range(0, len(e_1)):

            count += 1

            if count > 10000 * i:
                print(count)

                i += 1

            date_1 = pd.to_datetime(e_1['Date[G]'][row])

            time_1 = pd.to_datetime(e_1['Time[G]'][row])
            open_h = e_1['Open'][row]
            high_h = e_1['High'][row]
            low_h = e_1['Low'][row]
            close_1 = e_1['Last'][row]

            result = coll.insert_one(
                {
                    'Year': date_1.year,
                    'Month': date_1.month,
                    'Day': date_1.day,
                    'Hour': time_1.hour,
                    'Min_10': math.floor(time_1.minute / 10) * 10,
                    'Min_5': math.floor((time_1.minute - math.floor(time_1.minute / 10) * 10) / 5) * 5,
                    'Min_1': time_1.minute % 5,
                    'Open': open_h,
                    'High': high_h,
                    'Low': low_h,
                    'Close': close_1
                }
            )

        print(coll.count({}))

    def closeDB(self):

        self.client.close()

"""
Candle_Container
"""
class Candle_Container:
    def __init__(self):

        self._c = Connector()

        self.container = []

        self.__bucket = ''

    def __del__(self):

        self.container = []

        self._c.closeDB()

    def reset(self):

        self.container = []

    def contains(self):

        if self.size() == 2:

            # 通过最开始两根K线的关系进行包含方向的初始化
            f_k = self.container[0]
            s_k = self.container[1]

            pos = 'Up'

            # 无包含向下处理
            if f_k.getHigh() > s_k.getHigh() and f_k.getLow() > s_k.getLow():

                # 增加K线方向属性
                self.container[1].setPos('Down')

            # 无包含向上处理
            elif f_k.getHigh() < s_k.getHigh() and f_k.getLow() < s_k.getLow():

                self.container[1].setPos('Up')

            # 存在包含关系
            else:

                # 由于一开始不存在向上包含或者向下包含的说法,要第一次确定属性的方式就是开两个K线顶底部的差的比较关系
                # 如果顶部差比底部差宽,则认为向上包含,反之亦然
                # 包含关系的初始化只是为了程序的运行考虑,不会影响到实际后面的其他包含关系处理
                a_up = abs(f_k.getHigh() - s_k.getHigh())
                a_down = abs(f_k.getLow() - s_k.getLow())

                if a_up > a_down:

                    self.container[1].setPos('Up')

                else:

                    self.container[1].setPos('Down')


        # 存在较多K线
        elif self.size() > 2:

            i = len(self.container) - 1

            # 无包含向上处理
            if self.container[i].getHigh() > self.container[i - 1].getHigh() and \
                            self.container[i].getLow() > self.container[i - 1].getLow():

                self.container[i].setPos('Up')

            # 无包含向下处理
            elif self.container[i].getHigh() < self.container[i - 1].getHigh() and \
                            self.container[i].getLow() < self.container[i - 1].getLow():

                self.container[i].setPos('Down')

            # 存在包含关系
            else:

                try:
                    pos = self.container[i - 1].getPos()

                except:
                    print('getPos goes wrong at ', i)

                if pos == 'Up':
                    high = max(self.container[i].getHigh(), self.container[i - 1].getHigh())
                    low = max(self.container[i].getLow(), self.container[i - 1].getLow())

                    # 修改当前一个K线的属性
                    self.container[i].setHigh(high)
                    self.container[i].setLow(low)
                    self.container[i].setPos('Up')

                    self.container.pop(i - 1)

                elif pos == 'Down':
                    high = min(self.container[i].getHigh(), self.container[i - 1].getHigh())
                    low = min(self.container[i].getLow(), self.container[i - 1].getLow())

                    # 修改当前一个K线的属性
                    self.container[i].setHigh(high)
                    self.container[i].setLow(low)
                    self.container[i].setPos('Down')

                    self.container.pop(i - 1)

    # MACD计算函数
    # 12日EMA的计算：EMA12 = 前一日EMA12 X 11/13 + 今日收盘 X 2/13
    # 26日EMA的计算：EMA26 = 前一日EMA26 X 25/27 + 今日收盘 X 2/27
    # 差离值（DIF）的计算： DIF = EMA12 - EMA26
    # 今日DEA = （前一日DEA X 8/10 + 今日DIF X 2/10）
    # MACD=(DIF-DEA）*2
    def insertMACD(self):

        if self.size() == 1:

            macd = MACD.MACD(self.container[0].getClose(),
                             self.container[0].getClose(),
                             0,
                             0,
                             0)

            self.container[0].MACD = macd

        elif self.size() >= 2:

            cur_candle = self.container[self.size() - 1]
            pre_candle = self.container[self.size() - 2]

            pre_EMA12 = pre_candle.MACD.EMA12
            pre_EMA26 = pre_candle.MACD.EMA26
            pre_DEA = pre_candle.MACD.DEA

            EMA12 = pre_EMA12 * 11 / 13 + cur_candle.getClose() * 2 / 13
            EMA26 = pre_EMA26 * 25 / 27 + cur_candle.getClose() * 2 / 27
            DIF = EMA12 - EMA26
            DEA = pre_DEA * 8 / 10 + DIF * 2 / 10
            M = (DIF - DEA) * 2

            macd = MACD.MACD(EMA12, EMA26, DIF, DEA, M)

            self.container[self.size() - 1].MACD = macd

    # 抽象接口,每个不同级别的K线需要独立实现
    # 不同级别K线在此接口上的很大不同在于查询条件不同
    def loadDB(self, year, month, count, skips, types, pens, hubs):

        pass

    def size(self):

        return len(self.container)

    # 实现新增K线插入接口
    def insertCandle(self, candle):

        self.container.append(candle)

    def closeDB(self):

        self._c.closeDB()


"""
class Hour_Candle_Container(Candle_Container):

    collector = Candle_Container.c.mongodb.hour

    def __init__(self):

        Candle_Container.__init__(self)

    def loadBucket(self, hour_bucket):

        self.__bucket = hour_bucket

    # 2016-04-12
    # 由于目前采用的是数据库历史数据加载,使用的是函数内循环调用.在真实的情况应该是出现一次K线调用一次
    # 对于次级别数据处理的最简单方式就是在如同调用types,pens,hubs处理一样,一旦出现了新的本级别K线,就去判断某些如同标志位之类的东西
    # 如果标志位有效,则加载次级别数据,并同时处理类似本级别这样的type,pens,hubs结构变化的信息
    # 该如何改变标志位取决于中枢的走势以及本级别笔与中枢的变化关系
    def loadDB(self, year, month, count, types, pens, hubs):

        if count > Hour_Candle_Container.collector.count():

            print('Warm!!! Count is overside!!!')

            Hour_Candle_Container.c.closeDB()

        try:

            self.cursor = Hour_Candle_Container.collector.find({'Year': year, 'Month': month}, limit=count)

        except BaseException:

            print('mongoDB goes wrong in Hour_Candle_Container')

        for d in self.cursor:

            h = Hour_Candle(d['Year'],
                     d['Month'],
                     d['Day'],
                     d['Hour'],
                     d['Open'],
                     d['Close'],
                     d['High'], d['Low'])

            self.container.append(h)

            # 在进行容器初始化加载历史数据的时候,同时对这部分数据进行包含处理
            self.contains()

            # 2016-04-19
            # 一旦Bucket确认激活,最好地跟踪次级别的方式是一旦K线形成并处理完包含,马上进行次级别数据读取
            # 因为如果等待笔形成后再读取,由于笔的可变性,很容易出现漏读的情况
            self.dumpBucket()

            types.insertType(h)

            pens.insertPen()

            hubs.insertHub()

    def dumpBucket(self):

        if self.__bucket.isActive():

            i = len(self.container) - 1

            self.__bucket.loadCandleID(i)

    def __del__(self):

        Candle_Container.__del__(self)
"""


# 2016-05-16
class Ten_Min_Candle_Container(Candle_Container):
    def __init__(self):

        Candle_Container.__init__(self)

        self._collector = ''

    def loadDB(self, year, month, count, skips, types, pens, hubs, monitor):

        if count > self._collector.count():
            print('Warm!!! Count is overside!!!')

            self._c.closeDB()

        try:

            self.__cursor = self._collector.find({'Year': year, 'Month': month}, limit=count, skip=skips)

        except BaseException:

            print('mongoDB goes wrong in Ten_Min_Candle_Container')

        for d in self.__cursor:

            m = Ten_Min_Candle(d['Year'], d['Month'], d['Day'], d['Hour'], d['Min_10'], d['Open'], d['Close'],
                               d['High'], d['Low'])

            self.container.append(m)

            # 在进行容器初始化加载历史数据的时候,同时对这部分数据进行包含处理
            self.contains()

            # print('-------Current Candle ID:', (len(self.container) - 1), '-----价格:', self.container[len(self.container) - 1].getClose())

            self.insertMACD()

            types.insertType(m)

            pens.insertPen()

            # K线生成事件注入 
            can = monitor.genEvent(Event.Monitor.CAN_BORN)

            try:

                can._dict['can'] = self.container[len(self.container) - 1]
                can._dict['len_cans'] = len(self.container) - 1
                can._dict['hub'] = hubs.container[len(hubs.container) - 1]

            except:

                pass

            monitor._e.put(can)

            sleep(0.002)

            single = hubs.insertHub()

            # 中枢生成事件注入
            if single == 1:

                born = monitor.genEvent(Event.Monitor.HUB_BORN)

                try:

                    # 当下中枢ID 
                    born._dict['hub_id'] = len(hubs.container) - 1

                    # 当下K线
                    born._dict['can'] = self.container[len(self.container) - 1]

                    # 当下K线队列长度
                    born._dict['len_cans'] = len(self.container) - 1

                    # 用于交易信息的传递
                    # 当下中枢
                    born._dict['hub'] = hubs.container[len(hubs.container) - 1]
                    born._dict['pre'] = hubs.container[len(hubs.container) - 2]

                except:

                    pass

                monitor._e.put(born)

                sleep(0.002)


# 抽象类,用于给不同的具体产品实现
class Five_Min_Candle_Container(Candle_Container):
    def __init__(self):

        Candle_Container.__init__(self)

        self._collector = ''

    def loadDB(self, year, month, count, skips, types, pens, hubs, strategy):

        if count > self._collector.count():
            print('Warm!!! Count is overside!!!')

            self._c.closeDB()

        try:

            if count == 0:

                self.__cursor = self._collector.find({'Year': year, 'Month': month}, skip=skips)

            else:

                self.__cursor = self._collector.find({'Year': year, 'Month': month}, limit=count, skip=skips)

        except BaseException:

            print('mongoDB goes wrong in Ten_Min_Candle_Container')

        for d in self.__cursor:

            m = Five_Min_Candle(d['Year'], d['Month'], d['Day'], d['Hour'], d['Min_10'], d['Min_5'], d['Open'],
                                d['Close'], d['High'], d['Low'])

            self.container.append(m)

            # 在进行容器初始化加载历史数据的时候,同时对这部分数据进行包含处理
            self.contains()

            # print('-------Current Candle ID:', (len(self.container) - 1), '-----价格:', self.container[len(self.container) - 1].getClose())

            self.insertMACD()

            types.insertType(m)

            pens.insertPen()

            if hubs.insertHub() == 1:
                strategy.process()

    def __del__(self):

        Candle_Container.__del__(self)

# 抽象类
class One_Min_Candle_Container(Candle_Container):
    def __init__(self):

        Candle_Container.__init__(self)

        # 不同的产品会指向不同的数据库,这个属性会在具体的继承类中实现
        self._collector = ''

    def loadDB(self, year, month, day, hour, min_10, min_5, types, pens, hubs, bucket):

        from Strategy import Ten_Min_Bucket

        try:

            # 10min为高级别查询
            if isinstance(bucket, Ten_Min_Bucket):

                self.cursor = self._collector.find({'Year': year,
                                                    'Month': month,
                                                    'Day': day,
                                                    'Hour': hour,
                                                    'Min_10': min_10}, limit=10)
            # 5min为高级别查询
            else:

                self.cursor = self._collector.find({'Year': year,
                                                    'Month': month,
                                                    'Day': day,
                                                    'Hour': hour,
                                                    'Min_10': min_10,
                                                    'Min_5': min_5}, limit=5)

        except BaseException:

            print('mongoDB goes wrong in Ten_Min_Condle_Container')

        for d in self.cursor:
            m = One_Min_Candle(d['Year'],
                               d['Month'],
                               d['Day'],
                               d['Hour'],
                               d['Min_10'],
                               d['Min_5'],
                               d['Min_1'],
                               d['Open'],
                               d['Close'],
                               d['High'],
                               d['Low'])

            self.container.append(m)

            """
            print('One_Min_Candle_Container.loadCandleID() 次级别K线价格:', m.getClose())
            """

            """
            print('One_Min_Candle_Container.loadCandleID() -- 次级别K线时间', pd.Timestamp(pd.datetime(d['Year'],
                                                                                d['Month'],
                                                                                d['Day'],
                                                                                d['Hour'],
                                                                                d['Min_10']+d['Min_5']+d['Min_1'])).strftime('%Y-%m-%d %H:%M:%S'))
            """

            # 在进行容器初始化加载历史数据的时候,同时对这部分数据进行包含处理
            self.contains()

            types.insertType(m)

            pens.insertPen()

            hubs.insertHub()

    def __del__(self):

        Candle_Container.__del__(self)


class Typer:
    def __init__(self, candle, candle_index):
        self.candle = candle
        self.candle_index = candle_index


class Down_Typer(Typer):
    __pos = 'Down'

    def __init__(self, candle, candle_index):
        Typer.__init__(self, candle, candle_index)

    def getPos(self):
        return self.__pos


class Up_Typer(Typer):
    __pos = 'Up'

    def __init__(self, candle, candle_index):
        Typer.__init__(self, candle, candle_index)

    def getPos(self):
        return self.__pos


class Type_Container:
    def __init__(self, candle_container):

        self.container = []

        self.candle_container = candle_container

    def reset(self):

        self.container = []

    # 处理逻辑是当出现一个新的K线的时候,函数对最后的三个K线位置做判断.注意不是最后一个K线
    def insertType(self, candle):

        # 2016-04-21
        # 处理最初第一根K线的情况,因为没有左边的K线,所以对第一个K线的判断仅仅依赖右边的即可
        if self.candle_container.size() == 2:

            pos_candle = self.candle_container.container[1]
            cur_candle = self.candle_container.container[0]

            # 后探K线
            pos_high = pos_candle.getHigh()
            pos_low = pos_candle.getLow()

            # 当前K线
            cur_high = cur_candle.getHigh()
            cur_low = cur_candle.getLow()

            if cur_high > pos_high and cur_low > pos_low:

                t = Up_Typer(cur_candle, 0)

                self.container.append(t)

            elif cur_high < pos_high and cur_low < pos_low:

                t = Down_Typer(cur_candle, 0)

                self.container.append(t)

            return

        # 只有当存在至少三根K线后才做分型处理
        if self.candle_container.size() < 3:
            return

        # 当新增加一个K线后,对队列中倒数第二个K线做分型处理
        cur_candle = self.candle_container.container[self.candle_container.size() - 2]
        pre_candle = self.candle_container.container[self.candle_container.size() - 3]
        pos_candle = candle

        # 当前K线
        cur_high = cur_candle.getHigh()
        cur_low = cur_candle.getLow()

        # 前探K线
        pre_high = pre_candle.getHigh()
        pre_low = pre_candle.getLow()

        # 后探K线
        pos_high = pos_candle.getHigh()
        pos_low = pos_candle.getLow()

        # 顶分型-当前K线高点分别高于前后两K线高点,当前K线低点分别高于前后两K线低点
        if cur_high > pre_high and cur_high > pos_high and cur_low > pre_low and cur_low > pos_low:

            t = Up_Typer(cur_candle, self.candle_container.size() - 2)

            if self.size() != 0:

                # 读取列表里最后一个分型
                last = self.container[self.size() - 1]

                if last.candle_index == t.candle_index:
                    return

                # 如果最后一个分型与当前分型同向, 并且当前分型比最后一个分型高
                # 这个步骤的目的是对相邻的具有同向属性的分型做处理,这样就确保了任何一对相邻的分型必然有且仅有反向属性
                if last.getPos() == 'Up' and t.candle.getHigh() > last.candle.getHigh():
                    # 移除在队列中的最后一个分型
                    self.container.pop()

            self.container.append(t)

        # 低分型-当前K线高点分别低于前后两K线高点,当前K线低点分别低于前后两K线低点
        elif cur_low < pre_low and cur_low < pos_low and cur_high < pre_high and cur_high < pos_high:

            t = Down_Typer(cur_candle, self.candle_container.size() - 2)

            if self.size() != 0:

                # 读取列表里最后一个分型
                last = self.container[self.size() - 1]

                if last.candle_index == t.candle_index:
                    return

                # 如果最后一笔与当前分型同向, 并且当前笔比最后一笔低
                # 这个步骤的目的是对相邻的具有同向属性的分型做处理,这样就确保了任何一对相邻的分型必然有且仅有反向属性
                if last.getPos() == 'Down' and t.candle.getLow() < last.candle.getLow():
                    # 移除在队列中的最后一个分型
                    self.container.pop()

            self.container.append(t)

    def size(self):

        return len(self.container)

    def pop(self):

        self.container.pop()


class Pen():
    def __init__(self, high, low, beginType, endType, pos):
        self.high = high
        self.low = low
        self.beginType = beginType
        self.endType = endType
        self.pos = pos


class Pen_Container():
    def __init__(self, types):

        self.container = []

        # 引用实例变量记录最后访问分型队列的最后位置
        self.types_index = 0

        # 指针指向分型结构容器
        self.__types = types

        # 记录有效笔的总数量,用于构造中枢过程
        # 有效笔的意思是经过了笔合并处理
        # 变量在init_hub中被引用
        # 遍历点从1开始,避免向前删除越界
        # 理论上可以实现从第一个笔开始,只需适当考虑边界问题即可
        self.pens_index = 1

        # 记录临时笔所处的笔队列的索引位置
        self.pens_stack_index = 0

        # 2016-03-23
        # 记录二次延迟处理,和self.pens_stack相似
        self.pens_stack_delay = []

        # 记录临时笔,可用于回退
        self.pens_stack = []

    def reset(self):

        self.container = []
        self.types_index = 0
        self.pens_stack_index = 0
        self.pens_stack = []
        self.pens_stack_delay = []
        self.pens_index = 1

    def __del__(self):

        self.container = []
        self.types_index = 0
        self.pens_stack_index = 0
        self.pens_stack = []
        self.pens_stack_delay = []
        self.pens_index = 1

    def insertPen(self):

        # 遍历分型结构发现笔结构
        # 最后一个分型结构不存在构成笔的可能,省去最后一个分型结构的遍历

        # 未能对最后一个分型实现会导致当前的迟滞
        # 原因确定一笔至少要求出现两个新的分型并确认至少当下笔破坏形成
        # 所以在probeDown和probeUp的实现中都避免对当下最后一个分型做笔判断的实现
        while self.types_index < self.__types.size():

            curType = self.__types.container[self.types_index]

            if curType.getPos() == 'Up':

                # 调用朝下侦查函数发现对于笔结构的底分型,并返回对应的分型结构在数组中的索引
                nextIndex = self.probeDown()

                # nextIndex == -1说明侦查函数找不到合适的分型结构,仅有在遍历至分型数组结束时才可能发生
                if nextIndex != -1:

                    # 构造笔字典结构
                    pen = Pen(curType.candle.getHigh(),
                              self.__types.container[self.types_index].candle.getLow(),
                              curType,
                              self.__types.container[self.types_index],
                              'Down')

                    self.container.append(pen)

                else:
                    break

            elif curType.getPos() == 'Down':

                nextIndex = self.probeUp()

                if nextIndex != -1:

                    pen = Pen(self.__types.container[self.types_index].candle.getHigh(),
                              curType.candle.getLow(),
                              curType,
                              self.__types.container[self.types_index],
                              'Up')

                    self.container.append(pen)

                else:
                    break

        self.__merge_pen()

    def probeUp(self):

        cur_high = self.__types.container[self.types_index].candle.getHigh()
        cur_low = self.__types.container[self.types_index].candle.getLow()

        # 由于存在向前延伸的行为,数组遍历最大仅能到倒数第二个
        for j in range(self.types_index, self.__types.size() - 1):

            # 当前分型为顶分型
            if self.__types.container[j].getPos() == 'Up':

                # 如果当前顶分型的高点高于已记录的出现过的最高顶分型,则更新最高点数据,并保持当前分型所在数组指针
                if self.__types.container[j].candle.getLow() > cur_low and \
                                self.__types.container[j].candle.getHigh() > cur_high:

                    # 记录最后满足条件的信息
                    cur_high = self.__types.container[j].candle.getHigh()
                    self.types_index = j

                    # 如果当前顶分型的下一个分型为底分型,同时底分型的低点低于当前顶分型的高点,则说明构造潜在向下笔的条件成立
                    # 此时认为构造当前向上笔完成,返回已记录的最高顶分型指针
                    if self.__types.container[j + 1].getPos() == 'Down' and \
                                    self.__types.container[j + 1].candle.getHigh() < self.__types.container[
                                j].candle.getHigh() and \
                                    self.__types.container[j + 1].candle.getLow() < self.__types.container[
                                j].candle.getLow():

                        return self.types_index

                    # 或者下一笔虽然为同向笔,但具有反向性质
                    elif self.__types.container[j + 1].getPos() == 'Up' and \
                                    self.__types.container[j + 1].candle.getHigh() < self.__types.container[
                                j].candle.getHigh() and \
                                    self.__types.container[j + 1].candle.getLow() < self.__types.container[
                                j].candle.getLow():

                        return self.types_index

        # 遍历结束,返回结束标示
        return -1

    def probeDown(self):

        cur_high = self.__types.container[self.types_index].candle.getHigh()
        cur_low = self.__types.container[self.types_index].candle.getLow()

        # 由于存在向前延伸的行为,数组遍历最大仅能到倒数第二个
        for j in range(self.types_index, self.__types.size() - 1):

            if self.__types.container[j].getPos() == 'Down':

                # 构成向下笔的顶底分型必须同时满足下面条件是为了避开包含关系
                if self.__types.container[j].candle.getLow() < cur_low and \
                                self.__types.container[j].candle.getHigh() < cur_high:

                    # 记录最后满足条件的信息
                    cur_low = self.__types.container[j].candle.getLow()
                    self.types_index = j

                    # 要同时满足以下条件才能构成笔
                    # 下一个分型为反向分型.目前的实现是认为出现反向分型则此笔结束
                    # 构成向上笔的顶底分型必须同时满足条件以避开包含关系
                    if self.__types.container[j + 1].getPos() == 'Up' and \
                                    self.__types.container[j + 1].candle.getHigh() > self.__types.container[
                                j].candle.getHigh() and \
                                    self.__types.container[j + 1].candle.getLow() > self.__types.container[
                                j].candle.getLow():

                        return self.types_index

                    # 或者下一笔虽然为同向笔,但具有反向性质
                    elif self.__types.container[j + 1].getPos() == 'Down' and \
                                    self.__types.container[j + 1].candle.getHigh() > self.__types.container[
                                j].candle.getHigh() and \
                                    self.__types.container[j + 1].candle.getLow() > self.__types.container[
                                j].candle.getLow():

                        return self.types_index

        # 遍历结束,返回结束标示
        return -1

    # 处理不满足构成笔K线数量要求的情况
    # 处理不合法笔的关键在于当考虑把此不合法笔撤销的时候,如何处理此操作所可能引起的前后关联笔环境的变化
    # 无论是删除向上笔还是向下笔,都必须同时删除与之相连的一笔,这样才能保证相邻笔的在方向上相反的特性
    # 要判断是删除前一笔还是后一笔的关键在于那种删除方式能令具有更剧烈的涵盖范围,也就是高点更高,低点更低
    def __merge_pen(self):

        # 循环体在笔队列反向偏置2的位置结束的原因是防止越界

        # 2016-03-25
        # 按照当前保留2笔的设计虽然可以确保在处理不合法笔的时候不出现越界,但缺陷是对任何情况都必须等到至少有两笔的时候才能处理,对现实情况的反映
        # 存在延迟.
        # 并不是所有需要处理笔合并的情况都需要向后两笔,可以把这个约束条件针对各个特定情况实现,这样至少可以加快不需要约束条件的场景

        while self.pens_index < self.size() - 1:

            # 只有当用于回退的临时笔队列不为空(说明有回退操作的可能),回退笔与当前笔有至少两笔的距离的时候才进行操作
            # 2016-03-21
            # 关于是采用self.pens_index还是len(pens)与self.pens_stack_index的距离判断问题
            # 测试发现有些场景采用len(pens)的时候判断revert的准确性没有self.pens_index高,其实本质在于用self.pens_index的时候延迟时间较长,在走势
            # 上看,更容易出现了满足revert条件的K线而已,其他没有差别
            # 这是在时间和准确性上的平衡取舍

            # 2016-03-22
            # 修改为len(pens),同时修改了revert_pen的判决回退条件
            if self.size() - self.pens_stack_index >= 2 and len(self.pens_stack) != 0:
                self.__revert_pen()

            """
            # 2016-03-22
            # 继续保留以self.pens_index的判决方式,以便增加覆盖场景的概率
            # 2016-03-23
            # 但从测试结果来看并不理想,能够覆盖一定的场景,但同时又引入了另外的错误
            # 具体案例参考:ch.test(2002,2003,1600,1900)
            elif self.pens_index - self.pens_stack_index >= 2 and len(self.pens_stack_delay) != 0:

                revert_pen(pens)
            """

            # 读取笔开始位置以及结束位置的index,可用于判断笔在构成K线数量方面的合法性
            e_K_index = self.container[self.pens_index].endType.candle_index
            s_K_index = self.container[self.pens_index].beginType.candle_index

            # 目前定义一笔包括顶底K线的话至少要有5根构成
            if e_K_index - s_K_index < 4:

                pos = self.container[self.pens_index].pos

                # 如果不合法的笔是向下笔
                if pos == 'Down':

                    pre_pen = self.container[self.pens_index - 1]
                    post_pen = self.container[self.pens_index + 1]

                    # 这是当前不合法的向下笔的底部具有比上一个向下笔底部还低的特性
                    # 由于此笔即将要销毁,前一个向下笔的底部可以延伸到待销毁向下笔的底部
                    if pre_pen.low >= self.container[self.pens_index].low:

                        # 保护带.避免前向越界的可能,可以继续向前处理
                        if self.pens_index - 2 >= 0:

                            # 如果发现回调测试还未来得及执行就再次出现新低的情况的话,马上进行回调处理
                            if len(self.pens_stack) != 0:
                                self.__revert_pen()

                            # 在笔修改前,保存此笔于堆栈,命名为回退笔
                            self.pens_stack.append(copy.deepcopy(self.container[self.pens_index - 2]))
                            self.pens_stack_delay.append(copy.deepcopy(self.container[self.pens_index - 2]))

                            # 更新上一向下笔底部属性
                            self.container[self.pens_index - 2].low = self.container[self.pens_index].low
                            self.container[self.pens_index - 2].endType = self.container[self.pens_index].endType

                            # 销毁当前笔以及前一个与此笔相连的向上笔
                            # 注意销毁顺序必须是由后向前,否则会误删其他笔
                            self.container.pop(self.pens_index)

                            # 在删除笔前,保存此笔于堆栈
                            self.pens_stack.append(copy.deepcopy(self.container[self.pens_index - 1]))
                            self.pens_stack_delay.append(copy.deepcopy(self.container[self.pens_index - 1]))

                            self.container.pop(self.pens_index - 1)

                            # 在全局笔队列指针修改前,保存临时堆栈中笔所处于的全局笔队列的位置
                            # 注意,此处减了2,因为这是当前笔与回退笔的最小偏置,它指向的是被保存的笔
                            self.pens_stack_index = self.pens_index - 2

                            # 指针回退一个单位
                            self.pens_index -= 1

                        # 不满足保护带要求则不做处理
                        else:
                            self.pens_index += 1

                    # 与此不合法向下笔前后相连的向上笔中,后面的向上笔顶部比前面的向上笔顶部高
                    # 在销毁不合法笔的时候,修改前一向上笔顶部指向新的高点

                    # 2016-03-25
                    # 增加了一个当前处理笔与笔队列总长度的关系判断
                    # 由于这个场景需要删除后一笔,所以需要两者间至少有一个笔的距离
                    elif post_pen.high >= pre_pen.high and self.size() - self.pens_index >= 1:

                        # 更新顶部信息
                        self.container[self.pens_index - 1].high = post_pen.high
                        self.container[self.pens_index - 1].endType = post_pen.endType

                        # 销毁当前笔以及后一个向上笔
                        self.container.pop(self.pens_index + 1)
                        self.container.pop(self.pens_index)

                    # 最后一种情况是不合法向下笔被前一笔完全包含,这和第一个情况相反
                    # 同时不合法笔后面的向上笔也被前一向上笔完全包含
                    # 不合法笔以及后一向上笔将会被销毁,同时与后向上笔相连的向下笔高点指向前一向上笔的高点
                    elif pre_pen.low < self.container[self.pens_index].low and post_pen.high < pre_pen.high:

                        # 此场景的处理要遍历并删除到当前笔往后两笔的地方
                        if self.size() - self.pens_index > 2:

                            self.container[self.pens_index + 2].high = pre_pen.high
                            self.container[self.pens_index + 2].beginType = pre_pen.endType

                            # 不合法笔以及与其相连的后一向上笔被销毁
                            self.container.pop(self.pens_index + 1)
                            self.container.pop(self.pens_index)

                        # 如果此场景不满足了, 就暂时不做处理, 如果后面还有一笔的话也有可能可以处理笔合并

                        else:
                            # self.pens_index += 1
                            break

                # 处理向上的不合法笔,逻辑与向下笔处理一致
                else:

                    pre_pen = self.container[self.pens_index - 1]
                    post_pen = self.container[self.pens_index + 1]

                    if pre_pen.high <= self.container[self.pens_index].high:

                        if self.pens_index - 2 >= 0:

                            # 2016-03-21
                            # 在笔修改前,保存此笔于堆栈
                            self.pens_stack.append(copy.deepcopy(self.container[self.pens_index - 2]))

                            self.container[self.pens_index - 2].high = self.container[self.pens_index].high
                            self.container[self.pens_index - 2].endType = self.container[self.pens_index].endType

                            self.container.pop(self.pens_index)

                            # 2016-03-21
                            self.pens_stack.append(copy.deepcopy(self.container[self.pens_index - 1]))

                            self.container.pop(self.pens_index - 1)

                            # 2016-03-21
                            self.pens_stack_index = self.pens_index - 2

                            self.pens_index -= 1

                        else:
                            self.pens_index += 1

                    # 2016-03-25
                    # 增加了一个当前处理笔与笔队列总长度的关系判断
                    # 由于这个场景需要删除后一笔,所以需要两者间至少有一个笔的距离
                    elif post_pen.low <= pre_pen.low and self.size() - self.pens_index >= 1:

                        # 2016-03-20
                        # 如果已经出现了回退笔,同时出现了删除此向上笔的场景,则在删除之前先处理回退笔
                        """
                        if len(pens) - self.pens_stack_index >= 2 and len(self.pens_stack) != 0:

                            revert_pen(pens)
                            break
                        """

                        self.container[self.pens_index - 1].low = post_pen.low
                        self.container[self.pens_index - 1].endType = post_pen.endType
                        self.container.pop(self.pens_index + 1)
                        self.container.pop(self.pens_index)

                    elif pre_pen.high > self.container[self.pens_index].high and post_pen.low > pre_pen.low:

                        if self.size() - self.pens_index > 2:

                            self.container[self.pens_index + 2].low = pre_pen.low
                            self.container[self.pens_index + 2].beginType = pre_pen.endType
                            self.container.pop(self.pens_index + 1)
                            self.container.pop(self.pens_index)

                        else:
                            # self.pens_index += 1
                            break

            else:

                self.pens_index += 1

    # 回退笔操作函数
    # 回退操作可以分为向上和向下两种,目前仅实现了对向下笔的回退
    # 为什么需要回退操作:回退操作可以认为是merge函数的补充.merge函数已经可以处理绝大部分非法笔的合并处理,但有一种情况需要再进行一次额外的监控处理.
    # 这就是当前不合法的向下笔的底部具有比上一个向下笔底部还低的情况.merge函数在处理这种情况的时候会把与当前非法笔相邻的前一个合法向上笔一同删除
    # 如果是在出现此非法向下笔的底部后走势反转向上形成向上笔,则这个底部可以确定
    # 但如果在此非法笔底部之后仍然继续有新低,并且这个新低可以和被删除的合法向上笔的顶部构成一个向下笔,那么之前的合法向上笔不应该被删除,合法向上笔的前一个向下笔底部也不应该被修改
    # 程序负责对上述两种状态做判断,要保留修改后的笔还是恢复原来的笔
    def __revert_pen(self):

        # pen_r 为相对靠近右边的笔
        # pen_l 为相对靠近左边的笔
        if len(self.pens_stack) != 0:
            legend_pen_r = self.pens_stack.pop()
            legend_pen_l = self.pens_stack.pop()

        else:
            legend_pen_r = self.pens_stack_delay.pop()
            legend_pen_l = self.pens_stack_delay.pop()

        # 读取pen_l向右偏置为2的笔
        pen_2 = self.container[self.pens_stack_index + 2]

        # 这个偏置笔的方向决定了笔回调的方式
        # 如果是做向下的回调,核心就是判断在当前g_pens_stack_index位置的笔的底部K线与g_pens_stack_index+1笔的顶部K线之间的距离是否
        # 足够形成新的笔.  如果能够形成新笔,则需要把原有笔恢复,同时构造g_pens_stack_index底部和g_pens_stack_index+1顶部之间新的笔
        if pen_2.pos == 'Down':

            # 当前的K线底部K线索引以及分型信息
            # cur_bottom_k_index = pens[g_pens_index]['End_Type']['K_Index']
            # cur_bottom_k = pens[g_pens_index]['End_Type']
            # 2016-03-20
            cur_bottom_k_index = pen_2.endType.candle_index
            cur_bottom_k = pen_2.endType

            # 笔修改前的旧底部信息
            # 2016-03-22
            # 修改pre_bottom_k = pens[self.pens_stack_index]['End_Type']->pre_bottom_k = legend_pen_r['Begin_Type']
            pre_bottom_k = legend_pen_r.beginType

            # 之前被删除笔的顶部K线索引以及分型信息
            legend_top_k_index = legend_pen_r.endType.candle_index
            legend_top_k = legend_pen_r.endType

            # 最新的顶底间要满足几个条件
            # 1.至少要满足4根K线的关系
            # 2.顶底均比被删除笔的顶底分别要低
            # 3.要比前面一个向下笔的底部出新低

            # 2016-03-22
            # 修改判决条件:
            # 1. 删除cur_bottom_k['Low'] < pre_bottom_k['Low']
            # 2. 添加cur_bottom_k['High'] < pre_bottom_k['High'] and cur_bottom_k['Low'] < pre_bottom_k['Low']
            if cur_bottom_k_index - legend_top_k_index >= 4 and \
                            cur_bottom_k.candle.getLow() < legend_top_k.candle.getLow() and \
                            cur_bottom_k.candle.getHigh() < legend_top_k.candle.getHigh() and \
                            cur_bottom_k.candle.getHigh() < pre_bottom_k.candle.getHigh() and \
                            cur_bottom_k.candle.getLow() < pre_bottom_k.candle.getLow():

                # 构造笔字典结构
                pen = Pen(legend_top_k.candle.getHigh(),
                          cur_bottom_k.candle.getLow(),
                          legend_top_k,
                          cur_bottom_k,
                          'Down')

                # 修改向下笔的底部以便其恢复到遇到非法向下笔之前的状态
                self.container[self.pens_stack_index].endType = copy.deepcopy(legend_pen_l.endType)
                self.container[self.pens_stack_index].low = legend_pen_l.low

                # 下面的5个步骤都是关于删除/插入笔的动作.这个的关键是索引偏置
                # pens.pop(g_pens_index-1)
                self.container.pop(self.pens_stack_index + 2)

                # 在偏置为1的位置恢复向上笔
                self.container.insert(self.pens_stack_index + 1, copy.deepcopy(legend_pen_r))

                # 在偏置为2的位置新插入向下笔
                self.container.insert(self.pens_stack_index + 2, copy.deepcopy(pen))

                self.container.pop(self.pens_stack_index + 3)

                # 把全局指针往后移动1位以便指向当前需要处理的笔
                self.pens_index += 1

                # 如果在小距离笔已经可以完成回退,则不需要再处理大距离
                if len(self.pens_stack_delay) != 0:
                    self.pens_stack_delay = []

        # TODO 当前没有实现对上行笔的延迟判决，需要考虑实现.有过调测,但没有完成
        """
        # 2016-03-22
        # 实现向上的相似延迟处理
        else:

            cur_top_k_index = pen_2['End_Type']['K_Index']
            cur_top_k = pen_2['End_Type']

            pre_top_k_index =  legend_pen_r['Begin_Type']['K_Index']
            pre_top_k = legend_pen_r['Begin_Type']

            legend_bottom_k_index = legend_pen_r['End_Type']['K_Index']
            legend_bottom_k = legend_pen_r['End_Type']

            if cur_top_k_index - legend_bottom_k_index >= 4 and \
                            cur_top_k['High'] > legend_bottom_k['High'] and \
                            cur_top_k['Low'] > legend_bottom_k['Low'] and \
                            cur_top_k['High'] > pre_top_k['High'] and \
                            cur_top_k['Low'] > pre_top_k['Low']

                pen = {'High': cur_top_k['High'],
                       'Low': legend_bottom_k['Low'],
                       'Position': 'Up',
                       'Begin_Type': legend_bottom_k,
                       'End_Type': cur_top_k}

                pens.pop(self.pens_stack_index+2)

                pens.insert(self.pens_stack_index+1, copy.deepcopy(legend_pen_r))

                pens.insert(self.pens_stack_index+2, copy.deepcopy(pen))

                pens.pop(self.pens_stack_index+3)

                g_pens_index += 1
        """

    def size(self):

        return len(self.container)


class Hub:
    def __init__(self, ZG, ZD, GG, DD, s_pen, e_pen, s_pen_index, e_pen_index):
        self.ZG = ZG
        self.ZD = ZD
        self.GG = GG
        self.DD = DD
        self.s_pen = s_pen
        self.e_pen = e_pen
        self.s_pen_index = s_pen_index
        self.e_pen_index = e_pen_index

    # 2016-05-16
    # 新增管理中枢笔索引的接
    def update_e_pen_index(self, e_pen_index):
        self.e_pen_index = e_pen_index

    def pens(self):
        return self.e_pen_index - self.s_pen_index + 1


class Hub_Container:
    def __init__(self, pens):

        self.pens = pens

        self.container = []

        # 常量确定中枢的宽度
        self.hub_width = 3

        self.last_hub_end_pen_index = 0

    def reset(self):

        self.container = []

        self.last_hub_end_pen_index = 0

    # 2016-04-15
    # 父类定义了标准实现,用于高级别操作
    # 可适用于10分钟和5分钟等做为高级别操作的场景

    # 2016-06-20
    # 当前版本的时间封装能力很弱,需要把和中枢形态确认的无关的其他模块操作剥离出来,通过函数返回值的方式和其他模块进行交互
    # 函数返回三个状态:1) -1:无新中枢生成,无中枢扩张, 2) 0:无新中枢生成,存在中枢扩张, 3) +1:新中枢生成
    def insertHub(self):

        # 控制起始中枢
        if self.last_hub_end_pen_index == 0:

            # 当前已经遍历到的笔的索引位置
            cur_pen_index = 0

            # 2016-04-11
            # while cur_pen_index + self.hub_width <= min(self.pens.pens_index, self.pens.size()-1):

            # 2016-06-30
            # 从<变更为<=:只要能够满足进行三笔中枢的条件即可进行判决,相比原来的算法提前一笔实现
            # Best Effort模式。能马上处理则马上处理,不能的就等下一轮
            # 从self.pens.pens_index变更为min(self.pens.pens_index, self.pens.size()-1)
            # pen_index是来自Pen_Container的变量用于记录即将要进行笔合法性处理的索引位置,它可能出现的情况下指向笔队列最后一笔以外一笔的地方
            # 如果以<= self.pens.pens_index的方式会出现访问越界的异常,处理的方式是取self.pens.pens_index和实际笔队列有效长度的最小值
            # while cur_pen_index + self.hub_width <= self.pens.pens_index:
            while cur_pen_index + self.hub_width < self.pens.pens_index:

                r = self.isHub(cur_pen_index)

                if isinstance(r, tuple):

                    # 中枢构造的过程具有严格的顺序要求, 特别是ZG,ZD,GG,DD
                    # 一个考虑点:是否在中枢里面直接定义日前或者采用pens的引用也可以.但在考虑到直接定义好的日期更方便进行次级别走势索引后,决定保留
                    hub = Hub(r[0],
                              r[1],
                              r[2],
                              r[3],
                              self.pens.container[cur_pen_index + 1],
                              self.pens.container[cur_pen_index + self.hub_width],
                              cur_pen_index + 1,
                              cur_pen_index + self.hub_width)

                    # 2016-04-04
                    # 考虑到扩张开始的部分将来很有可能用于MACD以及此级别数据读取,因为在中枢可以确定存在扩张的时候记录起点指向原有中枢'End_Pen'
                    hub.x_pen = copy.deepcopy(hub.e_pen)

                    # 在中枢定义形成后,调用发现延伸函数
                    i = self.isExpandable(hub, cur_pen_index + self.hub_width)

                    # 存在延伸
                    if i != cur_pen_index + self.hub_width:

                        # 修改终结点
                        hub.e_pen = self.pens.container[i]

                        # 2016-05-16
                        # 新增管理中枢笔索引的接
                        hub.update_e_pen_index(i)

                        cur_pen_index = i + 1

                        self.last_hub_end_pen_index = i
                    else:

                        cur_pen_index += self.hub_width + 1

                        self.last_hub_end_pen_index = cur_pen_index - 1

                    # 2016-04-04
                    # 添加关于中枢相对位置的属性
                    # 此属性标示了当前中枢相对于相邻的前一个中枢的高低位置
                    # 由于第一个初始中枢没有相对位置的概念,这里用'--'表示无效值
                    hub.pos = '--'
                    self.container.append(hub)

                    # 2016-06-20
                    # 函数返回值
                    return 1

                # 返回-1 说明暂时没有找到合适的中枢,但同时搜索并没有到边界点,继续遍历
                else:
                    cur_pen_index += 1

            # 2016-06-20
            # 无合适中枢
            return -1

        # 已经存在中枢,则可能出现两种情况:
        # 1. 已知的最后一个中枢继续生长
        # 2. 已知的最后一个中枢无法生长,但新出现的笔可能构成新的中枢
        else:

            # 尝试扩张最后一个中枢,调用延伸函数
            last_hub_index = self.size() - 1
            last_hub = self.container[last_hub_index]

            i = self.isExpandable(last_hub, self.last_hub_end_pen_index)

            # 新生成的笔可以成功归入已有中枢
            # 2016-04-11
            # 中枢扩展的发现没有延迟的属性,每次加入的都是当前最新笔
            if i != self.last_hub_end_pen_index:

                # 2016-04-18
                # 中枢延伸的距离有时候会大于1笔,用这个变量记录原始起点
                # t = self.last_hub_end_pen_index

                # 修改最后形成中枢的笔索引
                self.last_hub_end_pen_index = i

                # 修改最后一个中枢的属性
                self.container[last_hub_index].e_pen = self.pens.container[self.last_hub_end_pen_index]

                # 2016-05-16
                # 新增管理中枢笔索引的接口
                self.container[last_hub_index].update_e_pen_index(self.last_hub_end_pen_index)

                return 0

            # 新生成的笔没能归入已知最后一个中枢,则从最后一个中枢笔开始进行遍历看是否在新生成笔后出现了新中枢的可能
            else:

                # 从离最后一个中枢最近的不属于任何中枢的笔开始遍历
                cur_pen_index = self.last_hub_end_pen_index + 1

                # 2016-04-11
                # 修改_pen.pens_index - 3指示中枢可以延迟3笔生成

                # 2016-06-30
                # 从<变更为<=:只要能够满足进行三笔中枢的条件即可进行判决,相比原来的算法提前一笔实现
                # Best Effort模式。能马上处理则马上处理,不能的就等下一轮
                # 从self.pens.pens_index变更为min(self.pens.pens_index, self.pens.size()-1)
                # pen_index是来自Pen_Container的变量用于记录即将要进行笔合法性处理的索引位置,它可能出现的情况下指向笔队列最后一笔以外一笔的地方
                # 如果以<= self.pens.pens_index的方式会出现访问越界的异常,处理的方式是取self.pens.pens_index和实际笔队列有效长度的最小值
                # while cur_pen_index + self.hub_width <= self.pens.pens_index:
                while cur_pen_index + self.hub_width < self.pens.pens_index:

                    # 重新寻找可能存在的新中枢
                    r = self.isHub(cur_pen_index)

                    if isinstance(r, tuple):

                        hub = Hub(r[0],
                                  r[1],
                                  r[2],
                                  r[3],
                                  self.pens.container[cur_pen_index + 1],
                                  self.pens.container[cur_pen_index + self.hub_width],
                                  cur_pen_index + 1,
                                  cur_pen_index + self.hub_width)

                        # 2016-04-04
                        # 考虑到扩张开始的部分将来很有可能用于MACD以及此级别数据读取,因为在中枢可以确定存在扩张的时候记录起点指向原有中枢'End_Pen'
                        hub.x_pen = copy.deepcopy(hub.e_pen)

                        # 2016-04-17
                        # 新临时变量临时保存cur_pen_index,用于加载Bucket的时候使用
                        t_cur_pen_index = cur_pen_index

                        # 2016-04-04
                        # 加入中枢位置对比
                        # 新中枢在向上的方向,则新中枢第一笔应该是向下笔
                        if hub.ZD > last_hub.ZG:

                            # 新生成的中枢第一笔方向不合理,需要重新处理
                            if hub.s_pen.pos != 'Down':

                                # 往后偏置对一笔,准备重新开始遍历
                                # 非法中枢,清空,不放入队列
                                cur_pen_index += 1

                            # 新中枢具有合法的第一笔
                            # 记录新中枢相对于前一个中枢的位置属性
                            else:

                                # 新中枢新的位置属性
                                hub.pos = 'Up'

                                # 2016-04-11
                                # 中枢扩展的发现没有延迟的属性,每次加入的都是当前最新笔
                                # 被断定为中枢扩展的次级别数据可以存储到本中枢中为次级别走势判断服务
                                e_hub_pen_index = self.isExpandable(hub, cur_pen_index + self.hub_width)

                                # 具有可扩展性
                                if e_hub_pen_index != cur_pen_index + self.hub_width:

                                    hub.e_pen = self.pens.container[e_hub_pen_index]

                                    # 2016-05-16
                                    # 中枢笔索引记录
                                    hub.update_e_pen_index(e_hub_pen_index)

                                    cur_pen_index = e_hub_pen_index + 1

                                    self.last_hub_end_pen_index = e_hub_pen_index

                                # 不具有可扩展新
                                else:

                                    cur_pen_index += self.hub_width + 1

                                    self.last_hub_end_pen_index = cur_pen_index - 1

                                self.container.append(hub)

                                return 1

                        # 新中枢在向下的方向,则新中枢第一笔应该是向上笔
                        elif hub.ZG < last_hub.ZD:

                            # 新生成的中枢第一笔方向不合理,需要重新处理
                            if hub.s_pen.pos != 'Up':

                                cur_pen_index += 1

                            else:

                                # 新中枢新的位置属性
                                hub.pos = 'Down'

                                # 调用扩张检查
                                e_hub_pen_index = self.isExpandable(hub, cur_pen_index + self.hub_width)

                                # 存在扩张
                                if e_hub_pen_index != cur_pen_index + self.hub_width:

                                    hub.e_pen = self.pens.container[e_hub_pen_index]

                                    # 2016-05-16
                                    # 中枢笔索引修改
                                    hub.update_e_pen_index(e_hub_pen_index)

                                    cur_pen_index = e_hub_pen_index + 1

                                    self.last_hub_end_pen_index = e_hub_pen_index

                                else:

                                    cur_pen_index += self.hub_width + 1

                                    self.last_hub_end_pen_index = cur_pen_index - 1

                                self.container.append(hub)

                                return 1

                        # TODO: 目前对于有重叠区间的中枢按照正常中枢留着,不做额外处理
                        # 前后两个中枢存在重叠区域,这种情况对中枢做合并
                        # 暂时没有实现,仅仅忽略中枢添加入队列,并且挪到笔
                        else:

                            cur_pen_index += 1

                    # -1 说明暂时没有找到合适的中枢,但同时搜索并没有到边界点
                    else:
                        cur_pen_index += 1

                ## 返回1的时候说明已经到了边界
                # return -1

                # 2016-06-28
                # 存在局部延伸，但又还不足构成完整中枢延伸
                m = self.isGrow(last_hub, self.last_hub_end_pen_index)

                if m != 0:

                    return m

                else:

                    return -1

    def size(self):

        return len(self.container)

    def isHub(self, index):

        h = []
        l = []

        # 偏置位从1开始,其实是避开了第一个K线.理论上第一个K线不属于中枢
        # 注意遍历的范围为width+1而不是width

        for i in range(0, self.hub_width + 1):
            h.append(self.pens.container[i + index].high)
            l.append(self.pens.container[i + index].low)

        ZG = min(h)
        ZD = max(l)

        GG = max(h)
        DD = min(l)

        if ZG > ZD:

            return ZG, ZD, GG, DD

        else:

            return -1

    # 发现中枢的延伸
    # end_pen_index是构成中枢至少三笔最后一笔的索引,它等于cur_index+hub_width-1
    # 基于笔的基本形态,end_pen_index+双数的笔必然和中枢同向,遍历的时候就采用end_pen_index+2*t, t = 1,2,3,4,5.....

    # 2016-04-11
    # 中枢的扩张部分采用实时跟踪,不需要考虑延迟
    # 同时中枢的扩张部分不再考虑对中枢区间的修改
    def isExpandable(self, hub, end_pen_index):

        # 中枢重叠区间
        hub_ZG = hub.ZG
        hub_ZD = hub.ZD

        # 保持临时index,最后用于返回,用中枢的最后一笔做为初始化
        # 结果返回后,如何值为中枢最后一笔,则没有延伸
        cur_index = end_pen_index

        # 初始化索引
        i = end_pen_index + 2

        while i < self.pens.pens_index:

            pen_high = self.pens.container[i].high
            pen_low = self.pens.container[i].low

            min_high = min(hub_ZG, pen_high)
            max_low = max(hub_ZD, pen_low)

            # 存在交集
            if min_high > max_low:

                # 保持最后索引位置
                cur_index = i

                # 刷新中枢重叠区间

                # 2016-04-30
                # 取消中枢扩张部分对于中枢区间的修改
                """
                hub.ZG = min_high
                hub.ZD = max_low

                hub_ZG = hub.ZG
                hub_ZD = hub.ZD
                """

                # 2016-04-11
                # 取消扩张部分对中枢区间的修改

                # 出现了中枢新高或新低

                hub.GG = max(pen_high, hub.GG)

                hub.DD = min(pen_low, hub.DD)

                # 索引继续往前探寻
                i += 2

            # 不存在交集,或者探寻结束
            else:

                break

        return cur_index

    # 2016-06-28
    # 用于失败中枢是否存在延伸的可能。这里的“可能性”是指目前的笔和中枢存在交集，但数量上没能达到end_pen_index+2*t, t = 1,2,3,4,5..的要求
    # 如果中枢和新笔存在交集则为延伸，接口返回笔索引，但不会对中枢做任何修改
    # 否则返回0
    def isGrow(self, hub, end_pen_index):

        # 中枢重叠区间
        hub_ZG = hub.ZG
        hub_ZD = hub.ZD

        # 初始化标识为0
        mark = 0

        # 初始化索引为当前中枢后一笔
        i = end_pen_index + 1

        while i < self.pens.pens_index:

            pen_high = self.pens.container[i].high
            pen_low = self.pens.container[i].low

            min_high = min(hub_ZG, pen_high)
            max_low = max(hub_ZD, pen_low)

            # 存在交集
            if min_high > max_low:

                # 保持最后索引位置
                mark = i

                # 索引继续往前探寻
                i += 1

            # 不存在交集,或者探寻结束
            else:

                break

        return mark


class Hour_Hub_Container(Hub_Container):
    def __init__(self, pens, bucket):
        Hub_Container.__init__(self, pens, bucket)


# 2016-04-17
# 对于中枢采用多态性的原因主要在于重写insertHub接口
# 不同级别的数据对于形态构成后的处理方式是不一样的
# 10分钟级别如果是做为最高级别或者中间级别处理,那么当本级别趋势确认的时候会生成Bucket去加载次级别数据,但如果已经是做为最小级别处理,当趋势确认的时候会触发买卖点交易
class Ten_Min_Hub_Container(Hub_Container):
    def __init__(self, pens):
        Hub_Container.__init__(self, pens)


class One_Min_Hub_Container(Hub_Container):
    def __init__(self, pens):

        Hub_Container.__init__(self, pens)

    # 函数重载
    # 由于1分钟级别是做为次级别操作,父类的具体实现不适合于此子类,所以重载

    # 2016-06-20
    # 增加函数返回值
    def insertHub(self):

        if self.last_hub_end_pen_index == 0:

            # 当前已经遍历到的笔的索引位置
            cur_pen_index = 0

            # 2016-04-11
            # 修改_pen.pens_index - 3指示中枢可以延迟3笔生成
            while cur_pen_index < self.pens.pens_index:

                r = self.isHub(cur_pen_index)

                if isinstance(r, tuple):

                    # 中枢构造的过程具有严格的顺序要求, 特别是ZG,ZD,GG,DD
                    # 一个考虑点:是否在中枢里面直接定义日前或者采用pens的引用也可以.但在考虑到直接定义好的日期更方便进行次级别走势索引后,决定保留
                    hub = Hub(r[0],
                              r[1],
                              r[2],
                              r[3],
                              self.pens.container[cur_pen_index + 1],
                              self.pens.container[cur_pen_index + self.hub_width],
                              cur_pen_index + 1,
                              cur_pen_index + self.hub_width)

                    # 2016-04-04
                    # 考虑到扩张开始的部分将来很有可能用于MACD以及此级别数据读取,因为在中枢可以确定存在扩张的时候记录起点指向原有中枢'End_Pen'
                    hub.x_pen = copy.deepcopy(hub.e_pen)

                    # 在中枢定义形成后,调用发现延伸函数
                    i = self.isExpandable(hub, cur_pen_index + self.hub_width)

                    # 存在延伸
                    if i != cur_pen_index + self.hub_width:

                        # 修改终结点
                        hub.e_pen = self.pens.container[i]

                        # 修改中枢笔索引
                        hub.update_e_pen_index(i)

                        cur_pen_index = i + 1

                        self.last_hub_end_pen_index = i

                    else:

                        cur_pen_index += self.hub_width + 1

                        self.last_hub_end_pen_index = cur_pen_index - 1

                    # 2016-04-04
                    # 添加关于中枢相对位置的属性
                    # 此属性标示了当前中枢相对于相邻的前一个中枢的高低位置
                    # 由于第一个初始中枢没有相对位置的概念,这里用'--'表示无效值
                    hub.pos = '--'
                    self.container.append(hub)

                    # 2016-06-20
                    # 增加函数返回值
                    return 1

                # -1 说明暂时没有找到合适的中枢,但同时搜索并没有到边界点
                elif r == -1:
                    cur_pen_index += 1

                # 返回 1的时候说明已经到了边界,没有继续遍历的需要
                else:

                    # 2016-06-20
                    # 增加函数返回值
                    return -1

        # 已经存在中枢,则可能出现两种情况:
        # 1. 已知的最后一个中枢继续生长
        # 2. 已知的最后一个中枢无法生长,但新出现的笔可能构成新的中枢
        else:

            # 尝试扩张最后一个中枢,调用延伸函数
            last_hub_index = self.size() - 1
            last_hub = self.container[last_hub_index]

            i = self.isExpandable(last_hub, self.last_hub_end_pen_index)

            # 新生成的笔可以成功归入已有中枢
            # 2016-04-11
            # 中枢扩展的发现没有延迟的属性,每次加入的都是当前最新笔
            # 被断定为中枢扩展的次级别数据可以存储到本中枢中为次级别走势判断服务
            if i != self.last_hub_end_pen_index:

                # 2016-04-18
                # 中枢延伸的距离有时候会大于1笔,用这个变量记录原始起点
                t = self.last_hub_end_pen_index

                # 修改最后形成中枢的笔索引
                self.last_hub_end_pen_index = i

                # 修改最后一个中枢的属性
                self.container[last_hub_index].e_pen = self.pens.container[self.last_hub_end_pen_index]

                # 修改中枢笔索引
                self.container[last_hub_index].update_e_pen_index(self.last_hub_end_pen_index)

                # 2016-06-20
                # 增加函数返回值
                return 0

            # 新生成的笔没能归入已知最后一个中枢,则从最后一个中枢笔开始进行遍历看是否在新生成笔后出现了新中枢的可能
            else:

                # 从离最后一个中枢最近的不属于任何中枢的笔开始遍历
                cur_pen_index = self.last_hub_end_pen_index + 1

                # 临时小变量用于保存中枢扩张的笔索引位置
                e_hub_pen_index = 0

                # 2016-04-11
                # 修改_pen.pens_index - 3指示中枢可以延迟3笔生成
                while cur_pen_index + self.hub_width <= self.pens.pens_index - 3:

                    # 重新寻找可能存在的新中枢
                    r = self.isHub(cur_pen_index)

                    if isinstance(r, tuple):

                        hub = Hub(r[0],
                                  r[1],
                                  r[2],
                                  r[3],
                                  self.pens.container[cur_pen_index + 1],
                                  self.pens.container[cur_pen_index + self.hub_width],
                                  cur_pen_index + 1,
                                  cur_pen_index + self.hub_width)

                        # 2016-04-04
                        # 考虑到扩张开始的部分将来很有可能用于MACD以及此级别数据读取,因为在中枢可以确定存在扩张的时候记录起点指向原有中枢'End_Pen'
                        hub.x_pen = copy.deepcopy(hub.e_pen)

                        # 2016-04-17
                        # 新临时变量临时保存cur_pen_index,用于加载Bucket的时候使用
                        t_cur_pen_index = cur_pen_index

                        # 2016-04-04
                        # 加入中枢位置对比
                        # 新中枢在向上的方向,则新中枢第一笔应该是向下笔
                        if hub.ZD > last_hub.ZG:

                            # 新生成的中枢第一笔方向不合理,需要重新处理
                            if hub.s_pen.pos != 'Down':

                                # 往后偏置对一笔,准备重新开始遍历
                                # 非法中枢,清空,不放入队列
                                cur_pen_index += 1

                            # 新中枢具有合法的第一笔
                            # 记录新中枢相对于前一个中枢的位置属性
                            else:

                                # 新中枢新的位置属性
                                hub.pos = 'Up'

                                # 2016-04-24
                                # 如果买卖点已经激活,但却出现了一个反向的中枢,这是去激活买卖点
                                if self._bucket.isBucketAct() and self._bucket.isEntryAct():

                                    print('One_Min_Hub_C.insertHub()--次级别新中枢生成,Bucket处于激活并且Entry处于激活')

                                    #  出现了反向中枢的情况下马上去激活买卖点
                                    if self._bucket.isSameTrending('Down'):
                                        print(
                                            'One_Min_Hub_C.insertHub()--次级别新中枢生成,Bucket处于激活并且Entry处于激活,新中枢方向为Down与Bucket相反,Entry去激活')

                                        self._bucket.deactEntry()

                                # 2016-04-11
                                # 中枢扩展的发现没有延迟的属性,每次加入的都是当前最新笔
                                # 被断定为中枢扩展的次级别数据可以存储到本中枢中为次级别走势判断服务
                                e_hub_pen_index = self.isExpandable(hub, cur_pen_index + self.hub_width)

                                # 具有可扩展性
                                if e_hub_pen_index != cur_pen_index + self.hub_width:

                                    hub.e_pen = self.pens.container[e_hub_pen_index]

                                    # 修改中枢笔索引
                                    hub.update_e_pen_index(e_hub_pen_index)

                                    cur_pen_index = e_hub_pen_index + 1

                                    self.last_hub_end_pen_index = e_hub_pen_index

                                # 不具有可扩展新
                                else:

                                    cur_pen_index += self.hub_width + 1

                                    self.last_hub_end_pen_index = cur_pen_index - 1

                                self.container.append(hub)

                                # 出现两次同向中枢

                                # 2016-04-11
                                # 根据当前所采用的中枢延迟判决的机制,当能够确认一个新中枢形成的时候,至少已经在最小满足中枢笔数量的基础上再多往前
                                # 生成了3笔.这个时候对于新中枢应该考虑加载第5笔以及以后笔的次级别信息

                                if last_hub.pos == 'Up':

                                    print('One_Min_Hub_C.insertHub()--连续出现两次同向中枢--UP')

                                    # 2016-05-17
                                    # 实现对中枢范围的判断
                                    # TODO 2016-05-18: 暂时屏蔽了对次级别实施中枢范围限制的条件
                                    # if self.isForTrade(last_hub):

                                    # print('One_Min_Hub_C.insertHub()--中枢范围合理')

                                    if self._bucket.isBucketAct() and self._bucket.isSameTrending('Up'):

                                        print('One_Min_Hub_C.insertHub()--Bucket处于激活状态,并且Bucket与新中枢同向--UP')

                                        # 2016-04-26
                                        # 买卖点跟随高级别中枢的而不跟随次级别中枢.在次级别连续出现同向中枢的情况下,原来已经设置了的买卖点不应该改变
                                        # 在实际的情况里面是不会出现这种情况的,因为如果要形成一个同时中枢那么必然已经出现了低于或者高于买卖点的情况,这个时候交易已经触发
                                        # TODO 目前的实现了中枢个数的限制,只有第二个同向中枢会激活买卖点和门限,随后出现的同向中枢不会再处理

                                        # 2016-05-08
                                        # 次级别中枢和本级别中枢ZG／ZD关系判断买卖点关系可以放宽到只要次级别趋势的ZD比本级别中枢的ZG高就行，不需要控制到要求次级别的第一个中枢的ZD>本级别中枢的ZG
                                        # if last_hub.ZD > self._bucket.exist_price():

                                        if hub.ZD > self._bucket.exist_price():

                                            print(
                                                'One_Min_Hub_C.insertHub()--次级别中枢范围合理,UP, hub.ZD > bucket.exist_price:',
                                                hub.ZD, self._bucket.exist_price())

                                            # Entry没有被激活
                                            if self._bucket.isEntryAct() == False:

                                                print('One_Min_Hub_C.insertHub()--没有Entry被激活, 直接激活Entry为hub.ZG--',
                                                      hub.ZG)

                                                # 2016-04-23
                                                # 如果次级别走势形成,触发Bucket买卖点状态,同时传递次级别中枢最高
                                                self._bucket.activeEntry(hub.ZG)

                                            # 如果Entry已经被激活,但出现了新的同向次级别中枢,修改Entry
                                            else:

                                                self._bucket.modEntry(hub.ZG)

                                                print('One_Min_Hub_C.insertHub()--修改Entry:', hub.ZG)

                                        else:

                                            print(
                                                'One_Min_Hub_C.insertHub()--次级别中枢范围不合理,UP, hub.ZD <= bucket.exist_price:',
                                                hub.ZD, self._bucket.exist_price())

                                    else:

                                        print('One_Min_Hub_C.insertHub()--次级别走势与Bucket反向,不做处理')

                                        # else:

                                        # print('One_Min_Hub_C.insertHub()--中枢范围不合理')


                        # 新中枢在向下的方向,则新中枢第一笔应该是向上笔
                        elif hub.ZG < last_hub.ZD:

                            # 新生成的中枢第一笔方向不合理,需要重新处理
                            if hub.s_pen.pos != 'Up':

                                cur_pen_index += 1

                            else:

                                # 新中枢新的位置属性
                                hub.pos = 'Down'

                                # 2016-04-24
                                # 如果买卖点已经激活,但却出现了一个反向的中枢,这是去激活买卖点
                                if self._bucket.isBucketAct() and self._bucket.isEntryAct():

                                    print('One_Min_Hub_C.insertHub()--次级别新中枢生成,Bucket处于激活并且Entry处于激活')

                                    if self._bucket.isSameTrending('Up'):
                                        print(
                                            'One_Min_Hub_C.insertHub()--次级别新中枢生成,Bucket处于激活并且Entry处于激活,次级别新中枢方向为Down与Bucket相反,Entry去激活')

                                        self._bucket.deactEntry()

                                # 调用扩张检查
                                e_hub_pen_index = self.isExpandable(hub, cur_pen_index + self.hub_width)

                                if e_hub_pen_index != cur_pen_index + self.hub_width:

                                    hub.e_pen = self.pens.container[e_hub_pen_index]

                                    # 修改中枢笔索引
                                    hub.update_e_pen_index(e_hub_pen_index)

                                    cur_pen_index = e_hub_pen_index + 1

                                    self.last_hub_end_pen_index = e_hub_pen_index

                                else:

                                    cur_pen_index += self.hub_width + 1

                                    self.last_hub_end_pen_index = cur_pen_index - 1

                                self.container.append(hub)

                                # 2016-04-11
                                # 根据当前所采用的中枢延迟判决的机制,当能够确认一个新中枢形成的时候,至少已经在最小满足中枢笔数量的基础上再多往前
                                # 生成了3笔.这个时候对于新中枢应该考虑加载第5笔以及以后笔的次级别信息
                                if last_hub.pos == 'Down':

                                    print('One_Min_Hub_C.insertHub()--连续出现两次同向中枢--DOWN')

                                    # 2016-05-17
                                    # 实现对中枢范围的判断
                                    # if self.isForTrade(last_hub):

                                    # print('One_Min_Hub_C.insertHub()--中枢范围合理')

                                    # 2016-04-23
                                    # 如果次级别走势形成,触发Bucket买卖点状态,同时传递次级别中枢最低点
                                    if self._bucket.isBucketAct() and self._bucket.isSameTrending('Down'):

                                        print('One_Min_Hub_C.insertHub()--Bucket处于激活状态,并且Bucket与新中枢同向--DOWN')

                                        # 2016-05-08
                                        # 次级别中枢和本级别中枢ZG／ZD关系判断买卖点关系可以放宽到只要次级别趋势的ZD比本级别中枢的ZG高就行，不需要控制到要求次级别的第一个中枢的ZD>本级别中枢的ZG
                                        # if last_hub.ZG < self._bucket.exist_price():

                                        if hub.ZG < self._bucket.exist_price():

                                            print(
                                                'One_Min_Hub_C.insertHub()--次级别中枢范围合理,Down, hub.ZG < bucket.exist_price:',
                                                hub.ZG, self._bucket.exist_price())

                                            if self._bucket.isEntryAct() == False:

                                                print('One_Min_Hub_C.insertHub()--没有Entry被激活,直接激活Entry为hub.ZD--',
                                                      hub.ZD)

                                                self._bucket.activeEntry(hub.ZD)

                                            else:

                                                self._bucket.modEntry(hub.ZD)

                                                print('One_Min_Hub_C.insertHub()--修改Entry:', hub.ZD)

                                        else:

                                            print(
                                                'One_Min_Hub_C.insertHub()--次级别中枢范围不合理,Down, hub.ZG >= bucket.exist_price:',
                                                hub.ZG, self._bucket.exist_price())

                                    else:

                                        print('One_Min_Hub_C.insertHub()--次级别走势与Bucket反向,不做处理')

                                        # else:

                                        # print('One_Min_Hub_C.insertHub()--中枢范围不合理')

                        # TODO: 目前对于有重叠区间的中枢按照正常中枢留着,不做额外处理
                        # 前后两个中枢存在重叠区域,这种情况对中枢做合并
                        # 暂时没有实现,仅仅忽略中枢添加入队列,并且挪到笔
                        else:

                            cur_pen_index += 1

                        # 2016-06-20
                        # 增加函数返回值
                        return 1


                    # -1 说明暂时没有找到合适的中枢,但同时搜索并没有到边界点
                    elif r == -1:

                        cur_pen_index += 1

                    # 返回 1的时候说明已经到了边界,没有继续遍历的需要
                    else:

                        # 2016-06-20
                        # 增加函数返回值
                        return -1


class Five_Min_Hub_Container(Hub_Container):
    def __init__(self, pens, bucket):
        Hub_Container.__init__(self, pens, bucket)


class Transcation:
    def __init__(self, hubId, trend_id, price):
        # 本中枢起点
        # Tran_Container.actTran(hub.s_pen.beginType.candle_index, last_hub.s_pen.beginType.candle_index, hub.ZD)

        # hub.s_pen.beginType.candle_index
        self.hubID = hubId

        # last_hub.s_pen.beginType.candle_index
        self.trend = trend_id

        # hub.ZD
        self.hub_price = price

        # 收益/损失
        self.profit = 0

    def entryID(self, id):
        self.entry = id

    # 识别做空做多
    def execute(self, strategy):
        self.strategy = strategy

    def tradeID(self, id, price):
        self.trade = id
        self.trade_price = price

    def exitID(self, id):
        self.exit = id

    def exitPrice(self, price):
        self.exit_price = price

    def profiting(self, p):
        self.profit = p

    def power(self, exit, entry):
        self.M_exit = exit
        self.M_entry = entry


# 2016-05-22
# 关于交易记录类对象化的思考
# 交易类原则上重点是记录交易的价格信息,这类信息以Bucket最为集中.如果把交易类和Bucket关联,就可以实现对交易信息的管理.
# 但考虑到目前还要在图形上辅助以分析,所以交易类还同时记录了K线信息对应的信息,比如ID,这就导致了交易类还要同时和中枢类以及Candle类进行互操作
# 但这些和K线相关的信息最终不是系统的核心.考虑上述的因素,在对交易类进行对象化的时候还是采用把交易类和Bucket进行管理的方式,但同时交易类对象
# 独立于Bucket存在
class Tran_Container:
    def __init__(self):

        self.container = []
        self.cur_tran = None

        self.entry_index = False
        self.trade_index = False
        self.exit_index = False

    def actTran(self, id, trend_id, price):

        self.cur_tran = Transcation(id, trend_id, price)

    def actEntry(self, id):

        self.cur_tran.entryID(id)

    def decatTran(self):

        self.cur_tran = None

        self.entry_index = False
        self.trade_index = False
        self.exit_index = False

    def traded(self, id, price):
        self.cur_tran.tradeID(id, price)

    def execute(self, strategy):

        self.cur_tran.execute(strategy)

    def existPrice(self, price):
        self.cur_tran.exitPrice(price)

    def profiting(self, p):
        self.cur_tran.profiting(p)

    def exitID(self, id):

        self.cur_tran.exitID(id)

        self.container.append(copy.deepcopy(self.cur_tran))

    def reset(self):

        self.container.clear()
        self.decatTran()

    def printing(self):

        i = 0

        while i < len(self.container):
            trendID = self.container[i].trend
            hubID = self.container[i].hubID
            entryID = self.container[i].entry
            tradeID = self.container[i].trade
            exitID = self.container[i].exit

            print('-------------------------------------------------------')
            print('第', i + 1, '笔交易--', self.container[i].strategy)
            print('大图:last_hub.s_pen.beginType.candle_index :', trendID)
            print('大图:hub.s_pen.beginType.candle_index:', hubID)
            print('小图:hub.s_pen.beginType.candle_index:', hubID - trendID, '(大图绝对位置ID:', hubID, ')')
            print('小图:Entry确认激活位置ID:', entryID - trendID, '(大图绝对位置ID:', entryID, ')')
            print('小图:交易进场位置ID:', tradeID - trendID, '(大图绝对位置ID:', tradeID, ')')
            print('小图:交易离场位置ID:', exitID - trendID, '(大图绝对位置ID:', exitID, ')')

            print('中枢边界价格:', self.container[i].hub_price)
            print('交易价格:', self.container[i].trade_price)
            print('离场价格:', self.container[i].exit_price)
            print('获利:', self.container[i].profit)
            print('MACD Entry:', self.container[i].M_entry)
            print('MACD Exit:', self.container[i].M_exit)

            i += 1

    def save(self, month):

        strategy = []
        hub_price = []
        trade_price = []
        exit_price = []
        M_entry = []
        M_exit = []
        months = []
        profits = []

        for _, tran in enumerate(self.container):
            strategy.append(tran.strategy)
            hub_price.append(tran.hub_price)
            trade_price.append(tran.trade_price)
            exit_price.append(tran.exit_price)
            M_entry.append(tran.M_entry)
            M_exit.append(tran.M_exit)
            profits.append(tran.profit)
            months.append(month)

        d = {'交易策略': strategy,
             '中枢边界价格': hub_price,
             '进场价格': trade_price,
             '离场价格': exit_price,
             'MACD Entry 力量': M_entry,
             'MACD Exit 力量': M_exit,
             '获利': profits,
             '月份': months}

        return d

if __name__ == '__main__':
   
    print('dfdff')

    Connector.dump_mongoDB()
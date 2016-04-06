# 2016-4-5
# New file to implement the design in Class Definition

import matplotlib.pyplot as plt

import matplotlib.patches as patches

import pandas as pd

import copy

import math

import imp

from pymongo import MongoClient


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

    def getMins(self):

        return self.__10min


class One_Min_Candle(Ten_Min_Candle):

    def __init__(self, year, month, day, hour, min_10, min_1, open, close, high, low):

        Ten_Min_Candle.__init__(self, year, month, day, hour, min_10, open, close, high, low)

        self.__1min = min_1

    def getMin(self):

        return self.__1min


class Connector:

    client = MongoClient()

    mongodb = client.AUD_trading

    def closeDB(self):

        self.client.close()

class Candle_Container:

    c = Connector()

    def __init__(self):

        self.container = []

    def __del__(self):

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
            if self.container[i].getHigh() > self.container[i-1].getHigh() and \
                            self.container[i].getLow() > self.container[i-1].getLow():

                self.container[i].setPos('Up')

            # 无包含向下处理
            elif self.container[i].getHigh() < self.container[i-1].getHigh() and \
                            self.container[i].getLow() < self.container[i-1].getLow():

                self.container[i].setPos('Down')

            # 存在包含关系
            else:

                try:
                    pos = self.container[i-1].getPos()

                except:
                    print('getPos goes wrong at ', i)

                if pos == 'Up':
                    high = max(self.container[i].getHigh(), self.container[i-1].getHigh())
                    low = max(self.container[i].getLow(), self.container[i-1].getLow())

                elif pos == 'Down':
                    high = min(self.container[i].getHigh(), self.container[i-1].getHigh())
                    low = min(self.container[i].getLow(), self.container[i-1].getLow())

                # 修改当前一个K线的属性
                self.container[i].setHigh(high)
                self.container[i].setLow(low)
                self.container[i].setPos('Up')

                # 删除被包含了的K线
                self.container.pop(i-1)

    def size(self):

        return len(self.container)

    # 实现新增K线插入接口
    def insertCandle(self, candle):

        self.container.append(candle)

    @staticmethod
    def closeDB():
        Candle_Container.c.closeDB()


class Hour_Candle_Container(Candle_Container):

    collector = Candle_Container.c.mongodb.hour

    def __init__(self):

        Candle_Container.__init__(self)

    def loadDB(self, year, month, count, types, pens):

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
                     d['High'],
                    d['Low'])

            # h.mins = Ten_Min_Condle_Container(h.getYear(), h.getMonth(), h.getDay(), h.getHour())

            self.container.append(h)

            # 在进行容器初始化加载历史数据的时候,同时对这部分数据进行包含处理
            self.contains()

            types.insertType(h)

            pens.insertPen()

    def __del__(self):

        Candle_Container.__del__(self)


class Ten_Min_Condle_Container(Candle_Container):

    collector = Candle_Container.c.mongodb.min_10

    def __init__(self):

        Candle_Container.__init__(self)

    def loadDB(self, year, month, count, types, pens):

        try:

            self.cursor = Ten_Min_Condle_Container.collector.find({'Year': year, 'Month': month}, limit=count)

        except BaseException:

            print('mongoDB goes wrong in Ten_Min_Condle_Container')

        for d in self.cursor:

            m = Ten_Min_Candle(d['Year'],
                        d['Month'],
                        d['Day'],
                        d['Hour'],
                        d['Min'],
                        d['Open'],
                        d['Close'],
                        d['High'],
                        d['Low'])

            # m.one_min = One_Min_Condle_Container(m.getYear(), m.getMonth(), m.getDay(), m.getHour(), m.getMins())

            self.container.append(m)

            # 在进行容器初始化加载历史数据的时候,同时对这部分数据进行包含处理
            self.contains()

            types.insertType(m)

            pens.insertPen()

    def __del__(self):

        Candle_Container.__del__(self)


class One_Min_Condle_Container(Candle_Container):

    collector = Candle_Container.c.mongodb.min_1

    def __init__(self):

        Candle_Container.__init__(self)

    def loadDB(self, year, month, day, hour, min, types, pens):

        try:

            self.cursor = One_Min_Condle_Container.collector.find({'Year': year, 'Month': month, 'Day': day, 'Hour': hour, 'Min': min})

        except BaseException:

            print('mongoDB goes wrong in Ten_Min_Condle_Container')

        for d in self.cursor:

            m = One_Min_Candle(d['Year'],
                        d['Month'],
                        d['Day'],
                        d['Hour'],
                        d['Min'],
                        d['Min_1'],
                        d['Open'],
                        d['Close'],
                        d['High'],
                        d['Low'])

            self.container.append(m)

            # 在进行容器初始化加载历史数据的时候,同时对这部分数据进行包含处理
            self.contains()

            types.insertType(m)

            pens.insertPen()

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

    # 处理逻辑是当出现一个新的K线的时候,函数对最后的三个K线位置做判断.注意不是最后一个K线
    def insertType(self, candle):

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

        # 引用实例变量纪录最后访问分型队列的最后位置
        self.pen_index = 0

        # 指针指向分型结构容器
        self.types = types
        
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

    def insertPen(self):

        # 遍历分型结构发现笔结构
        # 最后一个分型结构不存在构成笔的可能,省去最后一个分型结构的遍历

        # TODO 2016-03-29. 对全局分型做处理未能处理到最后一笔的实现也会导致当前的迟滞
        while self.pen_index < self.types.size() - 1:

            curType = self.types.container[self.pen_index]

            if curType.getPos() == 'Up':

                # 调用朝下侦查函数发现对于笔结构的底分型,并返回对应的分型结构在数组中的索引
                nextIndex = self.probeDown()

                # nextIndex == -1说明侦查函数找不到合适的分型结构,仅有在遍历至分型数组结束时才可能发生
                if nextIndex != -1:

                    # 构造笔字典结构
                    pen = Pen(curType.candle.getHigh(),
                              self.types.container[self.pen_index].candle.getLow(),
                              curType,
                              self.types.container[self.pen_index],
                              'Down')

                    self.container.append(pen)

                else:
                    break

            elif curType.getPos() == 'Down':

                nextIndex = self.probeUp()

                if nextIndex != -1:

                    pen = Pen(self.types.container[self.pen_index].candle.getHigh(),
                              curType.candle.getLow(),
                              curType,
                              self.types.container[self.pen_index],
                              'Up')

                    self.container.append(pen)

                else:
                    break

        self.__merge_pen()


    def probeUp(self):

        cur_high = self.types.container[self.pen_index].candle.getHigh()
        cur_low = self.types.container[self.pen_index].candle.getLow()

        # 由于存在向前延伸的行为,数组遍历最大仅能到倒数第二个
        for j in range(self.pen_index, self.types.size() - 1):

            # 当前分型为顶分型
            if self.types.container[j].getPos() == 'Up':

                # 如果当前顶分型的高点高于已记录的出现过的最高顶分型,则更新最高点数据,并保持当前分型所在数组指针
                if self.types.container[j].candle.getLow() > cur_low and \
                    self.types.container[j].candle.getHigh() > cur_high:

                    # 记录最后满足条件的信息
                    cur_high = self.types.container[j].candle.getHigh()
                    self.pen_index = j

                    # 如果当前顶分型的下一个分型为底分型,同时底分型的低点低于当前顶分型的高点,则说明构造潜在向下笔的条件成立
                    # 此时认为构造当前向上笔完成,返回已记录的最高顶分型指针
                    if self.types.container[j+1].getPos() == 'Down' and \
                        self.types.container[j+1].candle.getHigh() < self.types.container[j].candle.getHigh() and \
                        self.types.container[j+1].candle.getLow() < self.types.container[j].candle.getLow():

                        return self.pen_index

                    # 或者下一笔虽然为通向笔,但具有反向性质
                    elif self.types.container[j+1].getPos() == 'Up' and \
                        self.types.container[j+1].candle.getHigh() < self.types.container[j].candle.getHigh() and \
                        self.types.container[j+1].candle.getLow() < self.types.container[j].candle.getLow():

                        return self.pen_index

        # 遍历结束,返回结束标示
        return -1

    def probeDown(self):

        cur_high = self.types.container[self.pen_index].candle.getHigh()
        cur_low = self.types.container[self.pen_index].candle.getLow()

        # 由于存在向前延伸的行为,数组遍历最大仅能到倒数第二个
        for j in range(self.pen_index, self.types.size() - 1):

            if self.types.container[j].getPos() == 'Down':

                # 构成向下笔的顶底分型必须同时满足下面条件是为了避开包含关系
                if self.types.container[j].candle.getLow() < cur_low and \
                    self.types.container[j].candle.getHigh() < cur_high:

                    # 记录最后满足条件的信息
                    cur_low = self.types.container[j].candle.getLow()
                    self.pen_index = j

                    # 要同时满足以下条件才能构成笔
                    # 下一个分型为反向分型.目前的实现是认为出现反向分型则此笔结束
                    # 构成向上笔的顶底分型必须同时满足条件以避开包含关系
                    if self.types.container[j+1].getPos() == 'Up' and \
                        self.types.container[j+1].candle.getHigh() > self.types.container[j].candle.getHigh() and \
                        self.types.container[j+1].candle.getLow() > self.types.container[j].candle.getLow():

                        return self.pen_index

                    # 或者下一笔虽然为同向笔,但具有反向性质
                    elif self.types.container[j+1].getPos() == 'Down' and \
                        self.types.container[j+1].candle.getHigh() > self.types.container[j].candle.getHigh() and \
                        self.types.container[j+1].candle.getLow() > self.types.container[j].candle.getLow():

                        return self.pen_index

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
                            self.pens_stack.append(copy.deepcopy(self.container[self.pens_index-2]))
                            self.pens_stack_delay.append(copy.deepcopy(self.container[self.pens_index-2]))

                            # 更新上一向下笔底部属性
                            self.container[self.pens_index-2].low = self.container[self.pens_index].low
                            self.container[self.pens_index-2].endType = self.container[self.pens_index].endType

                            # 销毁当前笔以及前一个与此笔相连的向上笔
                            # 注意销毁顺序必须是由后向前,否则会误删其他笔
                            self.container.pop(self.pens_index)

                            # 在删除笔前,保存此笔于堆栈
                            self.pens_stack.append(copy.deepcopy(self.container[self.pens_index-1]))
                            self.pens_stack_delay.append(copy.deepcopy(self.container[self.pens_index-1]))

                            self.container.pop(self.pens_index-1)

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
                        self.container[self.pens_index-1].high = post_pen.high
                        self.container[self.pens_index-1].endType = post_pen.endType

                        # 销毁当前笔以及后一个向上笔
                        self.container.pop(self.pens_index+1)
                        self.container.pop(self.pens_index)

                    # 最后一种情况是不合法向下笔被前一笔完全包含,这和第一个情况相反
                    # 同时不合法笔后面的向上笔也被前一向上笔完全包含
                    # 不合法笔以及后一向上笔将会被销毁,同时与后向上笔相连的向下笔高点指向前一向上笔的高点
                    elif pre_pen.low < self.container[self.pens_index].low and post_pen.high < pre_pen.high:

                        # 此场景的处理要遍历并删除到当前笔往后两笔的地方
                        if self.size() - self.pens_index > 2:

                            self.container[self.pens_index+2].high = pre_pen.high
                            self.container[self.pens_index+2].beginType = pre_pen.beginType

                            # 不合法笔以及与其相连的后一向上笔被销毁
                            self.container.pop(self.pens_index+1)
                            self.container.pop(self.pens_index)

                        # 如果此场景不满足了, 就暂时不做处理, 如果后面还有一笔的话也有可能可以处理笔合并
                        else:
                            self.pens_index += 1
                            break

                # 处理向上的不合法笔,逻辑与向下笔处理一致
                else:

                    pre_pen = self.container[self.pens_index-1]
                    post_pen = self.container[self.pens_index+1]

                    if pre_pen.high <= self.container[self.pens_index].high:

                        if self.pens_index - 2 >= 0:

                            # 2016-03-21
                            # 在笔修改前,保存此笔于堆栈
                            self.pens_stack.append(copy.deepcopy(self.container[self.pens_index-2]))

                            self.container[self.pens_index-2].high = self.container[self.pens_index].high
                            self.container[self.pens_index-2].endType = self.container[self.pens_index].endType

                            self.container.pop(self.pens_index)

                            # 2016-03-21
                            self.pens_stack.append(copy.deepcopy(self.container[self.pens_index-1]))

                            self.container.pop(self.pens_index-1)

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

                        self.container[self.pens_index-1].low = post_pen.low
                        self.container[self.pens_index-1].endType = post_pen.endType
                        self.container.pop(self.pens_index+1)
                        self.container.pop(self.pens_index)

                    elif pre_pen.high > self.container[self.pens_index].high and post_pen.low > pre_pen.low:

                        if self.size()-self.pens_index > 2:

                            self.container[self.pens_index+2].low = pre_pen.low
                            self.container[self.pens_index+2].beginType = pre_pen.endType
                            self.container.pop(self.pens_index+1)
                            self.container.pop(self.pens_index)

                        else:
                            self.pens_index += 1
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
        pen_2 = self.container[self.pens_stack_index+2]

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
                self.container.pop(self.pens_stack_index+2)

                # 在偏置为1的位置恢复向上笔
                self.container.insert(self.pens_stack_index+1, copy.deepcopy(legend_pen_r))

                # 在偏置为2的位置新插入向下笔
                self.container.insert(self.pens_stack_index+2, copy.deepcopy(pen))

                self.container.pop(self.pens_stack_index+3)

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


def test(year, month, count):

    m_container = Hour_Candle_Container()

    m_types = Type_Container(m_container)

    m_pens = Pen_Container(m_types)

    m_container.loadDB(year, month, count, m_types, m_pens)

    ax_1 = plt.subplot(211)

    ax_2 = plt.subplot(212)

    draw_stocks(m_container.container, m_types.container, ax_1, ax_2)

    draw_pens(m_container.container, m_pens.container, ax_1)

    Candle_Container.closeDB()

# 画K线算法.内部采用了双层遍历,算法简单,但性能一般
def draw_stocks(stocks, types, ax_1, ax_2):

    c = 'b'

    piexl_x = []

    """
    DIF = []
    DEA = []
    MACD = []
    """

    height = []
    low = []
    c = []

    for i in range(len(stocks)):

        piexl_x.append(i)

        """
        DIF.append(stocks[i]['DIF'])
        DEA.append(stocks[i]['DEA'])
        MACD.append(stocks[i]['MACD'])
        """

        height.append(stocks[i].getHigh() - stocks[i].getLow())
        low.append(stocks[i].getLow())

        j = 0
        c.append('g')

        while j < len(types):

            if pd.Timestamp(pd.datetime(stocks[i].getYear(),
                                        stocks[i].getMonth(),
                                        stocks[i].getDay(),
                                        stocks[i].getHour())) == \
                    pd.datetime(types[j].candle.getYear(),
                                types[j].candle.getMonth(),
                                types[j].candle.getDay(),
                                types[j].candle.getHour()):

                c[i] = 'r'
                break

            else:
                j += 1

    ax_1.bar(piexl_x, height, 0.8, low, color = c)

    """
    ax_2.plot(piexl_x, DIF, color='#9999ff')
    ax_2.plot(piexl_x, DEA, color='#ff9999')
    ax_2.bar(piexl_x, MACD, 0.8, color='g')
    """

def draw_pens(stocks, pens, ax):

    date_index = {pd.Timestamp(pd.datetime(stocks[i].getYear(),
                                           stocks[i].getMonth(),
                                           stocks[i].getDay(),
                                           stocks[i].getHour())).strftime('%Y-%m-%d %H:%M:%S'): i for i in range(len(stocks))}

    piexl_x = []
    piexl_y = []

    for j in range(len(pens)):

        # 利用已经初始化的Date:Index字典,循环遍历pens数组以寻找其对于时间为关键值的X轴坐标位置
        # 添加起点
        piexl_x.append(date_index[pd.Timestamp(pd.datetime(pens[j].beginType.candle.getYear(),
                                                           pens[j].beginType.candle.getMonth(),
                                                           pens[j].beginType.candle.getDay(),
                                                           pens[j].beginType.candle.getHour())).strftime('%Y-%m-%d %H:%M:%S')])

        # 添加终点
        piexl_x.append(date_index[pd.Timestamp(pd.datetime(pens[j].endType.candle.getYear(),
                                                           pens[j].endType.candle.getMonth(),
                                                           pens[j].endType.candle.getDay(),
                                                           pens[j].endType.candle.getHour())).strftime('%Y-%m-%d %H:%M:%S')])

        if pens[j].pos == 'Down':

            # 如果笔的朝向向下,那么画线的起点为顶分型的高点,终点为底分型的低点
            piexl_y.append(pens[j].beginType.candle.getHigh())
            piexl_y.append(pens[j].endType.candle.getLow())

        # 如果笔的朝向向上,那么画线的起点为底分型的低点,终点为顶分型的高点
        else:

            piexl_y.append(pens[j].beginType.candle.getLow())
            piexl_y.append(pens[j].endType.candle.getHigh())

    # 画线程序调用
    ax.plot(piexl_x, piexl_y, color='m')


def close():

    plt.close()

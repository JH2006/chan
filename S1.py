# -*- coding: utf-8 -*-

import copy
import Event

# 中枢Mean Reversion操作的Benckmark
# 每次Mean Reversion操作都以中枢中点为基准，不具有实际操作意义，但提供了此模型的一个基础参考
class S1:

    _trans = []

    def __init__(self, candles, types, pens, hubs):

        self._signals = {}

        # 基本信息访问结构
        self._candles = candles
        self._types = types
        self._pens = pens
        self._hubs = hubs

        self._entryPrice = -1
        self._exitPrice = -1

        self._rPrice = -1

        self._curTran = []

        self._i = 0

        self._curHub = None

        self._trends = 0

        self._curSize = 0

    def process(self, event):

        self.exit(event)

        self.enter(event)

    def enter(self,event):

        try:

            #self._curHub = self._hubs[len(self._hubs) - 1]
            self._curHub = event._dict['hub']

        except:

            if __debug__:

                print('Strategy--exit() over')

                return

        # 第一个中枢不操作
        if self._curHub.pos == '--':

            return

        print('###########################')
        print('Trade id', self._i)

        # 中枢生成具有延迟性,最后的买卖点需要以最后一根K线收盘价为参考,而不能直接以中枢的高点为做空价格
        # TODO:当前实现比较粗糙,没有做任何关于当下K线和中枢关系的判断过滤,直接做Enter操作

        #lastCandle = self._candles[len(self._candles) - 1]
        lastCandle = event._dict['can']
        self._entryPrice = lastCandle.getClose()

        self._curTran.append(self._curHub.pos)
        print('Hub pos:', self._curHub.pos)
        print('begin K of Hub:', self._curHub.s_pen.beginType.candle_index)

        self._curSize = self.position(event)

        if self._curSize == 0:

            self._curTran.append(0)
            self._curTran.append(0)
            self._curTran.append(0)
            self._curTran.append(0)

            self._entryPrice = 0

            return

        print('pos size', self._curSize)

        self._curTran.append(self._curSize)

        self._rPrice = (self._curHub.ZD + self._curHub.ZG) / 2

        if self._curHub.pos == 'Up':

            self._curTran.append(self._rPrice)
            print('benchmark entry(mid hub):', self._rPrice)

            self._curTran.append(self._entryPrice)
            print('pra entry(last K of hub):', self._entryPrice)

            self._curTran.append(abs(self._entryPrice - self._rPrice))
            print('gap:', self._entryPrice - self._rPrice)


        else:

            self._curTran.append(self._rPrice)
            print('benchmark entry(mid hub)::', self._rPrice)

            self._curTran.append(self._entryPrice)
            print('pra entry(last K of hub):', self._entryPrice)

            self._curTran.append(abs(self._entryPrice - self._rPrice))
            print('gap:', self._entryPrice - self._rPrice)

    def exit(self,event):

        if self._entryPrice == -1:

            return

        if self._entryPrice == 0:

            self._curTran.append(0)
            self._curTran.append(0)
            self._curTran.append(0)
            self._curTran.append(0)
            self._curTran.append(0)

            S1._trans.append(copy.deepcopy(self._curTran))

            self._curTran.clear()

            self._entryPrice = -1

            self._i += 1

            return

        #curHub = self._hubs[len(self._hubs) - 1]
        curHub = event._dict['hub']

        midPrice = (curHub.ZG + curHub.ZD) / 2

        #lastCandle = self._candles[len(self._candles) - 1]
        lastCandle = event._dict['can']

        exitP = lastCandle.getClose()

        # 当下交易中枢向上
        if self._curHub.pos == 'Up':

            profit_1 = self._rPrice/midPrice - 1
            profit_2 = self._entryPrice/exitP - 1

        # 当下交易中枢向下
        else:

            profit_1 = midPrice/self._rPrice - 1
            profit_2 = exitP/self._entryPrice - 1

        print('pre hub pos:', self._curHub.pos)
        print('cur hub pos:', curHub.pos)
        print('cur hub id:', curHub.s_pen.beginType.candle_index)

        self._curTran.append(midPrice)
        print('benchmark exit(mid hub):', midPrice)

        self._curTran.append(exitP)
        print('pra exit(last k)', exitP)

        print('gap:', exitP - midPrice)
        self._curTran.append(abs(exitP - midPrice))

        self._curTran.append(profit_1)
        print('benchmark gain:', profit_1)

        self._curTran.append(profit_2)
        print('pra gain:', profit_2)

        print('trade id', self._i)
        print('###########################')

        S1._trans.append(copy.deepcopy(self._curTran))

        self._curTran.clear()

        self._entryPrice = -1

        self._i += 1

    def position(self,event):

        try:

            #preHub_1 = self._hubs[len(self._hubs) - 2]

            preHub_1 = event._dict['pre']

            if preHub_1.pos != self._curHub.pos:

                posSize = 0.1

                self._trends = 0

            else:

                self._trends += 1

                if self._trends == 1:

                    posSize = 0.4

                elif self._trends == 2:

                    posSize = 0.5

                else:

                    posSize = 0

        except:

            print('Strategy--position() over board')

            posSize = 0.1

        return posSize


"""
 中枢第一次延伸成功时调用
 Benckmark进入价格（次优）：中枢边界点
 Benchmark进入价格（最优）：中枢中间价
 实际进入价格：中枢末端K线收盘价
 实际进入价格：当下K线收盘价

 Benckmark离开价格（次优）：中枢边界点
 Benchmark离开价格（最优）：中枢中间价
 离场价格：中枢末端K线收盘价
 实际离场价格: 当下K线收盘价
"""

class S2:

    def __init__(self):

        # 当下K线价格(实际价格)
        self._entryPrice = -1
        self._exitPrice = -1

        # 中枢末端K线价格(理论价)
        self._rPrice = -1

        # 中枢中间价格(理论价)
        self._mPrice = -1

        # 当前还在执行的交易，由class Tran的实例构成
        self._curTran = {}

        # 交易记录存档
        self._trans = []

        # 交易编码(用于调试)
        self._i = 0

        # 当下中枢
        self._curHub = None

        # 前一中枢，用于Position计算
        self._preHub = None

        # 中枢在趋势中的位置
        self._trends = 0

        # 仓位信息
        self._curSize = 0

        # 和策略实体存在强相关的事件监听实体
        self._monitor = None

        # 是否交易已经发生
        # 当前中枢如果发生了交易就设置为True
        self._isTraded = False

    def __del__(self):

        self._trans = []
        self._curTran = []

    def process(self, event):

        self.exit(event)

        self.enter(event)

    def enter(self, event):

        try:

            self._curHub = event._dict['hub']

        except:

            if __debug__:

                print('Strategy--exit() 中枢访问越界')

                return

        # 第一个中枢不操作
        if self._curHub.pos == '--':

            return

        print('###########################')
        print('Tran ID:', self._i)

        # 中枢生成具有延迟性,最后的买卖点需要以最后一根K线收盘价为参考,而不能直接以中枢的高点为做空价格
        lastCandle = event._dict['can']
        self._entryPrice = lastCandle.getClose()

        # 1
        self._curTran.append(self._curHub.pos)
        print('Hub Pos:', self._curHub.pos)
        
        # 2
        self._curTran.append(self._curHub.e_pen.endType.candle_index)
        print('3th pen K:', self._curHub.e_pen.endType.candle_index)

        # 3
        self._curTran.append(event._dict['len_cans'])
        print('entry K :', event._dict['len_cans'])

        self._curSize = self.position(event)

        if self._curSize == 0:

            self._curTran.append(0)
            self._curTran.append(0)
            self._curTran.append(0)
            self._curTran.append(0)
            self._curTran.append(0)
            self._curTran.append(0)

            self._entryPrice = 0

            self._monitor._e.unregister(Event.Monitor.CAN_BORN, self._monitor.can_born)
            print('illegal position')

            return

        print('position size', self._curSize)

        # 4
        self._curTran.append(self._curSize)

        if self._curHub.pos == 'Up':

            self._rPrice = self._curHub.ZG

        else:

            self._rPrice = self._curHub.ZD

        # 5 ZG
        self._curTran.append(self._curHub.ZG)

        # 6 ZD
        self._curTran.append(self._curHub.ZD)

        print('ZG:', self._curHub.ZG, '  ZD:', self._curHub.ZD)

        # 7 理论价格 -- 中枢边界值
        self._curTran.append(self._rPrice)
        print('Benchmark entry point(edge of hub):', self._rPrice)

        # 8 理论最优价格 -- 中枢平均值
        self._mPrice = (self._curHub.ZG + self._curHub.ZD) / 2
        self._curTran.append(self._mPrice)
        print('Benchmark entry point(mid of hub):', self._mPrice)

        # 9
        self._curTran.append(self._entryPrice)
        print('Practical entry point(current K close):', self._entryPrice)

        print('Hub ZG:', self._curHub.ZG, 'Hub ZD:', self._curHub.ZD)

        self._monitor._e.unregister(Event.Monitor.CAN_BORN, self._monitor.can_born)

    def exit(self, event):

        if self._entryPrice == -1:

            return

        if self._entryPrice == 0:

            self._curTran.append(0)
            self._curTran.append(0)
            self._curTran.append(0)
            self._curTran.append(0)
            self._curTran.append(0)
            self._curTran.append(0)
            self._curTran.append(0)
            self._curTran.append(0)
            self._curTran.append(0)

            S2._trans.append(copy.deepcopy(self._curTran))

            self._curTran.clear()

            self._entryPrice = -1

            self._i += 1

            return

        curHub = event._dict['hub']

        if curHub.pos == 'Up':

            ePrice = curHub.ZD

        else:

            ePrice = curHub.ZG
        
        mPrice = (curHub.ZG + curHub.ZD) / 2

        lastCandle = event._dict['can']

        exitP = lastCandle.getClose()

        print('Pre Hub.Pos:', self._curHub.pos)
        print('Current Hub Pos:', curHub.pos)

        # 1
        print('3th pen K:', curHub.e_pen.endType.candle_index)
        self._curTran.append(curHub.e_pen.endType.candle_index)

        # 2
        print('Exit K:', event._dict['len_cans'])
        self._curTran.append(event._dict['len_cans'])

        # 3
        self._curTran.append(curHub.ZG)

        # 4
        self._curTran.append(curHub.ZD)

        print('ZG:', self._curHub.ZG, '  ZD:', self._curHub.ZD)

        # 5
        print('Benchmark Exit point(edge of hub):', ePrice)
        self._curTran.append(ePrice)
        
        # 6
        print('Benchmakr Exit point(mid of hub ):', mPrice)
        self._curTran.append(mPrice)

        # 7
        self._curTran.append(exitP)
        print('practical exit point(current K close):', exitP)

        if self._curHub.pos == 'Up':

            profit_1 = self._mPrice/mPrice - 1 
            profit_2 = self._entryPrice/exitP - 1
            
        else:
             
            profit_1 = mPrice/self._mPrice - 1
            profit_2 = exitP/self._entryPrice - 1  
                 
        # 8
        self._curTran.append(profit_1)
        print('理论获利:', profit_1)

        # 9
        self._curTran.append(profit_2)
        print('实际获利:', profit_2)

        print('trend id', self._i)
        print('###########################')

        S2._trans.append(copy.deepcopy(self._curTran))

        self._curTran.clear()

        self._entryPrice = -1

        self._i += 1

        # 一笔交易完成，保存可交易的当前中枢准备用于趋势计算
        # 注：不能形成交易的中枢不统计
        self._preHub = None
        self._preHub = copy.deepcopy(self._curHub)

    def position(self, event):

        try:

            preHub_1 = self._preHub

            if preHub_1.pos != self._curHub.pos:

                posSize = 0.1

                self._trends = 0

            else:

                self._trends += 1

                if self._trends == 1:

                    posSize = 0.4

                elif self._trends == 2:

                    posSize = 0.5

                else:

                    posSize = 0

        except:

            print('Strategy--position() over range')

            posSize = 0.1

        return posSize

    # 2016-07-03
    # 新中枢生成相应接口
    # 新中枢生成都是上一次交易的清仓时机
    # 新中枢生成也是新交易建仓时机
    def hub_born(self, event):

        curHub = event._dict['hub']

        # 每次产生新中枢的时候都对上一个中枢是否有发生交易做判断
        if not self._isTraded:

            preHub = self._curHub

            try:

                if preHub.ZD > curHub.ZG:

                    event._dict['hub'].pos = 'Down'

                elif preHub.ZG < curHub.ZD:

                    event._dict['hub'].pos = 'Up'

                elif preHub.ZG < curHub.ZG and preHub.ZG > curHub.ZD:

                    event._dict['hub'].pos = 'Up'

                elif preHub.ZD < curHub.ZG and preHub.ZD > curHub.ZD:

                    event._dict['hub'].pos = 'Down'

                else:

                    if preHub.pos == 'Down':

                        event._dict['hub'].pos = 'Up'

                    else:

                        event._dict['hub'].pos = 'Down'

            except BaseException:

                pass

        """
        新中枢生成会出现两个影响:
        生成新的建仓交易
        已经存在的交易准备平仓
        """

        try:
            t = self._curTran[Tran.START]

            # 同时判断这个新中枢导致已有交易是止损还是盈利
            # 新中枢与之前交易的中枢同向,为止损
            if self._curHub.pos == curHub.pos:

                t._op = Tran.OP_LOSS

            # 新中枢与之前中枢反向,为获利
            else:

                t._op = Tran.OP_GAIN

            # 转移已有交易
            self._curTran[Tran.PROCESS] = t

        except BaseException:

            return

        hub_k_pos = curHub.e_pen.endType.candle_index
        last_k_post = event._dict['len_cans']

        print('New Hub ID:', event._dict['hub_id'], 'Last C of Hub:', hub_k_pos, 'Current C:', last_k_post)

        # 当下不满足建仓交易条件,需要追踪单一K线级别状态变化
        # 注册K线生成事件监听接口
        # 根据当前的交易策略,只有一个地方实现此监听接口注销:买卖点成功执行 self.enter()
        if not self.isEnter(event):
            self._monitor._e.register(Event.Monitor.CAN_BORN, self._monitor.enter)

            # 复位交易指示器
            self._isTraded = False

        # 平仓条件和建仓条件独立存在
        # 当下不满足平仓交易条件,需要追踪单一K线级别状态变化
        # 注册K线生成事件监听接口
        # 根据当前的交易策略,只有一个地方实现此监听接口注销:买卖点成功执行 self.exit()
        if not self.isExit(event):

            self._monitor._e.register(Event.Monitor.CAN_BORN, self._monitor.exit)

    """
    一个Common的对新K线生成的响应接口
    主要负责对当下新生成K线做一些判断是否可以执行买卖逻辑
    由Event.Monitor.can_born调用
    """
    def isTrade(self, event):

        self.isEnter(event)

    """
    完成建仓逻辑的判断
    1. 5根K线
    2. Cross信号出现
    """
    def isEnter(self, event):

        curHub = event._dict['hub']
        last_k_post = event._dict['len_cans']

        #print('Calling isTrade, Current Can ID', last_k_post)

        curCandle = event._dict['can']

        close = curCandle.getClose()

        try:

            mid = (curHub.ZD + curHub.ZG)/2

        except BaseException:

            return 

        hub_k_pos = curHub.e_pen.endType.candle_index

        # Single-1
        if curHub.pos == 'Up' and mid <= close <= curHub.ZG:

            cross = True

            s = 'Cross meet mid <= close <= curHub.ZG' + repr(mid) + ',' + repr(close) + ',' + repr(curHub.ZG)

        elif curHub.pos == 'Down' and curHub.ZD <= close <= mid:

            s = 'Cross meet curHub.ZD <= close <= mid' + repr(curHub.ZD) + ',' + repr(close) + ',' + repr(mid)

            cross = True

        else:

            cross = False

            s = 'Cross NOT meet'

        print(s)

        # Single-2
        # 在K线数量上满足操作条件
        if last_k_post - hub_k_pos >= 5 and cross:

            # 建仓
            self.enter(event)

            # 设置交易指示器，说明交易在当前中枢发生
            self._isTraded = True

            return True

        else:

            return False

    """
    清平仓逻辑判断
    1.
    """
    def isExit(self, event):

        # 获取当下等待平仓的交易
        try:

            p_tran = self._curTran[Tran.PROCESS]

        except KeyError:

            print('无交易等待')

            return


class Tran:

    STATS = ''
    PROCESS = 'PROCESS'
    START = 'START'

    OP_LOSS = 'LOSS'
    OP_GAIN = 'GAIN'

    ENTER_K = 'ENTER_K'
    ENTER_P = 'ENTER_POINT'

    EXIT_K = 'EXIT_K'
    EXIT_P = 'EXIT_POINT'

    ENTER_HUB_ZG = 'EN_HUB_ZG'
    ENTER_HUB_ZD = 'EN_HUB_ZD'
    ENTER_HUB_M = 'EN_HUB_MID'

    EXIT_HUB_ZG = 'EX_HUB_ZG'
    EXIT_HUB_ZD = 'EX_HUB_ZD'
    EXIT_HUB_M = 'EX_HUB_MID'

    def __init__(self):

        self._buf = {}
        self._op = ''


    def __del__(self):

        self._buf.clear()




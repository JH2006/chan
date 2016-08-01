# -*- coding: utf-8 -*-

import copy
import Event
import Component

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
        lastCandle = event._dict['K']
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
        lastCandle = event._dict['K']

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

        # 交易记录存储
        # Key: id
        self._trans = {}

        # 交易编码
        self._id = 0

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
        # self._isTraded = False

        self._eTran = None
        self._xTran = None

        # Entries实体队列
        self._entries = {}

        # Exit实体队列
        self._exits = {}

        # 接口调用初始化建仓策略
        self.loadEntry()

    # 2016-07-30
    # 根据具体的策略要求组合不同的Entry
    def loadEntry(self):

        self._entries[Component.MidEntry._name] = Component.MidEntry(0.5)

        self._entries[Component.EdgeEntry._name] = Component.EdgeEntry(0.5)

    def enter(self, event):

        try:

            self._curHub = event._dict['HUB']

        except:

            print('Strategy--exit() 中枢访问越界')
            return

        # 第一个中枢不操作
        if self._curHub.pos == '--':
            return

        try:

            self._eTran = self._trans[self._id]

        except KeyError:

            if self._curHub.pos == 'Up':

                p = 'SHORT'

            else:

                p = 'LONG'

            self._eTran = Component.Tran(self._id, p)

        event._dict['TRAN'] = self._eTran

        for name in self._entries:

            if self._entries[name].order(event):

                print('###########################')
                print('Tran ID:', self._eTran._id)
                print('建仓类型:', name, '  建仓K线:', event._dict['len_cans'])
                print('成交价:', self._eTran._entries[name][0])
                print('中枢高点:', self._curHub.ZG, ' 中枢低点:', self._curHub.ZD,'  中枢方向:', self._curHub.pos)
                print('###########################')

                try:

                    t = self._trans[self._id]

                except KeyError:

                    self._trans[self._id] = self._eTran


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

        lastCandle = event._dict['K']

        exitP = lastCandle.getClose()

        #print('Pre Hub.Pos:', self._curHub.pos)
        #print('Current Hub Pos:', curHub.pos)

        # 1
        #print('中枢确认K线:', curHub.e_pen.endType.candle_index)
        self._curTran.append(curHub.e_pen.endType.candle_index)

        # 2
        #print('平仓操作K线:', event._dict['len_cans'])
        self._curTran.append(event._dict['len_cans'])

        # 3
        self._curTran.append(curHub.ZG)

        # 4
        self._curTran.append(curHub.ZD)

        #print('ZG:', self._curHub.ZG, '  ZD:', self._curHub.ZD)

        # 5
        #print('Benchmark Exit point(edge of hub):', ePrice)
        self._curTran.append(ePrice)
        
        # 6
        #print('Benchmakr Exit point(mid of hub ):', mPrice)
        self._curTran.append(mPrice)

        # 7
        self._curTran.append(exitP)
        #print('practical exit point(current K close):', exitP)

        if self._curHub.pos == 'Up':

            profit_1 = self._mPrice/mPrice - 1 
            profit_2 = self._entryPrice/exitP - 1
            
        else:
             
            profit_1 = mPrice/self._mPrice - 1
            profit_2 = exitP/self._entryPrice - 1  
                 
        # 8
        self._curTran.append(profit_1)
        #print('理论获利:', profit_1)

        # 9
        self._curTran.append(profit_2)
        #print('实际获利:', profit_2)

        #print('trend id', self._i)
        #print('###########################')

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
    def hub_gen(self, event):

        curHub = event._dict['HUB']

        self._id += 1

        # 每次产生新中枢的时候都对上一个中枢是否有发生交易做判断
        # if not self._isTraded:
        #
        #     preHub = self._curHub
        #
        #     try:
        #
        #         if preHub.ZD > curHub.ZG:
        #
        #             event.dict['hub'].pos = 'Down'
        #
        #         elif preHub.ZG < curHub.ZD:
        #
        #             event.dict['hub'].pos = 'Up'
        #
        #         elif preHub.ZG < curHub.ZG and preHub.ZG > curHub.ZD:
        #
        #             event.dict['hub'].pos = 'Up'
        #
        #         elif preHub.ZD < curHub.ZG and preHub.ZD > curHub.ZD:
        #
        #             event.dict['hub'].pos = 'Down'
        #
        #         else:
        #
        #             if preHub.pos == 'Down':
        #
        #                 event._dict['hub'].pos = 'Up'
        #
        #             else:
        #
        #                 event._dict['hub'].pos = 'Down'
        #
        #     except KeyError:
        #
        #         pass

        hub_k_pos = curHub.e_pen.endType.candle_index
        last_k_post = event._dict['len_cans']

        print('新中枢ID:', event._dict['hub_id'], '中枢确认K线:', hub_k_pos, '当下K线:', last_k_post)

        # 初始化所有Entry实体的交易状态为False,启动新一轮的交易
        for name in self._entries:

            self._entries[name]._ordered = False

        # 关闭建仓处理
        self._monitor._e.unregister(Event.Monitor.K_GEN, self._monitor.enter)

        self._monitor._e.register(Event.Monitor.K_GEN, self._monitor.tradeCommit)

    # 2016-08-01
    # 对中枢确认的辅助条件,根据具体认为的情况设定
    # 当前为确认中枢临时第4笔
    def tradeCommit(self, event):

        hub = event._dict['HUB']
        pens = event._dict['PENS']
        last_k_post = event._dict['len_cans']

        first_pen_index = hub.s_pen_index

        try:

            third_pen = pens[first_pen_index + 2]

        except IndexError:

            return False

        if third_pen.legal():

            try:

                fourth_pen = pens[first_pen_index + 3]

                if fourth_pen.legal():

                    print('第四笔确认--笔末端K:', fourth_pen.endType.candle_index, '当下K:', last_k_post)

                    self._monitor._e.unregister(Event.Monitor.K_GEN, self._monitor.tradeCommit)

                    # 启动建仓处理
                    self._monitor._e.register(Event.Monitor.K_GEN, self._monitor.enter)

                    return True

                else:

                    return False

            except IndexError:

                return False

    def __del__(self):

        self._trans.clear()

        self._entries.clear()

        self._exits.clear()




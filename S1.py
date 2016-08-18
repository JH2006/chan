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


class S2:

    def __init__(self):

        # 交易记录存储
        # Key: id
        self._trans = {}

        # 交易编码
        self._id = -1

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

         # 代表当下交易
        self._eTran = None

        # 待平仓交易队列
        self._xTrans = []

        # Entries实体队列
        self._entries = {}

        # Exit实体队列
        self._exits = {}

        # 止损实体
        self._stops = {}

        # 接口调用初始化建仓策略
        self.loadEntry()
        self.loadExit()
        self.loadStop()

    # 2016-07-30
    # 根据具体的策略要求组合不同的Entry
    def loadEntry(self):

        #self._entries[Component.MidEntry._name] = Component.MidEntry(0.3)

        self._entries[Component.EdgeEntry._name] = Component.EdgeEntry(0.3)

        #self._entries[Component.StepEntry._name] = Component.StepEntry(0.4)

    def loadExit(self):

        #self._exits[Component.MidExit._name] = Component.MidExit(0.5)

        self._exits[Component.EdgeExit._name] = Component.EdgeExit(0.5)

    def loadStop(self):

        #self._stops[Component.StopExit._name] = Component.StopExit(1)
        pass

    # enter为事件触发响应接口
    # 对应事件：Monitor.K_GEN.
    # 事件注册时机：新中枢辅助条件确认S2.trade_commit条件满足
    # 事件注销时机：新中枢生成S2.hub_gen
    def enter(self, event):

        hub = event._dict['HUB']

        # 第一个中枢不操作,无法判断方向性
        if hub.pos == '--':
            return

        # 建仓记录总数与注册的建仓策略数相同，说明建仓完全执行，直接退出
        if self._eTran is not None:

            if len(self._eTran._entries) == len(self._entries):

                return

        # 新中枢的第一个建仓记录
        else:

            if hub.pos == 'Up':

                p = 'SHORT'

            else:

                p = 'LONG'
            
            # 初始化Tran实体
            self._eTran = Component.Tran(self._id, p, hub.ZG, hub.ZD)

        # 把Tran实体做为event的一部分进行参数传递
        event._dict['TRAN'] = self._eTran

        # 对已经加载的所有建仓策略进行遍历
        for name in self._entries:

            # 如果返回True，说明策略被执行
            if self._entries[name].order(event):

                print('Tran ID:', self._eTran._id, ' 建仓类型:', name, ' 成交价:', self._eTran._entries[name][0], '  建仓K线:', event._dict['LENOFK'])

                # 新交易的出现伴随止损策略注册
                self._monitor._e.register(Event.Monitor.STOP, self._monitor.stop)

    # exit为事件触发响应接口
    # 对应事件：Monitor.K_GEN
    # 事件注册时机：新中枢生成S2.hub_gen
    # 事件注销时机：None
    def exit(self, event):

        # 用于标识判断当前待平仓的交易中是否有进一步调用平仓计算的必要
        # False表示没有平仓需要，则直接退出调用
        flag = False

        # 遍历待平仓队列
        for i, _ in enumerate(self._xTrans):

            # 仓位不为空或者没被止损平仓，继续平仓需求
            if self._xTrans[i]._entries:

                # 平仓记录总数与注册的平仓策略数不相同，说明还有平仓机会
                if len(self._xTrans[i]._exits) != len(self._exits):

                    flag = True

                    # 只要有一个平仓需求被发现就行，退出循环
                    break

        if flag is not True:

            return

        # 平仓队列输入进event进行参数传递
        event._dict['TRAN'] = self._xTrans

        # 遍历待平仓队列
        for name in self._exits:

            # 有平仓操作成功执行返回True
            if self._exits[name].order(event):

                for j, _ in enumerate(self._xTrans):

                    print('Tran ID:', self._xTrans[j]._id, ' 平仓类型:', name, ' 成交价:', self._xTrans[j]._exits[name][0], '  平仓K线:', event._dict['LENOFK'])

                    if __debug__:

                        if len(self._xTrans[j]._exits) == len(self._exits):

                            print('***********************')
                            print('Tran ID:', self._xTrans[j]._id, ' 完成!!!')

                            for name in self._xTrans[j]._entries:

                                print('建仓类型:', name, ' 成交价:', self._xTrans[j]._entries[name][0], ' 仓位:', self._xTrans[j]._entries[name][1])

                            for name in self._xTrans[j]._exits:

                                print('平仓类型:', name, ' 成交价:', self._xTrans[j]._exits[name][0], ' 仓位:', self._xTrans[j]._exits[name][1])

                            print('总收益:', self._xTrans[j].gain())

                            print('***********************')

    # stop为事件触发响应接口
    # 对应事件：Hunter_Container.isGrow
    # 事件注册时机：S2.enter新建仓交易形成
    # 事件注销时机：S2.hub_gen新中枢生成
    def stop(self, event):

        # 仓位为空，或者没有形成建仓条件，或者已经被止损平仓，没有继续止损需求，直接退出
        if not self._eTran._entries:

            return

        # 当下的交易
        event._dict['TRAN'] = self._eTran

        # 遍历已经注册的止损策略
        for name in self._stops:

            if self._stops[name].order(event):

                if __debug__:

                    print('Tran ID:', self._eTran._id, ' 止损类型:', name, ' 止损价:', self._eTran._stops[len(self._eTran._stops) - 1][Component.StopExit._name][1], '  止损K线:', event._dict['LENOFK'])

                    entries = self._eTran._stops[len(self._eTran._stops) - 1][Component.StopExit._name][0]

                    for t in entries:

                        print('止损对象:', t, '成交价:', entries[t][0])

                    if len(entries) == len(self._entries):

                        p = 0

                        for i in entries:

                            p += entries[i][0] * entries[i][1]
                        
                    else:

                        p = 0

                        for n in entries:

                            p += entries[n][0]

                        p = p / len(entries)

                    if self._eTran._placement == 'LONG':

                        g = self._eTran._stops[len(self._eTran._stops) - 1][Component.StopExit._name][1] / p - 1

                    else:

                        g = p / self._eTran._stops[len(self._eTran._stops) - 1][Component.StopExit._name][1] -1

                    print('平均成交价:', p, ' 止损价:', self._eTran._stops[len(self._eTran._stops) - 1][Component.StopExit._name][1], ' 总损失:', self._eTran.stop())

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
    # 新中枢生成响应接口
    # 新中枢生成都是之前一次交易的清仓时机
    # 新中枢生成也是新交易建仓时机
    def hub_gen(self, event):

        # 当下中枢
        curHub = event._dict['HUB']

        # 当下K线
        hub_k_pos = curHub.e_pen.endType.candle_index

        # 当下K线位置
        last_k_post = event._dict['LENOFK']

        print('新中枢ID:', event._dict['hub_id'], ' 中枢确认K线:', hub_k_pos, ' 当下K线:', last_k_post, ' 方向:', curHub.pos)

        # 关闭建仓处理
        self._monitor._e.unregister(Event.Monitor.K_GEN, self._monitor.enter)

        # 关闭止损处理
        self._monitor._e.unregister(Event.Monitor.STOP, self._monitor.stop)

        # 注册中枢确认附件条件处理
        self._monitor._e.register(Event.Monitor.K_GEN, self._monitor.trade_commit)

        # 清理待平仓队列里面已经完成平仓的交易
        tTran = []
        for i, _ in enumerate(self._xTrans):

            if self._xTrans[i]._exits:

                print('待平仓队列清空:', self._xTrans[i]._id)

            else:

                tTran.append(self._xTrans[i])

        self._xTrans = tTran

        if __debug__:

            for i, _ in enumerate(self._xTrans):

                print('待平仓交易:', self._xTrans[i]._id)
        
        # _eTran不为空说明前一中枢已经生成交易,或者已经被止损,或者等待平仓
        if self._eTran is not None:

            self._trans[self._id] = self._eTran

            #  如果建仓队列不为空,才有等待平仓的可能
            if self._eTran._entries:

                self._xTrans.append(self._trans[self._id])
                print('进入待平仓队列:', self._eTran._id)

            # 重新赋值eTran，准备开始新的建仓记录
            self._eTran = None

            # 注册平仓策略
            # 平仓操作可早于建仓启动
            self._monitor._e.register(Event.Monitor.K_GEN, self._monitor.exit)

        self._id += 1


    # 2016-08-01
    # 对中枢确认的辅助条件,根据具体认为的情况设定
    # 当前为确认中枢临时第4笔
    def trade_commit(self, event):

        hub = event._dict['HUB']
        pens = event._dict['PENS']
        last_k_post = event._dict['LENOFK']

        first_pen_index = hub.s_pen_index

        try:

            third_pen = pens.container[first_pen_index + 2]

        except IndexError:

            return False

        if third_pen.legal():

            try:

                fourth_pen = pens.container[first_pen_index + 3]

                if fourth_pen.legal():

                    print('第四笔确认--笔末端K:', fourth_pen.endType.candle_index, '当下K:', last_k_post)

                    # 去激活中枢附件判决条件
                    self._monitor._e.unregister(Event.Monitor.K_GEN, self._monitor.trade_commit)

                    # 注册建仓策略处理
                    self._monitor._e.register(Event.Monitor.K_GEN, self._monitor.enter)

                    return True

                else:

                    return False

            except IndexError:

                return False

    def __del__(self):

        self._trans = None

        self._entries = None

        self._exits = None

        self._stops = None




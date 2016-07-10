# 2016-6-10
# 交易策略模块

# 自定义模块
import Hunter
import MACD
import Currency
import copy

import pandas as pd

class Bucket:

    def __init__(self, candles):

        # 2016-04-16
        # 状态机
        self.__state = False

        # 指向本级别的Candles容器指针,本级别的K线需要通过此容器读取
        self._candles = candles

        self._candles.loadBucket(self)

        # 是否准备开始买卖点判断
        self.__isEntry = False

        # 买卖点进入操作价格点
        # 实质就是次级别走势中枢区间的最高/最低点
        self.__entry_price = 0

        # 在一个买卖点未完成的清空下不能开始新的Bucket操作
        self.__isFrozen = False

        # 这个属性是Bucket用于保存其次级别信息所用
        self.candle_container = None

        # 在K线初始化后,由具体子类分别生成各个对于的形态对象
        self.types = None

        self.pens = None

        self.hubs = None

        self.__power_MACD_entry = None
        self.__power_MACD_exit = None

        self._trader = Trader()

    def loadHubs(self, hubs):

        # 指向本级别hub_container,目前的用途在于帮忙Power_MACD获取对应的中枢信息,Bucket暂时没有使用
        self.__hub_container = hubs

    def isBucketAct(self):

        return self.__state

    # 激活Bucket的工作状态
    # 传递盈利点价格
    def activeBucket(self, exit_price):

        self.__state = True


        self.__exit_price = exit_price

        print('Bucket.activeBucket() -- exist_price:', exit_price)

    def __reset(self):

        self.hubs.reset()
        self.pens.reset()
        self.types.reset()
        self.candle_container.reset()

        print('Bucket.__reset() Bucket复位')

    def deactBucket(self):

        if self.__state:

            self.__state = False

            print('Bucket.deactBucket()')

        self.deactEntry()

        self.__reset()

        # 2016-05-09
        # 测试代码
        # False说明还未生成交易,这类去激活是由于Bucket反向出现导致或者同向连续出现
        if self._trans.trade_index == False:

            self._trans.decatTran()

    def exist_price(self):

        return self.__exit_price

    # 2016-04-13
    # 以高级别的笔做为次级别数据的生成条件
    # 抽象接口
    def loadCandleID(self, t):

        pass


    # 2016-04-23
    # 加入Bucket的一个方向属性,这个属性用于记录当前的Bucket所对应的本级别的走势方向,次级别的走势方向只有和本级别一致的时候才有买卖点操作的机会
    def setTrending(self, trend):

        self.__trend = trend

    def isSameTrending(self, trend):

        if self.__trend == trend:

            return True

        else:
            return False

    def activeEntry(self, entry_price):

        # 2016-04-24
        # 如果买卖点已经激活,不会再激活第二次,防止连续出现同向中枢的时候entry_price被连续更新
        if self.__isEntry:

            return

        self.__entry_price = entry_price

        self.__isEntry = True

        print('Bucket.activeEntry() -- entry:', entry_price)

        # 从逻辑管理上,MACD的判断时机应该和买卖点的具体确定时间一致
        # 买卖点确定的时候就是MACD力量计算的时间点
        # 买卖点去激活就是已经完成计算的MACD被注销的时间点
        # Power_MACD.init()
        self.__power_MACD_entry.loadMACD(self.__hub_container)
        self.__power_MACD_exit.loadMACD(self.__hub_container)

        # 2016-05-09
        # 测试代码
        self._trans.entry_index = True

    def modEntry(self, new_price):

        self.__entry_price = new_price

        self.__power_MACD_exit.updateMACD(self.__hub_container)

    def deactEntry(self):

        if self.__isEntry:

            self.__isEntry = False

            self.__entry_price = 0

            print('Bucket.deactEntry()')

            self.__power_MACD_entry.reset()
            self.__power_MACD_exit.reset()

    def isEntryAct(self):

        return self.__isEntry

    # 2016-05-11
    # 留意这里一直用的是收盘价进行比较
    # 因为目前的实现是在本级别K线形成后才能加载次级别K线，次级别的K线相比本级别已经是历史数据，当买卖点被次级别形态所确认的时候
    # 其实已经是历史数据，最早的交易也要等到一下本级别K线出现，所以当前K线的Close做为交易价格最接近实际情况
    def tradingEntry(self, candle):

        if self.__isEntry and self.__state:

            # short
            if self.__trend == 'Up':

                if candle.getClose() > self.__entry_price:

                    if self.__power_MACD_exit.candles_MACD < self.__power_MACD_entry.candles_MACD:

                        print('Bucket.tradingEntry(),做空!!!')

                        self._trader.exit = self.__exit_price

                        self._trader.traded = candle.getClose()
                        self._trader.stop = self._trader.stopping()
                        self._trader.isLong = False

                        print('Bucket.tradingEntry() 交易进场价格:', candle.getClose(), '止损价格:', self._trader.stop)
                        print('Bucket.tradingEntry() MACD力量对比 Entry VS Exit--:', self.__power_MACD_entry.candles_MACD, self.__power_MACD_exit.candles_MACD)

                        # 2016-05-09
                        # 测试代码
                        self._trans.trade_index = True
                        self._trans.cur_tran.power(self.__power_MACD_exit.candles_MACD, self.__power_MACD_entry.candles_MACD)
                        self._trans.cur_tran.execute('做空')

                        # 2016-04-24
                        # 一旦成功进行买卖操作,当前Bucket的状态数据应该全部清空.并且在当前买卖未完成的清空下,不应该再出现新的Buckect
                        self.froBucket()

                else:

                    print('Bucket.tradingEntry() MACD力量对比 Entry VS Exit--:', self.__power_MACD_entry.candles_MACD, self.__power_MACD_exit.candles_MACD)

                    print('Bucket.tradingEntry() MACD力量对比失败, 去激活Bucket')

                    self.deactBucket()


            # long
            else:

                if candle.getClose() < self.__entry_price:

                    if self.__power_MACD_exit.candles_MACD > self.__power_MACD_entry.candles_MACD:

                        print('Bucket.tradingEntry(),做多!!!')

                        self._trader.exit = self.__exit_price
                        self._trader.traded = candle.getClose()
                        self._trader.stop = self._trader.stopping()
                        self._trader.isLong = True

                        print('Bucket.tradingEntry() 交易进场价格:', candle.getClose(), '止损价格:', self._trader.stop)
                        print('Bucket.tradingEntry() MACD力量对比 Entry VS Exit--:', self.__power_MACD_entry.candles_MACD, self.__power_MACD_exit.candles_MACD)

                        # 2016-05-09
                        # 测试代码
                        self._trans.trade_index = True
                        self._trans.cur_tran.power(self.__power_MACD_exit.candles_MACD, self.__power_MACD_entry.candles_MACD)
                        self._trans.cur_tran.execute('做多')

                        # 2016-04-24
                        # 一旦成功进行买卖操作,当前Bucket的状态数据应该全部清空.并且在当前买卖未完成的清空下,不应该再出现新的Buckect
                        self.froBucket()


                else:

                    print('Bucket.tradingEntry() MACD力量对比 Entry VS Exit--:', self.__power_MACD_entry.candles_MACD, self.__power_MACD_exit.candles_MACD)

                    print('Bucket.tradingEntry() MACD力量对比失败, 去激活Bucket')

                    self.deactBucket()

    # 2016-05-20
    def tradingExit(self, candle):

        return self._trader.tradingExit(candle, self._trans)

    def isFrozen(self):

        return self.__isFrozen

    def froBucket(self):

        self.__isFrozen = True

        self.deactBucket()

        print('Bucket.froBucket() 交易执行,冻结Bucket')

    def deFroBucket(self):

        self.__isFrozen = False

        print('Bucket.deFroBucket() 解冻Bucket')

    # 任何额外需要初始化的代码放在这里
    def init(self):

        # 在K线初始化后,分别生成各个对于的形态对象
        self.types = Hunter.Type_Container(self.candle_container)

        self.pens = Hunter.Pen_Container(self.types)

        # 2016-05-03
        # MACD做为一种辅助性的判断因子应该随着形态的变化而处于不同的状态,不应该独立于形态之外发展
        # 考虑到目前Bucket管理了形态变化的各个关键状态,把MACD做为Bucket的一个属性设计也就符合逻辑了
        self.__power_MACD_entry = MACD.Power_MACD_Entry(self._candles)
        self.__power_MACD_exit = MACD.Power_MACD_Exit(self._candles)

    # 2016-05-22
    # 接口实现用于关联Tran_Container
    def loadTrans(self, trans):

        self._trans = trans

"""
class Hour_Bucket:

    def __init__(self, candles):

        # 2016-04-16
        # 状态机
        self.__state = 0

        # 2016-04-17
        # 记录最后一个被记录的Candle的位置
        self.__last_candle = 0

        # 指向本级别的Candles容器指针,本级别的K线需要通过此容器读取
        self.__candles = candles

        self.candle_container = Ten_Min_Candle_Container()

        # 在K线初始化后,分别生成各个对于的形态对象
        self.types = Type_Container(self.candle_container)

        self.pens = Pen_Container(self.types)

        self.hubs = Ten_Min_Hub_Container(self.pens)


    def isActive(self):

        if self.__state == 0:

            return False

        else:

            return True

    def active(self):

        self.__state = 1

    def __reset(self):

        self.hubs.reset()
        self.pens.reset()
        self.types.reset()
        self.candle_container.reset()

    def deactive(self):

        self.__state = 0

        self.__last_candle = 0

        self.__reset()

    def loadCandle(self, candle):

        print('Bucket代码调用-loadCandle, 高级别K线时间:', candle.getYear(), candle.getMonth(), candle.getDay(), candle.getHour())

        self.candle_container.loadDB(candle.getYear(),
                                     candle.getMonth(),
                                     candle.getDay(),
                                     candle.getHour(),
                                     self.types,
                                     self.pens,
                                     self.hubs)

    # 2016-04-13
    # 以高级别的笔做为次级别数据的生成条件
    def loadCandleID(self, t):

        print('Bucket代码调用--load,高级别K线范围ID:', t)

        candle = self.__candles.container[t]

        print('Bucket代码调用--load, 高级别K线时间:', candle.getYear(), candle.getMonth(), candle.getDay(), candle.getHour())

        self.candle_container.loadDB(candle.getYear(),
                                     candle.getMonth(),
                                     candle.getDay(),
                                     candle.getHour(),
                                     self.types,
                                     self.pens,
                                     self.hubs)
"""

class Trader:

    def __init__(self):
        # 成交位
        # 此属性不仅仅是成交价位的记录,而且也是判断是否交易条件是否成熟的标示
        # 如果此属性不为0,则说明当下处于交易运行过程中,正在等待获利了结或者止损离场的出现
        # 如果为0,则说明没有处于交易运行的过程中
        # 此属于由Bucket.isTradable()进行修改 0->非0
        # 由trader.isTrading()在交易完成后修改 非0->0
        self.traded = -1

        # 获利了解位
        self.exit = 0

        # 止损位
        self.stop = 0

        # True -- Long
        # False --  Short
        self.isLong = True

    # 2016-04-23
    # 止损位设定
    def stopping(self):

        return 2 * self.traded - self.exit

    # 2016-04-24
    # 如果实际交易成功返回True
    def tradingExit(self, candle, trans):

        if self.traded != -1:

            if self.isLong:

                # 2016-05-08
                # 关于成交点触发的时候不能仅关注Close()，同时要考虑Low and High, 这和TradingEntry有本质区别
                # TradingEntry的任务是寻找在各类条件满足后最接近的可以交易的点。因为系统是以K线的方式进行分析,当下K线通过分析确认
                # 可以触发交易行为的时候,当下的K线已经不具有操作上的意义,需要等到下一个K线来执行,所以close()是最接近下一个K线可操作点的地方

                #if candle.getClose() > trader.exit:

                if candle.getHigh() > self.exit:

                    print('trader.tradingExit() 执行做多获利离场')

                    print('离场价格:', candle.getHigh(), '进场价格:', self.traded)
                    print('获利:', (candle.getHigh()/self.traded) - 1)

                    # 2016-05-09
                    # 测试代码
                    trans.exit_index = True
                    trans.existPrice(candle.getHigh())
                    trans.profiting((candle.getHigh()/self.traded) - 1)

                    self.traded = -1

                    return True

                # 2016-05-08
                # 关于成交点触发的时候不能仅关注Close()，同时要考虑Low and High
                # 在做多止损中,应该考虑Low()
                # elif candle.getClose() < trader.stop:

                elif candle.getLow() < self.stop:

                    print('trader.tradingExit() 执行做多止损离场')

                    print('离场价格:', candle.getLow(), '进场价格:', self.traded)
                    print('损失:', (candle.getLow()/self.traded) - 1)

                    # 2016-05-09
                    # 测试代码
                    trans.exit_index = True
                    trans.existPrice(candle.getLow())
                    trans.profiting((candle.getLow()/self.traded) - 1)

                    self.traded = -1

                    return True

            else:

                # 2016-05-08
                # if candle.getClose() < trader.exit:

                if candle.getLow() < self.exit:

                    print('trader.tradingExit() 执行做空获利离场')

                    print('离场价格:', candle.getLow(), '进场价格:', self.traded)
                    print('获利:', (self.traded/candle.getLow()) - 1)

                    # 2016-05-09
                    # 测试代码
                    trans.exit_index = True
                    trans.existPrice(candle.getLow())
                    trans.profiting((self.traded/candle.getLow()) - 1)

                    self.traded = -1

                    return True

                # 2016-05-08
                # elif candle.getClose() > trader.stop:
                elif candle.getHigh() > self.stop:

                    print('trader.tradingExit() 执行做空止损离场')

                    print('离场价格:', candle.getHigh(), '进场价格:', self.traded)
                    print('止损:', (self.traded/candle.getHigh()) - 1)

                    # 2016-05-09
                    # 测试代码
                    trans.exit_index = True
                    trans.existPrice(candle.getHigh())
                    trans.profiting((self.traded/candle.getHigh()) - 1)

                    self.traded = -1

                    return True

        else:

            return False

    def takeProfit(self):

        pass

    def stopLoss(self):

        pass

class Ten_Min_Bucket(Bucket):

    def __init__(self, candles):

        Bucket.__init__(self, candles)

        if isinstance(candles, Currency.AUD_Ten_Min_Candle_Container):

            self.candle_container = Currency.AUD_One_Min_Candle_Container()

        elif isinstance(candles, Currency.CAD_Ten_Min_Candle_Container):

            self.candle_container = Currency.CAD_One_Min_Candle_Container()

        elif isinstance(candles, Currency.CHF_Ten_Min_Candle_Container):

            self.candle_container = Currency.CHF_One_Min_Candle_Container()

        elif isinstance(candles, Currency.GBP_Ten_Min_Candle_Container):

            self.candle_container = Currency.GBP_One_Min_Candle_Container()

        elif isinstance(candles, Currency.EUR_Ten_Min_Candle_Container):

            self.candle_container = Currency.EUR_One_Min_Candle_Container()

        elif isinstance(candles, Currency.JPY_Ten_Min_Candle_Container):

            self.candle_container = Currency.JPY_One_Min_Candle_Container()

        self.init()

        self.hubs = Hunter.One_Min_Hub_Container(self.pens, self)

    def loadCandleID(self, t):

        candle = self._candles.container[t]

        print('Bucket.loadCandleID()-- 高级别K线ID', t, '价格:', candle.getClose())

        """
        print('Bucket.loadCandleID() -- 本级别K线时间', pd.Timestamp(pd.datetime(candle.getYear(),
                                                                                candle.getMonth(),
                                                                                candle.getDay(),
                                                                                candle.getHour(),
                                                                                candle.get10Mins()+candle.get5Mins())).strftime('%Y-%m-%d %H:%M:%S'))
        """
        """
        self.candle_container.loadDB(candle.getYear(),
                                     candle.getMonth(),
                                     candle.getDay(),
                                     candle.getHour(),
                                     candle.get10Mins(),
                                     0,
                                     self.types,
                                     self.pens,
                                     self.hubs,
                                     self)
        """

class Five_Min_Bucket(Bucket):

    def __init__(self, candles):

        Bucket.__init__(self, candles)

        if isinstance(candles, Currency.AUD_Five_Min_Candle_Container):

            self.candle_container = Currency.AUD_One_Min_Candle_Container()

        elif isinstance(candles, Currency.CAD_Five_Min_Candle_Container):

            self.candle_container = Currency.CAD_One_Min_Candle_Container()

        elif isinstance(candles, Currency.CHF_Five_Min_Candle_Container):

            self.candle_container = Currency.CHF_One_Min_Candle_Container()

        elif isinstance(candles, Currency.GBP_Five_Min_Candle_Container):

            self.candle_container = Currency.GBP_One_Min_Candle_Container()

        elif isinstance(candles, Currency.EUR_Five_Min_Candle_Container):

            self.candle_container = Currency.EUR_One_Min_Candle_Container()

        else:

            self.candle_container = Currency.JPY_One_Min_Candle_Container()

        self.init()

        # 中枢容器的实现具有差异化,所以没有放入init()
        self.hubs = Hunter.One_Min_Hub_Container(self.pens, self)


    def loadCandleID(self, t):

        candle = self._candles.container[t]

        #print('Bucket.loadCandleID()-- 高级别K线ID', t, '价格:', candle.getClose())

        """
        print('Bucket.loadCandleID() -- 本级别K线时间', pd.Timestamp(pd.datetime(candle.getYear(),
                                                                                candle.getMonth(),
                                                                                candle.getDay(),
                                                                                candle.getHour(),
                                                                                candle.get10Mins()+candle.get5Mins())).strftime('%Y-%m-%d %H:%M:%S'))
        """
        """
        self.candle_container.loadDB(candle.getYear(),
                                     candle.getMonth(),
                                     candle.getDay(),
                                     candle.getHour(),
                                     candle.get10Mins(),
                                     candle.get5Mins(),
                                     self.types,
                                     self.pens,
                                     self.hubs,
                                     self)
        """







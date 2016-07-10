import copy

class S:

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

        self._curTran = []

        self._i = 0

        self._curHub = None

        self._trends = 0

        self._curSize = 0

        self._mPrice = -1 

    def process(self):

        self.exit()

        self.enter()

    def enter(self):

        try:

            self._curHub = self._hubs[len(self._hubs) - 1]
            #self._curHub = event._dict['hub']

        except:

            if __debug__:

                print('Strategy--exit() 中枢访问越界')

                return

        # 第一个中枢不操作
        if self._curHub.pos == '--':

            return

        print('###########################')
        print('交易开始编码', self._i)

        # 中枢生成具有延迟性,最后的买卖点需要以最后一根K线收盘价为参考,而不能直接以中枢的高点为做空价格
        # TODO:当前实现比较粗糙,没有做任何关于当下K线和中枢关系的判断过滤,直接做Enter操作

        lastCandle = self._candles[len(self._candles) - 1]
        #lastCandle = event._dict['can']

        self._entryPrice = lastCandle.getClose()

        self._mPrice = (self._curHub.ZG + self._curHub.ZD) / 2

        self._curTran.append(self._curHub.pos)
        print('中枢方向:', self._curHub.pos)
        print('中枢坐标:', self._curHub.s_pen.beginType.candle_index)

        self._curSize = self.position()

        if self._curSize == 0:

            self._curTran.append(0)
            self._curTran.append(0)
            self._curTran.append(0)
            self._curTran.append(0)

            self._entryPrice = 0

            return

        print('当前仓位比例', self._curSize)

        self._curTran.append(self._curSize)
        
        if self._curHub.pos == 'Up':

            self._curTran.append(self._curHub.ZG)
            print('理论进入价格:', self._curHub.ZG)

            self._curTran.append(self._entryPrice)
            print('实际进入价格:', self._entryPrice)

            self._curTran.append(abs(self._entryPrice - self._curHub.ZG))
            print('理论价差:', self._entryPrice - self._curHub.ZG)


        else:

            self._curTran.append(self._curHub.ZD)
            print('理论进入价格:', self._curHub.ZD)

            self._curTran.append(self._entryPrice)
            print('实际进入价格:', self._entryPrice)

            self._curTran.append(abs(self._entryPrice - self._curHub.ZD))
            print('理论价差:', self._entryPrice - self._curHub.ZD)


    def exit(self):

        if self._entryPrice == -1:

            return

        if self._entryPrice == 0:

            self._curTran.append(0)
            self._curTran.append(0)
            self._curTran.append(0)
            self._curTran.append(0)
            self._curTran.append(0)

            S._trans.append(copy.deepcopy(self._curTran))

            self._curTran.clear()

            self._entryPrice = -1

            self._i += 1

            return

        curHub = self._hubs[len(self._hubs) - 1]
        #curHub = event._dict['hub']

        midPrice = (curHub.ZG + curHub.ZD)/2

        lastCandle = self._candles[len(self._candles) - 1]
        #lastCandle = event._dict['can']

        exitP = lastCandle.getClose()

        # 当下交易中枢向上
        if self._curHub.pos == 'Up':

            profit_1 = self._mPrice/midPrice - 1
            profit_2 = self._entryPrice/exitP - 1

        # 当下交易中枢向下
        else:

            profit_1 = midPrice/self._mPrice - 1
            profit_2 = exitP/self._entryPrice - 1

        print('前一中枢方向:', self._curHub.pos)
        print('当前中枢方向:', curHub.pos)
        print('当前中枢坐标:', curHub.s_pen.beginType.candle_index)

        self._curTran.append(midPrice)
        print('理论离场价格:', midPrice)

        self._curTran.append(exitP)
        print('实际离场价格:', exitP)

        print('理论价差:', exitP - midPrice)
        self._curTran.append(abs(exitP - midPrice))

        self._curTran.append(profit_1)
        print('理论获利:', profit_1)

        self._curTran.append(profit_2)
        print('实际获利:', profit_2)

        print('交易结束编号', self._i)
        print('###########################')

        S._trans.append(copy.deepcopy(self._curTran))

        self._curTran.clear()

        self._entryPrice = -1

        self._i += 1

    def position(self):

        try:

            preHub_1 = self._hubs[len(self._hubs) - 2]

            #preHub_1 = event._dict['pre']

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

            print('Strategy--position() 中枢访问越界')

            posSize = 0.1

        return posSize
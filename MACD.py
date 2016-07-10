# 2016-6-10
# MACD计算模块

class MACD:

    def __init__(self, EMA12, EMA26, DIF, DEA, MACD):

        self.EMA12 = EMA12
        self.EMA26 = EMA26
        self.DIF = DIF
        self.DEA = DEA
        self.MACD = MACD

    def getMACD(self):

        return self.MACD


class Power_MACD:

    # 同一时间仅可能出现一个MACD判断,所以通过一个全局标示位控制状态即可
    isActive = False

    @staticmethod
    def isMACDAct():

        return Power_MACD.isActive

    @staticmethod
    def activeMACD():

        Power_MACD.isActive = True

    @staticmethod
    def init():

        Power_MACD.isActive = False

        print('Power_MACD.init() 初始化MACD')

    def __init__(self, candle_container):

        self.candles_MACD = 0

        self.candle_container = candle_container

    def loadMACD(self):

        pass

    def reset(self):

        self.candles_MACD = 0

        print('Power_MACD.reset() 复位Power_MACD')


class Power_MACD_Entry(Power_MACD):

    def loadMACD(self, hub):

        # 当前正在处理的中枢
        last_hub = hub.container[hub.size() - 1]
        # 倒数第二个中枢,也就是和当前中枢构成了趋势的两个中枢
        pre_hub = hub.container[hub.size() - 2]

        # 当前中枢为激活了Bucket的中枢
        # 这种情况直接取中枢的第一笔做为MACD阴影计算的结束部分

        # MACD阴影计算起始K线位置
        s_candle_index = 0

        # 结束K线位置
        e_candle_index = 0

        """
        if last_hub.isSticky:

            pass

        # 如果是盘整中枢
        else:

            last_hub = hub.container[hub.size() - 2]
            pre_hub = hub.container[hub.size() - 3]
        """

        start_pen = last_hub.s_pen
        end_pen = pre_hub.e_pen

        # 中枢的方向不同会对获取第一个K线位置的判断有少许差别
        if last_hub.pos == 'Up':


            # 计算MACD阴影的起始K线位置
            # 2016-05-08
            # 起始位置从最后一笔的起点开始

            """
            for i in range(end_pen.endType.candle_index, start_pen.beginType.candle_index + 1):

                if self.candle_container.container[i].getHigh() >= pre_hub.ZG:

                    # 记录MACD进入部分开始的第一个K线位置
                    s_candle_index = i

                    break
            """

            s_candle_index = end_pen.beginType.candle_index

            # 计算MACD阴影的结束K线位
            for j in range(start_pen.beginType.candle_index, start_pen.endType.candle_index + 1):

                if self.candle_container.container[j].getLow() <= last_hub.ZD:

                    e_candle_index = j

                    break

            # 趋势向上的时候,仅考察MACD为正的部分
            for t in range(s_candle_index, e_candle_index + 1):

                if self.candle_container.container[t].MACD.getMACD() > 0:

                    self.candles_MACD += self.candle_container.container[t].MACD.getMACD()

        # 中枢向下
        else:

            # 计算MACD阴影的起始K线位置

            # 2016-05-08
            # 起始位置从最后一笔的起点开始
            """
            for i in range(end_pen.endType.candle_index, start_pen.beginType.candle_index + 1):

                if self.candle_container.container[i].getLow() <= pre_hub.ZD:

                    s_candle_index = i

                    break
            """

            s_candle_index = end_pen.beginType.candle_index


            # 计算MACD阴影的结束K线位置
            for j in range(start_pen.beginType.candle_index, start_pen.endType.candle_index + 1):

                if self.candle_container.container[j].getHigh() >= last_hub.ZG:

                    e_candle_index = j

                    break

            # 趋势向下的时候,仅考察MACD为正的部分
            for t in range(s_candle_index, e_candle_index + 1):

                if self.candle_container.container[t].MACD.getMACD() < 0:

                    self.candles_MACD += self.candle_container.container[t].MACD.getMACD()

        print('Power_MACD_Entry.loadMACD() MACD阴影起始和结束K线:', s_candle_index, e_candle_index)
        print('Power_MACD_Entry.loadMACD() MACD力量强度:', self.candles_MACD)


class Power_MACD_Exit(Power_MACD):

    def loadMACD(self, hub):

        # 当前正在处理的中枢
        last_hub = hub.container[hub.size() - 1]

        # MACD阴影计算起始K线位置
        s_candle_index = 0

        # 结束K线位置
        e_candle_index = 0

        # 2016-05-08
        # 取消了盘整的概念

        """
        # 如果不是盘整中枢
        if last_hub.isSticky:

            pass

        # 盘整中枢的化再向前多取一个中枢
        else:

            last_hub = hub.container[hub.size() - 2]
        """

        end_pen = last_hub.e_pen

        # 中枢朝上
        if last_hub.pos == 'Up':

            # 计算MACD阴影的起始K线位置
            # 2016-05-08
            """
            for i in range(end_pen.endType.candle_index, self.candle_container.size()):

                if self.candle_container.container[i].getHigh() >= last_hub.ZG:

                    # 记录MACD进入部分开始的第一个K线位置
                    s_candle_index = i

                    break
            """

            s_candle_index = end_pen.beginType.candle_index

            # MACD阴影计算的结束K线就是当前最后的一根K线
            for t in range(s_candle_index, self.candle_container.size()):

                if self.candle_container.container[t].MACD.getMACD() > 0:

                    self.candles_MACD += self.candle_container.container[t].MACD.getMACD()

        # 中枢朝下
        else:

            # 2016-05-08
            """
            for i in range(end_pen.endType.candle_index, self.candle_container.size()):

                if self.candle_container.container[i].getLow() <= last_hub.ZD:

                    s_candle_index = i

                    break
            """
            s_candle_index = end_pen.beginType.candle_index

            # MACD阴影计算的结束K线就是当前最后的一根K线
            for t in range(s_candle_index, self.candle_container.size()):

                if self.candle_container.container[t].MACD.getMACD() < 0:

                    self.candles_MACD += self.candle_container.container[t].MACD.getMACD()

        print('Power_MACD_Exit.loadMACD() MACD阴影起始和结束K线:', s_candle_index, self.candle_container.size())
        print('Power_MACD_Exit.loadMACD() MACD力量强度:', self.candles_MACD)

    def updateMACD(self, hub):

        print('Power_MACD_Exit.updateMACD() 更新MACD')
        self.loadMACD(hub)




# 2016-6-10
# 画图模块

import matplotlib.pyplot as plt

import matplotlib.patches as patches

import pandas as pd

class Ten_Min_Drawer:

    def __init__(self, stocks):

        self.date_index = {pd.Timestamp(pd.datetime(candle.getYear(),
                                               candle.getMonth(),
                                               candle.getDay(),
                                               candle.getHour(),
                                               candle.get10Mins())).strftime('%Y-%m-%d %H:%M:%S'): i for i, candle in enumerate(stocks)}

    # 画MACD
    def draw_MACD(self, stocks, ax):

        piexl_x = []
        DIF = []
        DEA = []
        MACD = []

        for i in range(len(stocks)):

            piexl_x.append(i)

            DIF.append(stocks[i]['DIF'])
            DEA.append(stocks[i]['DEA'])
            MACD.append(stocks[i]['MACD'])

        ax.plot(piexl_x, DIF, color='#9999ff')
        ax.plot(piexl_x, DEA, color='#ff9999')

        # ax.bar(i, stocks[i]['MACD'], 0.8, stocks[i]['Low'])

    # 画K线算法.内部采用了双层遍历,算法简单,但性能一般

    def draw_stocks(self, candles, types, ax_1):

        piexl_x = []

        height = []
        low = []
        color = []

        for i, candle in enumerate(candles):

            piexl_x.append(i)

            height.append(candle.getHigh() - candle.getLow())
            low.append(candle.getLow())

            color.append('g')

            j = 0

            while j < len(types):

                if pd.Timestamp(pd.datetime(candle.getYear(),
                                            candle.getMonth(),
                                            candle.getDay(),
                                            candle.getHour(),
                                            candle.get10Mins())) == \
                        pd.datetime(types[j].candle.getYear(),
                                    types[j].candle.getMonth(),
                                    types[j].candle.getDay(),
                                    types[j].candle.getHour(),
                                    types[j].candle.get10Mins()):
                            
                            color[i] = 'r'
                            
                            break
                else:

                    j += 1

        ax_1.bar(piexl_x, height, 0.8, low, color = color)

        # self.draw_substocks(candles, height, low, ax_a, trans)

    def draw_substocks(self, stocks, height, low, ax_a, trans):

        i = 0

        while i < len(trans.container):

            trendID = trans.container[i].trend
            hubID = trans.container[i].hubID
            entryID = trans.container[i].entry
            tradeID = trans.container[i].trade
            exitID = trans.container[i].exit

            sub_height = []
            sub_low = []
            c = []
            sub_piexl = []

            p = 0

            # 小图的起始是从上一个中枢的起点开始的
            # last_hub.s_pen.beginType.candle_index
            for j in range(trendID, min((exitID + 100), len(stocks))):

                sub_height.append(height[j])

                sub_low.append(low[j])

                c.append('c')

                sub_piexl.append(p)

                p += 1

            c[hubID-trendID] = 'r'
            c[tradeID-trendID] = 'r'
            c[exitID-trendID] = 'r'

            ax_a[i].bar(sub_piexl, sub_height, 0.8, sub_low, color = c)

            sub_height.clear()
            sub_low.clear()
            c.clear()
            sub_piexl.clear()

            i += 1

    def draw_pens(self, pens, ax):

        piexl_x = []
        piexl_y = []

        for _, pen in enumerate(pens):

            # 利用已经初始化的Date:Index字典,循环遍历pens数组以寻找其对于时间为关键值的X轴坐标位置
            # 添加起点
            piexl_x.append(self.date_index[pd.Timestamp(pd.datetime(pen.beginType.candle.getYear(),
                                                               pen.beginType.candle.getMonth(),
                                                               pen.beginType.candle.getDay(),
                                                               pen.beginType.candle.getHour(),
                                                               pen.beginType.candle.get10Mins())).strftime('%Y-%m-%d %H:%M:%S')])

            # 添加终点
            piexl_x.append(self.date_index[pd.Timestamp(pd.datetime(pen.endType.candle.getYear(),
                                                               pen.endType.candle.getMonth(),
                                                               pen.endType.candle.getDay(),
                                                               pen.endType.candle.getHour(),
                                                               pen.endType.candle.get10Mins())).strftime('%Y-%m-%d %H:%M:%S')])

            if pen.pos == 'Down':

                # 如果笔的朝向向下,那么画线的起点为顶分型的高点,终点为底分型的低点
                piexl_y.append(pen.beginType.candle.getHigh())
                piexl_y.append(pen.endType.candle.getLow())

            # 如果笔的朝向向上,那么画线的起点为底分型的低点,终点为顶分型的高点
            else:

                piexl_y.append(pen.beginType.candle.getLow())
                piexl_y.append(pen.endType.candle.getHigh())

        # 画线程序调用
        ax.plot(piexl_x, piexl_y, color='m')

    # 画中枢
    def draw_hub(self, hubs, hub_container, ax):

        for _, hub in enumerate(hubs):

            # Rectangle x

            start_date = pd.Timestamp(pd.datetime(hub.s_pen.beginType.candle.getYear(),
                                                      hub.s_pen.beginType.candle.getMonth(),
                                                      hub.s_pen.beginType.candle.getDay(),
                                                      hub.s_pen.beginType.candle.getHour(),
                                                      hub.s_pen.beginType.candle.get10Mins())).strftime('%Y-%m-%d %H:%M:%S')

            x = self.date_index[start_date]

            # Rectangle y
            y = hub.ZD

            # Rectangle width
            end_date = pd.Timestamp(pd.datetime(hub.e_pen.endType.candle.getYear(),
                                                    hub.e_pen.endType.candle.getMonth(),
                                                    hub.e_pen.endType.candle.getDay(),
                                                    hub.e_pen.endType.candle.getHour(),
                                                    hub.e_pen.endType.candle.get10Mins())).strftime('%Y-%m-%d %H:%M:%S')

            end_index = self.date_index[end_date]
            start_index = self.date_index[start_date]

            w = end_index - start_index

            # Rectangle height
            h = hub.ZG - hub.ZD

            ax.add_patch(patches.Rectangle((x,y), w, h, color='b', fill=False))

class Five_Min_Drawer:

    def __init__(self, stocks):

        self.date_index = {pd.Timestamp(pd.datetime(stocks[i].getYear(),
                                               stocks[i].getMonth(),
                                               stocks[i].getDay(),
                                               stocks[i].getHour(),
                                               stocks[i].get10Mins()+
                                                    stocks[i].get5Mins())).strftime('%Y-%m-%d %H:%M:%S'): i for i in range(len(stocks))}

    # 画MACD
    def draw_MACD(self, stocks, ax):

        piexl_x = []
        DIF = []
        DEA = []
        MACD = []

        for i in range(len(stocks)):

            piexl_x.append(i)

            DIF.append(stocks[i]['DIF'])
            DEA.append(stocks[i]['DEA'])
            MACD.append(stocks[i]['MACD'])

        ax.plot(piexl_x, DIF, color='#9999ff')
        ax.plot(piexl_x, DEA, color='#ff9999')

        # ax.bar(i, stocks[i]['MACD'], 0.8, stocks[i]['Low'])

    # 画K线算法.内部采用了双层遍历,算法简单,但性能一般

    def draw_stocks(self, candles, ax_1, trans):

        piexl_x = []

        height = []
        low = []
        color = []

        for i, candle in enumerate(candles):

            piexl_x.append(i)

            height.append(candle.getHigh() - candle.getLow())
            low.append(candle.getLow())

            color.append('g')

        ax_1.bar(piexl_x, height, 0.8, low, color = color)

        # self.draw_substocks(candles, height, low, ax_a, trans)

    def draw_substocks(self, stocks, height, low, ax_a, trans):

        i = 0

        while i < len(trans.container):

            trendID = trans.container[i].trend
            hubID = trans.container[i].hubID
            entryID = trans.container[i].entry
            tradeID = trans.container[i].trade
            exitID = trans.container[i].exit

            sub_height = []
            sub_low = []
            c = []
            sub_piexl = []

            p = 0

            # 小图的起始是从上一个中枢的起点开始的
            # last_hub.s_pen.beginType.candle_index
            for j in range(trendID, min((exitID + 100), len(stocks))):

                sub_height.append(height[j])

                sub_low.append(low[j])

                c.append('c')

                sub_piexl.append(p)

                p += 1

            c[hubID-trendID] = 'r'
            c[tradeID-trendID] = 'r'
            c[exitID-trendID] = 'r'

            ax_a[i].bar(sub_piexl, sub_height, 0.8, sub_low, color = c)

            sub_height.clear()
            sub_low.clear()
            c.clear()
            sub_piexl.clear()

            i += 1

    def draw_pens(self, pens, ax):

        piexl_x = []
        piexl_y = []

        for _, pen in enumerate(pens):

            # 利用已经初始化的Date:Index字典,循环遍历pens数组以寻找其对于时间为关键值的X轴坐标位置
            # 添加起点
            piexl_x.append(self.date_index[pd.Timestamp(pd.datetime(pen.beginType.candle.getYear(),
                                                               pen.beginType.candle.getMonth(),
                                                               pen.beginType.candle.getDay(),
                                                               pen.beginType.candle.getHour(),
                                                               pen.beginType.candle.get10Mins() +
                                                                    pen.beginType.candle.get5Mins())).strftime('%Y-%m-%d %H:%M:%S')])

            # 添加终点
            piexl_x.append(self.date_index[pd.Timestamp(pd.datetime(pen.endType.candle.getYear(),
                                                               pen.endType.candle.getMonth(),
                                                               pen.endType.candle.getDay(),
                                                               pen.endType.candle.getHour(),
                                                               pen.endType.candle.get10Mins() +
                                                                    pen.endType.candle.get5Mins())).strftime('%Y-%m-%d %H:%M:%S')])

            if pen.pos == 'Down':

                # 如果笔的朝向向下,那么画线的起点为顶分型的高点,终点为底分型的低点
                piexl_y.append(pen.beginType.candle.getHigh())
                piexl_y.append(pen.endType.candle.getLow())

            # 如果笔的朝向向上,那么画线的起点为底分型的低点,终点为顶分型的高点
            else:

                piexl_y.append(pen.beginType.candle.getLow())
                piexl_y.append(pen.endType.candle.getHigh())

        # 画线程序调用
        ax.plot(piexl_x, piexl_y, color='m')

    # 画中枢
    def draw_hub(self, hubs, hub_container, ax):

        for _, hub in enumerate(hubs):

            # Rectangle x

            start_date = pd.Timestamp(pd.datetime(hub.s_pen.beginType.candle.getYear(),
                                                      hub.s_pen.beginType.candle.getMonth(),
                                                      hub.s_pen.beginType.candle.getDay(),
                                                      hub.s_pen.beginType.candle.getHour(),
                                                      hub.s_pen.beginType.candle.get10Mins()+
                                                      hub.s_pen.beginType.candle.get5Mins())).strftime('%Y-%m-%d %H:%M:%S')

            x = self.date_index[start_date]

            # Rectangle y
            y = hub.ZD

            # Rectangle width
            end_date = pd.Timestamp(pd.datetime(hub.e_pen.endType.candle.getYear(),
                                                    hub.e_pen.endType.candle.getMonth(),
                                                    hub.e_pen.endType.candle.getDay(),
                                                    hub.e_pen.endType.candle.getHour(),
                                                    hub.e_pen.endType.candle.get10Mins()+
                                                    hub.e_pen.endType.candle.get5Mins())).strftime('%Y-%m-%d %H:%M:%S')

            end_index = self.date_index[end_date]
            start_index = self.date_index[start_date]

            w = end_index - start_index

            # Rectangle height
            h = hub.ZG - hub.ZD

            ax.add_patch(patches.Rectangle((x,y), w, h, color='b', fill=False))


class One_Min_Drawer:

    # 画K线算法.内部采用了双层遍历,算法简单,但性能一般
    @staticmethod
    def draw_stocks(stocks, types, ax_1):

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

            height.append(stocks[i].getHigh() - stocks[i].getLow())
            low.append(stocks[i].getLow())

            j = 0
            c.append('g')

            while j < len(types):

                if pd.Timestamp(pd.datetime(stocks[i].getYear(),
                                            stocks[i].getMonth(),
                                            stocks[i].getDay(),
                                            stocks[i].getHour(),
                                            stocks[i].get10Mins(),
                                            stocks[i].getMin())) == \
                        pd.datetime(types[j].candle.getYear(),
                                    types[j].candle.getMonth(),
                                    types[j].candle.getDay(),
                                    types[j].candle.getHour(),
                                    types[j].candle.get10Mins(),
                                    types[j].candle.getMin()):

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

    @staticmethod
    def draw_pens(stocks, pens, ax):

        date_index = {pd.Timestamp(pd.datetime(stocks[i].getYear(),
                                               stocks[i].getMonth(),
                                               stocks[i].getDay(),
                                               stocks[i].getHour(),
                                               stocks[i].get10Mins(),
                                               stocks[i].getMin())).strftime('%Y-%m-%d %H:%M:%S'): i for i in range(len(stocks))}

        piexl_x = []
        piexl_y = []

        for j in range(len(pens)):

            # 利用已经初始化的Date:Index字典,循环遍历pens数组以寻找其对于时间为关键值的X轴坐标位置
            # 添加起点
            piexl_x.append(date_index[pd.Timestamp(pd.datetime(pens[j].beginType.candle.getYear(),
                                                               pens[j].beginType.candle.getMonth(),
                                                               pens[j].beginType.candle.getDay(),
                                                               pens[j].beginType.candle.getHour(),
                                                               pens[j].beginType.candle.get10Mins(),
                                                               pens[j].beginType.candle.getMin())).strftime('%Y-%m-%d %H:%M:%S')])

            # 添加终点
            piexl_x.append(date_index[pd.Timestamp(pd.datetime(pens[j].endType.candle.getYear(),
                                                               pens[j].endType.candle.getMonth(),
                                                               pens[j].endType.candle.getDay(),
                                                               pens[j].endType.candle.getHour(),
                                                               pens[j].endType.candle.get10Mins(),
                                                               pens[j].endType.candle.getMin())).strftime('%Y-%m-%d %H:%M:%S')])

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

    # 画中枢
    @staticmethod
    def draw_hub(stocks, hubs, ax):

        date_index = {pd.Timestamp(pd.datetime(stocks[i].getYear(),
                                               stocks[i].getMonth(),
                                               stocks[i].getDay(),
                                               stocks[i].getHour(),
                                               stocks[i].get10Mins(),
                                               stocks[i].getMin())).strftime('%Y-%m-%d %H:%M:%S'): i for i in range(len(stocks))}

        for i in range(len(hubs)):

            # Rectangle x

            start_date = pd.Timestamp(pd.datetime(hubs[i].s_pen.beginType.candle.getYear(),
                                                  hubs[i].s_pen.beginType.candle.getMonth(),
                                                  hubs[i].s_pen.beginType.candle.getDay(),
                                                  hubs[i].s_pen.beginType.candle.getHour(),
                                                  hubs[i].s_pen.beginType.candle.get10Mins(),
                                                  hubs[i].s_pen.beginType.candle.getMin())).strftime('%Y-%m-%d %H:%M:%S')

            x = date_index[start_date]

            # Rectangle y
            y = hubs[i].ZD

            # Rectangle width
            end_date = pd.Timestamp(pd.datetime(hubs[i].e_pen.endType.candle.getYear(),
                                                hubs[i].e_pen.endType.candle.getMonth(),
                                                hubs[i].e_pen.endType.candle.getDay(),
                                                hubs[i].e_pen.endType.candle.getHour(),
                                                hubs[i].e_pen.endType.candle.get10Mins(),
                                                hubs[i].e_pen.endType.candle.getMin())).strftime('%Y-%m-%d %H:%M:%S')

            w = date_index[end_date] - date_index[start_date]

            # print('Hub--', i ,'B--', start_date, 'E--', end_date, 'W--', w, 'GG--', hubs[i]['GG'], 'DD--', hubs[i]['DD'])

            # Rectangle height
            h = hubs[i].ZG - hubs[i].ZD

            #if hubs[i]['Level'] == 3:
            #   ax.add_patch(patches.Rectangle((x,y), w, h, color='r', fill=False))

            #else:

            ax.add_patch(patches.Rectangle((x,y), w, h, color='y', fill=False))
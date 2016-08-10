# 2016-6-10
# 测试模块

# 第三方模块
import matplotlib.pyplot as plt
import pandas as pd

# 系统模块
import threading
import queue

#自定义模块
import Hunter
import Mining
import Drawer
import Currency
import Component
import S1
import Event

# debug
import S1_B

def test_markets(markets, years):

    threads = []
    transRecorder = {}
    queueLocks = {}
    workQueues = {}

    for market in markets:

        transRecorder[market] = {}

        queueLocks[market] = threading.Lock()

        workQueues[market] = queue.Queue(12)

    for year in years:

        #start = time()

        for market in markets:

            for month in range(1, 13):

                thread = Mining.Executor(market, year, month, transRecorder[market], queueLocks[market], workQueues[market])

                thread.start()

                workQueues[market].put(object())

                threads.append(thread)

            for thread in threads:

                thread.join()

            while not workQueues[market].empty():

                pass

            fileName = str(year) + '年-' + market + '-市场' + '.xlsx'

            writer = pd.ExcelWriter(fileName, engine='xlsxwriter')

            for m in range(1, 13):

                trans = transRecorder[market].get(m)

                if not trans == None:

                    d = trans.save(m)

                    df = pd.DataFrame(d)

                    df.to_excel(writer, '月份-' + str(m))

                    trans.printing()

                    trans.reset()

            transRecorder[market].clear()

            writer.close()

            #end = time()

            #print('%0.3f seconds'%(end-start))

def test_month_10(market, year, month, count=0, skips=0):

    candles = Currency.AUD_Ten_Min_Candle_Container()

    types = Hunter.Type_Container(candles)

    pens = Hunter.Pen_Container(types)

    hubs = Hunter.Ten_Min_Hub_Container(pens)

    # 初始化Tran_Container对象
    # trans = Hunter.Tran_Container()

    #s1 = S1.S1(candles.container,types.container,pens.container,hubs.container)

    s2 = S1.S2()

    m = Event.Monitor(s2)

    candles.loadDB(year, month, count, skips, types, pens, hubs, m)

    ax_1 = plt.subplot(1, 1, 1)

    drawer = Drawer.Ten_Min_Drawer(candles.container)

    drawer.draw_stocks(candles.container, types.container, ax_1)

    drawer.draw_pens(pens.container, ax_1)

    drawer.draw_hub(hubs.container, hubs, ax_1)

    df_2 = pd.DataFrame(Component.Tran.archive(s2._trans))

    file = '2005_2_AUD.xlsx'

    writer = pd.ExcelWriter(file, engine='xlsxwriter')

    df_2.to_excel(writer)

    writer.close()

    s2._trans.clear()

    plt.show()

    """
    trans.printing()

    trans.reset()

    hubMining = Mining.Hub_Mining(hubs, candles)

    hubMining.mining()

    hubMining.save('AUD_2015_4.xlsx')
    """

def test_year(year, m1, m2):

    candles = Currency.AUD_Ten_Min_Candle_Container()

    types = Hunter.Type_Container(candles)

    pens = Hunter.Pen_Container(types)

    hubs = Hunter.Ten_Min_Hub_Container(pens)

    s2 = S1.S2()

    m = Event.Monitor(s2)

    c = []

    # 逐月调用
    for i in range(m1, m2+1):

        candles.loadDB(year, i, 0, 0, types, pens, hubs, m)

        c.extend(Component.Tran.archive(s2._trans))

        s2._trans.clear()

    df_2 = pd.DataFrame(c)

    file = '2005_AUD.xlsx'

    writer = pd.ExcelWriter(file, engine='xlsxwriter')

    df_2.to_excel(writer)

    writer.close()

    c.clear()


def test_month_5(market, year, month, count=0, skips=0):

    candles = Currency.Markets.candelOfMarket(market)

    types = Hunter.Type_Container(candles)

    pens = Hunter.Pen_Container(types)

    hubs = Hunter.Five_Min_Hub_Container(pens)

    # 初始化Tran_Container对象
    trans = Hunter.Tran_Container()

    s = S1.S(candles.container,types.container,pens.container,hubs.container)

    candles.loadDB(year, month, count, skips, types, pens, hubs, s)

    S1.S._trans.clear()

    print(hubs.size())

    ax_1 = plt.subplot(1, 1, 1)

    drawer = Drawer.Five_Min_Drawer(candles.container)

    drawer.draw_stocks(candles.container, ax_1, trans)

    drawer.draw_pens(pens.container, ax_1)

    drawer.draw_hub(hubs.container, hubs, ax_1)

    plt.show()

    """
    trans.printing()

    trans.reset()

    hubMining = Mining.Hub_Mining(hubs, candles)

    hubMining.mining()

    hubMining.save('AUD_2015_9.xlsx')
    """

def test_years(market, year_1, year_2):

    for y in range(year_1, year_2+1):

        test_year(market, y, 1, 12)

if __name__ == '__main__':

    test_month_10('', 2005, 2)
    #
    # for i in range(2005, 2006):
    #
    #     test_year(i, 1, 3)

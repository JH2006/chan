# 2016-6-9
# 应用于vnpy

# 系统模块
import sys
from queue import Queue, Empty
from threading import Thread

########################################################################
class EventEngine(object):
    """
    计时器使用python线程的事件驱动引擎
    """

    #----------------------------------------------------------------------
    def __init__(self):
        """初始化事件引擎"""
        # 事件队列
        self.__queue = Queue()

        # 事件引擎开关
        self.__active = False

        # 事件处理线程
        self.__thread = Thread(target = self.__run)

        # 这里的__handlers是一个字典，用来保存对应的事件调用关系
        # 其中每个键对应的值是一个列表，列表中保存了对该事件进行监听的函数功能
        self.__handlers = {}

    #----------------------------------------------------------------------
    def __run(self):
        """引擎运行"""
        while self.__active == True:
            try:
                event = self.__queue.get(block = True, timeout = 0.001)  # 获取事件的阻塞时间设为1ms
                self.__process(event)
            except Empty:
                pass

    #----------------------------------------------------------------------
    def __process(self, event):
        """处理事件"""
        # 检查是否存在对该事件进行监听的处理函数
        if event.type_ in self.__handlers:
            # 若存在，则按顺序将事件传递给处理函数执行
            [handler(event) for handler in self.__handlers[event.type_]]

            # 以上语句为Python列表解析方式的写法，对应的常规循环写法为：
            #for handler in self.__handlers[event.type_]:
                #handler(event)

    #----------------------------------------------------------------------
    def start(self):
        """引擎启动"""
        # 将引擎设为启动
        self.__active = True

        # 启动事件处理线程
        self.__thread.start()

    #----------------------------------------------------------------------
    def stop(self):
        """停止引擎"""
        # 将引擎设为停止
        self.__active = False

        # 等待事件处理线程退出
        self.__thread.join()

    #----------------------------------------------------------------------
    def register(self, type_, handler):
        """注册事件处理函数监听"""
        # 尝试获取该事件类型对应的处理函数列表，若无则创建
        try:
            handlerList = self.__handlers[type_]
        except KeyError:
            handlerList = []
            self.__handlers[type_] = handlerList

        # 若要注册的处理器不在该事件的处理器列表中，则注册该事件
        if handler not in handlerList:
            handlerList.append(handler)

        # print('Register', type_, handler)

    #----------------------------------------------------------------------
    def unregister(self, type_, handler):
        """注销事件处理函数监听"""
        # 尝试获取该事件类型对应的处理函数列表，若无则忽略该次注销请求
        try:
            handlerList = self.__handlers[type_]

            # 如果该函数存在于列表中，则移除
            if handler in handlerList:
                handlerList.remove(handler)

            # 如果函数列表为空，则从引擎中移除该事件类型
            if not handlerList:
                del self.__handlers[type_]

            # print('Deregister', type_, handler)

        except KeyError:
            pass

    #----------------------------------------------------------------------
    def put(self, event):
        """向事件队列中存入事件"""
        self.__queue.put(event)

########################################################################
class Event:
    """事件对象"""

    #----------------------------------------------------------------------
    def __init__(self, type_ = None):
        """Constructor"""
        self.type_ = type_      # 事件类型
        self._dict = {}         # 字典用于保存具体的事件数据

class Monitor:

    # 事件编号
    # 每个事件都对应至少一个响应机制
    HUB_GEN = 'hub_gen'
    HUB_GROW = 'hub_grow'
    HUB_END = 'hub_end'
    K_GEN = 'K_gen'
    STOP = 'stop_loss'

    def __init__(self, strategy):

        # 通过特定的策略类来进行初始化
        # 在特定状态被激活的时候调用策略类实例进行处理
        self._s = strategy

        # 策略实例和事件监听实例具有强耦合关系
        self._s._monitor = self

        # 事件管理器初始化
        self._e = EventEngine()

        # 事件响应处理注册
        self._e.register(Monitor.HUB_GEN, self.hub_gen)
        self._e.register(Monitor.HUB_GROW, self.hub_grow)
        self._e.register(Monitor.HUB_END, self.hub_end)

        self._e.start()

    def __del__(self):

        self._e.unregister(Monitor.HUB_GEN, self.hub_gen)
        self._e.unregister(Monitor.HUB_GROW, self.hub_grow)
        self._e.unregister(Monitor.HUB_END, self.hub_end)

        self._e.stop()

    # 中枢生成事件处理接口
    def hub_gen(self, event):

        self._s.hub_gen(event)

    # 中枢终结事件处理接口
    def hub_end(self, event):

        #print('中枢扩张完成:', len(self._hubs), '--中枢长度:',
        #      self._hubs[len(self._hubs) - 1].pens(), '中枢最后一笔K线位置--',
        #      self._hubs[len(self._hubs) - 1].e_pen.beginType.candle_index,
        #      self._hubs[len(self._hubs) - 1].e_pen.endType.candle_index)

        pass

    # 中枢生长延伸事件处理接口
    def hub_grow(self, event):

        #print('中枢 ID:', len(self._hubs), '--中枢长度:',
        #      self._hubs[len(self._hubs) - 1].pens(),
        #      '潜在笔:', event.dict_['single'], 'K线索引--',
        #      self._pens[event.dict_['single']].beginType.candle_index,
        #      self._pens[event.dict_['single']].endType.candle_index)

        pass

    # 跟踪中枢第四笔确认点
    def trade_commit(self, event):

        self._s.trade_commit(event)

    def genEvent(self, event):

        return Event(event)

    def enter(self, event):

        self._s.enter(event)

    def exit(self, event):

        self._s.exit(event)

    def stop(self, event):

        self._s.stop(event)
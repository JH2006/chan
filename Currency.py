# 2016-6-10
# 货币市场模块

#缠策略基础库😢
import Hunter

# 系统模块
from enum import Enum, unique

@unique
class Markets(Enum):

    AUD = 'AUD'
    GBP = 'GBP'
    CAD = 'CAD'
    CHF = 'CHF'
    JPY = 'JPY'
    EUR = 'EUR'

    @staticmethod
    def candelOfMarket(market):

        candles = None

        if Markets.AUD.value == market:
            candles = AUD_Five_Min_Candle_Container()

        elif Markets.CAD.value == market:
            candles = CAD_Five_Min_Candle_Container()

        elif Markets.CHF.value == market:
            candles = CHF_Five_Min_Candle_Container()

        elif Markets.EUR.value == market:
            candles = EUR_Five_Min_Candle_Container()

        elif Markets.GBP.value == market:
            candles = GBP_Five_Min_Candle_Container()

        elif Markets.JPY.value == market:
            candles = JPY_Five_Min_Candle_Container()

        else:
            print('产品调用错误,程序退出!!!!!!')

        return candles


class AUD_Five_Min_Candle_Container(Hunter.Five_Min_Candle_Container):

    def __init__(self):

        Hunter.Five_Min_Candle_Container.__init__(self)

        self._collector = self._c.mongodb.AUD5m

class CAD_Five_Min_Candle_Container(Hunter.Five_Min_Candle_Container):

    def __init__(self):

        Hunter.Five_Min_Candle_Container.__init__(self)

        self._collector = self._c.mongodb.CAD5m

class CHF_Five_Min_Candle_Container(Hunter.Five_Min_Candle_Container):

    def __init__(self):

        Hunter.Five_Min_Candle_Container.__init__(self)

        self._collector = self._c.mongodb.CHF5m

class GBP_Five_Min_Candle_Container(Hunter.Five_Min_Candle_Container):

    def __init__(self):

        Hunter.Five_Min_Candle_Container.__init__(self)

        self._collector = self._c.mongodb.GBP5m

class EUR_Five_Min_Candle_Container(Hunter.Five_Min_Candle_Container):

    def __init__(self):

        Hunter.Five_Min_Candle_Container.__init__(self)

        self._collector = self._c.mongodb.EUR5m

class JPY_Five_Min_Candle_Container(Hunter.Five_Min_Candle_Container):

    def __init__(self):

        Hunter.Five_Min_Candle_Container.__init__(self)

        self._collector = self._c.mongodb.JPY5m

class AUD_One_Min_Candle_Container(Hunter.One_Min_Candle_Container):

    def __init__(self):

        Hunter.One_Min_Candle_Container.__init__(self)

        self._collector = self._c.mongodb.AUD1m

class CHF_One_Min_Candle_Container(Hunter.One_Min_Candle_Container):

    def __init__(self):

        Hunter.One_Min_Candle_Container.__init__(self)

        self._collector = self._c.mongodb.CHF1m

class CAD_One_Min_Candle_Container(Hunter.One_Min_Candle_Container):

    def __init__(self):

        Hunter.One_Min_Candle_Container.__init__(self)

        self._collector = self._c.mongodb.CAD1m

class EUR_One_Min_Candle_Container(Hunter.One_Min_Candle_Container):

    def __init__(self):

        Hunter.One_Min_Candle_Container.__init__(self)

        self._collector = self._c.mongodb.EUR1m

class GBP_One_Min_Candle_Container(Hunter.One_Min_Candle_Container):

    def __init__(self):

        Hunter.One_Min_Candle_Container.__init__(self)

        self._collector = self._c.mongodb.GBP1m

class JPY_One_Min_Candle_Container(Hunter.One_Min_Candle_Container):

    def __init__(self):

        Hunter.One_Min_Candle_Container.__init__(self)

        self._collector = self._c.mongodb.JPY1m

class AUD_Ten_Min_Candle_Container(Hunter.Ten_Min_Candle_Container):

    def __init__(self):

        Hunter.Ten_Min_Candle_Container.__init__(self)

        # 2016-09-07
        # 临时性使用AUD1m替换10m进行测试,简化多样性One_Min_Candle_Container.loadDB带来的复杂性
        self._collector = self._c.mongodb.AUD10m
        # self._collector = self._c.mongodb.AUD1m

class CAD_Ten_Min_Candle_Container(Hunter.Ten_Min_Candle_Container):

    def __init__(self):

        Hunter.Ten_Min_Candle_Container.__init__(self)

        self._collector = self._c.mongodb.CAD10m

class CHF_Ten_Min_Candle_Container(Hunter.Ten_Min_Candle_Container):

    def __init__(self):

        Hunter.Ten_Min_Candle_Container.__init__(self)

        self._collector = self._c.mongodb.CHF10m

class EUR_Ten_Min_Candle_Container(Hunter.Ten_Min_Candle_Container):

    def __init__(self):

        Hunter.Ten_Min_Candle_Container.__init__(self)

        self._collector = self._c.mongodb.EUR10m

class GBP_Ten_Min_Candle_Container(Hunter.Ten_Min_Candle_Container):

    def __init__(self):

        Hunter.Ten_Min_Candle_Container.__init__(self)

        self._collector = self._c.mongodb.GBP10m

class JPY_Ten_Min_Candle_Container(Hunter.Ten_Min_Candle_Container):

    def __init__(self):

        Hunter.Ten_Min_Candle_Container.__init__(self)

        self._collector = self._c.mongodb.JPY10m
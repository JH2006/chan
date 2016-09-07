# 2016-07-28
# 交易系统组件,包括Entries, Stops, Exits
# 每个组件都有具体继承类,继承子类具体实现不同的信号判断,并执行交易动作
# 交易系统组件本身不构成完整交易系统,只有当把交易组件以有序地方式组合起来后才构成完整交易系统
import copy

class Entries:

    _type = 'ENTRY'

    def __init__(self, position):

        self._position = position

    def signaling(self, event):

        pass

    def order(self, event):

        pass

# 即时交易策略
# 一旦中枢确认立刻启动事件响应注册
# 中枢确认后的下一个K线完成交易
class ImmEntry(Entries):

    _name = 'IMM_ENTRY'

    def signaling(self, event):

        return True

    def order(self, event):

        tran = event._dict['TRAN']

        # 通过Key确保每个策略仅执行一次
        if ImmEntry._name not in tran._entries:

            if self.signaling(event):

                k = event._dict['K']

                point = k.getClose()

                tran._entries[ImmEntry._name] = (point, self._position)

                return True

        return False


# 趋势反转中的第三类买卖点
# 这类买卖点低于向上中枢低点,高于向下中枢高点,所以称之为趋势反转三买卖
class ReverseEntry(Entries):

    _name = 'REVERSE_ENTRY'

    def __init__(self, position):

        Entries.__init__(self, position)

        self._name = ReverseEntry._name

    def signaling(self, event):

        try:

            hub = event._dict['HUB']
            hubs = event._dict['HUBS']
            pens = event._dict['PENS']

        except KeyError:

            return False

        hub_zg = hub.ZG
        hub_zd = hub.ZD

        i = hubs.last_hub_end_pen_index

        if i < pens.pens_index:

            # 中枢最后一笔的条件要求
            # 此笔有至少4根K线
            # 笔的形态构成满足条件
            if pens.container[i].legal() is True and pens.illPen(pens.container[i]) is True:

                i += 1

                # 向后取一笔
                # 此笔有至少4根K线
                # 笔的形态构成满足条件
                # 和上一笔的判断条件相似

                try:

                    if pens.container[i].legal() is True and pens.illPen(pens.container[i]) is True:

                        # 取笔高低点
                        k_h = pens.container[i].endType.candle.getHigh()
                        k_l = pens.container[i].endType.candle.getLow()

                        # 向上中枢采用笔的低点和中枢高点比较
                        if hub.pos == 'Up':

                            if k_h < hub_zd:

                                return True

                        else:

                            if k_l > hub_zg:

                                return True

                except IndexError:

                    return False

        return False

    def order(self, event):
        
        tran = event._dict['TRAN']

        # 通过Key确保每个策略仅执行一次
        if ReverseEntry._name not in tran._entries and FollowEntry._name not in tran._entries:

            if self.signaling(event):

                k = event._dict['K']

                point = k.getClose()

                tran._entries[ReverseEntry._name] = (point, self._position)

                return True

        return False


# 趋势延伸中的第三类买卖点
# 这类买卖点高于向上中枢高点,低于向下中枢低点,所以称之为趋势延伸三买卖
class FollowEntry(Entries):

    _name = 'FOLLOW_ENTRY'

    def __init__(self, position):

        Entries.__init__(self, position)

        self._name = ReverseEntry._name

    def signaling(self, event):

        try:

            hub = event._dict['HUB']
            hubs = event._dict['HUBS']
            pens = event._dict['PENS']

        except KeyError:

            return False

        hub_zg = hub.ZG
        hub_zd = hub.ZD

        i = hubs.last_hub_end_pen_index + 1

        if i < pens.pens_index:

            pen_high = pens.container[i].high
            pen_low = pens.container[i].low

            min_high = min(hub_zg,pen_high)
            max_low = max(hub_zd, pen_low)

            # 中枢后一笔与中枢存在交集
            if min_high >= max_low:

                # 此笔有至少4根K线
                # 笔的形态构成满足条件
                if pens.container[i].legal() is True and pens.illPen(pens.container[i]) is True:

                    i += 1

                    # 向后取一笔
                    # 此笔有至少4根K线
                    # 笔的形态构成满足条件
                    # 和上一笔的判断条件相似

                    try:

                        if pens.container[i].legal() is True and pens.illPen(pens.container[i]) is True:

                            # 取笔高低点
                            k_h = pens.container[i].endType.candle.getHigh()
                            k_l = pens.container[i].endType.candle.getLow()

                            # 向上中枢采用笔的低点和中枢高点比较
                            if hub.pos == 'Up':

                                if k_l >= hub_zg:

                                    return True

                            else:

                                if k_h <= hub_zd:

                                    return True

                    except IndexError:

                        return False

        return False

    def order(self, event):

        tran = event._dict['TRAN']

        # 通过Key确保每个策略仅执行一次
        if FollowEntry._name not in tran._entries and ReverseEntry._name not in tran._entries:

            if self.signaling(event):

                k = event._dict['K']

                point = k.getClose()

                tran._entries[FollowEntry._name] = (point, self._position)

                return True

        return False


class MidEntry(Entries):

    _name = 'MID_ENTRY'

    def __init__(self, position):

        Entries.__init__(self, position)

        self._name = MidEntry._name


    def signaling(self, event):

        try:

            hub = event._dict['HUB']
            k = event._dict['K']

        except KeyError:

            return False

        high = k.getHigh()
        low = k.getLow()

        try:

            mid = (hub.ZD + hub.ZG) / 2

        except KeyError:

            return False

        if low <= mid <= high:

            cross = True

            s = 'Entry -- Cross meet low <= mid <= high ' + repr(low) + ' ,' + repr(mid) + ' ,' + repr(high)

            # print(s)

        else:

            cross = False

        return cross

    def order(self, event):

        tran = event._dict['TRAN']

        # 通过Key确保每个策略仅执行一次
        if MidEntry._name not in tran._entries and ReverseEntry._name not in tran._entries:

            if self.signaling(event):

                hub = event._dict['HUB']

                point = (hub.ZG + hub.ZD) / 2

                tran._entries[MidEntry._name] = (point, self._position)

                return True

        return False


class EdgeEntry(Entries):

    _name = 'EDGE_ENTRY'

    def __int__(self, position):

        Entries.__init__(self, position)

        self._name = EdgeEntry._name

    def signaling(self, event):

        try:

            hub = event._dict['HUB']
            k = event._dict['K']

        except KeyError:

            return False

        high = k.getHigh()
        low = k.getLow()

        try:

            if hub.pos == 'Up':

                if low <= hub.ZG <= high:

                    return True

                else:

                    return False

            else:

                if low <= hub.ZD <= high:

                    return True

                else:

                    return False

        except KeyError:

            return False

    def order(self, event):

        tran = event._dict['TRAN']
        hub = event._dict['HUB']

        # 通过Key确保每个策略仅执行一次
        if EdgeEntry._name not in tran._entries:

            if self.signaling(event):

                k = event._dict['K']

                if tran._placement == 'SHORT':

                    point = hub.ZG

                else:

                    point = hub.ZD

                tran._entries[EdgeEntry._name] = (point, self._position)

                return True

        return False


class StepEntry(Entries):
    
    _name = 'STEP_ENTRY'

    def __int__(self, position):

        super().__init__(self, position)

        self._name = StepEntry._name

    def signaling(self, event):

        try:

            hub = event._dict['HUB']
            k = event._dict['K']
            types = event._dict['TYPES']
            candles = event._dict['CANDLES']

        except KeyError:

            return False

        last_type = types.container[len(types.container) - 1]

        # 向上中枢以向上分型终结
        if hub.pos == 'Up' and last_type.getPos() == 'Up':

            # 向上分型高于中枢高点
            if last_type.candle.getLow() >= hub.ZG:

                last_revert_type = types.container[len(types.container) - 2]

                # 两个相邻分型间有额外三个K线，构成笔充分条件
                if last_type.candle_index - last_revert_type.candle_index >= 4:

                    high = candles.container[last_type.candle_index -1].getHigh()
                    low = candles.container[last_revert_type.candle_index].getLow()

                    m_h = min(high, hub.ZG)
                    m_l = max(low, hub.ZD)

                    # 充分笔和中枢有交集
                    # 并且当下K线低点高于中枢高点
                    if m_h > m_l and k.getLow() > hub.ZG:

                        return True

        elif hub.pos == 'Down' and last_type.getPos() == 'Down':

            if last_type.candle.getHigh() <= hub.ZD:

                last_revert_type = types.container[len(types.container) - 2]

                if last_type.candle_index - last_revert_type.candle_index >= 4:

                    low = candles.container[last_type.candle_index -1].getLow()
                    high = candles.container[last_revert_type.candle_index].getHigh()

                    m_h = min(high, hub.ZG)
                    m_l = max(low, hub.ZD)

                    if m_h > m_l and k.getHigh() < hub.ZD:

                        return True

        return False


    def order(self, event):

        tran = event._dict['TRAN']

        if StepEntry._name not in tran._entries:

           if self.signaling(event):

               k = event._dict['K']
               point = k.getClose()
               tran._entries[StepEntry._name] = (point, self._position)

               return True

        return False


class Exits:

    _type = 'EXIT'

    def __init__(self, position):

        self._position = position

    def signaling(self, event):

        pass

    def order(self, event):

        pass

# 即时交易策略
# 一旦中枢确认立刻启动事件响应注册
# 中枢确认后的下一个K线完成交易
class ImmExit(Exits):

    _name = 'IMM_EXIT'

    def signaling(self, event):

        return True

    def order(self, event):

        trans = event._dict['TRAN']

        flag = False

        for i, _ in enumerate(trans):

            # 通过Key确保每个策略仅执行一次
            if MidExit._name not in trans[i]._exits:

                if self.signaling(event):

                    k = event._dict['K']

                    point = k.getClose()

                    trans[i]._exits[ImmExit._name] = (point, self._position)

                    flag = True

        return flag


class StopExit(Exits):

    _name = 'STOP_EXIT'

    def __init__(self, position):

        Exits.__init__(self, position)

        self._name = StopExit._name

    def signaling(self, event):

        return True

    def order(self, event):

        if self.signaling(event):

            tran = event._dict['TRAN']

            if len(tran._entries) != 0:

                k = event._dict['K']
                point = k.getClose()

                s = {}
                s[StopExit._name] = (copy.deepcopy(tran._entries), point)

                tran._stops.append(s)
                tran._entries.clear()

                return True

        return False


class MidExit(Exits):

    _name = 'MID_EXIT'

    def __init__(self, position):

        Exits.__init__(self, position)

        self._name = EdgeExit._name

    def signaling(self, event):

        try:

            hub = event._dict['HUB']
            k = event._dict['K']

        except KeyError:

            return False

        high = k.getHigh()
        low = k.getLow()

        try:

            mid = (hub.ZD + hub.ZG) / 2

        except KeyError:

            return False

        if low <= mid <= high:

            cross = True

            s = 'Exit -- Cross meet low <= mid <= high' + repr(low) + ',' + repr(mid) + ',' + repr(high)

            # print(s)

        else:

            cross = False

        return cross

    def order(self, event):

        trans = event._dict['TRAN']

        flag = False

        for i, _ in enumerate(trans):

            # 通过Key确保每个策略仅执行一次
            if MidExit._name not in trans[i]._exits:

                if self.signaling(event):

                    hub = event._dict['HUB']

                    point = (hub.ZG + hub.ZD) / 2

                    trans[i]._exits[MidExit._name] = (point, self._position)

                    flag = True

        return flag


class EdgeExit(Exits):

    _name = 'EDGE_EXIT'

    def __init__(self, position):

        Exits.__init__(self, position)

        self._name = MidExit._name

    def signaling(self, event):

        try:

            hub = event._dict['HUB']
            k = event._dict['K']
            tran = event._dict['T']

        except KeyError:

            return False

        high = k.getHigh()
        low = k.getLow()

        try:

            if tran._placement == 'LONG':

                # 2016-08-19
                # 两种情况都应该考虑平仓：1)当下K线和中枢上沿出现交集；2)当下K线最低点已经高于中枢上沿
                # 对做空，反之亦然
                if low <= hub.ZG <= high or low > hub.ZG:

                    s = 'Exit - Cross meet low <= ZG <= high ' + repr(low) + ', ' + repr(hub.ZG) + ', ' + repr(high)

                    # print(s)

                    return True

                else:

                    return False

            else:

                if low <= hub.ZD <= high or high < hub.ZD:

                    s = 'Exit - Cross meet low <= ZD <= high ' + repr(low) + ', ' + repr(hub.ZD) + ', ' + repr(high)

                    # print(s)

                    return True

                else:

                    return False

        except KeyError:

            return False

    def order(self, event):

        trans = event._dict['TRAN']
        hub = event._dict['HUB']

        flag = False

        for i, _ in enumerate(trans):

            # 通过Key确保每个策略仅执行一次
            if EdgeExit._name not in trans[i]._exits:

                event._dict['T'] = trans[i]

                if self.signaling(event):

                    if trans[i]._placement == 'LONG':

                        point = hub.ZG

                    else:
                        
                        point = hub.ZD

                    trans[i]._exits[EdgeExit._name] = (point, self._position)

                    flag = True

        return flag


class Tran:

    def __init__(self, id, p, ZG, ZD):

        self._id = id

        self._hub_ZG = ZG
        self._hub_ZD = ZD

        # long or short
        self._placement = p

        # 建仓交易记录
        self._entries = {}

        # 平仓交易记录
        self._exits = {}

        # 止损交易记录,可能多于一次相同规则的止损,所以不能采用Key/Value
        self._stops = []

        # 获利
        self._gain = 0

    def gain(self):

        # 计算建仓均价
        e = 0

        # 计算平仓均价
        x = 0

        # 满仓操作
        # 建仓均价按标准定义仓位计算
        if len(self._entries) == 3:

            for n in self._entries:

                e += self._entries[n][0] * self._entries[n][1]

        # 非满仓操作
        # 建仓均价按照操作次数平均值计算
        else:

            for n in self._entries:

                e += self._entries[n][0]

            e = e / len(self._entries)


        for n in self._exits:

            x += self._exits[n][0]

        x = x / len(self._exits)

        if self._placement == 'LONG':

            g = x / e - 1

        else:

            g = e / x - 1

        l = self.stop()

        self._gain = g + l

        return self._gain

    def stop(self):

        lost = 0

        # 记录的止损次数
        for i, _ in enumerate(self._stops):

            # 每次止损操作可能出现不同的止损策略
            for name in self._stops[i]:

                entries = self._stops[i][name][0]

                # 满仓操作
                # 建仓均价按标准定义仓位计算
                if len(entries) == 3:

                    p = 0

                    for n in entries:

                        p += entries[n][0] * entries[n][1]

                # 非满仓操作
                # 建仓均价按照操作次数平均值计算
                else:

                    p = 0

                    for n in entries:

                        p += entries[n][0]

                    p = p / len(entries)

                if self._placement == 'LONG':

                    lost += self._stops[i][name][1] / p - 1

                else:

                    lost += p / self._stops[i][name][1] - 1

        return lost

    @staticmethod
    def archive(trans):

        tran = []

        buf = []

        for _, i in enumerate(trans):

            # 从止损记录列表开始
            for _, stop in enumerate(trans[i]._stops):

                # 读取一条止损记录
                for name in stop:

                    # 基础信息填充
                    buf.append(trans[i]._id)
                    buf.append(trans[i]._hub_ZG)
                    buf.append(trans[i]._hub_ZD)
                    buf.append(trans[i]._placement)

                    # 读取止损记录中的建仓记录
                    entries = stop[name][0]

                    # 填充建仓信息
                    try:

                        buf.append(entries[MidEntry._name][0])

                    except KeyError:

                        buf.append(0)

                    try:

                        buf.append(entries[EdgeEntry._name][0])

                    except KeyError:

                        buf.append(0)

                    try:

                        buf.append(entries[StepEntry._name][0])

                    except KeyError:

                        buf.append(0)

                    try:

                        buf.append(entries[FollowEntry._name][0])

                    except KeyError:

                        buf.append(0)

                    try:

                        buf.append(entries[ReverseEntry._name][0])

                    except KeyError:

                        buf.append(0)

                    try:

                        buf.append(entries[ImmEntry._name][0])

                    except KeyError:

                        buf.append(0)

                    # 填充平仓交易信息
                    buf.append(0)
                    buf.append(0)
                    buf.append(0)
                    buf.append(0)

                    # 填充止损价位
                    buf.append(stop[name][1])

                    # Gain/Loss计算
                    # 满仓操作
                    # 建仓均价按标准定义仓位计算
                    if len(entries) == 3:

                        p = 0

                        for n in entries:

                            p += entries[n][0] * entries[n][1]

                    # 非满仓操作
                    # 建仓均价按照操作次数平均值计算
                    else:

                        p = 0

                        for n in entries:

                            p += entries[n][0]

                        p = p / len(entries)

                    if trans[i]._placement == 'LONG':

                        buf.append(stop[name][1] / p - 1)

                    else:

                        buf.append(p / stop[name][1] - 1)

                    tran.append(copy.deepcopy(buf))

                    buf.clear()

            # 有成功建仓/平仓记录
            if len(trans[i]._entries) != 0:

                # 基础信息填充
                buf.append(trans[i]._id)
                buf.append(trans[i]._hub_ZG)
                buf.append(trans[i]._hub_ZD)
                buf.append(trans[i]._placement)

                # 填充建仓信息
                try:

                    buf.append(trans[i]._entries[MidEntry._name][0])

                except KeyError:

                    buf.append(0)

                try:

                    buf.append(trans[i]._entries[EdgeEntry._name][0])

                except KeyError:

                    buf.append(0)

                try:

                    buf.append(trans[i]._entries[StepEntry._name][0])

                except KeyError:

                    buf.append(0)

                try:

                    buf.append(trans[i]._entries[FollowEntry._name][0])

                except KeyError:

                    buf.append(0)

                try:

                    buf.append(trans[i]._entries[ReverseEntry._name][0])

                except KeyError:

                    buf.append(0)

                try:

                    buf.append(trans[i]._entries[ImmEntry._name][0])

                except KeyError:

                    buf.append(0)


                # 填充平仓信息
                try:

                    buf.append(trans[i]._exits[MidExit._name][0])

                except KeyError:

                    buf.append(0)

                try:

                    buf.append(trans[i]._exits[EdgeExit._name][0])

                except KeyError:

                    buf.append(0)

                try:

                    buf.append(trans[i]._exits[ImmExit._name][0])

                except KeyError:

                    buf.append(0)

                try:

                    buf.append(trans[i]._exits['STEP_EXIT'][0])

                except KeyError:

                    buf.append(0)

                # 止损信息填充
                buf.append(0)

                # 计算建仓均价
                e = 0

                # 计算平仓均价
                x = 0

                # 满仓操作
                # 建仓均价按标准定义仓位计算
                if len(trans[i]._entries) == 3:

                    for n in trans[i]._entries:

                        e += trans[i]._entries[n][0] * trans[i]._entries[n][1]

                # 非满仓操作
                # 建仓均价按照操作次数平均值计算
                else:

                    for n in trans[i]._entries:

                        e += trans[i]._entries[n][0]

                    e = e / len(trans[i]._entries)

                for n in trans[i]._exits:

                    x += trans[i]._exits[n][0]

                # 异常情况出现在未来得及平仓
                try:

                    x = x / len(trans[i]._exits)

                except ZeroDivisionError:

                    x = 0

                if x != 0:

                    if trans[i]._placement == 'LONG':

                        buf.append(x / e - 1)

                    else:

                        buf.append(e / x - 1)

                else:

                    buf.append(0)

                tran.append(copy.deepcopy(buf))

                buf.clear()

            # 无交易记录的空中枢
            else:

                # 基础信息填充
                buf.append(trans[i]._id)
                buf.append(trans[i]._hub_ZG)
                buf.append(trans[i]._hub_ZD)
                buf.append(trans[i]._placement)

                # 建仓信息填充
                buf.append(0)
                buf.append(0)
                buf.append(0)
                buf.append(0)
                buf.append(0)
                buf.append(0)

                # 平仓信息填充
                buf.append(0)
                buf.append(0)
                buf.append(0)
                buf.append(0)

                # 止损信息填充
                buf.append(0)

                # 获利信息填充
                buf.append(0)

                tran.append(copy.deepcopy(buf))
                buf.clear()

        return tran

    def __del__(self):
        self._entries.clear()

        self._exits.clear()

        self._stops.clear()
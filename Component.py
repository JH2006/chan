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
        if MidEntry._name not in tran._entries:

            if self.signaling(event):

                k = event._dict['K']
                point = k.getClose()

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

                    s = 'Entry -- Cross meet low <= ZG <= high ' + repr(low) + ', ' + repr(hub.ZG) + ', ' + repr(high)

                    # print(s)

                    return True

                else:

                    return False

            else:

                if low <= hub.ZD <= high:

                    s = 'Entry -- Cross meet low <= ZD <= high ' + repr(low) + ', ' + repr(hub.ZD) + ', ' + repr(high)

                    # print(s)

                    return True

                else:

                    return False

        except KeyError:

            return False

    def order(self, event):

        tran = event._dict['TRAN']

        # 通过Key确保每个策略仅执行一次
        if EdgeEntry._name not in tran._entries:

            if self.signaling(event):

                k = event._dict['K']
                point = k.getClose()
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
                    if m_h > m_l:

                        return True

        elif hub.pos == 'Down' and last_type.getPos() == 'Down':

            if last_type.candle.getHigh() <= hub.ZD:

                last_revert_type = types.container[len(types.container) - 2]

                if last_type.candle_index - last_revert_type.candle_index >= 4:

                    low = candles.container[last_type.candle_index -1].getLow()
                    high = candles.container[last_revert_type.candle_index].getHigh()

                    m_h = min(high, hub.ZG)
                    m_l = max(low, hub.ZD)

                    if m_h > m_l:

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

        tran = event._dict['TRAN']

        # 通过Key确保每个策略仅执行一次
        if MidExit._name not in tran._exits:

            if self.signaling(event):

                k = event._dict['K']
                point = k.getClose()

                tran._exits[MidExit._name] = (point, self._position)

                return True

        return False

class EdgeExit(Exits):

    _name = 'EDGE_EXIT'

    def __init__(self, position):

        Exits.__init__(self, position)

        self._name = MidExit._name

    def signaling(self, event):

        try:

            hub = event._dict['HUB']
            k = event._dict['K']
            tran =  event._dict['TRAN']

        except KeyError:

            return False

        high = k.getHigh()
        low = k.getLow()

        try:

            if tran._placement == 'LONG':

                if low <= hub.ZG <= high:

                    s = 'Exit - Cross meet low <= ZG <= high ' + repr(low) + ', ' + repr(hub.ZG) + ', ' + repr(high)

                    # print(s)

                    return True

                else:

                    return False

            else:

                if low <= hub.ZD <= high:

                    s = 'Exit - Cross meet low <= ZD <= high ' + repr(low) + ', ' + repr(hub.ZD) + ', ' + repr(high)

                    # print(s)

                    return True

                else:

                    return False

        except KeyError:

            return False

    def order(self, event):

        tran = event._dict['TRAN']

        # 通过Key确保每个策略仅执行一次
        if EdgeExit._name not in tran._exits:

            if self.signaling(event):

                k = event._dict['K']
                point = k.getClose()

                tran._exits[EdgeExit._name] = (point, self._position)

                # 首先触碰中枢边界，100%平仓
                if MidExit._name not in tran._exits:

                    tran._exits[MidExit._name] = (point, self._position)

                return True

        return False


class Tran:

    def __init__(self, id, p):

        self._id = id

        # long or short
        self._placement = p

        # 建仓交易记录
        self._entries = {}
        # 平仓交易记录
        self._exits = {}
        # 止损交易记录
        self._stops = []

    def __del__(self):
        self._entries.clear()
        self._exits.clear()
        self._stops.clear()
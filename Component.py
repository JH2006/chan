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

            s = 'Cross meet low <= mid <= high' + repr(low) + ',' + repr(mid) + ',' + repr(high)

            print(s)

        else:

            cross = False

        return cross

    def order(self, event):

        if self.signaling(event):

            tran = event._dict['TRAN']

            # 通过Key确保每个策略仅执行一次
            if not tran._entries.has_key(MidEntry._name):

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

                    s = 'Cross meet low <= ZG <= high ' + repr(low) + ', ' + repr(hub.ZG) + ', ' + repr(high)

                    print(s)

                    return True

                else:

                    return False

            else:

                if low <= hub.ZD <= high:

                    s = 'Cross meet low <= ZD <= high ' + repr(low) + ', ' + repr(hub.ZD) + ', ' + repr(high)

                    print(s)

                    return True

                else:

                    return False

        except KeyError:

            return False

    def order(self, event):

        if self.signaling(event):

            tran = event._dict['TRAN']

            # 通过Key确保每个策略仅执行一次
            if not tran._entries.has_key(EdgeEntry._name):

                k = event._dict['K']
                point = k.getClose()
                tran._entries[EdgeEntry._name] = (point, self._position)

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

            s = 'Cross meet low <= mid <= high' + repr(low) + ',' + repr(mid) + ',' + repr(high)

            print(s)

        else:

            cross = False

        return cross

    def order(self, event):

        if self.signaling(event):

            tran = event._dict['TRAN']

            # 通过Key确保每个策略仅执行一次
            if not tran._exits.has_value(MidExit._name):

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

            if tran._placement == 'Long':

                if low <= hub.ZG <= high:

                    s = 'Long - Cross meet low <= ZG <= high ' + repr(low) + ', ' + repr(hub.ZG) + ', ' + repr(high)

                    print(s)

                    return True

                else:

                    return False

            else:

                if low <= hub.ZD <= high:

                    s = 'Short - Cross meet low <= ZD <= high ' + repr(low) + ', ' + repr(hub.ZD) + ', ' + repr(high)

                    print(s)

                    return True

                else:

                    return False

        except KeyError:

            return False

    def order(self, event):

        if self.signaling(event):

            tran = event._dict['TRAN']

            # 通过Key确保每个策略仅执行一次
            if not tran._exits.has_value(EdgeExit._name):

                k = event._dict['K']
                point = k.getClose()

                tran._exits[EdgeExit._name] = (point, self._position)

                # 首先触碰中枢边界，100%平仓
                if not tran._exits.has_value(MidExit._name):

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
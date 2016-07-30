# 2016-07-28
# 交易系统组件,包括Entries, Stops, Exits
# 每个组件都有具体继承类,继承子类具体实现不同的信号判断,并执行交易动作
# 交易系统组件本身不构成完整交易系统,只有当把交易组件以有序地方式组合起来后才构成完整交易系统

class Entries:

    def __init__(self, position):

        self._position = position

        # 标示指示每个策略仅执行一次
        self._ordered = False

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

        if not self._ordered:

            if self.signaling(event):

                tran = event._dict['TRAN']

                k = event._dict['K']
                point = k.getClose()

                tran._trans[MidEntry._name] = (point, self._position)

                self._ordered = True

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

        if not self._ordered:

            if self.signaling(event):

                tran = event._dict['TRAN']

                k = event._dict['K']
                point = k.getClose()

                tran._trans[EdgeEntry._name] = (point, self._position)

                self._ordered = True

                return True

        return False


class Stops:

    def __init__(self):

        pass

    def signaling(self):

        pass

    def order(self):

        pass



class Exits:

    def __init__(self):

        pass

    def signaling(self):

        pass

    def order(self):

        pass


class Tran:

    def __init__(self, id):

        self._id = id

        self._trans = {}
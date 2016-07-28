# 2016-07-28
# 交易系统组件,包括Entries, Stops, Exits
# 每个组件都有具体继承类,继承子类具体实现不同的信号判断,并执行交易动作
# 交易系统组件本身不构成完整交易系统,只有当把交易组件以有序地方式组合起来后才构成完整交易系统

class Entries:

    def __init__(self):

        pass

    def signaling(self):

        pass

    def order(self):

        pass


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

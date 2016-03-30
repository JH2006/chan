
import matplotlib.pyplot as plt

import matplotlib.patches as patches

import pandas as pd

import copy

# 全局变量,记录分型队列位置
# 变量在构造笔函数中引用
g_fractal_index = 0

# 全局变量,记录有效笔的总数量,用于构造中枢过程
# 有效笔的意思是经过了笔合并处理
# 变量在init_hub中被引用
# 遍历点从1开始,避免向前删除越界
# 理论上可以实现从第一个笔开始,只需适当考虑边界问题即可
g_pens_index = 1

# 全局变量,记录在构造中枢过程中,形成最后一个中枢的笔的索引位置
# 变量在init_hub中被引用
g_last_hub_end_pen = 0

# 全局变量,记录临时笔,可用于回退
g_pens_stack = []

# 全局变量,记录临时笔所处的笔队列的索引位置
g_pens_stack_index = 0

# 2016-03-23
# 全局变量,记录二次延迟处理,和g_pens_stack相似
g_pens_stack_delay = []

# 数据获取以及初始化
# 次级数据连同本级数据一起处理
# 函数参数说明处理数据年份,默认值为2000
def connectxl(year_start, year_end, start, end):

    data_1 = []

    #e_1 = pd.read_csv('ccon5094@uni.sydney.edu.au-AUD1h-N112284510.csv')
    #e_m = pd.read_csv('ccon5094@uni.sydney.edu.au-AUD10m-N112284425.csv')

    e_1 = pd.read_csv('ccon5094@uni.sydney.edu.au-AUD10m-N112284425.csv')
    # e_2 = pd.read_csv('ccon5094@uni.sydney.edu.au-AUD10m-N112284425XXX.csv')

    count = 0
    row_2 = 0

     # 本级别数据读取的开始/结束时间戳
    start_date_1 = pd.datetime.now()
    end_date_1 = pd.datetime.now()

    for row_h in range(0, len(e_1)):

        date_1 = pd.to_datetime(e_1['Date[G]'][row_h])

        # 如果遍历的数据年份和参数相同
        if year_start <= date_1.year < year_end:

            count += 1

            # 第一次进入循环体,记录起点
            if count == 1:
                start_date_1 = date_1

            if start <= count <= end:

                time_1 = pd.to_datetime(e_1['Time[G]'][row_h])
                open_h = e_1['Open'][row_h]
                high_h = e_1['High'][row_h]
                low_h = e_1['Low'][row_h]
                close_1 = e_1['Last'][row_h]

                # 构造高级别K线字典
                d_1 = {'Year': date_1.year,
                       'Month': date_1.month,
                       'Day': date_1.day,
                       'Hour': time_1.hour,
                       'Min': time_1.minute,
                       'Open': open_h,
                       'High': high_h,
                       'Low': low_h,
                       'Close': close_1}

                # 初始化子级别数据存储
                data_2 = []
                """
                while row_2 in range(len(e_2)):

                    date_2 = pd.to_datetime(e_2['Date[G]'][row_2])
                    time_2 = pd.to_datetime(e_2['Time[G]'][row_2])
                    open_2 = e_2['Open'][row_2]
                    high_2 = e_2['High'][row_2]
                    low_2 = e_2['Low'][row_2]
                    close_2 = e_2['Last'][row_2]

                    d_2 = {'Year': date_2.year,
                           'Month': date_2.month,
                           'Day': date_2.day,
                           'Hour': time_2.hour,
                           'Min': time_2.minute,
                           'Open': open_2,
                           'High': high_2,
                           'Low': low_2,
                           'Close': close_2}

                    # TODO 等实际数据到来后可以实现次级别数据的嵌套
                """

                data_1.append(d_1)


                # 记录可能出现的最后一个本级别数据
                end_date_1 = date_1

        elif date_1.year >= year_end:

            break
    """

    # 次级别数据和高级别相同的处理逻辑
    for row_m in range(len(e_m)):

        date_m = pd.to_datetime(e_m['Date[G]'][row_m])

        if start_date_m <= date_m < end_date_m:

            time_m = pd.to_datetime(e_m['Time[G]'][row_m])
            open_m = e_m['Open'][row_m]
            high_m = e_m['High'][row_m]
            low_m = e_m['Low'][row_m]
            close_m = e_m['Last'][row_m]

            d_m = {'Year': date_m.year, 'Month': date_m.month, 'Day': date_m.day,
                   'Hour': time_m.hour, 'Min': time_m.minute, 'Open': open_m, 'High': high_m,
                   'Low': low_m, 'Close': close_m}

            data_2.append(d_m)
    """

    return data_1


# 处理包含函数
# 每生成一次K线调用一次
def init_contain(stocks):

    if len(stocks) == 2:

        # 通过最开始两根K线的关系进行包含方向的初始化
        f_k = stocks[0]
        s_k = stocks[1]

        pos = 'Up'

        # 无包含向下处理
        if f_k['High'] > s_k['High'] and f_k['Low'] > s_k['Low']:

            # 增加K线方向属性
            stocks[1]['Pos'] = 'Down'

        # 无包含向上处理
        elif f_k['High'] < s_k['High'] and f_k['Low'] < s_k['Low']:

            stocks[1]['Pos'] = 'Up'

        # 存在包含关系
        else:

            # 由于一开始不存在向上包含或者向下包含的说法,要第一次确定属性的方式就是开两个K线顶底部的差的比较关系
            # 如果顶部差比底部差宽,则认为向上包含,反之亦然
            # 包含关系的初始化只是为了程序的运行考虑,不会影响到实际后面的其他包含关系处理
            a_up = abs(f_k['High'] - s_k['High'])
            a_down = abs(f_k['Low'] - s_k['Low'])

            if a_up > a_down:

                stocks[1]['Pos'] = 'Up'

            else:

                stocks[1]['Pos'] = 'Down'

    elif len(stocks) > 2:

        i = len(stocks) - 1

        # 无包含向上处理
        if stocks[i]['High'] > stocks[i-1]['High'] and stocks[i]['Low'] > stocks[i-1]['Low']:

            stocks[i]['Pos'] = 'Up'

        # 无包含向下处理
        elif stocks[i]['High'] < stocks[i-1]['High'] and stocks[i]['Low'] < stocks[i-1]['Low']:

            stocks[i]['Pos'] = 'Down'

        # 存在包含关系
        else:

            pos = stocks[i-1]['Pos']

            if pos == 'Up':
                high = max(stocks[i]['High'], stocks[i-1]['High'])
                low = max(stocks[i]['Low'], stocks[i-1]['Low'])

                stocks[i]['High'] = high
                stocks[i]['Low'] = low
                stocks[i]['Pos'] = 'Up'

                stocks.pop(i-1)

            elif pos == 'Down':
                high = min(stocks[i]['High'], stocks[i-1]['High'])
                low = min(stocks[i]['Low'], stocks[i-1]['Low'])

                stocks[i]['High'] = high
                stocks[i]['Low'] = low
                stocks[i]['Pos'] = 'Down'

                stocks.pop(i-1)

    # 每次处理完一个新K线后,调用MACD处理
    init_MACD(stocks)


def init_fractals(stocks, fractals):

    # 只有当存在至少三根K线后才做分型处理
    if len(stocks) < 3:
        return 0

    # 当新增加一个K线后,对队列中倒数第二个K线做分型处理
    cur_index = len(stocks) - 2
    pre_index = cur_index - 1
    pos_index = cur_index + 1

    # 当前K线
    cur_high = stocks[cur_index]['High']
    cur_low = stocks[cur_index]['Low']

    # 前探K线
    pre_1igh = stocks[pre_index]['High']
    pre_low = stocks[pre_index]['Low']

    # 后探K线
    fur_high = stocks[pos_index]['High']
    fur_low = stocks[pos_index]['Low']

    # 顶分型-当前K线高点分别高于前后两K线高点,当前K线低点分别高于前后两K线低点
    if cur_high > pre_1igh and cur_high > fur_high and cur_low > pre_low and cur_low > fur_low:

        t = {'K': stocks[cur_index],
             'Hour': stocks[cur_index]['Hour'],
             'Min': stocks[cur_index]['Min'],
             'High': stocks[cur_index]['High'],
             'Low': stocks[cur_index]['Low'],
             'Close': stocks[cur_index]['Close'],
             'Position': 'Up',
             'K_Index': cur_index}

        if len(fractals) != 0:
            # 读取列表里最后一个分型
            last = fractals[len(fractals)-1]

            if last['K_Index'] == t['K_Index']:

                return len(fractals)

            # 如果最后一个分型与当前分型同向, 并且当前分型比最后一个分型高
            # 这个步骤的目的是对相邻的具有同向属性的分型做处理,这样就确保了任何一对相邻的分型必然有且仅有反向属性
            if last['Position'] == 'Up' and t['High'] > last['High']:

                # 移除在队列中的最后一个分型
                fractals.pop()

        fractals.append(t)

        return len(fractals)

    # 低分型-当前K线高点分别低于前后两K线高点,当前K线低点分别低于前后两K线低点
    elif cur_low < pre_low and cur_low < fur_low and cur_high < pre_1igh and cur_high < fur_high:

        t = {'K': stocks[cur_index],
             'Hour': stocks[cur_index]['Hour'],
             'Min': stocks[cur_index]['Min'],
             'High': stocks[cur_index]['High'],
             'Low': stocks[cur_index]['Low'],
             'Close': stocks[cur_index]['Close'],
             'Position': 'Down',
             'K_Index': cur_index}

        if len(fractals) != 0:

            # 读取列表里最后一个分型
            last = fractals[len(fractals)-1]

            if last['K_Index'] == t['K_Index']:

                return False

            # 如果最后一笔与当前分型同向, 并且当前笔比最后一笔低
            # 这个步骤的目的是对相邻的具有同向属性的分型做处理,这样就确保了任何一对相邻的分型必然有且仅有反向属性
            if last['Position'] == 'Down' and t['Low'] < last['Low']:

                # 移除在队列中的最后一个分型
                fractals.pop()

        fractals.append(t)

        return True

    else:

        return False


# 定义笔,函数输入为顶低分型数组
def init_pen(pens, fractals):

    # 引用全局变量纪录最后访问分型队列的最后位置
    global g_fractal_index

    # 遍历分型结构发现笔结构
    # 最后一个分型结构不存在构成笔的可能,省去最后一个分型结构的遍历

    # TODO 2016-03-29. 对全局分型做处理未能处理到最后一笔的实现也会导致当前的迟滞
    while g_fractal_index < len(fractals)-1:

        # 发现当前分型为顶分型
        if fractals[g_fractal_index]['Position'] == 'Up':

            # 调用朝下侦查函数发现对于笔结构的底分型,并返回对应的分型结构在数组中的索引
            nextIndex = spy_down(g_fractal_index, fractals)

            # nextIndex == -1说明侦查函数找不到合适的分型结构,仅有在遍历至分型数组结束时才可能发生
            if nextIndex != -1:

                # 构造笔字典结构
                pen = {'High': fractals[g_fractal_index]['High'],
                       'Low': fractals[nextIndex]['Low'],
                       'Position': 'Down',
                       'Begin_Type': fractals[g_fractal_index],
                       'End_Type': fractals[nextIndex]}

                # 重置下一个笔的起点:下一个笔的起点就是上一个笔的终点
                g_fractal_index = nextIndex

                pens.append(pen)

            # nextIndex == -1发生,使用Break结束遍历
            else:
                break

        # 发现当前分型为底分型
        elif fractals[g_fractal_index]['Position'] == 'Down':

            # 调用朝上侦查函数发现对于笔结构的底分型,并返回对应的分型结构在数组中的索引
            nextIndex = spy_up(g_fractal_index, fractals)

            if nextIndex != -1:

                pen = {'High': fractals[nextIndex]['High'],
                       'Low': fractals[g_fractal_index]['Low'],
                       'Position': 'Up',
                       'Begin_Type': fractals[g_fractal_index],
                       'End_Type': fractals[nextIndex]}

                g_fractal_index = nextIndex

                pens.append(pen)

            else:
                break

    return len(pens)


# 朝上侦查函数用于发现底分型对应的顶分型所构成的笔
# 算法不断向上寻找出现的最高的顶分型,直到出现可以构成向下笔的底分型出现
def spy_up(index, types):

    cur_high = types[index]['High']
    cur_low = types[index]['Low']

    # 由于存在向前延伸的行为,数组遍历最大仅能到倒数第二个
    for j in range(index, len(types)-1):

        # 当前分型为顶分型
        if types[j]['Position'] == 'Up':

            # 如果当前顶分型的高点高于已记录的出现过的最高顶分型,则更新最高点数据,并保持当前分型所在数组指针
            if types[j]['High'] > cur_high and types[j]['Low'] > cur_low:

                cur_high = types[j]['High']
                cur_index = j

                # 如果当前顶分型的下一个分型为底分型,同时底分型的低点低于当前顶分型的高点,则说明构造潜在向下笔的条件成立
                # 此时认为构造当前向上笔完成,返回已记录的最高顶分型指针
                if types[j+1]['Position'] == 'Down' and \
                            types[j+1]['Low'] < types[j]['Low'] and \
                            types[j+1]['High'] < types[j]['High']:

                    return cur_index

                # 或者下一笔虽然为通向笔,但具有反向性质
                elif types[j+1]['Position'] == 'Up' and types[j+1]['High'] < types[j]['High'] and types[j+1]['Low'] < types[j]['Low']:

                    return cur_index

    # 遍历结束,返回结束标示
    return -1


# 下侦查函数
def spy_down(index, types):

    cur_high = types[index]['High']
    cur_low = types[index]['Low']

    for j in range(index, len(types)-1):

        if types[j]['Position'] == 'Down':

            # 构成向下笔的顶底分型必须同时满足下面条件是为了避开包含关系
            if types[j]['Low'] < cur_low and types[j]['High'] < cur_high:

                # 记录最后满足条件的信息
                cur_low = types[j]['Low']
                cur_index = j

                # 要同时满足以下条件才能构成笔
                # 下一个分型为反向分型.目前的实现是认为出现反向分型则此笔结束
                # 构成向上笔的顶底分型必须同时满足条件以避开包含关系
                if types[j+1]['Position'] == 'Up' and \
                                types[j+1]['High'] > types[j]['High'] and \
                                types[j+1]['Low'] > types[j]['Low']:

                        return cur_index

                # 或者下一笔虽然为同向笔,但具有反向性质
                elif types[j+1]['Position'] == 'Down' and \
                                types[j+1]['High'] > types[j]['High'] and \
                                types[j+1]['Low'] > types[j]['Low']:

                    return cur_index

    return -1


# 处理不满足构成笔K线数量要求的情况
# 处理不合法笔的关键在于当考虑把此不合法笔撤销的时候,如何处理此操作所可能引起的前后关联笔环境的变化
# 无论是删除向上笔还是向下笔,都必须同时删除与之相连的一笔,这样才能保证相邻笔的在方向上相反的特性
# 要判断是删除前一笔还是后一笔的关键在于那种删除方式能令具有更剧烈的涵盖范围,也就是高点更高,低点更低
def merge_pen(pens):

    global g_pens_index
    global g_pens_stack_index
    global g_pens_stack_delay
    global g_pens_stack

    # 循环体在笔队列反向偏置2的位置结束的原因是防止越界

    # 2016-03-25
    # 按照当前保留2笔的设计虽然可以确保在处理不合法笔的时候不出现越界,但缺陷是对任何情况都必须等到至少有两笔的时候才能处理,对现实情况的反映
    # 存在延迟.
    # 并不是所有需要处理笔合并的情况都需要向后两笔,可以把这个约束条件针对各个特定情况实现,这样至少可以加快不需要约束条件的场景

    while g_pens_index < len(pens) - 1:

        # 只有当用于回退的临时笔队列不为空(说明有回退操作的可能),回退笔与当前笔有至少两笔的距离的时候才进行操作
        # 2016-03-21
        # 关于是采用g_pens_index还是len(pens)与g_pens_stack_index的距离判断问题
        # 测试发现有些场景采用len(pens)的时候判断revert的准确性没有g_pens_index高,其实本质在于用g_pens_index的时候延迟时间较长,在走势
        # 上看,更容易出现了满足revert条件的K线而已,其他没有差别
        # 这是在时间和准确性上的平衡取舍

        # 2016-03-22
        # 修改为len(pens),同时修改了revert_pen的判决回退条件
        if len(pens) - g_pens_stack_index >= 2 and len(g_pens_stack) != 0:

            revert_pen(pens)

        """
        # 2016-03-22
        # 继续保留以g_pens_index的判决方式,以便增加覆盖场景的概率
        # 2016-03-23
        # 但从测试结果来看并不理想,能够覆盖一定的场景,但同时又引入了另外的错误
        # 具体案例参考:ch.test(2002,2003,1600,1900)
        elif g_pens_index - g_pens_stack_index >= 2 and len(g_pens_stack_delay) != 0:

            revert_pen(pens)
        """

        # 读取笔开始位置以及结束位置的index,可用于判断笔在构成K线数量方面的合法性
        e_K_index = pens[g_pens_index]['End_Type']['K_Index']
        s_K_index = pens[g_pens_index]['Begin_Type']['K_Index']

        # 目前定义一笔包括顶底K线的话至少要有5根构成
        if e_K_index - s_K_index < 4:

            pos = pens[g_pens_index]['Position']

            # 如果不合法的笔是向下笔
            if pos == 'Down':

                pre_pen = pens[g_pens_index - 1]
                post_pen = pens[g_pens_index + 1]

                # 这是当前不合法的向下笔的底部具有比上一个向下笔底部还低的特性
                # 由于此笔即将要销毁,前一个向下笔的底部可以延伸到待销毁向下笔的底部
                if pre_pen['Low'] >= pens[g_pens_index]['Low']:

                    # 保护带.避免前向越界的可能,可以继续向前处理
                    if g_pens_index - 2 >= 0:

                        # 如果发现回调测试还未来得及执行就再次出现新低的情况的话,马上进行回调处理
                        if len(g_pens_stack) != 0:
                            revert_pen(pens)

                        # 在笔修改前,保存此笔于堆栈,命名为回退笔
                        g_pens_stack.append(copy.deepcopy(pens[g_pens_index-2]))
                        g_pens_stack_delay.append(copy.deepcopy(pens[g_pens_index-2]))

                        # 更新上一向下笔底部属性
                        pens[g_pens_index-2]['Low'] = pens[g_pens_index]['Low']
                        pens[g_pens_index-2]['End_Type'] = pens[g_pens_index]['End_Type']

                        # 销毁当前笔以及前一个与此笔相连的向上笔
                        # 注意销毁顺序必须是由后向前,否则会误删其他笔
                        pens.pop(g_pens_index)

                        # 在删除笔前,保存此笔于堆栈
                        g_pens_stack.append(copy.deepcopy(pens[g_pens_index-1]))
                        g_pens_stack_delay.append(copy.deepcopy(pens[g_pens_index-1]))

                        pens.pop(g_pens_index-1)

                        # 在全局笔队列指针修改前,保存临时堆栈中笔所处于的全局笔队列的位置
                        # 注意,此处减了2,因为这是当前笔与回退笔的最小偏置,它指向的是被保存的笔
                        g_pens_stack_index = g_pens_index - 2

                        # 指针回退一个单位
                        g_pens_index -= 1

                    # 不满足保护带要求则不做处理
                    else:
                        g_pens_index += 1

                # 与此不合法向下笔前后相连的向上笔中,后面的向上笔顶部比前面的向上笔顶部高
                # 在销毁不合法笔的时候,修改前一向上笔顶部指向新的高点

                # 2016-03-25
                # 增加了一个当前处理笔与笔队列总长度的关系判断
                # 由于这个场景需要删除后一笔,所以需要两者间至少有一个笔的距离
                elif post_pen['High'] >= pre_pen['High'] and len(pens) - g_pens_index >= 1:

                    # 更新顶部信息
                    pens[g_pens_index-1]['High'] = post_pen['High']
                    pens[g_pens_index-1]['End_Type'] = post_pen['End_Type']

                    # 销毁当前笔以及后一个向上笔
                    pens.pop(g_pens_index+1)
                    pens.pop(g_pens_index)

                # 最后一种情况是不合法向下笔被前一笔完全包含,这和第一个情况相反
                # 同时不合法笔后面的向上笔也被前一向上笔完全包含
                # 不合法笔以及后一向上笔将会被销毁,同时与后向上笔相连的向下笔高点指向前一向上笔的高点
                elif pre_pen['Low'] < pens[g_pens_index]['Low'] and post_pen['High'] < pre_pen['High']:

                    # 此场景的处理要遍历并删除到当前笔往后两笔的地方
                    if len(pens)-g_pens_index > 2:

                        pens[g_pens_index+2]['High'] = pre_pen['High']
                        pens[g_pens_index+2]['Begin_Type'] = pre_pen['End_Type']

                        # 不合法笔以及与其相连的后一向上笔被销毁
                        pens.pop(g_pens_index+1)
                        pens.pop(g_pens_index)

                    # 如果此场景不满足了, 就暂时不做处理, 如果后面还有一笔的话也有可能可以处理笔合并
                    else:
                        g_pens_index += 1
                        break

            # 处理向上的不合法笔,逻辑与向下笔处理一致
            else:

                pre_pen = pens[g_pens_index-1]
                post_pen = pens[g_pens_index+1]

                if pre_pen['High'] <= pens[g_pens_index]['High']:

                    if g_pens_index - 2 >= 0:

                        # 2016-03-21
                        # 在笔修改前,保存此笔于堆栈
                        g_pens_stack.append(copy.deepcopy(pens[g_pens_index-2]))

                        pens[g_pens_index-2]['High'] = pens[g_pens_index]['High']
                        pens[g_pens_index-2]['End_Type'] = pens[g_pens_index]['End_Type']

                        pens.pop(g_pens_index)

                        # 2016-03-21
                        g_pens_stack.append(copy.deepcopy(pens[g_pens_index-1]))

                        pens.pop(g_pens_index-1)

                        # 2016-03-21
                        g_pens_stack_index = g_pens_index - 2

                        g_pens_index -= 1

                    else:
                        g_pens_index += 1

                # 2016-03-25
                # 增加了一个当前处理笔与笔队列总长度的关系判断
                # 由于这个场景需要删除后一笔,所以需要两者间至少有一个笔的距离
                elif post_pen['Low'] <= pre_pen['Low'] and len(pens) - g_pens_index >= 1:

                    # 2016-03-20
                    # 如果已经出现了回退笔,同时出现了删除此向上笔的场景,则在删除之前先处理回退笔
                    """
                    if len(pens) - g_pens_stack_index >= 2 and len(g_pens_stack) != 0:

                        revert_pen(pens)
                        break
                    """

                    pens[g_pens_index-1]['Low'] = post_pen['Low']
                    pens[g_pens_index-1]['End_Type'] = post_pen['End_Type']
                    pens.pop(g_pens_index+1)
                    pens.pop(g_pens_index)

                elif pre_pen['High'] > pens[g_pens_index]['High'] and post_pen['Low'] > pre_pen['Low']:

                    if len(pens)-g_pens_index > 2:

                        pens[g_pens_index+2]['Low'] = pre_pen['Low']
                        pens[g_pens_index+2]['Begin_Type'] = pre_pen['End_Type']
                        pens.pop(g_pens_index+1)
                        pens.pop(g_pens_index)

                    else:
                        g_pens_index += 1
                        break

        else:
        
            g_pens_index += 1


# 回退笔操作函数
# 回退操作可以分为向上和向下两种,目前仅实现了对向下笔的回退
# 为什么需要回退操作:回退操作可以认为是merge函数的补充.merge函数已经可以处理绝大部分非法笔的合并处理,但有一种情况需要再进行一次额外的监控处理.
# 这就是当前不合法的向下笔的底部具有比上一个向下笔底部还低的情况.merge函数在处理这种情况的时候会把与当前非法笔相邻的前一个合法向上笔一同删除
# 如果是在出现此非法向下笔的底部后走势反转向上形成向上笔,则这个底部可以确定
# 但如果在此非法笔底部之后仍然继续有新低,并且这个新低可以和被删除的合法向上笔的顶部构成一个向下笔,那么之前的合法向上笔不应该被删除,合法向上笔的前一个向下笔底部也不应该被修改
# 程序负责对上述两种状态做判断,要保留修改后的笔还是恢复原来的笔
def revert_pen(pens):

    global g_pens_index
    global g_pens_stack_index
    global g_pens_stack_delay


    # pen_r 为相对靠近右边的笔
    # pen_l 为相对靠近左边的笔
    if len(g_pens_stack) != 0:
        legend_pen_r = g_pens_stack.pop()
        legend_pen_l = g_pens_stack.pop()

    else:
        legend_pen_r = g_pens_stack_delay.pop()
        legend_pen_l = g_pens_stack_delay.pop()

    # 读取pen_l向右偏置为2的笔
    pen_2 = pens[g_pens_stack_index+2]

    # 这个偏置笔的方向决定了笔回调的方式
    # 如果是做向下的回调,核心就是判断在当前g_pens_stack_index位置的笔的底部K线与g_pens_stack_index+1笔的顶部K线之间的距离是否
    # 足够形成新的笔.  如果能够形成新笔,则需要把原有笔恢复,同时构造g_pens_stack_index底部和g_pens_stack_index+1顶部之间新的笔
    if pen_2['Position'] == 'Down':

        # 当前的K线底部K线索引以及分型信息
        # cur_bottom_k_index = pens[g_pens_index]['End_Type']['K_Index']
        # cur_bottom_k = pens[g_pens_index]['End_Type']
        # 2016-03-20
        cur_bottom_k_index = pen_2['End_Type']['K_Index']
        cur_bottom_k = pen_2['End_Type']

        # 笔修改前的旧底部信息
        # 2016-03-22
        # 修改pre_bottom_k = pens[g_pens_stack_index]['End_Type']->pre_bottom_k = legend_pen_r['Begin_Type']
        pre_bottom_k = legend_pen_r['Begin_Type']

        # 之前被删除笔的顶部K线索引以及分型信息
        legend_top_k_index = legend_pen_r['End_Type']['K_Index']
        legend_top_k = legend_pen_r['End_Type']

        # 最新的顶底间要满足几个条件
        # 1.至少要满足4根K线的关系
        # 2.顶底均比被删除笔的顶底分别要低
        # 3.要比前面一个向下笔的底部出新低

        # 2016-03-22
        # 修改判决条件:
        # 1. 删除cur_bottom_k['Low'] < pre_bottom_k['Low']
        # 2. 添加cur_bottom_k['High'] < pre_bottom_k['High'] and cur_bottom_k['Low'] < pre_bottom_k['Low']
        if cur_bottom_k_index - legend_top_k_index >= 4 and \
                        cur_bottom_k['Low'] < legend_top_k['Low'] and \
                        cur_bottom_k['High'] < legend_top_k['High'] and \
                        cur_bottom_k['High'] < pre_bottom_k['High'] and \
                        cur_bottom_k['Low'] < pre_bottom_k['Low']:

            # 构造笔字典结构
            pen = {'High': legend_top_k['High'],
                    'Low': cur_bottom_k['Low'],
                    'Position': 'Down',
                    'Begin_Type': legend_top_k,
                    'End_Type': cur_bottom_k}

            # 修改向下笔的底部以便其恢复到遇到非法向下笔之前的状态
            pens[g_pens_stack_index]['End_Type'] = copy.deepcopy(legend_pen_l['End_Type'])
            pens[g_pens_stack_index]['Low'] = legend_pen_l['Low']

            # 下面的5个步骤都是关于删除/插入笔的动作.这个的关键是索引偏置
            # pens.pop(g_pens_index-1)
            pens.pop(g_pens_stack_index+2)

            # 在偏置为1的位置恢复向上笔
            pens.insert(g_pens_stack_index+1, copy.deepcopy(legend_pen_r))

            # 在偏置为2的位置新插入向下笔
            pens.insert(g_pens_stack_index+2, copy.deepcopy(pen))

            pens.pop(g_pens_stack_index+3)

            # 把全局指针往后移动1位以便指向当前需要处理的笔
            g_pens_index += 1

            # 如果在小距离笔已经可以完成回退,则不需要再处理大距离
            if len(g_pens_stack_delay) != 0:
                g_pens_stack_delay = []

    # TODO 当前没有实现对上行笔的延迟判决，需要考虑实现.有过调测,但没有完成
    """
    # 2016-03-22
    # 实现向上的相似延迟处理
    else:

        cur_top_k_index = pen_2['End_Type']['K_Index']
        cur_top_k = pen_2['End_Type']

        pre_top_k_index =  legend_pen_r['Begin_Type']['K_Index']
        pre_top_k = legend_pen_r['Begin_Type']

        legend_bottom_k_index = legend_pen_r['End_Type']['K_Index']
        legend_bottom_k = legend_pen_r['End_Type']

        if cur_top_k_index - legend_bottom_k_index >= 4 and \
                        cur_top_k['High'] > legend_bottom_k['High'] and \
                        cur_top_k['Low'] > legend_bottom_k['Low'] and \
                        cur_top_k['High'] > pre_top_k['High'] and \
                        cur_top_k['Low'] > pre_top_k['Low']

            pen = {'High': cur_top_k['High'],
                   'Low': legend_bottom_k['Low'],
                   'Position': 'Up',
                   'Begin_Type': legend_bottom_k,
                   'End_Type': cur_top_k}

            pens.pop(g_pens_stack_index+2)

            pens.insert(g_pens_stack_index+1, copy.deepcopy(legend_pen_r))

            pens.insert(g_pens_stack_index+2, copy.deepcopy(pen))

            pens.pop(g_pens_stack_index+3)

            g_pens_index += 1
    """

# MACD计算函数
# 12日EMA的计算：EMA12 = 前一日EMA12 X 11/13 + 今日收盘 X 2/13
# 26日EMA的计算：EMA26 = 前一日EMA26 X 25/27 + 今日收盘 X 2/27
# 差离值（DIF）的计算： DIF = EMA12 - EMA26
# 今日DEA = （前一日DEA X 8/10 + 今日DIF X 2/10）
# MACD=(DIF-DEA）*2
def init_MACD(stocks):

    if len(stocks) == 1:

        stocks[0]['EMA12'] = stocks[0]['Close']
        stocks[0]['EMA26'] = stocks[0]['EMA12']
        stocks[0]['DIF'] = stocks[0]['EMA12'] - stocks[0]['EMA26']
        stocks[0]['DEA'] = 0
        stocks[0]['MACD'] = (stocks[0]['DIF'] - stocks[0]['DEA']) * 2

    else:
        cur_stock = stocks[len(stocks) - 1]
        pre_stock = stocks[len(stocks) - 2]

        pre_EMA12 = pre_stock['EMA12']
        pre_EMA26 = pre_stock['EMA26']
        pre_DEA = pre_stock['DEA']

        cur_stock['EMA12'] = pre_EMA12 * 11/13 + cur_stock['Close'] * 2/13
        cur_stock['EMA26'] = pre_EMA26 * 25/27 + cur_stock['Close'] * 2/27
        cur_stock['DIF'] = cur_stock['EMA12'] - cur_stock['EMA26']
        cur_stock['DEA'] = pre_DEA * 8/10 + cur_stock['DIF'] * 2/10
        cur_stock['MACD'] = (cur_stock['DIF'] - cur_stock['DEA']) * 2


# 中枢定义函数
# 中枢关键属性:
# ZG:重叠区域顶部
# ZD:重叠区域底部
# GG:构成笔中枢的最高点
# DD:构成比中枢的最低点
# hub_width:定义至少的构成中枢的笔数量
def init_hub(pens, hubs, hub_width=3, hub_fit=7):

    global g_last_hub_end_pen
    global g_pens_index

    # 还没有存在中枢
    if g_last_hub_end_pen == 0:

        cur_index = 0

        while cur_index < g_pens_index - 2:

            r = isHub(pens, cur_index, hub_width)

            if r != -1:

                # 中枢构造的过程具有严格的顺序要求, 特别是ZG,ZD,GG,DD
                # 一个考虑点:是否在中枢里面直接定义日前或者采用pens的引用也可以.但在考虑到直接定义好的日期更方便进行次级别走势索引后,决定保留
                h = {'ZG': r[0],
                     'ZD': r[1],
                     'GG': r[2],
                     'DD': r[3],
                     'Start_Pen': pens[cur_index+1],
                     'End_Pen': pens[cur_index+hub_width],
                     'Start_Type': pens[cur_index+1]['Begin_Type'],
                     'End_Type': pens[cur_index+hub_width]['End_Type']}

                # 在中枢定义形成后,调用发现延伸函数
                i = isExpandable(pens, h, cur_index+hub_width)

                # 存在延伸
                if i != cur_index + hub_width:

                    # 修改终结点
                    h['End_Pen'] = pens[i]
                    h['End_Type'] = pens[i]['End_Type']

                    h['Level'] = define_1ub_level(cur_index, i, hub_fit)

                    cur_index = i + 1

                    g_last_hub_end_pen = i

                else:

                    h['Level'] = 1

                    cur_index += hub_width + 1

                    g_last_hub_end_pen = cur_index - 1

                hubs.append(h)

            else:

                cur_index += 1

    # 已经存在中枢,则可能出现两种情况:
    # 1. 已知的最后一个中枢继续生长
    # 2. 已知的最后一个中枢无法生长,但新出现的笔可能构成新的中枢
    else:

        # 尝试扩张最后一个中枢,调用延伸函数
        last_hub_index = len(hubs) - 1
        last_hub = hubs[last_hub_index]

        i = isExpandable(pens, last_hub, g_last_hub_end_pen)

        # 新生成的笔可以成功归入已有中枢
        if i != g_last_hub_end_pen:

            # 修改最后形成中枢的笔索引
            g_last_hub_end_pen = i

            # 修改最后一个中枢的属性
            hubs[last_hub_index]['End_Pen'] = pens[g_last_hub_end_pen]
            hubs[last_hub_index]['End_Type'] = pens[g_last_hub_end_pen]['End_Type']

        # 新生成的笔没有归入中枢,则从最后一个中枢笔开始进行遍历看是否在新生成笔后出现了新中枢的可能
        else:

            # 从离最后一个中枢最近的不属于任何中枢的笔开始遍历
            cur_index = g_last_hub_end_pen + 1

            while cur_index < g_pens_index:

                r = isHub(pens, cur_index, hub_width)

                if r != -1:

                    # 中枢构造的过程具有严格的顺序要求, 特别是ZG,ZD,GG,DD
                    # 一个考虑点:是否在中枢里面直接定义日前或者采用pens的引用也可以.但在考虑到直接定义好的日期更方便进行次级别走势索引后,决定保留
                    h = {'ZG': r[0],
                         'ZD': r[1],
                         'GG': r[2],
                         'DD': r[3],
                         'Start_Pen': pens[cur_index+1],
                         'End_Pen': pens[cur_index+hub_width],
                         'Start_Type': pens[cur_index+1]['Begin_Type'],
                         'End_Type': pens[cur_index+hub_width]['End_Type']}

                    # 在中枢定义形成后,调用延伸函数
                    i = isExpandable(pens, h, cur_index+hub_width)

                    # 存在延伸
                    if i != cur_index+hub_width:

                        # 修改终结点
                        h['End_Pen'] = pens[i]
                        h['End_Type'] = pens[i]['End_Type']

                        h['Level'] = define_1ub_level(cur_index, i, hub_fit)

                        cur_index = i + 1

                        g_last_hub_end_pen = i

                    else:

                        h['Level'] = 1

                        cur_index += hub_width + 1

                        g_last_hub_end_pen = cur_index-1

                    hubs.append(h)

                else:

                    cur_index += 1


# 识别是否存在连续重叠区域函数
def isHub(pens, index, width):

    global g_pens_index
    # 局部变量存储笔信息
    h = []
    l = []

    if g_pens_index - index - 2 > width:

        # 偏置位从1开始,其实是避开了第一个K线.理论上第一个K线不属于中枢
        # 注意遍历的范围为width+1而不是width
        for i in range(1, width + 1):

            h.append(pens[i+index]['High'])
            l.append(pens[i+index]['Low'])

        ZG = min(h)
        ZD = max(l)

        GG = max(h)
        DD = min(l)

        if ZG > ZD:

            return ZG, ZD, GG, DD

        else:

            return -1

    else:

        return -1


# 发现中枢的延伸
# end_pen_index是构成中枢至少三笔最后一笔的索引,它等于cur_index+hub_width-1
# 基于笔的基本形态,end_pen_index+双数的笔必然和中枢同向,遍历的时候就采用end_pen_index+2*t, t = 1,2,3,4,5.....
def isExpandable(pens, hub, end_pen_index):

    # 中枢重叠区间
    hub_ZG = hub['ZG']
    hub_ZD = hub['ZD']

    # 保持临时index,最后用于返回,用中枢的最后一笔做为初始化
    # 结果返回后,如何值为中枢最后一笔,则没有延伸
    cur_index = end_pen_index

    # 初始化索引
    i = end_pen_index + 2

    while i <= g_pens_index - 2:

        pen_high = pens[i]['High']
        pen_low = pens[i]['Low']

        min_high = min(hub_ZG, pen_high)
        max_low = max(hub_ZD, pen_low)

        # 存在交集
        if min_high > max_low:

            # 保持最后索引位置
            cur_index = i

            # 刷新中枢重叠区间
            hub['ZG'] = min_high
            hub['ZD'] = max_low

            hub_ZG = hub['ZG']
            hub_ZD = hub['ZD']

            # 出现了中枢新高或新低
            if pen_high > hub['GG']:

                hub['GG'] = pen_high

            elif pen_low < hub['DD']:

                hub['DD'] = pen_low

            # 索引继续往前探寻
            i += 2

        # 不存在交集,或者探寻结束
        else:

            break

    return cur_index


# 定义中枢级别
# minor-1: 仅有3笔
# median-2: 3<&<9笔
# huge-100: 9<笔
def define_1ub_level(start_index, end_index, hub_fit):

    if 3 < end_index-start_index <= 5:
        return 2

    elif 5 <= end_index-start_index <= hub_fit:
        return 3

    elif hub_fit < end_index-start_index:
        return 100


# 画K线算法.内部采用了双层遍历,算法简单,但性能一般
def draw_stocks(stocks, ax_1, ax_2):

    c = 'b'

    piexl_x = []
    DIF = []
    DEA = []
    MACD = []

    height = []
    low = []

    for i in range(len(stocks)):

        piexl_x.append(i)

        DIF.append(stocks[i]['DIF'])
        DEA.append(stocks[i]['DEA'])
        MACD.append(stocks[i]['MACD'])

        height.append(stocks[i]['High'] - stocks[i]['Low'])
        low.append(stocks[i]['Low'])

    ax_1.bar(piexl_x, height, 0.8, low)

    ax_2.plot(piexl_x, DIF, color='#9999ff')
    ax_2.plot(piexl_x, DEA, color='#ff9999')
    ax_2.bar(piexl_x, MACD, 0.8)


# 测试调用接口
def test(year_start=2001, year_end=2002, start=2000, end=2800):

    stocks = connectxl(year_start, year_end, start, end)

    print('Stocks Before--', len(stocks))

    global g_pens_index

    s_dum = []

    fractals = []

    pens = []

    hubs = []

    count_fractals = 0

    for i in range(len(stocks)):

        s_dum.append(stocks[i])

        init_contain(s_dum)

        f_len = init_fractals(s_dum, fractals)

        # 3016-03-25
        # 尽可能快得使程序有机会进行笔的处理,只有在笔的处理之后才有可能进行进一步的结构处理
        if f_len - count_fractals > 0:

            count_fractals = f_len

            pen_len = init_pen(pens, fractals)

            # TODO 任何这类的判决条件都会引入迟滞
            if pen_len - g_pens_index >= 1:

                merge_pen(pens)

                init_hub(pens, hubs)

    print('Fractals -- ', len(fractals))

    print('Pens -- ', len(pens))

    print('Hubs -- ', len(hubs))

    ax_1 = plt.subplot(211)

    ax_2 = plt.subplot(212)

    draw_stocks(s_dum, ax_1, ax_2)

    draw_fractals(s_dum, fractals, ax_1)

    draw_pens(s_dum, pens, ax_1)

    draw_hub(s_dum, hubs, ax_1)

    file_name = 'Year:' + str(year_start) + 'Start:' + str(start) + '--End:' + str(end)

    plt.savefig(file_name, dpi='figure', format='pdf')

    plt.close()

    print('File save DONE!')


# 画K线算法.内部采用了双层遍历,算法简单,但性能一般
def draw_fractals(stocks, types, ax):

    c = 'b'

    for i in range(len(stocks)):

        # 潜在优化: 动态修改遍历types的开始位置,而不是每次都从0开始
        for j in range(len(types)):

            # 以时间轴为坐标,发现为分型结构的K线颜色改为红色
            if pd.Timestamp(pd.datetime(stocks[i]['Year'],
                                        stocks[i]['Month'],
                                        stocks[i]['Day'],
                                        stocks[i]['Hour'],
                                        stocks[i]['Min'])) == \
                    pd.Timestamp(pd.datetime(types[j]['K']['Year'],
                                             types[j]['K']['Month'],
                                             types[j]['K']['Day'],
                                             types[j]['K']['Hour'],
                                             types[j]['K']['Min'])):

                c = 'r'

                break

            else:

                c = 'g'

        # 在循环中每次画一个K线,并没有采用数组的调用方式
        ax.bar(i, stocks[i]['High'] - stocks[i]['Low'], 0.8, stocks[i]['Low'], color=c)


def draw_pens(stocks, pens, ax):

    # 遍历所存储的所有K线记录,初始化以Date为关键字的字典序列
    date_index = {pd.Timestamp(pd.datetime(stocks[i]['Year'],
                                           stocks[i]['Month'],
                                           stocks[i]['Day'],
                                           stocks[i]['Hour'],
                                           stocks[i]['Min'])).strftime('%Y-%m-%d %H:%M:%S'): i for i in range(len(stocks))}

    piexl_x = []
    piexl_y = []

    for j in range(len(pens)):

        # 利用已经初始化的Date:Index字典,循环遍历pens数组以寻找其对于时间为关键值的X轴坐标位置
        # 添加起点
        piexl_x.append(date_index[pd.Timestamp(pd.datetime(pens[j]['Begin_Type']['K']['Year'],
                                                           pens[j]['Begin_Type']['K']['Month'],
                                                           pens[j]['Begin_Type']['K']['Day'],
                                                           pens[j]['Begin_Type']['K']['Hour'],
                                                           pens[j]['Begin_Type']['K']['Min'])).strftime('%Y-%m-%d %H:%M:%S')])

        # 添加终点
        piexl_x.append(date_index[pd.Timestamp(pd.datetime(pens[j]['End_Type']['K']['Year'],
                                                           pens[j]['End_Type']['K']['Month'],
                                                           pens[j]['End_Type']['K']['Day'],
                                                           pens[j]['End_Type']['K']['Hour'],
                                                           pens[j]['End_Type']['K']['Min'])).strftime('%Y-%m-%d %H:%M:%S')])

        if pens[j]['Position'] == 'Down':

            # 如果笔的朝向向下,那么画线的起点为顶分型的高点,终点为底分型的低点
            piexl_y.append(pens[j]['Begin_Type']['High'])
            piexl_y.append(pens[j]['End_Type']['Low'])

        # 如果笔的朝向向上,那么画线的起点为底分型的低点,终点为顶分型的高点
        else:

            piexl_y.append(pens[j]['Begin_Type']['Low'])
            piexl_y.append(pens[j]['End_Type']['High'])

    # 画线程序调用
    ax.plot(piexl_x, piexl_y, color='m')


# 画中枢
def draw_hub(stocks, hubs, ax):

    # 遍历所存储的所有K线记录,初始化以Date为关键字的字典序列
    date_index = {pd.Timestamp(pd.datetime(stocks[i]['Year'],
                                           stocks[i]['Month'],
                                           stocks[i]['Day'],
                                           stocks[i]['Hour'],
                                           stocks[i]['Min'])).strftime('%Y-%m-%d %H:%M:%S'): i for i in range(len(stocks))}

    for i in range(len(hubs)):

        # Rectangle x

        start_date = pd.Timestamp(pd.datetime(hubs[i]['Start_Type']['K']['Year'],
                                              hubs[i]['Start_Type']['K']['Month'],
                                              hubs[i]['Start_Type']['K']['Day'],
                                              hubs[i]['Start_Type']['K']['Hour'],
                                              hubs[i]['Start_Type']['K']['Min'])).strftime('%Y-%m-%d %H:%M:%S')
        x = date_index[start_date]

        # Rectangle y
        y = hubs[i]['ZD']

        # Rectangle width
        end_date = pd.Timestamp(pd.datetime(hubs[i]['End_Type']['K']['Year'],
                                            hubs[i]['End_Type']['K']['Month'],
                                            hubs[i]['End_Type']['K']['Day'],
                                            hubs[i]['End_Type']['K']['Hour'],
                                            hubs[i]['End_Type']['K']['Min'])).strftime('%Y-%m-%d %H:%M:%S')

        w = date_index[end_date] - date_index[start_date]

        # print('Hub--', i ,'B--', start_date, 'E--', end_date, 'W--', w, 'GG--', hubs[i]['GG'], 'DD--', hubs[i]['DD'])


        # Rectangle height
        h = hubs[i]['ZG'] - hubs[i]['ZD']

        if hubs[i]['Level'] == 3:
            ax.add_patch(patches.Rectangle((x,y), w, h, color='r', fill=False))

        else:
            ax.add_patch(patches.Rectangle((x,y), w, h, color='y', fill=False))


# 画MACD
def draw_MACD(stocks, ax):

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


def close():

    plt.close()

    global g_fractal_index
    global g_pens_index
    global g_last_hub_end_pen
    global g_pens_stack_index
    global g_pens_stack
    global g_pens_stack_delay

    g_fractal_index = 0
    g_pens_index = 0
    g_last_hub_end_pen = 0
    g_pens_stack_index = 0
    g_pens_stack = []
    g_pens_stack_delay = []

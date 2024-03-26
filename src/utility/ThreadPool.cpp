//
// Created by JerryH on 21/12/2023.
//

#include "../include/utility/ThreadPool.h"

ThreadPool::ThreadPool(int num) : _threads{}, _tasks{}, _stop{ false } {

    auto fun = [this]() {
        while (true) {
            auto lock = unique_lock<mutex>{ _m };
            _cv.wait(lock, [this]() { return !_tasks.empty() || _stop; });

            if (_stop & _tasks.empty())
                return;

            function<void(void)> task = std::move(_tasks.front());
            lock.unlock();
            _tasks.pop();

            task();
        }
    };

    for (auto i = 0; i < 1; i++)
        _threads.emplace_back(fun );
}

//template<typename Func, typename... Ts>
//void ThreadPool::enhance(Func&& f, Ts&& ... params) {
//    auto task = std::bind(std::forward<Func>(f), std::forward<Ts>(params)...);
//
//    {
//        auto lock = scoped_lock<mutex>{_m};
//        _tasks.emplace(task);
//    }
//
//    _cv.notify_one();
//}

ThreadPool::~ThreadPool() {

    _stop = true;
    _cv.notify_all();

    for(auto& i : _threads)
        i.join();
}

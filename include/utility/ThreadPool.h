#pragma once

#include <vector>
#include <queue>
#include <atomic>
#include <thread>
#include <functional>
#include <condition_variable>
#include <mutex>

using namespace std;

class ThreadPool {
public:
    ThreadPool(int num);

    template<typename Func, typename ... Ts>
    void enhance(Func&& f, Ts&& ... params);

    ~ThreadPool();

private:
    vector<thread> _threads;
    queue<std::function<void(void)>> _tasks;
    atomic<bool> _stop;
    mutex _m{};
    condition_variable _cv{};
};

template<typename Func, typename... Ts>
void ThreadPool::enhance(Func&& f, Ts&& ... params) {
    auto task = std::bind(std::forward<Func>(f), std::forward<Ts>(params)...);

    {
        auto lock = scoped_lock<mutex>{_m};
        _tasks.emplace(task);
    }

    _cv.notify_one();
}

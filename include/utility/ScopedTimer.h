//
// Created by Jerry Huang on 25/12/2023.
//

#ifndef MAIN_SCOPEDTIMER_H
#define MAIN_SCOPEDTIMER_H

#include <chrono>
#include <iostream>

using namespace std;

class ScopedTimer {
public:
    using ClockType = std::chrono::steady_clock;
    ScopedTimer(const char* func)
            : function_name_{func}, start_{ClockType::now()} {}
    ScopedTimer(const ScopedTimer&) = delete;
    ScopedTimer(ScopedTimer&&) = delete;
    auto operator=(const ScopedTimer&) -> ScopedTimer& = delete;
    auto operator=(ScopedTimer&&) -> ScopedTimer& = delete;
    ~ScopedTimer() {
        using namespace std::chrono;
        auto stop = ClockType::now();
        auto duration = (stop - start_);
        auto ms = duration_cast<milliseconds>(duration).count();
        std::cout << ms << " ms " << function_name_ << '\n';
    }
private:
    const char* function_name_{};
    const ClockType::time_point start_{};
};

#endif //MAIN_SCOPEDTIMER_H

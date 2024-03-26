//
// Created by Jerry Huang on 25/12/2023.
//

#ifndef MAIN_TEST_MEMORY_H
#define MAIN_TEST_MEMORY_H

#include "utility/MemoryPool.h"
#include "utility/ScopedTimer.h"
#include "utility/short_alloc.h"


struct A{
    A(){}

    A(double d, int a, char c) : d{d}, a{a}, c{c}{
    }

    double d;
    int a;
    char c;

    ~A(){
        d = 0;
        a = 0;
        c = 'a';
    }
};

auto test_memory_pool(){

    auto memory_pool = MemoryPool<A>(1000);
    auto timer = ScopedTimer("Pool");

    for(auto i = 0; i < 1000 * 50; i++){
        for(auto j = 0; j < 1000; j++){
            auto p = memory_pool.allocate(5.5, 5, 'a');
//            p->d = p->d * 2;
//            memory_pool.deAllocate(p);
        }
    }
}

auto test_dynamic_allocat(){
    auto timer = ScopedTimer("Dynamic");
    for(auto i = 0; i < 1000 * 50; i++){
        A* p[1000];
        for(auto j = 0; j < 1000; j++){
            p[j] = new A{5.5, 3, 'a'};
            p[j]->d = p[j]->d * 2;
//            delete p;
        }
        for(auto j = 0; j < 1000; j++)
            delete p[j];
    }
}

auto test_arena(){
    constexpr auto N = sizeof(A) * 1000;
    constexpr auto alignment = alignof(A);
    constexpr auto s = sizeof(A);

    auto a = arena<N, alignof(A)>{};
    A* pa[1000];

    // Only One time
    for (auto j = 0; j < 1000; j++) {
        pa[j] = reinterpret_cast<A *>(a.allocate<alignment>(s));
        pa[j] = ::new(pa[j]) A{};
    }

    auto timer = ScopedTimer("Arena");
    for(auto i = 0; i < 1000 * 50; i++) {
        for (auto j = 0; j < 1000; j++) {
            pa[j] = reinterpret_cast<A *>(a.allocate<alignment>(s));
            pa[j]->d = pa[j]->d * 2;
        }
//        a.reset();
    }

}


#endif //MAIN_TEST_MEMORY_H

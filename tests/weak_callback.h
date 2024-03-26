#pragma once

#include <iostream>
#include <chrono>
#include <unistd.h>
#include <cstring>
#include <signal.h>
#include <thread>
#include <sys/shm.h>
#include <sys/ipc.h>
#include <memory>
#include <functional>

using namespace std;

/*
1. 如何在生成智能指针时绑定对象析构时的回调函数
2. 回调函数采用callable wrapper而非一般lambda或者函数对象的原因：生成wrapper时把参数已经一同准备好
3. 如果设定了回调函数，智能指针对象释放时不再会主动调用被管理的对象析构函数，需要在回调函数内显性delete
4. 关于shared_ptr和weak_ptr应用场景的理解
5. 如何在类对象内部提取智能指针enable_shared_from_this
*/


class A
{
    public:
        ~A(){
            cout << "Calling A deconstructor" << endl;
        }
};

class Container : public enable_shared_from_this<Container>
{
    public:
        weak_ptr<A> a_;

        shared_ptr<A> get();

        ~Container();
};

void killer(weak_ptr<Container> c, A* p)
{
    auto wp = c.lock();

    if(wp)
        cout << "Container clean resource:" << endl;
    else
        cout << "Container died earlier" << endl;

    delete p;
}


shared_ptr<A> Container::get()
{
    shared_ptr<A> pA;

    // Bind Callback function with smart pointer
    pA.reset(new A(), bind(killer, static_cast<weak_ptr<Container>>(shared_from_this()), std::placeholders::_1));

    // Lambda Callback funciton
    // pA.reset(new A(), [this](A *ptr)
    //          {
    //             // cout << "Calling Lambda" << endl;
    //             killer(static_cast<weak_ptr<Container>>(this->shared_from_this()), ptr);
    //             });

    a_ = pA;

    return pA;
}

Container::~Container()
{
    cout << "Calling Container D..." << endl;
}


void test(){
    {
        cout << "Test Case 1: Container die first" << endl;
        shared_ptr<A> p{};
        {
            auto c = make_shared<Container>();
            p = c->get();
            cout << "running out of Container scope" << endl;
        }
    }
    cout << "\n\n";

    {
        cout << "Test Case 2: Class A die first" << endl;

        auto c = make_shared<Container>();
        {
            auto p = c->get();
            cout << "running out of A scope" << endl;
        }
    }
}
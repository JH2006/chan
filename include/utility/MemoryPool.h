//
// Created by JerryH on 22/12/2023.
//

#ifndef TRADING_MEMORYPOOL_H
#define TRADING_MEMORYPOOL_H

#include <vector>
#include <queue>

using namespace std;

template<typename T>
class MemoryPool{
private:
    struct ObjectBlock {
        T object;
        bool is_free;
    };

public:
    explicit MemoryPool(int size);

    MemoryPool() = delete;
    MemoryPool(const MemoryPool&) = delete;
    MemoryPool(MemoryPool&& ) = delete;
    MemoryPool & operator = (const MemoryPool&) = delete;
    MemoryPool & operator = (MemoryPool&&) = delete;

    template<typename ... Agrs>
    auto allocate(Agrs&& ... agrs)->T*;

    void deallocate(T* item) noexcept;

private:
    vector<ObjectBlock> pool_;
    size_t next_free_index_;

private:
    void updateNextFreeIndex();
    void expandPool();
};

template<typename T>
MemoryPool<T>::MemoryPool(int size) : next_free_index_{0} {
    pool_ = vector<ObjectBlock>(size, ObjectBlock{T{}, true});
    assert(reinterpret_cast<ObjectBlock*>(&pool_[0].object) == &pool_[0]);
}

template<typename T>
template<typename ... Agrs>
auto MemoryPool<T>::allocate(Agrs&& ... agrs)->T*{
    auto* object_block = &pool_[next_free_index_];
    T* object = &object_block->object;
    object = ::new(object) T(std::forward<Agrs>(agrs)...);
    object_block->is_free = false;

    updateNextFreeIndex();

    return object;
}

template<typename T>
void MemoryPool<T>::updateNextFreeIndex(){
    const auto initial_free_index = next_free_index_;

    while(!pool_[next_free_index_].is_free){
        next_free_index_++;

        if(next_free_index_ == pool_.size())
            next_free_index_ = 0;

        if(next_free_index_ == initial_free_index)
            assert(next_free_index_ != initial_free_index);

    }

}

template<typename T>
void MemoryPool<T>::deallocate(T *item) noexcept {
    ObjectBlock * objectBlock = reinterpret_cast<const ObjectBlock*>(item);
    const auto elem_index = static_cast<size_t>(objectBlock - pool_[0]);

    assert(elem_index >= 0 && elem_index < pool_.size());
    assert(pool_[elem_index].is_free == false);

    pool_[elem_index].is_free = true;

}

template<typename T>
void MemoryPool<T>::expandPool() {

}

#endif //TRADING_MEMORYPOOL_H

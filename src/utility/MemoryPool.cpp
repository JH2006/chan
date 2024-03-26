//
// Created by JerryH on 22/12/2023.
//

//#include "MemoryPool.h"
//template<typename T>
//MemoryPool<T>::MemoryPool() : _pool(10, T{}) {
//    for(auto i = 0; i < 10; i++)
//        _freeBlock.emplace(i);
//}
//
//template<typename T>
//template<typename ... Agrs>
//T* MemoryPool<T>::allocate(Agrs ... agrs){
//    auto index = updateNextFreeIndex();
//
//    auto* object_block = &_pool[index];
//
//    object_block = ::new(object_block) T(agrs...);
//
//    return object_block;
//}
//
//template<typename T>
//void MemoryPool<T>::deAllocate(T *block) noexcept {
//    auto freeBlockIndex = reinterpret_cast<const T*>(block) - _pool[0];
//    _freeBlock.emplace(freeBlockIndex);
//}
//
//template<typename T>
//auto MemoryPool<T>::updateNextFreeIndex(){
//    if(!_freeBlock.empty()){
//        auto index = _freeBlock.front();
//        _freeBlock.pop();
//        return index;
//    }
//    else{
//        // Need more space or something
//    }
//}
//
//template<typename T>
//void MemoryPool<T>::expandPool() {
//
//}

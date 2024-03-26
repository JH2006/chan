//
// Created by JerryH on 7/11/2023.
//

#ifndef UNTITLED_NODE_H
#define UNTITLED_NODE_H

#include <memory>
#include <string>
#include <vector>

using namespace std;

struct TreeNode{
    int val;
    shared_ptr<TreeNode> left;
    shared_ptr<TreeNode> right;
//    TreeNode() : _val{0}, _left{nullptr}, _right{nullptr} {}
    TreeNode(int x) : val{x}, left{nullptr}, right{nullptr} {}
//    TreeNode(int x, unique_ptr<TreeNode> left, unique_ptr<TreeNode> right) : _val{x}, _left{std::move(left)}, _right{std::move(right)} {}
};

shared_ptr<TreeNode> buildTree(const vector<string> &v);

#endif //UNTITLED_NODE_H

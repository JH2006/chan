//
// Created by JerryH on 7/11/2023.
//
#include <queue>
#include "Node.h"

using namespace std;

auto c{[](string &s){return s == "null" ? -1 : stoi(s);}};

shared_ptr<TreeNode> buildTree(const vector<string> & arr)
{
    if (arr.empty()) {
        return nullptr;
    }

    size_t s{0};
    std::queue<std::shared_ptr<TreeNode>> nodeQueue{};
    std::shared_ptr<TreeNode> root{nullptr};
    if (arr[0] != "null")
    {
        root = std::make_shared<TreeNode>(stoi(arr[s++]));
        nodeQueue.push(root);
    }
    else
        return nullptr;

    while (!nodeQueue.empty())
    {
        std::shared_ptr<TreeNode> currNode = nodeQueue.front();
        nodeQueue.pop();

        // Left
        if (s < arr.size())
        {
            if (arr[s] != "null")
            {
                currNode->left = std::make_shared<TreeNode>(stoi(arr[s]));
                nodeQueue.push(currNode->left);
            }
            s++;
        }
        else
            break;
        // Right
        if (s < arr.size())
        {
            if (arr[s] != "null")
            {
                currNode->right = std::make_shared<TreeNode>(stoi(arr[s]));
                nodeQueue.push(currNode->right);
            }
            s++;
        }
        else
            break;
    }

    return root;
}
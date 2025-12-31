#!/bin/bash
# git-flow-helper.sh

# 开始新功能
start_feature() {
    echo "请输入功能名称："
    read feature_name
    echo "请输入功能描述："
    read feature_desc
    
    git flow feature start $feature_name
    echo "✅ 已创建功能分支: feature/$feature_name"
    echo "📝 功能描述: $feature_desc"
}

# 完成功能
finish_feature() {
    current_branch=$(git branch --show-current)
    if [[ $current_branch != feature/* ]]; then
        echo "❌ 当前不在功能分支上"
        return 1
    fi
    
    echo "请总结本次功能的提交："
    echo "格式：<类型>(<作用域>): <描述>"
    read merge_message
    
    git flow feature finish -m "$merge_message"
    echo "✅ 功能已完成并合并到develop"
}

# 检查提交信息
check_commit() {
    msg_file=$1
    commit_msg=$(cat $msg_file)
    
    # 检查是否遵循Conventional Commits
    if [[ ! $commit_msg =~ ^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)\(.*\): ]]; then
        echo "❌ 提交信息格式错误，请遵循Conventional Commits规范"
        echo "格式应为：<类型>(<作用域>): <描述>"
        exit 1
    fi
}
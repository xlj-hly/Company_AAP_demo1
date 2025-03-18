#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import argparse
from config.ignore_config import ignore_config

def main():
    parser = argparse.ArgumentParser(description='管理日志忽略规则')
    parser.add_argument('action', choices=['add', 'list', 'remove'], help='操作类型')
    parser.add_argument('--level', choices=['info', 'warning', 'error'], help='日志级别')
    parser.add_argument('--pattern', help='匹配模式')
    parser.add_argument('--module', help='模块名称（可选）')
    
    args = parser.parse_args()
    
    if args.action == 'add':
        if not args.level or not args.pattern:
            print("添加规则需要指定level和pattern")
            return
        ignore_config.add_ignore_rule(args.level, args.pattern, args.module)
        print(f"已添加忽略规则: {args.level} - {args.pattern}")
    
    elif args.action == 'list':
        print("当前忽略规则:")
        for level, rules in ignore_config.ignore_rules.items():
            print(f"\n{level.upper()}:")
            for module, patterns in rules.items():
                print(f"  {module}:")
                for pattern in patterns:
                    print(f"    - {pattern}")
    
    elif args.action == 'remove':
        # TODO: 实现删除规则功能
        pass

if __name__ == "__main__":
    main() 
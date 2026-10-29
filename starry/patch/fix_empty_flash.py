#!/usr/bin/env python3
"""修复：开启「启动直接进入浏览页」时，先闪一下“空文件夹”。
在应用汉化补丁之后运行：python3 starry/patch/fix_empty_flash.py
"""
import re, sys

def sub_once(path, pattern, repl, flags=re.S):
    s = open(path, encoding='utf-8').read()
    new, n = re.subn(pattern, repl, s, count=1, flags=flags)
    if n != 1:
        sys.exit(f'FAILED to patch {path}: pattern not found')
    open(path, 'w', encoding='utf-8').write(new)

# 1) Provider：init() 完成前标记为未初始化
sub_once(
    'lib/providers/file_manager_provider.dart',
    r'  Future<void> init\(\) async \{\n',
    '''  bool _initialized = false;
  bool get initialized => _initialized;

  Future<void> init() async {
    try {
      await _initInternal();
    } finally {
      _initialized = true;
      notifyListeners();
    }
  }

  Future<void> _initInternal() async {
''')

# 2) DirectoryScreen：未初始化时显示转圈，而不是“空文件夹”
#    兼容汉化补丁前后的写法（有无 provider.tabs.isEmpty ||）
sub_once(
    'lib/ui/screens/directory_screen.dart',
    r'provider\.isLoading\s*&&\s*provider\.currentFiles\.isEmpty(?=\)+\s*\?\s*const Center\(child: CircularProgressIndicator)',
    '!provider.initialized || (provider.isLoading && provider.currentFiles.isEmpty)')
print('OK')

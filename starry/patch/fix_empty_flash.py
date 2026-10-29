#!/usr/bin/env python3
"""启动直进浏览页：先在启动页阶段把目录读好，首帧就是文件列表（无空文件夹、无转圈）。
在应用汉化补丁之后运行：python3 starry/patch/fix_empty_flash.py
"""
import re, sys

def read(p): return open(p, encoding='utf-8').read()
def write(p, s): open(p, 'w', encoding='utf-8').write(s)

# 1) Provider：init() 幂等（可重复调用，只执行一次），并记录是否完成
p = 'lib/providers/file_manager_provider.dart'
s = read(p)
old = '  Future<void> init() async {\n'
if old not in s: sys.exit('FAILED: provider init() not found')
s = s.replace(old, '''  bool _initialized = false;
  bool get initialized => _initialized;
  Future<void>? _initFuture;

  Future<void> init() => _initFuture ??= _runInit();

  Future<void> _runInit() async {
    try {
      await _initInternal();
    } finally {
      _initialized = true;
      notifyListeners();
    }
  }

  Future<void> _initInternal() async {
''', 1)
write(p, s)

# 2) 兜底：未初始化时 DirectoryScreen 显示转圈（兼容汉化补丁前后写法）
p = 'lib/ui/screens/directory_screen.dart'
s = read(p)
pat = r'provider\.isLoading\s*&&\s*provider\.currentFiles\.isEmpty(?=\)+\s*\?\s*const Center\(child: CircularProgressIndicator)'
s, n = re.subn(pat, '!provider.initialized || (provider.isLoading && provider.currentFiles.isEmpty)', s, count=1)
if n != 1: sys.exit('FAILED: directory_screen condition not found')
write(p, s)

# 3) main.dart：权限确认后、显示 HomeScreen 之前先预加载目录
p = 'lib/main.dart'
s = read(p)
blk = '      if (mounted) {\n        setState(() {\n          _hasPermission = granted;\n        });'
if s.count(blk) < 1: sys.exit('FAILED: main.dart permission block not found')
s = s.replace(blk, '      if (granted) await _warmUpFileList();\n' + blk)
anchor = '  Future<void> _initializeApplication() async {\n'
if anchor not in s: sys.exit('FAILED: main.dart anchor not found')
s = s.replace(anchor, '''  /// 在启动空白页阶段先读好目录，HomeScreen 首帧即有内容；最多等 3 秒。
  Future<void> _warmUpFileList() async {
    if (!mounted) return;
    try {
      await context
          .read<FileManagerProvider>()
          .init()
          .timeout(const Duration(seconds: 3));
    } catch (_) {}
  }

''' + anchor, 1)
write(p, s)
print('OK')

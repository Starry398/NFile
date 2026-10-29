#!/usr/bin/env python3
"""启动直进浏览页：先在启动页阶段把目录读好，首帧就是文件列表。

在应用汉化补丁之后运行：python3 starry/patch/fix_empty_flash.py

说明：目录页的加载占位已经由补丁换成骨架屏（_DirSkeleton），
本脚本不再改 directory_screen.dart，只负责：
  1) provider.init() 幂等（main 预热 + DirectoryScreen 各调一次，不能重复扫目录）
  2) main.dart 在显示 HomeScreen 之前把目录预读好
"""
import sys

def read(p): return open(p, encoding='utf-8').read()
def write(p, s): open(p, 'w', encoding='utf-8').write(s)

# ---------- 1) Provider：init() 幂等 ----------
p = 'lib/providers/file_manager_provider.dart'
s = read(p)
if 'Future<void>? _initFuture;' in s:
    print('provider: already patched, skip')
else:
    old = '  Future<void> init() async {\n'
    if old not in s:
        sys.exit('FAILED: provider init() not found')
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
    print('provider: init() made idempotent')

# ---------- 2) main.dart：显示 HomeScreen 前预热目录 ----------
p = 'lib/main.dart'
s = read(p)
if '_warmUpFileList' in s:
    print('main: already patched, skip')
else:
    blk = '      if (mounted) {\n        setState(() {\n          _hasPermission = granted;\n        });'
    if s.count(blk) < 1:
        sys.exit('FAILED: main.dart permission block not found')
    s = s.replace(blk, '      if (granted) await _warmUpFileList();\n' + blk)
    anchor = '  Future<void> _initializeApplication() async {\n'
    if anchor not in s:
        sys.exit('FAILED: main.dart anchor not found')
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
    print('main: warm-up added')

print('OK')

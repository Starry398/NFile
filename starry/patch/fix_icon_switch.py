#!/usr/bin/env python3
"""图标切换：先启用目标 alias，再禁用其余，避免出现“无启动入口”的瞬间。
汉化补丁不涉及 MainActivity.kt，可在任意时机运行：python3 starry/patch/fix_icon_switch.py
"""
import re, sys
p = 'android/app/src/main/kotlin/com/rubex/nfile/MainActivity.kt'
s = open(p, encoding='utf-8').read()
pat = re.compile(
    r'(?P<i>[ \t]*)for \(alias in aliases\) \{\s*'
    r'val componentName = android\.content\.ComponentName\(packageName, alias\)\s*'
    r'val state = if \(alias == iconAlias\) \{\s*'
    r'PackageManager\.COMPONENT_ENABLED_STATE_ENABLED\s*'
    r'\} else \{\s*'
    r'PackageManager\.COMPONENT_ENABLED_STATE_DISABLED\s*'
    r'\}\s*'
    r'packageManager\.setComponentEnabledSetting\(\s*componentName,\s*state,\s*PackageManager\.DONT_KILL_APP\s*\)\s*\}',
    re.S)
def repl(m):
    i = m.group('i')
    return (
f'''{i}packageManager.setComponentEnabledSetting(
{i}    android.content.ComponentName(packageName, iconAlias),
{i}    PackageManager.COMPONENT_ENABLED_STATE_ENABLED,
{i}    PackageManager.DONT_KILL_APP
{i})
{i}for (alias in aliases) {{
{i}    if (alias == iconAlias) continue
{i}    packageManager.setComponentEnabledSetting(
{i}        android.content.ComponentName(packageName, alias),
{i}        PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
{i}        PackageManager.DONT_KILL_APP
{i}    )
{i}}}''')
new, n = pat.subn(repl, s, count=1)
if n != 1:
    sys.exit('FAILED: changeAppIcon loop not found')
open(p, 'w', encoding='utf-8').write(new)
print('OK')

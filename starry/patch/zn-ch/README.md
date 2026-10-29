# NFile 汉化补丁（zn-ch）

上游 [`Senzme/NFile`](https://github.com/Senzme/NFile) 的中文汉化补丁。
基线：**1.0.44 预发行版**，commit `00dcc95`（上游 main HEAD）。

选 1.0.44 而不是 v1.0.43 的原因：1.0.43 缺「主题跟随系统」和「首页存储分析」，
上游在 1.0.44 已修复/新增。

## 目录

```
starry/patch/zn-ch/
├── nfile-zh.patch   # 汉化补丁（654KB，76 个文件）
└── README.md
```

## CI 怎么用

`.github/workflows/build.yml`（**手动触发** `workflow_dispatch`）：

```yaml
- name: Apply 汉化补丁
  run: |
    git apply --check starry/patch/zn-ch/nfile-zh.patch
    git apply         starry/patch/zn-ch/nfile-zh.patch
```

编译：

```bash
flutter build apk --release --split-per-abi --target-platform android-arm64 \
  --build-number=$((43000 + run_number)) \
  --obfuscate --split-debug-info=build/symbols --no-tree-shake-icons
```

产物：`NFile-v1.0.44-arm64-v8a.apk`（约 55MB，**只编译 arm64-v8a**）
发布：tag `v1.0.44`，Release 名 `v1.0.44`。

## 补丁内容

### 文案层：1621 处 / 58 个文件
- 词库 962 条，原文见 `tools/i18n/src/*.tsv`，合并后 `zh.json`
- 专有名词保留英文：FTP / SFTP / SMB / WebDAV / SAF / ZIP / RAR / APK / PDF / SQL
- 上游更新后重新注入：`python3 tools/i18n/apply_zh.py`（幂等）

### 代码层
| 文件 | 改动 |
|---|---|
| `pubspec.yaml` | + `flutter_localizations` |
| `lib/main.dart` | `locale: zh_CN`、`localizationsDelegates`、`Intl.defaultLocale='zh_CN'`；**启动权限检查串行化（防闪退）** |
| `lib/core/utils.dart` | 日期格式 `yyyy年M月d日` |
| `lib/ui/screens/home_screen.dart` | **启动直接进存储页，不再先闪一下首页** |
| `lib/providers/file_manager_provider.dart` | 图标 alias 用新包名 |
| `AndroidManifest.xml` | `label="NFile"`（无后缀）；documents provider authority → `${applicationId}.documents` |
| `MainActivity.kt` | 图标 alias 跟随 `packageName` |
| `build.gradle.kts` | `applicationId=com.rubex.nfile.starry`；`localeFilters` 加 `zh`；无 keystore 回落 debug 签名 |

## 两个已知问题的说明

**启动闪退（Reply already submitted）**
启动时连查 3 个权限，`permission_handler` 原生侧对同一 MethodChannel 结果重复 reply，
Java 层异常直接杀进程。已改成「先查 `manageExternalStorage`，未授权再间隔 150ms 查 `storage`」。

**启动先闪首页**
`_currentIndex` 原本在 `initState` 里从 `FileManagerProvider` 读 `defaultToBrowseScreen`，
而 Provider 的设置是异步加载的，首帧拿到默认 false → 先渲染首页，加载完再切存储页。
现改为直接读已初始化的 `PreferencesService.getDefaultToBrowseScreen()`，首帧即正确。

## 签名

Secrets 需要 4 项：`KEYSTORE_BASE64` / `KEY_ALIAS` / `KEY_PASSWORD` / `STORE_PASSWORD`。

## 注意

- 包名 `com.rubex.nfile.starry`，可与官方版共存。
- 上游换基线后 patch 需重新生成（词库可复用，改完源码重跑 apply_zh.py 再 diff）。

# Photos Backup for iOS（中文说明）

<p align="center">
  <strong><a href="README.md">English</a></strong> |
  <strong><a href="README_cn.md">简体中文</a></strong>
</p>

<p align="center">
  <img src="App/Resources/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png" width="160" alt="Photos Backup 应用图标">
</p>

一款实验性的、完全在 iPhone 本地运行的相册备份应用：把选定的照片、视频和相册备份到 Google Photos。它是单一 SwiftUI 应用，通过应用内网页视图完成 Google 账号设置，所有操作都在手机上完成，无需桌面伴侣或托管服务。

> [!WARNING]
> 本项目使用 Google 私有的、未文档化的 Photos 接口和 Android 风格的认证流程。它与 Google 无关，也未经 Google 认可，相关集成随时可能失效。请将其视为实验性软件，自行承担使用风险。

## 多语言支持（本次新增）

从 0.3.7 起，应用内置 **英文（en）** 与 **简体中文（zh-Hans）** 两种语言：

- 在 **iOS 系统设置 → Photos Backup → 语言（Language）** 中即可切换，无需重新安装。
- 切换后立即生效：界面文案、应用显示名称、相册权限说明都会跟随系统所选语言。
- 应用显示名称在中文环境下为「照片备份」，英文环境下为 "Photos Backup"。
- 翻译表位于 `App/Resources/{en,zh-Hans}.lproj/Localizable.strings`，两套各 356 条，一一对应。
- 代码中所有用户可见文案均通过 `NSLocalizedString` 取翻译，未匹配到翻译时自动回退英文。

### 如何添加更多语言

1. 新建目录 `App/Resources/<语言代码>.lproj/`（如法语 `fr.lproj`），放入 `Localizable.strings`，key 与英文表完全一致，右侧写对应翻译。
2. 在 `App/Resources/Info.plist` 的 `CFBundleLocalizations` 数组中追加该语言代码（如 `<string>fr</string>`）。
3. 可选：在该 `.lproj` 下添加 `InfoPlist.strings` 翻译应用名与权限文案。
4. 运行 `python3 Scripts/verify_localization.py` 校验 key 配对与语法，然后重新构建。

> [!NOTE]
> 使用 `NSLocalizedString` 兼容 iOS 15，本项目最低支持 **iOS 15.0**（iOS 16 设备同样生效）。

## 功能特性

- 通过 Google 的 EmbeddedSetup 流程，在应用内网页视图中连接 Google 账号。
- 在进程内从网页视图的 Cookie 存储中捕获一次性 `oauth_token`。
- 完全在设备上把该令牌交换为 Google Photos 凭据。
- 从本地照片图库中选择相册。
- 支持队列上传单张照片、单个视频，或所选相册中的全部内容。
- 逐项显示哈希、去重、上传与收尾进度。
- 避免重复上传 Google Photos 中已存在的媒体。
- 重试瞬时失败、取消任务，并在重连后恢复。
- 以 Google 的原始错误文案显示上传失败原因（可从行内和诊断页复制），并在 Google 账号存储空间耗尽时停止队列。
- 应用重启后恢复未完成的相册上传，并按 Google 账号记住已完成备份的图库资源。
- 显示每个相册的备份进度，并重新上传备份后被编辑过的资源。
- 按 iPhone 上的实际效果备份编辑后的照片——也就是 Google Photos 应用自己会上传的那个文件，从而让 Google Photos 的「释放空间」能够识别它。
- 开启「备份实况照片动态」后，实况照片连同动态一起备份，可在 Google Photos 中作为实况照片播放，Google Photos 应用的「释放空间」也会提供该选项。早期仅备份为静态图的实况照片，其动态会在后台补传。
- 备份在 Google Photos 应用中编辑过的照片，使该应用将其计为已备份。Google Photos 会在相机人像虚化或裁切之上叠加自己的编辑，只有账号持有该中间版本时才会计数，因此该中间版本会连同最终编辑一起上传。
- 支持原始质量上传，或请求 Google 的 Storage Saver 处理。
- 并发上传数可在 1 到 10 之间调节。
- 在队列与请求两个层面强制「仅 Wi-Fi」或「Wi-Fi + 蜂窝」策略，当允许的传输方式丢失时取消进行中的后台传输。
- 离开应用后继续备份（iOS 26 及更高版本）：应用在前台且队列有任务时，会请求 iOS 在后台继续执行；iOS 通过灵动岛 Live Activity 显示进度，并可在其中取消。后台同时最多执行 2 个上传。
- 为所选相册的备份请求周期性的 iOS 后台处理窗口。
- 在 iOS 16+ 上提供 **Back Up Photos** 快捷指令动作，可用于充电、定时、Wi-Fi 等个人自动化场景。即使关闭「自动备份」也能运行，因此可以用自定义计划替代它。
- 让文件 PUT 在 iOS 托管的后台 `URLSession` 中持续运行，并在 iOS 重新启动应用后提交完成的回执。
- 在 iOS 16+ 上跟踪 PhotoKit 持久化变更，从而发现补录的导入。
- 单个项目持续导致应用关闭时也能继续：连续两次在准备阶段卡住的项目会被跳过并允许重试，而不是每次启动都中断。
- 生成隐私安全的诊断报告：包含通俗语言摘要、近期运行记录及 iOS 运行条件、来自 iOS 的崩溃与终止数据，以及应用决策时间线及原因。
- 在签名允许时，将可长期使用的凭据存入 iOS 钥匙串。

## 当前状态

完整的认证路径已在 iOS 17 真机与模拟器上验证通过：应用内网页视图收到 `oauth_token`，应用从网页视图自身的 Cookie 存储中读取、交换为未绑定的主令牌与 Photos 凭据，并成功发起带认证的 `photosdata-pa` 请求。

Xcode 工程、应用 target 与 scheme 均命名为 `PhotosBackup`；面向用户的显示名称是 **Photos Backup**（中文环境为「照片备份」）。

最新版本：**0.3.7**（[Releases](https://github.com/g8row/PhotosBackup/releases)）。每次推送与拉取请求都会在 iPhone 模拟器上运行测试套件：191 个测试，189 个通过，0 个失败，2 个可选的在线测试被跳过。

每个版本的 `.ipa` 都由 GitHub Actions 从对应 tag 的提交构建并附 SHA-256 校验，因此可以核对二进制与它所声称的来源代码是否一致。

### 应用标识（自 0.0.2 起）

| 项目 | 值 |
| --- | --- |
| App bundle ID | `com.g8row.photosbackup` |
| 后台任务 | `com.g8row.photosbackup.background-backup` |
| 续传备份（iOS 26+） | `<bundle ID>.continued-backup.<UUID>`，由 `<bundle ID>.continued-backup.*` 授权 |
| 后台上传会话 | `com.g8row.photosbackup.background-upload` |

> [!IMPORTANT]
> bundle ID 与钥匙串服务在 0.0.2 中发生过变更。从旧版本更新后，请重新连接一次 Google 账号，然后强制退出并重新打开，确认连接保持。

## 报告问题

打开 **设置 → 支持 → 创建诊断报告**，点击 **生成报告**，然后 **分享或保存报告**。将文本文件附加到 [GitHub issue](https://github.com/g8row/PhotosBackup/issues)。报告开头有一段简短的 **值得注意** 列表，往往能直接说明问题。报告不会包含凭据、账号地址、照片标识、文件名、媒体与请求 URL。

**诊断 → 事件时间线** 可在应用内查看同一时间线。来自 iOS 的崩溃详情仅在开启「与 App 开发者共享」（设置 → 隐私与安全性 → 分析与改进）时才会包含，通常在崩溃后一两天到达。

## 系统要求

- 装有 Xcode 16.4 及 iOS Simulator 运行时的 macOS
- [XcodeGen](https://github.com/yonaskolb/XcodeGen) 2.40 或更高版本
- **iOS 15.0 或更高版本**
- 用于在线连接流程的 Google 账号
- 真机安装需要 Apple 签名身份，或 SideStore / AltStore 等侧载工具

如需安装 XcodeGen：

```sh
brew install xcodegen
```

## 构建与运行

生成 Xcode 工程：

```sh
xcodegen generate
open PhotosBackup.xcodeproj
```

在 Xcode 中选择 `PhotosBackup` scheme 和一个 iPhone 模拟器，然后运行应用。也可以使用命令行构建模拟器版本：

```sh
xcodebuild \
  -project PhotosBackup.xcodeproj \
  -scheme PhotosBackup \
  -destination 'generic/platform=iOS Simulator' \
  CODE_SIGNING_ALLOWED=NO \
  build
```

如需签名真机构建，在 `project.yml` 中设置 `DEVELOPMENT_TEAM`，重新生成工程，并让 Xcode 管理签名。

### 测试后台执行

调试构建会暴露 **设置 → 诊断 → 模拟后台运行**。它会立即执行同样的扫描/入队/等待路径，是日常最快的测试循环。

要在已连接的真机上触发真实的 `BGProcessingTask` 启动处理器：从 Xcode 运行应用，将其退到后台，暂停调试器，在 LLDB 控制台输入：

```text
e -l objc -- (void)[[BGTaskScheduler sharedScheduler] _simulateLaunchForTaskWithIdentifier:@"com.g8row.photosbackup.background-backup"]
```

诊断页也有一个按钮可以复制该命令。

### 构建未签名 IPA

仓库内置了面向 SideStore/AltStore 侧载的打包脚本：

```sh
./Scripts/make-ipa.sh
```

脚本默认使用 `DEVELOPER_DIR=/Applications/Xcode-16.4.0.app/Contents/Developer`。若 Xcode 在其他位置，可覆盖：

```sh
DEVELOPER_DIR=/path/to/Xcode.app/Contents/Developer ./Scripts/make-ipa.sh
```

未签名包会输出到 `build/PhotosBackup.ipa`，由侧载工具使用设备上配置的 Apple ID 重新签名。

## 通过 SideStore 安装

每个 [GitHub release](https://github.com/g8row/PhotosBackup/releases) 都会附带预构建的未签名 IPA。

如需自动获取新版本，可在 SideStore、AltStore 或 Feather 中添加以下源（每次发布都会重新生成）：

```text
https://g8row.github.io/PhotosBackup/apps.json
```

> [!TIP]
> 在 iPhone（已安装 SideStore 或 AltStore）上，一键安装最新版本：
>
> - **[安装 Photos Backup](https://g8row.github.io/PhotosBackup/install.html)** —— 在 iPhone 上打开，点击使用 SideStore / AltStore 安装。
>
> GitHub 会在 Markdown 中剥离自定义 `sidestore://` / `altstore://` URL scheme，因此按钮放在该页面而不是 README 中。它安装的是
> `https://github.com/g8row/PhotosBackup/releases/latest/download/PhotosBackup.ipa`。

- 将 `PhotosBackup.ipa` AirDrop 到 iPhone 并存入「文件」。
- 打开 LocalDevVPN。
- 在 SideStore 中点击 +，选择 `PhotosBackup.ipa`，进行安装。
- 如果跨越 0.0.2 的 bundle ID 变更升级，请重新连接一次 Google 账号。

## 连接 Google 账号

1. 安装并启动 Photos Backup。
2. 在引导页（或 设置 → 连接账号）点击 **连接 Google 账号**。
3. 在应用内窗口中登录并同意 Google 的授权提示。页面之后可能一直停在加载动画，这是预期行为——应用会自行捕获令牌并关闭窗口。
4. 授予所需的照片访问权限并选择相册。

捕获的 `oauth_token` 是一次性的，只会从网页视图的 Cookie 存储中读取一次，随后网页会话即被丢弃。

## 认证与凭据处理

正常流程：

```text
应用内 EmbeddedSetup 网页视图
        │  oauth_token（从 WKHTTPCookieStore 读取）
        ▼
Android 主令牌 → Photos 访问令牌 → 私有 Photos API
```

- 令牌交换在本地完成，没有配套后端。
- 凭据在钥匙串可用时，以单个钥匙串条目、使用 `AfterFirstUnlockThisDeviceOnly` 存储。
- 导出的照片图库项目暂存于受保护的 Application Support，后台传输完成前一直保留，之后移除。
- `oauth_token` 在进程内从应用自身非持久化的网页视图 Cookie 存储读取；绝不通过扩展、App Group 或自定义 URL scheme 离开应用。
- 绑定的/加密的 Google 令牌会被拒绝，因为尚未实现令牌绑定。

## 已知限制

- Google 可能随时变更或停用私有认证与 Photos 接口。
- 当账号开启了 Google 侧设置时，Google Photos 应用的「释放空间」会跳过已编辑照片（包括相机保存带调整的实况照片，如人像），即使 Google 自己的备份已经上传了它们。Photos Backup 会完整备份它们，但无法让 Google 提供删除选项。Google Photos 应用的多选「从设备删除」可以删除它们，因为它只要求照片已备份。
- 从 Google Photos 保存到 iPhone 的照片或视频（文件名形如 `AIXW8346.JPG`）在 Google Photos 应用中永远不会被计为已备份，即使图库已持有它：相同字节的上传会并入该既有项目。在 Apple 照片中做任何编辑都会产生新文件，备份后才会计数。
- 编辑后的照片/视频按 iPhone 上的实际效果备份。其未编辑的原件仅当早期备份已上传时才保留。
- 后台相册备份是机会式的：iOS 决定每个处理请求何时运行，并可能根据使用情况、电量和系统策略延迟。
- 离开应用后继续备份需要 iOS 26，且 iOS 仅在应用处于前台时接受该请求。iOS 仍可能提前结束它以回收资源，并在应用切换器中划掉应用时结束它；未完成的工作会等待应用下次运行。
- 快捷指令可在 iOS 16+ 上创造额外备份机会，但 iOS 每次运行只给约 30 秒。该动作会入队持久化工作并把已准备好的文件传输交给后台 URL 会话；它不是周期性保证。
- 后台扫描每次入队有上限的 250 个项目批次。该上限限制内存，而非限制窗口上传量：队列是持久的，窗口未完成的部分会等下一次。前台扫描以及手动的「立即备份」「重新检查备份」按钮会把整个选择一次性入队，因此它们报告的计数就是完整运行量，队列的并发设置决定每次移动多少。
- iOS 16+ 后台扫描使用持久的 PhotoKit 变更令牌；iOS 15 与令牌过期恢复使用以正确性优先的当前图库扫描。令牌在一次扫描的所有来源都交给队列后才会推进，因此饱和队列不会在每个窗口重复枚举图库。
- 导出、哈希、去重查找与上传初始化仍需要执行窗口。一旦初始化，文件 PUT 会在处理窗口过期后继续在 iOS 下运行；应用在提交前持久化回执。
- 仅云端（cloud-only）的 PhotoKit 资源会在短暂的后台处理窗口期间推迟，应用回到前台且有网络时恢复。
- 未签名的模拟器构建无法将凭据持久化到钥匙串。免费个人团队构建通常七天后过期，需要刷新。
- 收到绑定/加密主令牌的 Google 账号不受支持。
- 这不是可上架 App Store 的版本。

## 测试

对任意已安装模拟器运行离线单元测试套件：

```sh
xcodebuild \
  -project PhotosBackup.xcodeproj \
  -scheme PhotosBackup \
  -destination 'platform=iOS Simulator,name=<你的模拟器>' \
  CODE_SIGNING_ALLOWED=NO \
  test
```

查看可用模拟器名称：

```sh
xcrun simctl list devices available
```

在线测试是可选加入的，因为它们会连接 Google。完整的交换测试还需要全新的一次性 `oauth_token`：

```sh
TEST_RUNNER_GPMC_LIVE=1 \
xcodebuild ... test \
  -only-testing:PhotosBackupTests/LiveExchangeTests/testInvalidTokenIsRejectedByGoogleNotByUs

TEST_RUNNER_GPMC_LIVE=1 \
TEST_RUNNER_GPMC_OAUTH_TOKEN=oauth_XXXX \
xcodebuild ... test \
  -only-testing:PhotosBackupTests/LiveExchangeTests/testFullExchangeWithRealToken
```

切勿提交令牌或捕获的账号凭据。

## 仓库结构

```text
App/Sources/                  SwiftUI 应用、引导、账号与上传队列
App/Sources/AutomaticBackupCoordinator.swift  BGProcessingTask 调度
App/Sources/ContinuedBackup.swift             iOS 26 离开应用后的续传备份
App/Sources/BackgroundUploadTransport.swift   可安全重启的文件 PUT 传输
App/Sources/PhotoLibraryChangeTracker.swift   持久化 PhotoKit 扫描令牌
App/Sources/NetworkPolicy.swift               仅 Wi-Fi / 蜂窝网络策略
App/Sources/UploadQueuePersistence.swift      持久的账号级队列
App/Resources/                Info.plist、应用图标资源与本地化文件（en/zh-Hans .lproj）
App/Sources/AccountConnectWebView.swift       应用内 EmbeddedSetup 网页视图
GPMC/Core/                    Photos 协议客户端与 protobuf 辅助
Tests/PhotosBackupTests/      离线单元测试与受控在线测试
Scripts/make-ipa.sh           未签名 IPA 打包
Scripts/verify_localization.py 本地化校验（key 配对、语法、代码覆盖）
docs/                         可行性记录与认证 ADR
project.yml                   XcodeGen 工程定义
```

实现历史与协议细节参见：

- [`docs/ADR-001-auth-route.md`](docs/ADR-001-auth-route.md)
- [`docs/feasibility-probe.md`](docs/feasibility-probe.md)

## 致谢

协议工作基于 [GPMC by xob0t](https://github.com/xob0t/gpmc)，浏览器认证路线基于 gotohp。固定的上游版本与设计依据记录在认证 ADR 中。

## 许可证

本项目基于 [MIT License](LICENSE) 发布。

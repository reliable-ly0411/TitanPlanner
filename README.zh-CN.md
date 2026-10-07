# TitanPlanner 中文双版本

基于 Titan-Dynamics/TitanPlanner，在保留原项目许可和署名的基础上维护简体中文体验、Windows 构建及自动上游同步。见 [COPYING.txt](COPYING.txt)、[上游说明](README.md)。

## 选择界面语言

- **中文(简体)**：原版 `zh-Hans`，69 个原版资源文件按基线哈希保留。
- **中文(简体)2**：增强 `zh-CN`，补齐主界面、规划、设置、日志等资源和动态文本。

首次启动且没有语言偏好时默认使用增强版；已有偏好保留。改变语言后保存，下次启动生效，不关闭当前会话；保存失败恢复原选择。无效语言配置会安全回退为增强简体中文。

新版修正“姿态”“无遥控接收机”等语境译法，设置页按可用宽度分为一至三列，文字控件按内容调整大小。MAVLink 参数、枚举、协议字段、数值格式保留原值。

## 获取和更新

本仓库 [Releases](https://github.com/reliable-ly0411/TitanPlanner/releases) 提供通过自动测试的 Windows 便携预发布包。解压完整 ZIP 到新目录，运行 `MissionPlanner.exe`，保留全部中文卫星程序集及原生库。`SHA256SUMS` 用于核对下载完整性。

应用内更新入口也指向本仓库，不再用上游二进制覆盖中文版本。自动发布仍需真实飞控、飞行、高 DPI 与完整功能验收；不能把通过单元测试等同于飞行验证。

## 用 VS Code 构建

需要 Git、独立 .NET 8 SDK；Python 静态校验需要 Python 3.12。无需 Visual Studio IDE。

```powershell
git clone https://github.com/reliable-ly0411/TitanPlanner.git
cd TitanPlanner
git submodule update --init --recursive
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/localization/build_windows.ps1
```

便携 SDK 可使用 `-DotNet D:\Programs\dotnet\dotnet.exe`。`-OutputDirectory D:\TitanPlanner-test` 把程序放入独立目录，`-Configuration Debug` 构建调试版本。默认输出 `bin/Release/net461/` 是上游保留的目录名，实际主程序目标仍是 .NET Framework 4.7.2。

VS Code 的简体中文包为 `MS-CEINTL.vscode-language-pack-zh-hans`，C# 扩展为 `ms-dotnettools.csharp`；VS Code 不提供 Visual Studio 的 WinForms 可视化设计器。

## 测试与自动化

详见 [AUTOMATION.zh-CN.md](AUTOMATION.zh-CN.md)。每日检查上游，先验证候选版本再推进主分支和发布；冲突或测试失败保留待审查分支。构建包括 Release/Debug、中文静态及运行测试、真实 Windows 控件、离线回归测试、依赖漏洞审计和 ZIP 校验。

```powershell
python scripts/localization/verify_zh_hans.py
python -m unittest discover -s scripts/ci/tests -v
dotnet run --project MissionPlannerTests/Localization/Localization.csproj
```

## 维护翻译

在 `localization/zh-Hans/ui-translations.json` 和 `code-translations.json` 维护增强译文，再执行：

```powershell
python scripts/localization/update_zh_hans.py
python scripts/localization/build_ui_catalog.py
python scripts/localization/verify_zh_hans.py
```

历史词典目录名继续沿用 `zh-Hans`，生成目标是增强 `zh-CN`。不要改动原版 `zh-Hans` 资源；`original-resources.json` 校验原版基线。空的 `UiText.zh-Hans` 兼容资源防止增量构建残留旧增强译文。

动态文本只在显示位置调用 `UiText.Translate` / `UiText.Format`；保留格式占位符、链接和协议标识。原版与其他语言不会串用增强版动态译文。

原版资源基线：`26d0836e3854c2166dc0cbcacbbbb9813b890b2d`。本轮不改飞控控制算法。

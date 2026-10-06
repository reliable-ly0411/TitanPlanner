# TitanPlanner 简体中文补丁

本仓库继承 [Titan-Dynamics/TitanPlanner](https://github.com/Titan-Dynamics/TitanPlanner) 的 Git 历史与功能，在其原有简体中文基础上补齐界面资源和代码中的显示文本。TitanPlanner 本身继承自 ArduPilot Mission Planner。原项目许可与作者署名保留，见 [COPYING.txt](COPYING.txt) 和 [上游说明](README.md)。

## 使用

首次启动且没有已保存的语言偏好时，默认使用简体中文。已有配置的语言选择会保留；可在规划器设置的语言选项中选择简体中文，重启后让所有已创建界面使用同一语言。

本次交付是源码补丁，尚未提供经过 Windows 界面验收的安装包。不能将原上游 Releases 中的安装包当作本仓库的汉化构建；程序原有的上游更新渠道也未改成此 fork，使用它更新可能覆盖汉化版本。

## 覆盖内容

- 补齐主窗口、飞行数据、航线规划、初始设置、调参、数传、RTK、日志、测绘和集群等界面的简体中文资源。
- 翻译 3D 地图设置、电机智能分配、参数编辑器、连接与应答机状态、弹窗、输入提示、工具提示以及 HUD 方向与状态文字。
- 新增 2,179 条显示文本词典；新增或补齐 1,040 个窗体/HUD 资源条目，共修改或新增 69 个 RESX 文件。
- 保留已有语言资源；动态文本仅在简体中文文化下使用新译文，其他语言回退到原始文本。

MAVLink 命令、参数名、端口类型、固件/仿真器标识、型号和单位保留原值。飞控返回的消息、在线参数说明、用户脚本及外部插件提供的文本不做不可靠的自动翻译。因此，这份补丁不等于对所有可能出现的界面文字作出“零英文”的保证。

## 从源码构建

遵循 TitanPlanner 的 Windows 构建方式：安装 Visual Studio 2022、.NET 桌面开发组件及 .NET Framework 4.7.2 开发工具。

```sh
git clone https://github.com/reliable-ly0411/TitanPlanner.git
cd TitanPlanner
git submodule update --init --recursive
```

在 Visual Studio 中打开 `MissionPlanner.sln`，还原依赖并构建。分发时须保留 `zh-Hans` 目录中的卫星资源程序集，不能仅复制主程序 EXE。

本次在 Ubuntu 上尝试了整程序构建：原配置遇到 `open.snk` 与实际 `Open.snk` 的大小写差异；仅在验证命令中禁用签名后，又遇到上游插件资源路径大小写及 WinForms 非字符串资源构建限制。没有为绕过这些问题修改上游签名或发布配置。**完整 Windows 构建、实际 GUI 排版以及硬件连接场景尚未验收。**

## 校验与维护

Python 3 校验无需第三方包：

```sh
python3 scripts/localization/verify_zh_hans.py
```

独立翻译运行测试使用 .NET 8，不需要启动地面站或连接飞控：

```sh
dotnet run --project MissionPlannerTests/Localization/Localization.csproj
```

共享 `MissionPlanner.Utilities` 项目也已在本地完成编译（验证命令禁用签名，0 个错误）。Roslyn 对 215 个已修改的 C# 文件作语法检查，未发现新增语法错误；这些检查不替代完整 Windows 程序构建。

测试覆盖全部 2,179 条编译译文、`zh-Hans`/`zh-CN`/`zh-SG` 文化回退、切换回其他语言、带格式参数的文本和协议标识保留，共 2,214 项断言。测试入口使用 `.cs.txt` 并在测试项目中显式引用，避免被上游主程序或现有测试项目自动编译。

维护流程：

1. 在 `localization/zh-Hans/ui-translations.json` 补充窗体资源的原文与译文，在 `code-translations.json` 维护动态文本。保留 `{0}`、`{0:0.0}`、`{name}`、链接和控制用标记。
2. 执行 `python3 scripts/localization/update_zh_hans.py` 补齐窗体资源，再执行 `python3 scripts/localization/build_ui_catalog.py` 生成动态卫星资源。已有上下文译文不会被通用词典覆盖。
3. 动态代码只在显示位置调用 `UiText.Translate("原文")`；插值字符串使用 `UiText.Format($"Motor {number}")`。不要翻译配置键、枚举值、协议载荷或字典索引。
4. 执行上述校验及运行测试，再在 Windows 检查主界面、对话框、工具提示和高 DPI 排版。

`UiText` 对原文使用稳定 SHA-256 资源键，以区分 RESX 编译器会视为重复的大小写词条；仅缓存资源键，不缓存语言结果。界面语言与数值文化分开，避免汉化改变坐标、参数和文件中的数字格式。

汉化基线：`26d0836e3854c2166dc0cbcacbbbb9813b890b2d`。本补丁不改飞控协议与控制算法，也未配置额外的自动同步或发布任务。

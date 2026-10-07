# 上游同步、验证与发布

主工作流位于 `.github/workflows/main.yml`。上游为 `Titan-Dynamics/TitanPlanner` 的 `master`。

- 每天 03:17 UTC（北京时间 11:17）、主分支推送及手动运行时，检查上游更新。
- 有更新时创建独立候选分支，以合并保留本仓库修改；不强制覆盖主分支。
- 校验原版中文资源哈希、增强中文词典、自动化回归、翻译运行、Windows 界面及离线单元测试。
- 使用独立 .NET 8 SDK 构建 Release 和 Debug，检查直接及传递依赖的已知漏洞。
- 全部通过后，仅当主分支仍是本次验证的起点时才快进；并发用户提交不会被覆盖。
- 发布 Windows 便携 ZIP、SHA256SUMS 和构建提交信息。每个提交使用唯一 `zh2-<提交前12位>` 标签，重跑不会覆盖已有发布。
- 自动构建标记为预发布版。真实飞控、飞行、所有外部网络服务及不同显示器 DPI 不由这些自动测试证明。

发生合并冲突、上游改动自动化策略，或候选验证失败时，主分支与已有发布保持不变，工作流尝试创建待审查 PR。仓库 Settings → Actions → General 中需要允许 GitHub Actions 创建 PR；若未允许，候选分支仍保留，运行会清楚报错。主分支保护不允许机器人推送时，也应通过 PR 处理，不绕过保护规则。

只使用仓库自带 `GITHUB_TOKEN`，不要求个人令牌。构建与测试作业只有读取权限；推送与发布由单独作业执行。自动化动作固定到提交 SHA。

GitHub 定时任务可能延迟；公共仓库长时间没有活动时，GitHub 可能自动停用定时工作流。可在 Actions 页面手动恢复。推送和定时运行共用一条并发队列，避免重复发布。

旧 Android/macOS 工作流保留为手动入口，供迁移旧 Xamarin 项目时参考；不属于 Windows 发布流程，也未宣称移动端已通过构建或完成签名。此仓库不自动提交到 Google Play。

## 本地复现

在 Windows 的 VS Code 终端中，使用 .NET 8 SDK、Git 和 Python 3.12：

```powershell
python scripts/localization/verify_zh_hans.py
python -m unittest discover -s scripts/ci/tests -v
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/localization/build_windows.ps1 -OutputDirectory D:\TitanPlanner-test
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ci/test_windows.ps1 -BuildDirectory D:\TitanPlanner-test -ResultsDirectory D:\TitanPlanner-test-results
```

界面探针默认要求非交互会话，避免显示测试窗体干扰正在操作的桌面；GitHub 托管测试环境通过 `CI=true` 明确标识。需要插拔飞控并扫描串口的上游测试标记 `Hardware`，自动流程明确排除，实机验证时单独运行。网络相关上游测试标记 `Network`，可给 `test_windows.ps1` 加 `-IncludeNetwork` 单独运行，外部服务中断不会被误报为离线单元测试通过。

发布打包从干净构建目录生成，排除用户配置、航迹日志和地图缓存；包含两套中文卫星程序集及原生依赖。应用内更新入口指向本仓库 Releases，避免上游二进制覆盖中文改动。

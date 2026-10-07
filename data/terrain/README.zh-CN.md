# 中国区 30 米高程离线包

从 [MP 官方地形服务](https://terrain.ardupilot.org/SRTM1/) 下载同名 HGT 原始文件，供 Mission Planner / TitanPlanner 离线使用。数据通过独立 Release 分发，仓库只存打包脚本、覆盖清单和说明。

- 下载：[terrain-cn30-20261007-r2](https://github.com/reliable-ly0411/TitanPlanner-zh-CN/releases/tag/terrain-cn30-20261007-r2)
- 安装：[INSTALL.zh-CN.txt](INSTALL.zh-CN.txt)
- 请求及来源：[request.json](request.json)
- 覆盖：[china-tiles.txt](china-tiles.txt)

## 覆盖定义

按前期核查的 MFE 中国区包提取 1166 个图幅名称，**仅复用覆盖名称，不采用其高程值**。其中 1162 个在官方 SRTM1 服务存在；另外四个 `N18E111`、`N20E108`、`N20E111`、`N27E122` 返回 404，旧 MFE 文件也全部是 `-9999` 无效值，已明确排除。

“完整”表示清单内官方可用图幅完整收录，不是行政边界裁切或全部海岛覆盖承诺。图幅边缘包含邻近区域。文件为 3601×3601、1 角秒 HGT；30 米是水平格网间距，不能解释为垂直精度。

## 可复核性

每幅验证 ZIP CRC、文件名、25934402 字节长度、SHA-256；记录无效节点数量、来源 URL、HTTP Last-Modified 与获取时间。分包后回读全部 HGT，核对 SHA-256。Release 的 `manifest.json` 记录全部图幅和分包映射，`SHA256SUMS` 校验发行文件。

HGT 原始字节不改动；ZIP 内文件时间改为打包时间，避免部分新版 MP / TitanPlanner 把时间戳早于 2026-03-01 的新下载缓存删除。原始 HTTP Last-Modified 单独保留，不能当成测绘日期。

官方文档将现行数据归于 JAXA ALOS AW3D30，本仓库未独立鉴定逐幅上游版本或补洞来源。版权、署名和条款见安装说明；地形数据不自动套用仓库软件许可证。

## 复现

Python 3.10+，只使用标准库：

```sh
python3 -m unittest discover -s scripts/terrain/tests -v
python3 scripts/terrain/package.py --output terrain-release --workers 4
```

需下载约 8.7 GiB 上游 ZIP。打包按图幅流式处理，无须落盘完整 28.1 GiB HGT，但应给输出分包留至少 12 GiB 空间。输出目录须为空，不覆盖已有发布。

工作流 `.github/workflows/terrain-china.yml` 在请求文件变更或手动运行时执行；无定时任务。下载前先固定版本标签并创建 Release 草稿，提前确认权限；标签不随主分支移动。下载、校验和回读验证全部成功才上传。发布前核对 GitHub 返回的每个资产大小与 SHA-256，不把地形数据设为程序的 Latest Release。以后生成新快照需先改 `request.json` 的唯一标签，已发布版本不覆盖。

这套检查证明下载与打包完整，不代表实地高程精度或真实飞控运行验证。HGT 与飞控的 DAT 缓存不同；安装与更新步骤见安装说明。

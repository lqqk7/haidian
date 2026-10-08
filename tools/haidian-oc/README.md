# 海淀城市设计制作工具链

本目录属于 `Haidian_Open_City` 项目，保存「万感京张 / EVERY SENSE JING-ZHANG」的图版、字体、PDF、场景截图与校验工具。2026-10-08 从项目外的同级 `Haidian_OC_toolchain` 迁入；完整本地目录及历史文件保留，后续制作文件在本项目内维护。

## 文件与版本控制

- `w81-*` 至 `w100-*`、`wp*`：历史制作轮次，保留原子目录名称及脚本关系。
- Git 保存制作源码、依赖锁文件、必要几何基线、HTML 源输入与已有字体子集。`wp4b/build` 内是生成器源码；`wp4b/out` 中部分 HTML 是后续图版制作的输入，不能统一当作缓存删除。
- 虚拟环境、Node 依赖、截图、PDF、备份和其他中间产物完整保留在本地，由本目录 `.gitignore` 排除；个人仓库不是这些历史文件的完整备份。
- `wpn2b -> .` 是历史路径别名，用于解析 `wpn2b/wp4b/...`；遍历时不要跟随该软链。
- 投稿包内原有工具路径记录是历史记录，未为本次迁移改写。其 `Haidian_OC_toolchain/<路径>` 对应本目录 `<路径>`。

## 环境

迁移保留了 Python 3.14 虚拟环境，并修正其启动脚本路径。新检出可在本目录执行：

```sh
python3.14 -m venv venv
venv/bin/python -m pip install -r requirements.txt
npm ci
```

Python 版本和依赖以迁移前现存环境为基线；Playwright 从本目录的依赖加载，不再依赖个人 npm 临时缓存。浏览器仍需本机安装；部分截图脚本接受 `CHROME_EXE`。部分制作流程还需要 `pngquant`、`zopflipng`、ImageMagick、Poppler，以及本机 Source Han Sans SC 字体，具体见脚本。

项目路径与工具路径由脚本所在位置推导。运行前查看参数和写入范围：部分历史制作脚本会覆盖投稿包图件，不应作为只读验证直接执行。

## 可用检查与已知限制

可从项目根目录执行字体覆盖检查：

```sh
tools/haidian-oc/venv/bin/python tools/haidian-oc/wpe3/font_coverage_check.py submissions/lqqk7/every-sense-jingzhang
```

本次迁移不是全部历史制作流程的重建。原目录已缺少 `wp4b/mkfont.py`、`wp4b/build/tokens.js`，部分流程依赖未保留下来的 `wpv70/dsp`、`wpc4` 等历史输入；这些入口仍可能无法运行。迁移修正了历史临时路径的归属，但没有虚构或补造缺失素材。字体子集和现存 HTML 输入保留，用于后续恢复和核验。

本次提交与推送仅面向个人仓库 `lqqk7/haidian`，不创建或更新 PR。

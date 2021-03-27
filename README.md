# resolve_batch_io_point
按照特定规则通过设定IO点批量添加基于 *Single Clip* 的渲染任务

## 安装
- 请将 *Batch_io.py* 拷贝至达芬奇指定的脚本存放目录下
- macOS: /Users/{你的用户名}/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts
- Windows: C:\Users\{你的用户名}\AppData\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts
- 请使用v16及以上版本
- 在菜单：工作区(Workspace) > 脚本(Scripts) 中即可找到
- 仅支持在达芬奇内使用，不支持在外部运行

## 用法
在工具中提供了4个选项，均为必选项
- 渲染输出路径
- 按照指定颜色的片段，分别设置IO点，并将其各自添加为渲染任务
- 添加任务时使用的渲染预设（请在开始前设置好）
- 添加任务时扫描的某一视频轨道，由于本工具仅针对基于 *Single Clip模式* 的情况，因此请注意这一渲染模式的特点，选取所需的基准视频轨道（通常为最低轨道V1）

请根据您的需求选择，最后点击 *Run* 即可批量添加渲染任务

## 需要
- Python 3.6 64-bit 
- 其他版本的 Python 达芬奇并不支持
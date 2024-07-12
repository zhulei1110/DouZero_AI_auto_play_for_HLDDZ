# 欢乐斗地主 AI 辅助（腾讯QQ游戏大厅版）

douZero_AI_auto_play_for_HLDDZ

* 本项目基于 [DouZero](https://github.com/kwai/DouZero)
* 模型训练及配置请移步 [DouZero](https://github.com/kwai/DouZero)
* 感谢 [Vincentzyx](https://github.com/Vincentzyx) 提供的 resnet 模型文件
* 本项目仅供学习以及技术交流，请勿用于其它目的，否则后果自负

## 使用说明

* 运行本程序之前，请先打开欢乐斗地主游戏窗口
* 仅在 经典模式 下进行过充分测试
* 明牌的逻辑尚未实现，愿意完善的可提交 PR
* 初始化运行时，会将游戏窗口的尺寸调整为 1600 x 900（窗口尺寸）
* opencv 模板匹配的基准尺寸是 1920 x 1080（模板截图都是基于该尺寸）
* 不建议修改窗口尺寸，修改后可能会影响角色、牌面、动作的识别成功率
* 当开启图片日志时（`screenshot_image_logs` 、 `template_match_image_logs` 等等），程序运行时会产生大量图片文件，建议仅在测试时开启图片日志
* 图片日志目录 `screenshots/logs`（需要手动创建）

## 如何运行

1. clone 本项目后，使用终端或命令行进入根目录
2. 创建 python 虚拟环境：python3 -m venv venv
3. 激活虚拟环境：venv\Scripts\activate
4. 安装项目依赖：pip install -r requirements.txt
5. 运行本程序：python -m main

## 程序截图

![jietu01](https://raw.githubusercontent.com/zhulei1110/DouZero_AI_auto_play_for_HLDDZ/main/jietu01.png)
![jietu02](https://raw.githubusercontent.com/zhulei1110/DouZero_AI_auto_play_for_HLDDZ/main/jietu02.png)
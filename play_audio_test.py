# 最简化的 ffpyplayer 测试版本

from ffpyplayer.player import MediaPlayer
import time

# 尝试播放一个音频文件
player = MediaPlayer(r".\\files\\未竟（《黑神话：悟空》结局主题曲）（Unfinished） [zON6tyIp5wA].ogg")  # 替换为实际文件路径

# 简单播放10秒
# print("开始播放")
# for i in range(100):
#     frame, val = player.get_frame()
#     if val == 'eof':
#         break
#     time.sleep(0.1)

# # 关闭播放器
# player.close_player()
# print("播放结束")

# 使用 ffpyplayer 完整播放该音频
while True:
    frame, val = player.get_frame()
    if val == 'eof':
        break
    time.sleep(0.1)

# 关闭播放器
player.close_player()
print("播放结束")


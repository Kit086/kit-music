# 如何将 ffmpeg 打包进应用（在可分发的 Python 包中包含并使用 ffmpeg）

**注意：** ffmpeg 的许可证问题

您已经在开发环境的 `.venv\share\ffpyplayer\ffmpeg\bin` 目录下找到了 ffmpeg。当您将应用打包为可通过 pipx 安装的工具时，确实会面临 ffmpeg 依赖的问题。以下是几种解决方案：

## 方案一：将 ffmpeg 二进制文件打包进您的应用

这是最直接的方法，确保不论在何种环境下，您的应用都能找到所需的 ffmpeg。

### 1. 项目结构示例

```
your_cli_project/
├── src/
│   └── your_package/
│       ├── __init__.py
│       ├── main.py
│       ├── player.py
│       └── bin/
│           ├── ffmpeg.exe       # Windows
│           ├── ffmpeg           # Linux
│           └── ffmpeg-darwin    # macOS
├── pyproject.toml
├── setup.py
└── MANIFEST.in
```

### 2. 在 setup.py 中包含二进制文件

```python
from setuptools import setup, find_packages

setup(
    name="your-cli-player",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,  # 重要：包含非 Python 文件
    package_data={
        "your_package": ["bin/*"],  # 包含 bin 目录下的所有文件
    },
    # ...其他元数据...
)
```

### 3. 创建 MANIFEST.in 文件

```
include src/your_package/bin/*
```

### 4. 或者使用 pyproject.toml (如果使用 Poetry 或 modern setuptools)

```toml
[tool.setuptools.package-data]
"your_package" = ["bin/*"]
```

### 5. 在代码中动态查找 ffmpeg 路径

```python
import os
import sys
import subprocess
from pathlib import Path

def get_ffmpeg_path():
    """获取 ffmpeg 可执行文件的路径"""
    # 1. 首先检查包内的 ffmpeg
    package_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 确定当前操作系统
    if sys.platform.startswith('win'):
        ffmpeg_name = "ffmpeg.exe"
    elif sys.platform.startswith('darwin'):
        ffmpeg_name = "ffmpeg-darwin"
    else:  # Linux 和其他系统
        ffmpeg_name = "ffmpeg"
        
    # 检查包内的 bin 目录
    bundled_ffmpeg = os.path.join(package_dir, "bin", ffmpeg_name)
    if os.path.isfile(bundled_ffmpeg) and os.access(bundled_ffmpeg, os.X_OK):
        return bundled_ffmpeg
        
    # 2. 然后检查 ffpyplayer 安装的 ffmpeg
    try:
        import ffpyplayer
        ffpy_path = os.path.dirname(ffpyplayer.__file__)
        possible_dirs = ["bin", "share/ffpyplayer/ffmpeg/bin"]
        
        for dir_name in possible_dirs:
            potential_path = os.path.join(ffpy_path, dir_name, ffmpeg_name)
            if os.path.isfile(potential_path) and os.access(potential_path, os.X_OK):
                return potential_path
    except ImportError:
        pass
        
    # 3. 最后尝试系统 PATH 中的 ffmpeg
    try:
        if sys.platform.startswith('win'):
            # Windows 上使用 where 命令
            result = subprocess.run(["where", "ffmpeg"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split("\n")[0]
        else:
            # Linux/macOS 上使用 which 命令
            result = subprocess.run(["which", "ffmpeg"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
    except Exception:
        pass
    
    # 如果都找不到，返回 None
    return None

# 在需要使用 ffmpeg 的地方
def download_audio(url, output_dir):
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        print("错误: 找不到 ffmpeg，请确保已安装 ffmpeg 或将其添加到 PATH 环境变量中")
        return False
    
    cmd = [
        "yt-dlp", 
        "-x", 
        "--audio-format", "vorbis", 
        "--ffmpeg-location", ffmpeg_path,
        "-o", os.path.join(output_dir, "%(title)s.%(ext)s"),
        url
    ]
    
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"下载失败: {e}")
        return False
```

## 方案二：使用已有的 ffmpeg 包装库

有些库已经解决了 ffmpeg 打包问题，您可以直接依赖它们：

### 1. 使用 ffmpeg-binaries 库

```python
# 安装时添加依赖
# pip install ffmpeg-binaries

import ffmpeg_binaries

# 在代码中获取路径
ffmpeg_path = ffmpeg_binaries.FFMPEG_PATH

# 在 yt-dlp 中使用
cmd = ["yt-dlp", "-x", "--audio-format", "vorbis", "--ffmpeg-location", ffmpeg_path, url]
```

### 2. 或使用 pyffmpeg

```python
# 安装时添加依赖
# pip install pyffmpeg

from pyffmpeg import FFmpeg
ffmpeg_instance = FFmpeg()

# 获取 ffmpeg 路径
ffmpeg_path = ffmpeg_instance.get_ffmpeg_path()
```

## 方案三：添加安装说明和运行时检查

如果您不想打包二进制文件，可以将检查作为应用启动的一部分：

```python
def check_ffmpeg():
    """检查 ffmpeg 是否可用，如果不可用则提供安装指南"""
    try:
        # 尝试运行 ffmpeg -version
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("警告: 找不到 ffmpeg，某些功能将不可用")
        print("请按照以下步骤安装 ffmpeg:")
        if sys.platform.startswith('win'):
            print("1. 访问 https://ffmpeg.org/download.html 下载 Windows 版本")
            print("2. 解压文件，并将 bin 目录添加到系统 PATH 环境变量")
        elif sys.platform.startswith('darwin'):
            print("1. 使用 Homebrew 安装: brew install ffmpeg")
        else:
            print("1. 使用包管理器安装: sudo apt install ffmpeg 或 sudo dnf install ffmpeg")
        return False

# 在应用启动时运行检查
def main():
    ffmpeg_available = check_ffmpeg()
    if not ffmpeg_available:
        # 继续运行但禁用依赖 ffmpeg 的功能
        pass
    # 其他应用逻辑...
```

## 最佳实践建议

1. **结合方案一和方案三**：在包中打包 ffmpeg，但也添加系统 ffmpeg 的检测和优雅降级
   
2. **添加清晰的文档**：在 README 和帮助文档中说明:
   - 应用依赖 ffmpeg
   - 如何手动安装 ffmpeg (如果自动方法失败)
   - 如何指定自定义的 ffmpeg 路径

3. **添加命令行参数**：让用户能够指定 ffmpeg 路径
   ```python
   import argparse
   
   parser = argparse.ArgumentParser()
   parser.add_argument("--ffmpeg-path", help="指定 ffmpeg 可执行文件的路径")
   args = parser.parse_args()
   
   ffmpeg_path = args.ffmpeg_path if args.ffmpeg_path else get_ffmpeg_path()
   ```

4. **平台兼容性**：确保您的应用可以处理不同操作系统上 ffmpeg 的路径和命名差异

5. **考虑文件大小**：ffmpeg 二进制文件可能很大，请确保您了解这会如何影响您的包大小

通过这些方法，您的CLI播放器应用可以在任何通过 pipx 安装的环境中都能找到并使用 ffmpeg，而不需要依赖开发环境中的 `.venv` 目录。
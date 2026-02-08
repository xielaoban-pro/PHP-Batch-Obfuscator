# 🔐 PHP批量混淆加密工具 (PHP Batch Obfuscator)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7+-green.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com)

> **声达网络 (sdczz.com)** 出品的专业 PHP 代码保护工具  
> 支持多级混淆强度、批量处理、无需扩展依赖的纯 PHP 加密方案

---

## ✨ 项目特色

- 🛡️ **四种加密强度**：从基础到超高强度，满足不同安全需求
- 🚀 **纯 PHP 运行**：无需安装 ionCube、Zend Guard 等扩展
- 📦 **批量处理**：支持递归加密整个项目目录
- 💾 **配置记忆**：自动保存上次使用的路径和加密模式
- 🎯 **智能注释处理**：可选保留版权注释或完全清理
- 🔧 **双模式运行**：支持交互式 GUI 和命令行批量操作

---

## 📋 加密模式详解

### 1️⃣ **Base64 (基础)**
- **原理**：Base64 编码 + `eval` 执行
- **安全性**：⭐⭐ (低)
- **适用场景**：快速测试、非敏感代码

### 2️⃣ **Gzip (中级)**
- **原理**：Gzip 压缩 + Base64 编码
- **安全性**：⭐⭐⭐ (中)
- **文件体积**：可减少 40-60%
- **适用场景**：大文件加密、带宽优化

### 3️⃣ **Xor (高级)** ⭐ 推荐
- **原理**：动态 XOR 异或加密 + Gzip + 变量混淆
- **安全性**：⭐⭐⭐⭐ (高)
- **特点**：每次加密密钥随机生成
- **适用场景**：商业源码、核心配置文件

### 4️⃣ **Ultra (超高强度)** 🔥 最强
- **原理**：双层 XOR + 乱码变量名 + 多重编码
- **安全性**：⭐⭐⭐⭐⭐ (极高)
- **特点**：使用 Extended ASCII 字符集生成不可读变量名
- **适用场景**：整站源码、授权系统、支付模块

---

## 🚀 快速开始

### 环境要求
```bash
Python 3.7+
目标服务器需支持 PHP 5.3+ (base64_decode, gzuncompress, eval)
```

### 安装使用

#### 方式一：直接运行可执行文件
```bash
# 双击运行 dist/sdczz_encryptor.exe (Windows)
# 或从命令行启动
dist/sdczz_encryptor.exe
```

#### 方式二：从源码运行
```bash
# 克隆仓库
git clone https://github.com/yourusername/php-obfuscator.git
cd php-obfuscator

# 运行脚本
python php_obfuscator.py
```

### 交互式使用

```bash
$ python php_obfuscator.py

==========================================
      声达网络 PHP 混淆加密工具 (sdczz.com)
      支持多强度加密、批量文件夹处理
==========================================

[?] 请输入 PHP 文件或目录路径: ./myproject
[?] 请输入输出路径: ./encrypted
[?] 选择加密强度
  1. Base64  [基础]
  2. Gzip    [中级]
  3. Xor     [高级] ⭐ 推荐
  4. Ultra   [超高] 🔥 最强

输入序号 (1-4, 默认 3): 4
[?] 保留原文件注释 (y/N): n

✅ 开始处理...
```

### 命令行模式

```bash
# 加密单个文件
python php_obfuscator.py input.php -o output.php -m 4

# 加密整个目录
python php_obfuscator.py ./project -o ./encrypted -m 3

# 保留注释
python php_obfuscator.py input.php -o output.php -m 3 --keep-comments
```

---

## 📊 加密效果对比

### 原始代码
```php
<?php
function calculatePrice($base, $tax) {
    return $base * (1 + $tax);
}
echo calculatePrice(100, 0.15);
?>
```

### Ultra 模式加密后
```php
<?php
/* PROTECTED BY GEMINI OBFUSCATOR */
/* HIGH SECURITY ENCRYPTION */
$¢ÏlÏ1Ø="PhcXGBAUzc7T1gsVcQ5bVllGBnhGAWBhZEZC...";
$ØØØ0ØØllØ0Ì="477800305367";
$ØllØÌØÌ0l10="";
$¢ÏlÏ1ØlØll0=base64_decode($¢ÏlÏ1ØlØll0);
for($lØ0Ø0l=0;$lØ0Ø0l<strlen($¢ÏlÏ1ØlØll0);$lØ0Ø0l++){
    $ØllØÌØÌ0l10.=chr(ord($¢ÏlÏ1ØlØll0[$lØ0Ø0l])^ord($ØØØ0ØØllØ0Ì[$lØ0Ø0l%strlen($ØØØ0ØØllØ0Ì)]));
}
eval($ØllØÌØÌ0l10);
?>
```

---

## 🔍 环境检测

项目提供了 `check_env.php` 环境检测脚本：

```bash
# 上传到服务器
upload check_env.php to: http://yoursite.com/

# 浏览器访问
http://yoursite.com/check_env.php

# 如果显示 ✅ "环境完美支持"，说明所有加密模式均可正常运行
```

---

## 🏗️ 构建可执行文件

```bash
# 安装 PyInstaller
pip install pyinstaller

# 构建
pyinstaller php_obfuscator.spec

# 生成的可执行文件位于
dist/sdczz_encryptor.exe
```

---

## ⚠️ 注意事项

### ✅ 优势
- ✔️ 无需购买加密扩展授权
- ✔️ 支持所有主流 PHP 版本 (5.3 - 8.x)
- ✔️ 跨平台运行 (Windows/Linux/Mac)
- ✔️ 可与防火墙和缓存系统兼容

### ⚠️ 安全提醒
- ⚠️ **Ultra 模式**可能被部分安全软件误报（因乱码变量），建议先在测试环境验证
- ⚠️ 此工具为**混淆**而非**编译**，高级逆向工程师仍可能破解
- ⚠️ 建议结合**服务端授权验证**实现完整保护方案

### 🚫 不适用场景
- ❌ 开源项目（违反开源协议）
- ❌ 需要他人二次开发的代码
- ❌ 性能要求极高的场景（eval 有轻微性能损耗）

---

## 🛠️ 技术栈

- **Python 3.7+**: 主程序语言
- **Base64/Gzip**: 编码与压缩
- **XOR Cipher**: 异或加密算法
- **PyInstaller**: 可执行文件打包

---

## 📝 开源协议

本项目采用 MIT 协议开源。

**版权所有 © 2026 声达网络 (sdczz.com)**

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some feature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

## 📧 联系方式

- 🌐 官网：[sdczz.com](https://sdczz.com)
- 📮 反馈：提交 GitHub Issue

---

## ⭐ Star History

如果这个项目对您有帮助，请给我们一个 ⭐ Star！

---

**声明**：本工具仅供合法的软件保护用途，请勿用于非法目的。使用者需自行承担法律责任。

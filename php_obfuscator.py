import os
import sys
import base64
import zlib
import random
import string
import argparse
import re
import shutil
import json

# ==========================================
# 配置管理 (sdczz.com)
# ==========================================

# 配置文件路径：存放在可执行文件同级目录
if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(APP_DIR, 'obfuscator_config.json')

def load_config():
    """从本地 JSON 读取上次使用的配置"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_config(key, value):
    """持久化保存配置项到本地"""
    config = load_config()
    config[key] = value
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[-] 警告: 无法保存配置文件: {e}")

# ==========================================
# 核心加密逻辑 (声达网络加密)
# ==========================================

def generate_random_name(length=6):
    """生成常规混淆变量名 (如: _O0l1l)"""
    chars = "Il10O"
    first = random.choice(string.ascii_letters + "_")
    return first + "".join(random.choice(chars) for _ in range(length))

def generate_weird_name(length=4):
    """生成高强度乱码变量名 (Extended ASCII)"""
    # PHP 允许变量名包含 0x7f-0xff 的字符，增加逆向难度
    chars = "µñßðåæçøÿþ" 
    return "".join(random.choice(chars) for _ in range(length))

def xor_encrypt(data, key):
    """核心异或加密算法"""
    if isinstance(data, str):
        data_bytes = data.encode('latin1')
    else:
        data_bytes = data
        
    key_bytes = key.encode('utf-8')
    key_len = len(key_bytes)
    
    result = bytearray()
    for i, byte in enumerate(data_bytes):
        result.append(byte ^ key_bytes[i % key_len])
    
    return result.decode('latin1')

def extract_doc_comment(content):
    """提取文件开头的注释块 (支持 /** ... */ 和 /* ... */)"""
    # 优化后的正则：
    # 1. ^\s* : 允许文件开头有空白
    # 2. (?:<\?php\s*)? : 允许可选的 <?php 标签和随后的空白
    # 3. \s* : 允许标签和注释之间有换行符
    # 4. (\/\*.*?\*\/) : 捕获 /* ... */ 内容 (包括 /**)
    match = re.search(r'^\s*(?:<\?php\s*)?\s*(\/\*.*?\*\/)', content, re.DOTALL)
    if match:
        return match.group(1)
    return ""

def prepare_content(content):
    """预处理：清理 PHP 标签"""
    content = content.strip()
    if content.startswith("<?php"):
        content = content[5:]
    if content.startswith("<?"):
        content = content[2:]
    if content.endswith("?>"):
        content = content[:-2]
    return content

# ==========================================
# 加密桩生成器 (各强度方案)
# ==========================================

def stub_simple(content, header):
    """方案 1: 基础 Base64 加密"""
    b64 = base64.b64encode(content.encode('utf-8')).decode('ascii')
    return f"""<?php
{header}
eval(base64_decode('{b64}'));
?>"""

def stub_gzip(content, header):
    """方案 2: Gzip 压缩 + Base64"""
    compressed = zlib.compress(content.encode('utf-8'))
    b64 = base64.b64encode(compressed).decode('ascii')
    return f"""<?php
{header}
eval(gzuncompress(base64_decode('{b64}')));
?>"""

def stub_xor(content, header):
    """方案 3: 高强度动态 XOR + 变量混淆"""
    compressed = zlib.compress(content.encode('utf-8'))
    key = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(random.randint(10, 20)))
    encrypted = xor_encrypt(compressed, key)
    payload = base64.b64encode(encrypted.encode('latin1')).decode('ascii')
    
    v_code, v_key, v_res, v_i, f_dec = [generate_random_name() for _ in range(5)]
    
    stub = f"""<?php
{header}
${v_code}="{payload}";
${v_key}="{key}";
function {f_dec}(${v_code}, ${v_key}) {{
    ${v_code} = base64_decode(${v_code});
    ${v_res} = '';
    for(${v_i}=0; ${v_i}<strlen(${v_code}); ${v_i}++) {{
        ${v_res} .= chr(ord(${v_code}[${v_i}]) ^ ord(${v_key}[${v_i} % strlen(${v_key})]));
    }}
    return ${v_res};
}}
eval(gzuncompress({f_dec}(${v_code}, ${v_key})));
?>"""
    return stub

def stub_ultra(content, header):
    """方案 4: 超高强度双层异或 + 乱码混淆"""
    
    # 层 1: 核心代码
    compressed = zlib.compress(content.encode('utf-8'))
    key1 = "".join(random.choice(string.ascii_letters) for _ in range(15))
    layer1_enc = xor_encrypt(compressed, key1)
    layer1_b64 = base64.b64encode(layer1_enc.encode('latin1')).decode('ascii')
    
    v1_code, v1_key, v1_res, v1_i = [generate_weird_name() for _ in range(4)]
    
    layer1_php = f"""
    ${v1_code}="{layer1_b64}";
    ${v1_key}="{key1}";
    ${v1_res}="";
    ${v1_code}=base64_decode(${v1_code});
    for(${v1_i}=0;${v1_i}<strlen(${v1_code});${v1_i}++){{
        ${v1_res}.=chr(ord(${v1_code}[${v1_i}])^ord(${v1_key}[${v1_i}%strlen(${v1_key})]));
    }}
    eval(gzuncompress(${v1_res}));
    """
    
    # 层 2: 外壳
    key2 = "".join(random.choice(string.digits) for _ in range(12))
    layer2_enc = xor_encrypt(layer1_php, key2)
    layer2_b64 = base64.b64encode(layer2_enc.encode('latin1')).decode('ascii')
    
    v2_code, v2_key, v2_out, v2_idx = [generate_random_name(10) for _ in range(4)]
    
    stub = f"""<?php
{header}
/* HIGH SECURITY ENCRYPTION - SDCZZ.COM */
${v2_code}="{layer2_b64}";
${v2_key}="{key2}";
${v2_out}="";
${v2_code}=base64_decode(${v2_code});
for(${v2_idx}=0;${v2_idx}<strlen(${v2_code});${v2_idx}++){{
    ${v2_out}.=chr(ord(${v2_code}[${v2_idx}])^ord(${v2_key}[${v2_idx}%strlen(${v2_key})]));
}}
eval(${v2_out});
?>"""
    return stub

# ==========================================
# 业务处理逻辑
# ==========================================

def process_file(input_file, output_file, mode, keep_comments, silent=False):
    """单个 PHP 文件处理"""
    if not os.path.exists(input_file):
        if not silent: print(f"[-] 错误: 文件 {input_file} 不存在")
        return False

    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            raw_content = f.read()
    except Exception as e:
        if not silent: print(f"[-] 读取文件失败: {e}")
        return False

    # 提取或生成版权注释
    header_comment = ""
    if keep_comments:
        header_comment = extract_doc_comment(raw_content)
    
    mode_map_cn = {'simple': '低', 'gzip': '中', 'xor': '高', 'ultra': '超高'}
    strength_cn = mode_map_cn.get(mode, '未知')

    if not header_comment:
        header_comment = f"/* sdczz.com 声达网络加密 强度: {strength_cn} */"

    clean_content = prepare_content(raw_content)

    if not silent:
        print(f"[*] 正在加密: {mode.upper()} (强度: {strength_cn})")

    try:
        if mode == 'simple':
            final_php = stub_simple(clean_content, header_comment)
        elif mode == 'gzip':
            final_php = stub_gzip(clean_content, header_comment)
        elif mode == 'xor':
            final_php = stub_xor(clean_content, header_comment)
        elif mode == 'ultra':
            final_php = stub_ultra(clean_content, header_comment)
        else:
            return False
            
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_php)
        if not silent: print(f"[+] 加密成功: {output_file}")
        return True
    except Exception as e:
        if not silent: print(f"[-] 处理出错: {e}")
        return False

def process_directory(input_dir, output_dir, mode, keep_comments):
    """递归文件夹批量处理"""
    if not os.path.exists(input_dir):
        print(f"[-] 目录不存在: {input_dir}")
        return

    mode_map_cn = {'simple': '低', 'gzip': '中', 'xor': '高', 'ultra': '超高'}
    strength_cn = mode_map_cn.get(mode, '未知')

    print(f"[*] 批量处理开始: {input_dir}")
    print(f"[*] 强度选择: {mode.upper()} ({strength_cn})")
    print("=" * 45)

    count_enc, count_copy, count_err = 0, 0, 0

    for root, dirs, files in os.walk(input_dir):
        rel_path = os.path.relpath(root, input_dir)
        target_path = os.path.join(output_dir, rel_path)
        
        if not os.path.exists(target_path):
            os.makedirs(target_path)
            
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_path, file)
            
            if file.lower().endswith('.php'):
                print(f"[*] 加密 PHP: {os.path.join(rel_path, file)}")
                if process_file(src_file, dst_file, mode, keep_comments, silent=True):
                    count_enc += 1
                else:
                    shutil.copy2(src_file, dst_file)
                    count_err += 1
            else:
                shutil.copy2(src_file, dst_file)
                count_copy += 1
                
    print("=" * 45)
    print(f"[OK] 任务完成! 加密:{count_enc} 复制:{count_copy} 失败:{count_err}")
    print(f"[*] 输出目录: {output_dir}")

# ==========================================
# 入口程序 (交互模式)
# ==========================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("==========================================")
        print("      声达网络 PHP 混淆加密工具 (sdczz.com)")
        print("      支持多强度加密、批量文件夹处理")
        print("==========================================")
        
        config = load_config()
        last_output_dir = config.get('last_output_dir', '')
        
        while True:
            file_path = input("\n[?] 请输入要加密的文件或文件夹路径 (可拖入): ").strip()
            if file_path.startswith('"') and file_path.endswith('"'):
                file_path = file_path[1:-1]
            if file_path: break
        
        is_dir = os.path.isdir(file_path)
        base_name = os.path.basename(file_path)
        
        # 智能建议输出路径
        if last_output_dir and os.path.isdir(last_output_dir):
            if is_dir:
                default_out = os.path.join(last_output_dir, base_name + "_encrypted")
            else:
                default_out = os.path.join(last_output_dir, "enc_" + base_name)
        else:
            default_out = file_path + "_encrypted" if is_dir else "encrypted.php"
                
        out_path = input(f"[?] 请输入输出路径 (回车默认: {default_out}): ").strip()
        if not out_path: out_path = default_out
            
        # 记录输出目录偏好
        try:
            current_out_dir = os.path.dirname(os.path.abspath(out_path))
            if current_out_dir != last_output_dir:
                save_config('last_output_dir', current_out_dir)
        except: pass
            
        print("\n加密强度选择:")
        print("  1. simple : [低]   - 纯 Base64")
        print("  2. gzip   : [中]   - Gzip 压缩 + Base64")
        print("  3. xor    : [高]   - 动态 XOR + 随机变量 (推荐)")
        print("  4. ultra  : [超高] - 双层加密 + 乱码混淆")
        
        mode_input = input("\n[?] 请选择强度 (输入序号 1-4 或名称, 默认 3): ").strip().lower()
        mode_map = {
            '1': 'simple', '2': 'gzip', '3': 'xor', '4': 'ultra',
            'simple': 'simple', 'gzip': 'gzip', 'xor': 'xor', 'ultra': 'ultra'
        }
        mode = mode_map.get(mode_input, 'xor')
        
        keep = input("[?] 是否保留原文件头部注释 (y/N): ").strip().lower()
        keep_comments = keep == 'y'
        
        if is_dir:
            process_directory(file_path, out_path, mode, keep_comments)
        else:
            process_file(file_path, out_path, mode, keep_comments)
        
        input("\n[OK] 处理完成，按回车键退出...")
        sys.exit(0)

    # 命令行模式 (用于自动化脚本)
    parser = argparse.ArgumentParser(description="声达网络 PHP 加密工具")
    parser.add_argument("input", help="输入路径")
    parser.add_argument("-o", "--output", help="输出路径")
    parser.add_argument("-m", "--mode", choices=['simple', 'gzip', 'xor', 'ultra'], default='xor')
    parser.add_argument("-k", "--keep-comments", action="store_true")
    
    args = parser.parse_args()
    if os.path.isdir(args.input):
        out = args.output if args.output else args.input + "_encrypted"
        process_directory(args.input, out, args.mode, args.keep_comments)
    else:
        out = args.output if args.output else "encrypted.php"
        process_file(args.input, out, args.mode, args.keep_comments)
import json
import os
from datetime import datetime

def remove_keys_with_arrow(json_data):
    """
    递归移除JSON数据中所有key包含"->"的键值对
    支持字典、列表嵌套结构
    """
    # 如果是字典，遍历并过滤key
    if isinstance(json_data, dict):
        # 过滤掉key包含"->"的项，同时递归处理每个value
        cleaned_dict = {}
        for key, value in json_data.items():
            if "->" not in key:
                cleaned_dict[key] = remove_keys_with_arrow(value)
        return cleaned_dict
    
    # 如果是列表，递归处理每个元素
    elif isinstance(json_data, list):
        return [remove_keys_with_arrow(item) for item in json_data]
    
    # 其他类型（字符串、数字、布尔、None）直接返回
    else:
        return json_data

def process_json_file(input_file, output_file=None, backup_original=True):
    """
    处理JSON文件，移除所有key包含"->"的键值对
    
    参数:
    input_file: 输入JSON文件路径
    output_file: 输出文件路径（默认覆盖输入文件）
    backup_original: 是否备份原始文件（默认True）
    """
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误：文件 {input_file} 不存在！")
        return False
    
    # 设置输出文件路径
    if output_file is None:
        output_file = input_file
    
    # 备份原始文件
    if backup_original and input_file == output_file:
        backup_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{input_file}.backup.{backup_suffix}"
        try:
            with open(input_file, 'rb') as src, open(backup_file, 'wb') as dst:
                dst.write(src.read())
            print(f"已备份原始文件到：{backup_file}")
        except Exception as e:
            print(f"警告：备份文件失败 - {e}")
            # 询问用户是否继续
            confirm = input("是否继续处理文件（可能会覆盖原始文件）？(y/n): ")
            if confirm.lower() != 'y':
                return False
    
    # 读取JSON文件
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"成功读取文件：{input_file}")
    except json.JSONDecodeError as e:
        print(f"错误：JSON格式无效 - {e}")
        return False
    except Exception as e:
        print(f"错误：读取文件失败 - {e}")
        return False
    
    # 处理数据（移除目标key）
    print("正在处理数据...")
    cleaned_data = remove_keys_with_arrow(data)
    
    # 写入处理后的文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # ensure_ascii=False 保留中文字符，indent=2 保持格式化
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
        print(f"处理完成！结果已保存到：{output_file}")
        return True
    except Exception as e:
        print(f"错误：写入文件失败 - {e}")
        return False

def main():
    # 示例用法：请根据实际需求修改以下参数
    INPUT_JSON_FILE = "./data/地点-坐标汇总.json"    # 输入JSON文件路径
    OUTPUT_JSON_FILE = None          # 输出文件路径（None表示覆盖输入文件）
    BACKUP_ORIGINAL = True           # 是否备份原始文件
    
    print("=== 开始处理JSON文件 ===")
    print(f"输入文件：{INPUT_JSON_FILE}")
    print(f"输出文件：{OUTPUT_JSON_FILE if OUTPUT_JSON_FILE else INPUT_JSON_FILE}")
    print(f"备份原始文件：{'是' if BACKUP_ORIGINAL else '否'}")
    print("-" * 50)
    
    success = process_json_file(INPUT_JSON_FILE, OUTPUT_JSON_FILE, BACKUP_ORIGINAL)
    
    if success:
        print("\n=== 处理完成 ===")
    else:
        print("\n=== 处理失败 ===")

if __name__ == "__main__":
    main()
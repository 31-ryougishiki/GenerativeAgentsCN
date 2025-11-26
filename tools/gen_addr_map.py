import json
import os
from typing import Dict, List, Tuple, Optional

# 定义数据类型：地点层级路径 -> 坐标列表（坐标为[int, int]）
LocationCoordDict = Dict[str, List[List[int]]]

def extract_location_coords_from_json(json_path: str) -> LocationCoordDict:
    """
    从单个JSON文件中提取地点层级路径及其对应的二维坐标
    地点路径规则：address数组按层级拼接（例：["星澜里2号", "浴室"] → "星澜里2号"、"星澜里2号->浴室"）
    """
    location_coords = {}
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 获取核心数据：tiles数组（包含coord和address）
        tiles = data.get('tiles', [])
        if not tiles:
            print(f"警告：{json_path} 中未找到 tiles 数组")
            return location_coords
        
        # 遍历每个tile，提取地点和坐标
        for tile_idx, tile in enumerate(tiles, 1):
            # 验证坐标（必须是长度为2的整数列表）
            coord = tile.get('coord', [])
            if not isinstance(coord, list) or len(coord) != 2 or not all(isinstance(c, int) for c in coord):
                print(f"警告：{json_path} 中 tile[{tile_idx}] 的 coord 格式无效（跳过）→ {coord}")
                continue
            
            # 验证地点（address必须是非空字符串数组）
            address = tile.get('address', [])
            if not isinstance(address, list) or len(address) == 0 or not all(isinstance(a, str) for a in address):
                continue  # 无有效地点的tile直接跳过
            
            # 生成地点层级路径（支持多层级，如"星澜里2号" → "星澜里2号->浴室"）
            current_path = []
            for level in address:
                current_path.append(level.strip())  # 去除空格
                full_path = "->".join(current_path)  # 拼接层级路径
                
                # 坐标去重（转为元组判断，避免重复添加相同坐标）
                coord_tuple = tuple(coord)
                if full_path not in location_coords:
                    location_coords[full_path] = []
                
                # 仅添加未存在的坐标
                if coord_tuple not in [tuple(c) for c in location_coords[full_path]]:
                    location_coords[full_path].append(coord.copy())
    
    except json.JSONDecodeError:
        print(f"错误：{json_path} 是无效的JSON文件（跳过）")
    except Exception as e:
        print(f"错误：处理 {json_path} 时失败 - {str(e)}")
    
    return location_coords

def merge_all_location_coords(root_dir: str) -> Tuple[LocationCoordDict, int]:
    """
    递归遍历目录及其所有子目录，批量处理所有JSON文件
    合并所有地点-坐标数据（自动去重）
    返回：(合并后的地点坐标字典, 处理的JSON文件总数)
    """
    all_location_coords = {}
    processed_files = 0
    
    # 递归遍历所有目录和子目录
    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            if filename.endswith('.json'):
                json_path = os.path.join(root, filename)
                processed_files += 1
                print(f"正在处理 [{processed_files}]：{json_path}")
                
                # 提取单个文件的地点坐标
                file_location_coords = extract_location_coords_from_json(json_path)
                
                # 合并到总结果（跨文件去重）
                for location_path, coords in file_location_coords.items():
                    if location_path not in all_location_coords:
                        all_location_coords[location_path] = []
                    
                    # 坐标去重（跨文件合并时避免重复）
                    existing_coords = [tuple(c) for c in all_location_coords[location_path]]
                    for coord in coords:
                        coord_tuple = tuple(coord)
                        if coord_tuple not in existing_coords:
                            all_location_coords[location_path].append(coord)
                            existing_coords.append(coord_tuple)
    
    return all_location_coords, processed_files

def print_location_coords(location_coords: LocationCoordDict):
    """
    格式化打印地点及其对应的坐标（按层级排序，清晰易读）
    """
    print("\n" + "="*80)
    print("所有地点及其对应二维坐标（按层级路径排序）")
    print("="*80)
    
    if not location_coords:
        print("未提取到任何地点-坐标数据")
        return
    
    # 按地点路径长度排序（短路径在前，即高层级在前），再按字母排序
    sorted_paths = sorted(
        location_coords.keys(),
        key=lambda x: (len(x.split('->')), x)
    )
    
    for i, location_path in enumerate(sorted_paths, 1):
        coords = location_coords[location_path]
        # 格式化坐标显示（如"[85, 12], [86, 12]"）
        coords_str = ", ".join([str(c) for c in coords])
        print(f"\n【{i}】地点路径：{location_path}")
        print(f"   对应坐标（共{len(coords)}个）：{coords_str}")

def save_location_coords_to_json(
    location_coords: LocationCoordDict,
    output_path: str = "地点-坐标汇总.json"
):
    """
    将提取的地点-坐标数据保存为JSON文件（结构化，便于后续使用）
    """
    # 按路径排序后保存（保持和打印一致的顺序）
    sorted_location_coords = dict(sorted(
        location_coords.items(),
        key=lambda x: (len(x[0].split('->')), x[0])
    ))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_location_coords, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到：{os.path.abspath(output_path)}")

if __name__ == "__main__":
    # -------------------------- 配置参数 --------------------------
    ROOT_DIRECTORY = "./data"  # 根目录（会递归查找所有子目录的JSON）
    OUTPUT_JSON = "地点-坐标汇总.json"  # 输出文件路径
    # --------------------------------------------------------------
    
    # 检查根目录是否存在
    if not os.path.exists(ROOT_DIRECTORY):
        print(f"错误：根目录 {ROOT_DIRECTORY} 不存在，请检查路径是否正确")
        exit(1)
    
    # 递归提取并合并所有地点-坐标
    print(f"开始递归查找 {ROOT_DIRECTORY} 下的所有JSON文件...")
    all_location_coords, processed_files = merge_all_location_coords(ROOT_DIRECTORY)
    
    # 格式化打印结果
    print_location_coords(all_location_coords)
    
    # 保存结果到JSON文件
    if all_location_coords:
        save_location_coords_to_json(all_location_coords, OUTPUT_JSON)
    else:
        print("\n未提取到有效数据，不生成输出文件")
    
    # 打印统计信息
    total_locations = len(all_location_coords)
    total_coords = sum(len(coords) for coords in all_location_coords.values())
    print(f"\n" + "-"*50)
    print(f"提取完成！统计信息：")
    print(f"- 处理JSON文件总数：{processed_files}")
    print(f"- 提取地点总数（含层级）：{total_locations}")
    print(f"- 提取坐标总数（去重后）：{total_coords}")
    print("-"*50)
import json
import os
import importlib.util
import requests
from http import HTTPStatus


def SAVE_INVITE_CODE(file_name, new_data):
    # 读取现有JSON文件（如果存在）
    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        # 如果文件不存在，创建所需目录并一个新的空JSON文件
        directory = os.path.dirname(file_name)
        if not os.path.exists(directory):
            os.makedirs(directory)
        data = {}

    # 检查是否已存在相同的键，如果存在，合并数据
    for key, value in new_data.items():
        if key in data:
            # 如果键已存在，将新数据合并到现有数据中
            data[key].update(value)
        else:
            # 如果键不存在，直接插入新数据
            data[key] = value

    # 将更新后的数据写入JSON文件
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)


# 将参数转换为字典
def create_dict_from_string(self, data_string):
    params = {}
    key_value_pairs = data_string.split(',')
    for pair in key_value_pairs:
        key, value = pair.split('=')
        params[key] = value
    return params


def compare_versions(local_version, server_version):
    local_parts = local_version.split('.')  # 将本地版本号拆分成数字部分
    server_parts = server_version.split('.')  # 将服务器版本号拆分成数字部分

    for l, s in zip(local_parts, server_parts):
        if int(l) < int(s):
            return True  # 当前版本低于服务器版本
        elif int(l) > int(s):
            return False  # 当前版本高于服务器版本

    # 如果上述循环没有返回结果，则表示当前版本与服务器版本的数字部分完全相同
    if len(local_parts) < len(server_parts):
        return True  # 当前版本位数较短，即版本号形如 x.y 比 x.y.z 低
    else:
        return False  # 当前版本与服务器版本相同或更高


def CHECK_UPDATE(local_version, server_version_url, server_script_url, script_filename):
    """
    检查版本并更新

    Args:
        local_version (str): 本地版本号
        server_version_url (str): 服务器版本文件地址
        server_script_url (str): 服务器脚本地址
        script_filename (str): 要保存的脚本文件名

    Returns:
        bool: 是否进行了更新操作
    """
    try:
        # 获取服务器版本号
        response = requests.get(server_version_url, verify=False)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        # print(response.text)
        server_version = response.text.strip()  # 去除首尾空格
        print(f'当前版本：【{local_version}】')
        print(f'服务器版本：【{server_version}】')

        if compare_versions(local_version, server_version):
            # 需要更新，下载服务器脚本
            AUTO_UPDATE = os.getenv("SCRIPT_UPDATE", "True").lower() != "false"
            # print(AUTO_UPDATE)
            if AUTO_UPDATE:
                print(">>>>>>>发现新版本的脚本，默认自动更新，准备更新...")
                print(">>>>>>>禁用更新请定义变量export SCRIPT_UPDATE = 'False'")
                response_script = requests.get(server_script_url, verify=False, timeout=10)
                response_script.raise_for_status()

                with open(script_filename, 'wb') as f:
                    f.write(response_script.content)
                print(f'{script_filename} 下载完成！')
                print(f'尝试运行新脚本')
                import subprocess, sys
                # 使用 sys.executable 获取 Python 可执行文件的完整路径
                python_executable = sys.executable
                subprocess.Popen([python_executable, script_filename])

            else:
                print(">>>>>>>发现新版本的脚本，您禁用了自动更新，如需启用请删除变量SCRIPT_UPDATE")
        else:
            print(f'当前版本高于或等于服务器版本')

    except requests.exceptions.RequestException as e:
        print(f'发生网络错误：{e}')

    except Exception as e:
        print(f'发生未知错误：{e}')

    return False  # 返回 False 表示没有进行更新操作


def get_AuthorInviteCode(url):
    global AuthorCode
    try:
        response = requests.get(url, verify=False, timeout=10)
        if response.status_code == 200:
            content = json.loads(response.text)
            AuthorCode = list(content.values())
            # print(f'获取到作者邀请码：{AuthorCode}')
            return AuthorCode
        else:
            print("无法获取文件。状态代码:", response.status_code)
            return {}

    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


def GET_TIPS(server_base_url):
    url = f'{server_base_url}tips.txt'
    try:
        response = requests.get(url, verify=False)
        # 检查响应的编码
        encoding = response.encoding
        # print(f"编码: {encoding}")
        # 设置正确的编码（根据实际情况可能需要调整）
        response.encoding = 'utf-8'
        # 读取内容
        content = response.text
        if 'code' in content:
            content = ''
    except:
        content = ''
        print('获取通知内容失败')
    print('***********通知内容************')
    print(content)
    print('***********通知内容************\n')


def CHECK_PARAMENTERS(index, input_string,required_parameters):
    # required_parameters = ['deviceid', 'jysessionid', 'shopid', 'memberid', 'access_token', 'sign']

    # 记录缺少的参数
    missing_parameters = []

    # 将输入字符串和参数列表中的所有字符都转换为小写
    input_string_lower = input_string.lower()
    required_parameters_lower = [param.lower() for param in required_parameters]

    # 判断字符串中是否包含所有必需的参数
    for param in required_parameters_lower:
        if param not in input_string_lower:
            missing_parameters.append(param)

    if missing_parameters:
        print(f"\n第【{index + 1}】个账号，缺少以下参数:【{missing_parameters}】")
        return False
    else:
        print(f"\n第【{index + 1}】个账号，URL包含所有必需的参数，开始执行脚本")
        return True


def QIANWEN(tongyiSysPromt, content, api_key):
    print('开始调用通义千问')
    # 检查dashscope库是否已安装
    if not importlib.util.find_spec("dashscope"):
        # 如果未安装，则尝试通过pip安装
        try:
            from pip._internal import main as pip_main
            pip_main(['install', 'dashscope'])
        except ImportError:
            # 对于老版本pip可能需要这样调用
            from pip import main as pip_main
            pip_main(['install', 'dashscope'])

    # 导入dashscope模块
    import dashscope
    dashscope.api_key = api_key
    response = dashscope.Generation.call(
        model='qwen-max',
        messages=[
            {"role": "system",
             "content": tongyiSysPromt},
            {"role": "user", "content": content}],
        seed=1234,
        top_p=0.8,
        result_format='message',
        enable_search=False,
        max_tokens=1500,
        temperature=1.0,
        repetition_penalty=1.0,
    )
    if response.status_code == HTTPStatus.OK:
        # print(response)
        video_info = response.output['choices'][0]['message']['content']
        print('通义生成【成功】！')
        return video_info
    else:
        print(f"无法解析通义返回的信息:{response}")
        return None

# 取环境变量，并分割
def ENV_SPLIT(input_str):
    if '&' in input_str:
        parts = []
        amp_parts = input_str.split('&')
        for part in amp_parts:
            if '#' in part:
                hash_parts = part.split('#')
                for hash_part in hash_parts:
                    parts.append(hash_part)
            else:
                parts.append(part)
        # print(parts)
        return(parts)

    elif '#' in input_str:
        hash_parts = input_str.split('#')
        # print(hash_parts)
        return(hash_parts)
    else:
        # print(input_str)
        return(input_str)




if __name__ == '__main__':
    input_str = "账号1&账号2#账号3&账号4&账号5#账号6"
    ENV_SPLIT(input_str)

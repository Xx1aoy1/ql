'''
!/usr/bin/python3
-- coding: utf-8 --
-------------------------------
✨✨✨ 朴朴超市脚本✨✨✨
✨ 功能：
      积分签到
      组队互助
✨ 抓包步骤：
      打开朴朴超市APP
      已登录先退出
      打开抓包
      登陆
      找https://cauth.pupuapi.com/clientauth/user/verify_login
      复制返回body中的refresh_token
      多个账号可清理APP数据进行换号别点退出否则token失效
✨ 设置青龙变量：
export PPCS= 'E0oXq3++6a4LG4xxxxxxxx'多账号#分割
export SCRIPT_UPDATE = 'False' 关闭脚本自动更新，默认开启
export QIANWEN_API_KEY = 'sk-xxxxxx'
✨ 多账号默认第一个账号与作者组队，其余互助
✨ 推荐定时：0 9 * * *
✨✨✨ @Author CHERWIN✨✨✨

cron "0 9 * * *" script-path=xxx.py,tag=匹配cron用
const $ = new Env('朴朴超市APP')
'''
import hashlib
import json
import os
import time
from os import  path
from sys import exit

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 尝试导入CHERWIN_TOOLS模块
CHERWIN_TOOLS = 'CHERWIN_TOOLS.py'
url = f'https://pan.ziyuand.cn/d/%E8%BD%AF%E4%BB%B6%E8%B5%84%E6%BA%90%E7%B1%BB/%E8%84%9A%E6%9C%AC/{CHERWIN_TOOLS}'
# 计算文件的SHA-256哈希值
def file_hash(filename):
    h = hashlib.sha256()
    with open(filename, 'rb') as file:
        while True:
            # 每次读取64KB的数据
            chunk = file.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()
try:
    # 检查本地文件是否存在并计算它的哈希值
    if os.path.isfile(CHERWIN_TOOLS):
        local_file_hash = file_hash(CHERWIN_TOOLS)
    else:
        local_file_hash = None
    # 从服务器获取文件
    response = requests.get(url,verify=False)
    if response.status_code == 200:
        # 计算服务器文件的哈希值
        server_file_hash = hashlib.sha256(response.content).hexdigest()
        # 对比本地文件和服务器文件的哈希值
        if local_file_hash != server_file_hash:
            print("*****本地CHERWIN_TOOLS模块与服务器文件有差异，正在下载新版本...")
            with open(CHERWIN_TOOLS, 'wb') as f:
                f.write(response.content)
            print("*****CHERWIN_TOOLS模块下载完成*****")
            try:
                # 保存文件后尝试重新导入模块
                import CHERWIN_TOOLS
                print("*****重新导入CHERWIN_TOOLS模块成功*****")
            except ImportError as ex:
                print("*****重新导入失败，错误：", ex)
                exit()
        else:
            print("*****本地CHERWIN_TOOLS模块已是最新*****")
            import CHERWIN_TOOLS
    else:
        print("*****无法从服务器获取文件，HTTP状态码为:", response.status_code)
except Exception as e:
    print("*****发生错误:", e)
    exit()


def load_send():
    global send, mg
    cur_path = path.abspath(path.dirname(__file__))
    if path.exists(cur_path + "/notify.py"):
        try:
            from notify import send
            print("加载通知服务成功！")
        except:
            send = False
            print("加载通知服务失败~")
    else:
        send = False
        print("加载通知服务失败~")


load_send()
send_msg = ''
inviteCode = {}

def Log(cont):
    global send_msg
    print(cont)
    send_msg += f'{cont}\n'

class PPCS:
    def __init__(self, refresh_token):
        self.UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x6309080f) XWEB/8555'
        self.refresh_token = refresh_token
        self.params = {
            'supplement_id': '',
            'lat_y': '',
            'lng_x': '',
        }
        self.getAccessToken_result = self.get_AccessToken()


    # 将参数转换为字典
    def create_dict_from_string(self, data_string):
        params = {}
        key_value_pairs = data_string.split(',')
        for pair in key_value_pairs:
            key, value = pair.split('=')
            params[key] = value
        return params

    def get_AccessToken(self):
        # Log('获取access_token')
        url = "https://cauth.pupuapi.com/clientauth/user/refresh_token"
        data = {
            "refresh_token": self.refresh_token
        }
        headers = {
            "User-Agent": "Pupumall/4.7.3;Android/11;dda37894d1b4c3ed09b6272c55b37cf2",
            "Content-Type": "application/json; charset=UTF-8",
            "Host": "cauth.pupuapi.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
        }

        try:
            response = requests.put(url, headers=headers, data=json.dumps(data), verify=False)
            response.raise_for_status()

            json_response = response.json()
            data = json_response.get('data', {})
            access_token = data.get('access_token', '')
            if access_token:
                self.access_token = f'Bearer '+access_token
                # print(access_token)
                return True
            else:
                return False
        except requests.exceptions.HTTPError as http_err:
            Log(f"HTTP请求出错: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            Log(f"网络连接出错: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            Log(f"请求超时: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            Log(f"出现了一个意外的请求错误: {req_err}")
        except json.JSONDecodeError as json_err:
            Log(f"JSON解码错误: {json_err}")
        return False

    def getUserInfo(self):
        global inviteCode
        Log(f'>>>>>>获取用户信息')
        url = "https://cauth.pupuapi.com/clientauth/user/info"
        headers = {
            "Host": 'cauth.pupuapi.com',
            "Authorization": self.access_token,
            "Content-Type": "application/json",
            'Accept': 'application/json, text/plain, */*',
            "User-Agent": self.UA,
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://servicewechat.com/wx122ef876a7132eb4/332/page-frame.html",
            'pp_storeid': '7f7adc3e-ffa5-473d-a082-9a346fdf929c',
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        # response = self.do_request(url, headers=headers,req_type='get')
        response = self.make_request(url,method='get',headers=headers)
        # print(response)
        if 'errcode' in response and response.get('errcode', '') == 0:
            data = response.get('data')
            self.user_id = data['user_id']
            phone_number = data['phone']
            self.phone = phone_number[:3] + '****' + phone_number[7:]
            self.invite_code = data['invite_code']
            Log(f'用户ID：【{self.user_id}】\n手机号：【{self.phone}】\n邀请码：【{self.invite_code}】')
            new_data = {
                self.user_id:
                    {
                        'phone': self.phone,
                        'invite_code': self.invite_code
                    }
            }
            CHERWIN_TOOLS.SAVE_INVITE_CODE("INVITE_CODE/PPCS_INVITE_CODE.json", new_data)
            return True
        else:
            Log(f'>获取用户信息失败')
            print(response)
            return False

    def signStu(self):
        Log(f'>>>>>>获取签到状态')
        url = "https://j1.pupuapi.com/client/game/sign/period_info"
        # response = self.do_request(url, req_type='get')
        response = self.make_request(url,method='get')
        # print(response)
        if 'errcode' in response and response.get('errcode', '') == 0:
            data = response.get('data')
            # 今日是否签到
            is_signed = data['is_signed']
            # 已签到天数
            signed_days = data['signed_days']
            # 签到详情
            sign_content = data['sign_content']
            # print(f'今日是否签到:【{is_signed}】,已签到天数:【{signed_days}】,签到详情:【{sign_content}】')
            if not is_signed:
                Log('今日未签到，开始执行签到')
                # print(f'已签到天数:【{signed_days}】\n签到详情:【{sign_content}】')
                self.sign()
            else:
                Log('今日已签到')
                Log(f'已签到天数:【{signed_days}】\n签到详情:【{sign_content}】')
            return True
        else:
            Log(f'>获取签到状态失败')
            print(response)
            return False

    def getCoinInfo(self):
        url = "https://j1.pupuapi.com/client/coin"
        # response = self.do_request(url, req_type='get')
        response = self.make_request(url,method='get')
        # print(response)
        if 'errcode' in response and response.get('errcode', '') == 0:
            data = response.get('data')
            # 当前朴分
            coin = data['balance']
            Log(f'当前朴分：【{coin}】')
        else:
            Log(f'>获取当前朴分失败')
            print(response)


    def make_request(self, url, method='post',headers={},params={}):
        if headers == {}:
            headers = {
                'Host': 'j1.pupuapi.com',
                'Authorization': self.access_token,
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': self.UA,
                'pp_storeid': '7f7adc3e-ffa5-473d-a082-9a346fdf929c',
                'Origin': 'https://ma.pupumall.com',
                'Sec-Fetch-Site': 'cross-site',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': 'https://ma.pupumall.com/',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'pp-os': '0'
            }
        if params =={}:
            params = self.params
        try:
            if method.lower() == 'get':
                response = requests.get(url, headers=headers, verify=False)
            elif method.lower() == 'post':
                response = requests.post(url, headers=headers, json=params, verify=False)
            else:
                raise ValueError("不支持的请求方法: " + method)

            return response.json()
        except requests.exceptions.RequestException as e:
            print("请求异常：", e)
        except ValueError as e:
            print("值错误或不支持的请求方法：", e)
        except Exception as e:
            print("发生了未知错误：", e)

    def sign(self):
        Log(f'>>>>>>开始签到')
        url = "https://j1.pupuapi.com/client/game/sign/v2?supplement_id="
        # 签到
        response = self.make_request(url,params={})
        # response = requests.post(url, headers=self.headers, params=self.params,verify=False).json()
        if 'errcode' in response and response.get('errcode', '') == 0:
            data = response.get('data')
            # 今日获得积分
            daily_sign_coin = data['daily_sign_coin']
            # 签到详情
            reward_explanation = data['reward_explanation']
            Log(f'>签到成功！获得积分:【{daily_sign_coin}】，{reward_explanation}')
            return True
        elif response.get('errcode', '') == 350011:
            Log(response.get('errmsg', ''))
            return False
        else:
            Log(f'>获取签到状态失败')
            print(response)
            return False

    # 发起组队
    def creatTeam(self):
        global inviteCode
        Log(f'>>>>>>开始发起组队')
        url = "https://j1.pupuapi.com/client/game/coin_share/team"
        response = self.make_request(url)
        # print(response)
        if 'errcode' in response and response.get('errcode', '') == 0:
            data = response.get('data')
            self.teamId = data
            Log(f'>发起组队成功，ID：【{data}】')
            new_data = {
                self.user_id:
                    {
                        'teamId': self.teamId
                    }
            }
            new_inviteCode = {self.phone:self.teamId}
            inviteCode[self.user_id]['teamId'] = self.teamId
            CHERWIN_TOOLS.SAVE_INVITE_CODE("INVITE_CODE/PPCS_INVITE_CODE.json", new_data)
            return True
        elif 'errcode' in response and response.get('errcode', '') != 0:
            Log(f'>发起组队失败:【{response.get("errmsg", "")}】')
        else:
            Log(f'>发起组队失败')
            print(response)
            return False
    # 组队
    def joinAuthorTeam(self):
        Log(f'>>>>>>第1个账号开始助力作者')
        if len(AuthorCode) > 0:
            for code in AuthorCode:
                print(code['teamId'])
                url = f"https://j1.pupuapi.com/client/game/coin_share/teams/{code['teamId']}/join"
                response = self.make_request(url)
                # print(response)
                if 'errcode' in response and response.get('errcode', '') == 0:
                    Log(f'>入队成功:【{code}】')
                    break
                elif 'errcode' in response and response.get('errcode', '') != 0:
                    Log(f'>入队失败:【{response.get("errmsg", "")}】')
                else:
                    Log(f'>入队失败')
                    print(response)
# 组队
    def joinTeam(self):
        global inviteCode
        Log(f'>>>>>>开始组队')
        with open('INVITE_CODE/PPCS_INVITE_CODE.json', 'r') as file:
            data = json.load(file)
        inviteCode = list(data.values())
        for code in inviteCode:
            url = f"https://j1.pupuapi.com/client/game/coin_share/teams/{code['teamId']}/join"
            response = self.make_request(url)
            # print(response)
            if 'errcode' in response and response.get('errcode', '') == 0:
                Log(f">入队成功:【{code['teamId']}】")
            elif 'errcode' in response and response.get('errcode', '') != 0:
                Log(f'>入队失败:【{response.get("errmsg", "")}】')
            else:
                Log(f'>入队失败')
                print(response)

    def main(self, indx):
        index = indx + 1
        Log(f"\n---------开始执行第{index}个账号>>>>>")
        if self.getAccessToken_result:
            print('成功获取了access token.')
            self.getUserInfo()
            self.signStu()
            self.getCoinInfo()
            return True
        else:
            Log( f'账号{indx} {CK_NAME}:【{self.refresh_token}】已失效请及时更新')
            send('朴朴超市账号失效通知', f'账号{indx} {CK_NAME}:【{self.refresh_token}】已失效请及时更新')
            return False

    def help(self, indx):
        if not self.getAccessToken_result:
            Log(f'账号{indx+1} {CK_NAME}:【{self.refresh_token}】已失效请及时更新')
            send('朴朴超市账号失效通知', f'账号{indx+1} {CK_NAME}:【{self.refresh_token}】已失效请及时更新')
            return False
        else:
            if indx == 0:
                Log('--------签到组队--------')
                self.joinAuthorTeam()
                Log('--------元宵灯谜组队--------')
                self.joinAuthorYuanxiaoTeam()
            else:
                Log('--------签到组队--------')
                self.joinTeam()
                Log('--------元宵灯谜组队--------')
                self.joinYuanxiaoTeam()
            return True

if __name__ == '__main__':
    APP_NAME = '朴朴超市'
    ENV_NAME = 'PPCS'
    CK_NAME = 'refresh_token'
    print(f'''
✨✨✨ 朴朴超市脚本✨✨✨
✨ 功能：
      积分签到
      组队互助
✨ 抓包步骤：
      打开朴朴超市APP
      已登录先退出
      打开抓包
      登陆
      找https://cauth.pupuapi.com/clientauth/user/verify_login
      复制返回body中的{CK_NAME}
      多个账号可清理APP数据进行换号别点退出否则token失效
✨ 设置青龙变量：
export {ENV_NAME}= 'E0oXq3++6a4LG4xxxxxxxx'多账号#分割
export SCRIPT_UPDATE = 'False' 关闭脚本自动更新，默认开启
✨ 多账号默认第一个账号与作者组队，其余互助
✨ 推荐定时：0 9 * * *
✨✨✨ @Author CHERWIN✨✨✨
        ''')
    local_script_name = os.path.basename(__file__)
    # print(local_script_name)
    # 检查更新
    local_version = '2024.02.23'  # 本地版本
    server_base_url = f"https://pan.ziyuand.cn/d/软件资源类/脚本/{APP_NAME}/"
    server_script_url = f"{server_base_url}{local_script_name}"
    server_version_url = f'{server_base_url}version.txt' # 服务器版本文件
    CHERWIN_TOOLS.GET_TIPS(server_base_url)
    CHERWIN_TOOLS.CHECK_UPDATE(local_version, server_version_url, server_script_url, local_script_name)
    AuthorInviteCodeUrl="https://yhsh.ziyuand.cn/PPCS_INVITE_CODE.json"
    AuthorCode = CHERWIN_TOOLS.get_AuthorInviteCode(AuthorInviteCodeUrl)
    # print(AuthorCode)
    info = ''
    ENV = os.environ.get(ENV_NAME)
    token = ENV if ENV else info
    if not token:
        print(f"未填写{ENV_NAME}变量\n青龙可在环境变量设置 {ENV_NAME} 或者在本脚本文件上方将{CK_NAME}填入info =''")
        exit()
    # parts = token.split('#')
    tokens = CHERWIN_TOOLS.ENV_SPLIT(token)
    if len(tokens) > 0:
        Log(f"\n>>>>>>>>>>共获取到{len(tokens)}个账号<<<<<<<<<<")
        for indx, info in enumerate(tokens):
            run = PPCS(info).main(indx)
            if run != True: continue
            time.sleep(1)
        Log(f"\n>>>>>>>>>>开始互助<<<<<<<<<<")
        for indx, info in enumerate(tokens):
            Log(f"\n********账号【{indx + 1}】开始互助********")
            run = PPCS(info).help(indx)
            if not run : continue
            time.sleep(1)

        send(f'{APP_NAME}挂机通知', send_msg)


import requests
from fake_useragent import UserAgent
from curl_cffi.requests import Session
import subprocess
from functools import partial
subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
from concurrent.futures import ThreadPoolExecutor, as_completed
import execjs
import threading
import time,os
import glob
import json
import time
from xtools import *
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger
from discord_tools import *
from decorators import *
# 获取当前脚本的绝对路径
current_script_path = os.path.abspath(__file__)
# 获取当前脚本的目录
current_script_directory = os.path.dirname(current_script_path)
ua=UserAgent()
load_dotenv()
PROXIES_TYPE=os.getenv('PROXIES_TYPE')
USE_PROXIES=os.getenv('USE_PROXIES')
PROXIES = {
    "http": f"{PROXIES_TYPE}://%(user)s:%(pwd)s@%(proxy)s/" % {"user": os.getenv('PROXIES_USERNAME'), "pwd": os.getenv('PROXIES_PASSWORD'), "proxy": os.getenv('PROXIES_TUNNEL')},
    "https": f"{PROXIES_TYPE}://%(user)s:%(pwd)s@%(proxy)s/" % {"user": os.getenv('PROXIES_USERNAME'), "pwd": os.getenv('PROXIES_PASSWORD'), "proxy": os.getenv('PROXIES_TUNNEL')}
}
class SuoerFiBotManager:
    def __init__(self,proxies=None):
        self.proxies=proxies
        self.tokens=self._read_all()
        self.wallets=self._read_all(type='wallets')
        self._init_js()
        self.lock=threading.Lock()
        
    def _init_js(self):
        js_list=glob.glob(os.path.join(current_script_directory,'js','*'))
        self.js_mapping={}
        for js in js_list:
            with open(js,'r',encoding='utf8') as f:
                name=js.split('\\')[-1].split('.')[0]
                js_str=f.read()
                js=execjs.compile(js_str)
                self.js_mapping[name]=js
    def _read_all(self,type='tokens'):
        try:
            tokens=open(os.path.join(current_script_directory,f'{type}.json'),'r').read()
            return json.loads(tokens)
        except:
            return []
    def _save(self,type='tokens'):
        with open(os.path.join(current_script_directory,f'{type}.json'),'w') as f:
            if type=='tokens':
                tokens=json.dumps(self.tokens,ensure_ascii=False)
                f.write(tokens)
            elif type=='wallets':
                wallets=json.dumps(self.wallets,ensure_ascii=False)
                f.write(wallets)
    def _create_wallet(self):
        wallet=self.js_mapping['create'].call('create')
        with self.lock:
            self.wallets.append(wallet)
        
    def run(self,wallet,token):
        cls=SuoerFiBot(wallet=wallet,proxies=self.proxies,Twitter_Token=token['Twitter_Token'],Discord_Token=token['Discord_Token'])
        with self.lock:
            wallet['points']=cls.run()        
    def run_all(self,max_workers=1):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.run, wallet,self.tokens[index]) for index,wallet in enumerate(self.wallets)]
            for future in as_completed(futures):
                try:
                    data = future.result()
                except Exception as e:
                    logger.error(f"初始化钱包失败: {e}")    
        self._save(type='wallets')
    def show_points(self):
        print_str=f'\n{"钱包地址":<75}\t{"积分":<10}\n'
        for wallet in self.wallets:
            print_str+=f'{wallet.get("address"):<75}\t{wallet.get("points","未初始化"):<10}\n'
        logger.success(print_str)
    def create_wallet_by_num(self,num=1,max_workers=10):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self._create_wallet) for i in range(num)]
            for future in as_completed(futures):
                try:
                    data = future.result()
                except Exception as e:
                    logger.error(f"创建钱包失败: {e}")
                    return
            logger.success(f"创建钱包成功-数量：{num}")  
        self._save(type='wallets')
    def menu(self):
        print("*"*10+'SuperFiBot'+"*"*10) 
        print(f'{"1.创建钱包":^20}') 
        print(f'{"2.查询积分":^20}') 
        print(f'{"3.脚本启动":^20}') 
    def start(self):
        while True:
            self.menu()
            choice=input('请输入功能选项：')
            if choice=='1':
                os.system('cls')
                num=int(input('请输入数量：'))
                self.create_wallet_by_num(num)
                os.system('pause')
            elif choice=='2':
                os.system('cls')
                self.show_points()
                os.system('pause')
            elif choice=='3':
                os.system('cls')
                self.run_all()
                os.system('pause')
            else:
                os.system('cls')
                logger.error('没有该选项')
                os.system('pause')
            os.system('cls')
class SuoerFiBot:
    def __init__(self,wallet:dict,proxies=None,Twitter_Token=None,Discord_Token=None) -> None:
        self.wallet=wallet
        self.address=wallet.get('address')
        self.Twitter_Token=Twitter_Token
        self.points=None
        self.Discord_Token=Discord_Token
        
        self.defualt_cookies = {
            '_ga': 'GA1.1.533581549.1728363001',
            '_ga_ZW2GRGPR2S': 'GS1.1.1728451475.6.1.1728451926.0.0.0',
        }
        self.defualt_headers={
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept, POST, GET, PATCH',
            'Access-Control-Allow-Origin': '*',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            # Already added when you pass json=
            # 'Content-Type': 'application/json',
            'Origin': 'https://zaar.superfi.gg',
            'Pragma': 'no-cache',
            'Referer': 'https://zaar.superfi.gg/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': ua.chrome,
            'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'timeout': '60000',
            'x-frame-options': 'DENY',
        }
        if proxies:
            self.session=Session(timeout=120,impersonate='edge99',headers=self.defualt_headers,cookies=self.defualt_cookies,proxies=proxies)
        else:
            self.session=Session(timeout=120,impersonate='edge99',headers=self.defualt_headers)
        self._init_js()
        self.proxies=proxies
        self._init_account()
    def _sign_message(self,wif, message, type='bip322-simple'):
        # 定义要执行的命令
        command = ["node", os.path.join(current_script_directory,'js',"sign.js"), wif, message, type]
        try:
            # 执行命令并捕获输出
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # 检查是否有错误输出
            if result.returncode != 0:
                print(f"Error: {result.stderr.strip()}")
                return None
            
            # 返回签名结果
            return result.stdout.strip()
    
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    def _init_account(self):
        try:
            self.Discord=Discord_Sync(self.Discord_Token,proxies=self.proxies)
            self.Twitter=Twitter_Sync(self.Twitter_Token,proxies=self.proxies)
        except Exception as e:
            logger.error(f'初始化社交账户失败：{e},token:{token}')
            self._init_account()
    def _init_js(self):
        js_list=glob.glob(os.path.join(current_script_directory,'js','*'))
        self.js_mapping={}
        for js in js_list:
            with open(js,'r',encoding='utf8') as f:
                name=js.split('\\')[-1].split('.')[0]
                js_str=f.read()
                js=execjs.compile(js_str)
                self.js_mapping[name]=js
    def get_x_signature(self):
        data=self.js_mapping['get_x_signature'].call('get_x_signature')
        return data
    def get_x_signature_join(self):
        data=self.js_mapping['get_x_signature'].call('get_x_signature_join')
        return data
    def get_x_signature_quest(self,quest_id):
        data=self.js_mapping['get_x_signature'].call('get_x_signature_quest',quest_id)
        return data
    def get_x_signature_nonce(self):
        data=self.js_mapping['get_x_signature'].call('get_x_signature_nonce',self.address)
        return data
    def get_x_signature_login(self,nonce,signature):
        data=self.js_mapping['get_x_signature'].call('get_x_signature_login',self.address,nonce,signature)
        return data
    def http(self,url,type:str='POST',data=None):
        count=3
        while count>0:
            try:
                if type.upper()=="GET":
                    response = self.session.get(url,params=data,timeout=10)
                elif type.upper()=="POST":
                    response = self.session.post(url,json=data,timeout=10)
                elif type.upper()=="PUT":
                    response = self.session.put(url,json=data,timeout=10)  
                elif type.upper()=="DELETE":
                    response = self.session.delete(url,json=data,timeout=10)  
                else:
                    raise ValueError(f'不支持{type}')
                try:
                    resp=response.json()
                except:
                    raise ValueError(response.text)
                return resp
            except:
                pass
            count-=1
            return self.http(url,type,data)
            
    def _is_expired(self,time:str):
        t=int(time)/1000
        now=datetime.now()
        expires=datetime.fromtimestamp(t)
        return now>expires
    @print_logging('获取nonce')
    def get_nonce(self)->dict:
        json_data = {
            'address': self.address,
        }
        x_signature=self.get_x_signature_nonce()
        self.session.headers.update({'X-Signature': x_signature[1]})
        self.session.headers.update({'X-Timestamp': x_signature[0]})
        response = self.http('https://zaar.superfi.gg/superstellar-api/v1/wallet/login/nonce',type='POST',data=json_data)
        assert response.get('nonce'),f'请求失败，resp:{response}'
        return response
    @print_logging('获取社交账户数据')
    def get_me(self)->dict:
        x_signature=self.get_x_signature()
        self.session.headers.update({'X-Signature': x_signature[1]})
        self.session.headers.update({'X-Timestamp': x_signature[0]})
        response = self.http('https://zaar.superfi.gg/superstellar-api/v1/account/me',type='GET')
        return response
    @print_logging('登录')
    def login(self):
        WIF=self.wallet.get('WIF')
        assert WIF,'未找到该钱包'
        nonce=self.get_nonce()
        message=nonce.get('sign_message')
        signature=self._sign_message(WIF,message,'bip322-simple')
        json_data = {
            'address': self.address,
            'nonce':nonce.get('nonce'),
            'signature':signature
        }
        x_signature=self.get_x_signature_login(nonce.get('nonce'),signature)
        self.session.headers.update({'X-Signature': x_signature[1]})
        self.session.headers.update({'X-Timestamp': x_signature[0]})
        response = self.http('https://zaar.superfi.gg/superstellar-api/v1/wallet/ordzaar/login', data=json_data)
        assert response.get('access_token'),f'请求失败，resp:{response}'
        self.session.headers.update({'Authorization': response.get('access_token')})
        return True
        
    def link_Twitter(self):
        x_signature=self.get_x_signature()
        self.session.headers.update({'X-Signature': x_signature[1]})
        self.session.headers.update({'X-Timestamp': x_signature[0]})
        response = self.http('https://zaar.superfi.gg/superstellar-api/v1/account/connect-twitter?next=https://zaar.superfi.gg/', type='GET')
        url=response.get('url')
        assert url,f'请求失败，resp:{response}'
        connect_params={
            'client_id' :get(get(url.split('client_id='),1).split('&')),
            'state' : get(get(url.split('state='),1).split('&')),
            'scope':get(get(url.split('scope='),1).split('&')),
            'code_challenge' : get(get(url.split('code_challenge='),1).split('&')),
            'response_type' : get(get(url.split('response_type='),1).split('&')),
            'code_challenge_method' : get(get(url.split('code_challenge_method='),1).split('&')),
            'redirect_uri':get(get(url.split('redirect_uri='),1).split('&')),
        }
        self.Twitter.twitter_authorizeV2(**connect_params)
    def link_Discord(self):
        x_signature=self.get_x_signature()
        self.session.headers.update({'X-Signature': x_signature[1]})
        self.session.headers.update({'X-Timestamp': x_signature[0]})
        response = self.http('https://zaar.superfi.gg/superstellar-api/v1/account/connect-discord?next=https://zaar.superfi.gg/', type='GET')
        url=response.get('url')
        connect_params={
            'client_id' :get(get(url.split('client_id='),1).split('&')),
            'state' : get(get(url.split('state='),1).split('&')),
            'scope':get(get(url.split('scope='),1).split('&')),
            'response_type' : get(get(url.split('response_type='),1).split('&')),
            'redirect_uri':get(get(url.split('redirect_uri='),1).split('&')),
        }
        
        self.Discord.Discord_authorizeV2(**connect_params)
        self.join()
    @print_logging('账号激活')
    def join(self):
        x_signature=self.get_x_signature_join()
        self.session.headers.update({'X-Signature': x_signature[1]})
        self.session.headers.update({'X-Timestamp': x_signature[0]})
        json_data = {
            'project': 'ordzaar',
        }
        response=self.http('https://zaar.superfi.gg/superstellar-api/v1/quest/ordzaar/join',type='post',data=json_data)
        assert response.get('success'),f'请求失败：resp:{response}'
    @print_logging('账号签到')
    def checkin(self):
        x_signature=self.get_x_signature()
        self.session.headers.update({'X-Signature': x_signature[1]})
        self.session.headers.update({'X-Timestamp': x_signature[0]})
        json_data = {
        }
        response=self.http('https://zaar.superfi.gg/superstellar-api/v1/account/ordzaar/check-in',type='post',data=json_data)
        if 'Checked in today' in str(response):
            raise Exception('今天已签到')
        assert response.get('points'),f'请求失败：resp:{response}' 
        return response.get('points')
    @print_logging('获取用户信息')
    def dashboard(self):
        x_signature=self.get_x_signature()
        self.session.headers.update({'X-Signature': x_signature[1]})
        self.session.headers.update({'X-Timestamp': x_signature[0]})
        
        response=self.http('https://zaar.superfi.gg/superstellar-api/v1/quest/ordzaar/dashboard',type='get')
        self.points=response.get('points')
        assert response.get('quests'),f'请求失败：resp:{response}'
        return response.get('quests',{}).get('quest',[])
    def start_quest(self,quest_id):
        x_signature=self.get_x_signature_quest(quest_id)
        self.session.headers.update({'X-Signature': x_signature[1]})
        self.session.headers.update({'X-Timestamp': x_signature[0]})
        json_data = {
            'quest_id':quest_id
        }
        response=self.http('https://zaar.superfi.gg/superstellar-api/v1/quest/ordzaar/start',type='post',data=json_data)
        assert 'success' in str(response),f'请求失败：resp:{response}'

        return response.get('success')
    def claim_quest(self,quest_id):
        time.sleep(31)
        x_signature=self.get_x_signature_quest(quest_id)
        self.session.headers.update({'X-Signature': x_signature[1]})
        self.session.headers.update({'X-Timestamp': x_signature[0]})
        json_data = {
            'quest_id':quest_id
        }
        response=self.http('https://zaar.superfi.gg/superstellar-api/v1/quest/ordzaar/claim',type='post',data=json_data)
        if not response.get('success'):
            logger.warning(f'address:{self.address}-任务id:{quest_id}-执行失败，重试中...')
        return response.get('success')
    def do_quest(self,quest):
        quest_id=quest.get('id')
        prefix_name=quest.get('url').split('/')[-1]
        if 'Follow' in quest.get('title'):
            try:
                self.Twitter.create(prefix_name)
            except Exception as e:
                logger.error(f'address:{self.address}-任务id:{quest_id}-执行失败-error:{e}')

        elif 'Like & RT' in quest.get('title'):
            try:
                self.Twitter.like(prefix_name)
                self.Twitter.retweet(prefix_name)
            except Exception as e:
                logger.error(f'address:{self.address}-任务id:{quest_id}-执行失败-error:{e}')
        elif 'Join' in quest.get('title'):
            pass

    def claim_quests(self):
        quests=self.dashboard()
        for quest in quests:
            if not quest.get('claimed'):
                
                quest_id=quest.get('id')
                logger.info(f'address:{self.address}-任务id:{quest_id}-开始执行')
                # 真做就开启
                # self.do_quest(quest)
                count=10
                self.start_quest(quest_id)
                while count>0:
                    if self.claim_quest(quest_id):
                        logger.success(f'address:{self.address}-任务id:{quest_id}-执行成功')
                        break
                    count-=1
                time.sleep(3)
                self.dashboard()
            time.sleep(3)

    def run(self):
        self.login()
        info=self.get_me()
        if not info.get('twitter_username'):
            assert self.Twitter_Token,'推特_token为空'
            self.link_Twitter()
        if not info.get('discord_username'):
            assert self.Discord_Token,'DC_token为空'
            self.link_Discord()
            twitter=f'The first-ever SocialFi community for $ZAAR on BTC Runes!   Join the $ZAAR movement and be part of the Token Launch this October!   💾 Get started now: https://zaar.superfi.gg\n\n@Ordzaar\n@OdinSwap\nPowered by\n@SuperstellarBTC\n\n{str(uuid.uuid4())}'
            self.Twitter.create_twitter(twitter)
        self.checkin()
        self.claim_quests()
        self.dashboard()
        return self.points
if __name__=='__main__':

    cls=SuoerFiBotManager(PROXIES)
    
    cls.start()

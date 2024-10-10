from fake_useragent import UserAgent
from curl_cffi.requests import Session
from loguru import logger
import time
import urllib.parse
ua=UserAgent()
class Discord_Sync:
    def __init__(self, auth_token,proxies=None):
        self.auth_token = auth_token
        defaulf_cookies = {
             '__dcfduid': '3d140d46d98711eebab5628f4db44770',
            '__sdcfduid': '3d140d46d98711eebab5628f4db4477037ec5e693d8df63143030b8c7a6f18c1f2c7992ba4eed1ac52f472f0e14d2230',
            '_ga': 'GA1.1.1892447230.1726278577',
            '_ga_YL03HBJY7E': 'GS1.1.1726278577.1.1.1726278595.0.0.0',
            'locale': 'zh-CN',
            '_gcl_au': '1.1.2053326885.1726278823',
            '_cfuvid': '6OfqLdiT7YMf2xQ8H77iRt2Bm2mJ_7v8QfMl5cOr17w-1728529581965-0.0.1.1-604800000',
            'cf_clearance': 'eIKWWFmw01Q8ojymWZIrt0yktm9DmBXDV6W9zba2_3c-1728529594-1.2.1.1-ycvJ1UVtNe5stNeqmkcMyM.eFt6T8kW8IAVDyWFOLV1RiDM1aBFaVzHylYPxc_zRcC8z5fYdhPipzn.Uq5HcX7bxBVaWvaiyjOiSA59Iu4grU9njEprHYitZgJRkjVa60ddNcuISWM1clr7GVBIcrP91CmEav.fBKTwj5_vos0CbaPX4oW..4iYFAkIZMAhHdYrZPZQRfghE390YpbNkvoRjeagHKV01NAPiBR7AMDCx_mq37inFUgswTfHyRsBvB0NlDwnRx.qD.yrwG.oqXcixRNjimb1E4mjgfBcCWFl7zKHbhOxqexwClL7LFnZIUCt582d.EmXG5m1kMWxDVSnaelii5hwZWgm6jNyhF4s7fbnK7l7eIq89RwSUGGLD2E2nFxSImBdza1aNs_e4Hw',
            'OptanonConsent': 'isIABGlobal=false&datestamp=Thu+Oct+10+2024+11%3A06%3A34+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=6.33.0&hosts=&landingPath=https%3A%2F%2Fdiscord.com%2F&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1',
            '_ga_Q149DFWHT7': 'GS1.1.1728529595.1.0.1728529607.0.0.0',
            '__cfruid': 'e54bfe3eabe5032c48af7cba343ce579d4bdf1bc-1728529886'
        }
        defaulf_headers = {
            "authority": "x.com",
            "origin": "https://x.com",
            "x-Discord-active-user": "yes",
            "x-Discord-client-language": "en",
            "authorization": auth_token,
            "user-agent":ua.edge,
            'Origin': 'https://discord.com',
            'Pragma': 'no-cache',
            'Referer': 'https://discord.com/oauth2/authorize?client_id=1237047186513072168&redirect_uri=https%3A%2F%2Fapi.superstellar.world%2Fapi%2Fv1%2Faccount%2Fconnect-discord%2Fcallback&response_type=code&scope=identify+guilds+guilds.members.read&state=8d690ab0051758bf4bb7d8a4672c78d00c9405bcc45619d655e50f4b55b8195e',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Debug-Options': 'bugReporterEnabled',
            'X-Discord-Locale': 'zh-CN',
            'X-Discord-Timezone': 'Asia/Shanghai',
            'sec-ch-ua': '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        if proxies:
            self.Discord = Session(headers=defaulf_headers, cookies=defaulf_cookies, timeout=120,impersonate='edge99',proxies=proxies)
        else:
            self.Discord = Session(headers=defaulf_headers, cookies=defaulf_cookies, timeout=120,impersonate='edge99')
        self.auth_code = None
        self.auth_success = False  # 增加标志位记录授权是否成功
    def get_auth_codeV2(self, client_id, state, redirect_uri,scope,integration_type='0',response_type='code'):
        # 如果已经授权成功，直接返回 True，不再进行授权
        if self.auth_success:
            logger.info(f'{self.auth_token} 已成功授权，跳过重新授权')
            return True

        try:
            params = {
                'integration_type': urllib.parse.unquote(integration_type),
                'client_id': urllib.parse.unquote(client_id),
                'redirect_uri': urllib.parse.unquote(redirect_uri),
                'response_type': urllib.parse.unquote(response_type),
                'scope': urllib.parse.unquote(scope).replace('+',' '),
                'state': state
            }
            
            response = self.Discord.get('https://discord.com/api/v9/oauth2/authorize', params=params)
            if "code" in response.json() and response.json()["code"] == 353:
                self.Discord.headers.update({"x-csrf-token": response.cookies["ct0"]})
                logger.warning(f'{response.json()}')
                return self.get_auth_codeV2(client_id, state, redirect_uri,scope,integration_type,response_type)
            elif response.status_code == 429:
                time.sleep(5)
                return self.get_auth_codeV2(client_id, state,redirect_uri,scope,integration_type,response_type)
            elif response.status_code == 200:
                self.auth_code = response.json()
                params.pop('integration_type')
                return params
            logger.error(f'{self.auth_token} 获取auth_code失败')
            return False
        except Exception as e:
            logger.error(e)
            return False
    def Discord_authorizeV2(self, client_id, state, redirect_uri,scope,integration_type='0',response_type='code'):
        # 如果已经授权成功，直接返回 True，不再进行授权
        if self.auth_success:
            logger.info(f'{self.auth_token} 已成功授权，跳过重新授权')
            return True
        try:
            params=self.get_auth_codeV2(client_id, state,redirect_uri,scope,integration_type,response_type)
            if not params:
                return False
            json_data = {
                'permissions': '0',
                'authorize': True,
                'integration_type': 0,
                'location_context': {
                    'guild_id': '10000',
                    'channel_id': '10000',
                    'channel_type': 10000,
                },
            }
            response = self.Discord.post('https://discord.com/api/v9/oauth2/authorize', json=json_data,params=params)
            if 'location' in response.text:
                self.auth_success = True  # 授权成功，设置标志位
                url=response.json().get('location')
                response = self.Discord.get(url)
                logger.success(f'{self.auth_token} Discord授权成功')
                return True
            elif response.status_code == 429:
                time.sleep(5)
                return self.Discord_authorizeV2(client_id, state,redirect_uri,scope,integration_type,response_type)
            logger.error(f'{self.auth_token} Discord授权失败')
            return False
        except Exception as e:
            logger.error(f'{self.auth_token} Discord授权异常：{e}')
            return False
def get(li:list,index:int=0):
    if len(li)>index:
        return li[index]
    else:
        return ""
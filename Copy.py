from bs4 import BeautifulSoup
import captcha_test
import CSDN_OCR
import requests
import json
import time
import execjs
import re
import urllib
import os

# 全局参数
cookies = "preview_hidden=0; FEED_NEW_VERSION_7130177=1; " \
		  "UM_distinctid=16c0a179d9a202-00ff9970083d5f-c343162-189420-16c0a179d9ba7d; FEED_NEW_VERSION_11887100=1; " \
		  "__SDID=32a7d854ba36e6af; analytics=b1f4e5c43a3d945d; " \
		  "yd_cookie=0d57c30a-cc0a-43a6563366d9896176feb7a6645a9895cbbd; " \
		  "_ydclearance=6a3c546f8e9ea03c46001647-43b8-4800-92c8-d27b191c6659-1570102092; " \
		  "YB_SSID=d86cca437c8f1feacff03c4823ba6c1f; CNZZDATA1253488264=1474242759-1542784100-null%7C1570091073; " \
		  "_cnzz_CV1253488264=%E5%AD%A6%E6%A0%A1%E9%A1%B5%E9%9D%A2%7C%3A%2FIndex%2FLogin%2Findex%7C1570095214636%26" \
		  "%E5%AD%A6%E6%A0%A1%E5%90%8D%E7%A7%B0%7C%E5%85%B6%E4%BB%96%7C1570095214636 "

session = ""
Name = ""
Channel_id = ""
User_id = ""  # 就是userid
Nick = ""


def login(name, username, password,):
	# 全局变量声明
	global Name
	global session
	Name = name
	session = requests.session()

	header = get_html_header("https://www.yiban.cn/login")
	# print(header)
	r = session.get("https://www.yiban.cn/login", headers=header)
	soup = BeautifulSoup(r.text, "html.parser")
	ul = soup.find("ul", id="login-pr")
	# 从html当中获取私钥
	try:
		data_keys = ul['data-keys']
		# 从html当中获取时间
		data_keys_time = ul['data-keys-time']
		code = ""
		# 获取到验证码
		encrypt_password = password
		login_json = json.loads(login_request(username, encrypt_password, code, data_keys_time))
		# print("login_json")
		# 获取到返回的json数据
		if login_json['code'] == 200:
			start(login_json,)
		else:
			if login_json['code'] == '711':
				code = wirte_code("yanzhengma.jpg")
				print(Name + "--使用了验证码，验证码是:", str(code))
				if code == 0:
					login(name, username, password,)
					return
				else:
					login_json = json.loads(login_request(
						username, encrypt_password, code, data_keys_time))
				if login_json['code'] == '201':
					login(name, username, password,)
					return
				elif login_json['code'] == 200:
					start(login_json)
					return
				else:
					print(Name + "--错误码:", login_json['code'], " 原因:", login_json['message'])
					print("--------------分---割---线--------------")
					session.close()
			else:
				print(Name + "--错误码:", login_json['code'], " 原因:", login_json['message'])
				print("--------------分---割---线--------------")
				session.close()
				# print(r.text)
	except TypeError as e:
		f = open('1.html', 'wb')
		text = r.content
		f.write(text)
		f.close()
		print(Name + "--出错了")
		print("--------------分---割---线--------------")
		print(e)
		login(name, username, password,)
		session.close()
		pass


def get_html_header(url):
	res = requests.get(url)
	if res.status_code == 200:
		header = {"cookie": str(res.cookies.get_dict())}
		return header
	soup_script = BeautifulSoup(res.text, "html.parser")
	script = soup_script.find("script")
	scriptStr = script.text
	fun_str = re.search(r'function (..)', scriptStr).group(1)
	param = scriptStr[re.search(fun_str + "\(", scriptStr).end():re.search("....200", scriptStr).start()]
	scriptStr = re.sub(r'window.onload=setTimeout................', "", scriptStr)
	scriptStr = re.sub(r'eval."qo=eval;qo.po.;".;', "return po;", scriptStr)
	ctx = execjs.compile(scriptStr)
	fun_res = ctx.call(fun_str, param)
	cookies = fun_res.replace("document.cookie='", "")
	cookies = cookies.replace("'; window.document.location=document.URL", "")
	header = {"cookie": cookies}
	# print("get 到了cookies")
	return header


def cookie2session(cookies):
	if cookies == "":
		return session
	for i in cookies:
		cookie = {'name': i['name'].replace(" ", ""), 'value': i["value"]}
		session.cookies.set(cookie.get("name"), cookie.get("value"))
	# print("session的cookie已装填好准备签到")
	return session


def ParseCookiestr(cookie_str):
	cookielist = []
	# print(cookie_str,"this is str")
	if cookie_str == "{}":
		return cookielist
	for item in cookie_str.split(';'):
		cookie = {}
		itemname = item.split('=')[0]
		iremvalue = item.split('=')[1]
		cookie['name'] = itemname
		cookie['value'] = urllib.parse.unquote(iremvalue)
		cookielist.append(cookie)
	return cookielist


def login_request(username, encrypt_password, code, data_keys_time):
	form_data = {
		'account': username,
		'password': encrypt_password,
		'captcha': code,
		'keysTime': data_keys_time
	}
	# print(form_data)
	cookie_str = get_html_header("https://www.yiban.cn/login/doLoginAjax")
	# print(cookie_str, "143")
	cookies = ParseCookiestr(cookie_str=cookie_str.get("cookie"))
	session = cookie2session(cookies)
	r = session.post("https://www.yiban.cn/login/doLoginAjax",
					 data=form_data, allow_redirects=False)
	# print(r.text)
	return r.text


# 验证码保存
def wirte_code(saveUrl):
	r = session.get("https://www.yiban.cn/captcha/index?" +
					(str(int(time.time()))))
	with open(saveUrl, 'wb') as f:
		f.write(r.content)
	captcha_test.automation(r'yanzhengma.jpg')
	code = CSDN_OCR.Recognise(r'transfered_image.png')
	# code = quote(code, safe=string.printable)
	return code


def start(login_json,):
	os.system('cls')
	print(Name + "--模拟登陆成功")
	App_Vote()
	print(Name + "--执行完毕")
	print("--------------分---割---线--------------")
	session.close()


def App_Vote():
	#暂时写死
	Vote_Data = {
		"App_id": 780382,
		"Vote_id": 127102,
		"VoteOption_id[]": 1753786
	}
	r=session.post("https://q.yiban.cn/vote/insertBoxAjax",data=Vote_Data,timeout=5)
	print(Name+"--轻应用投票成功！")

"""登陆时调用的函数。可以从这里使用login开始调试"""
#login("杨永杰","13008157173", "123abc")


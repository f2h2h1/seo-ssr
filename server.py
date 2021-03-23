# -*- coding: UTF-8 -*-
from playwright.sync_api import sync_playwright
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from urllib import request
from urllib import response
import re
import os
import sys
import getopt
import configparser
from socketserver import ThreadingMixIn
import dns.resolver
import platform

class ThreadingHttpServer(ThreadingMixIn, HTTPServer):
	pass

def getSourceCode(url, ua):
	with sync_playwright() as p:

		windowSize = {'width': pc_window_w, 'height': pc_window_h}
		isMobile = False
		if re.search(mobile_reg, ua) != None:
			windowSize = {'width': mobile_window_w, 'height': mobile_window_h}
			isMobile = True
		# print(windowSize, isMobile)
		# 不能不加载图片 不然 vue 的渲染会不完整，猜测是因为 vue 的渲染会用到加载图片的事件
		# browser = p.chromium.launch(args=['--blink-settings=imagesEnabled=false'], headless=False)
		# browser_context = p.chromium.launch_persistent_context(user_data_dir='./playwright_temp/user', devtools=True, headless=False, viewport=windowSize, is_mobile=isMobile)
		# browser_context = p.chromium.launch_persistent_context(user_data_dir='./playwright_temp/user', viewport=windowSize, is_mobile=isMobile)
		if devtools == True and isMobile == True:
			windowSize['width'] = windowSize['width'] * 2
		if user_agent != None:
			ua = user_agent
		if images_enabled == True:
			browser_context = p.chromium.launch_persistent_context(args=['--blink-settings=imagesEnabled=false'], devtools=devtools, headless=headless, user_data_dir='./playwright_temp/user', user_agent=ua, viewport=windowSize, is_mobile=isMobile)
		else:
			browser_context = p.chromium.launch_persistent_context(devtools=devtools, headless=headless, user_data_dir='./playwright_temp/user', user_agent=ua, viewport=windowSize, is_mobile=isMobile)
		browser = browser_context
		page = browser.new_page()

		if load_script != None:
			page.on("load", lambda :page.evaluate(load_script))
		page.goto(url)
		time.sleep(waittime) # 等待页面渲染完成
		if after_script != None:
			page.evaluate(after_script)
		html = page.content()
		browser.close()
	return html

class myHTTPServerRequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		# print(self)
		url = hostUrl + self.path
		ua = None
		ua = self.headers['user-agent']
		if (ua == None):
			print(url+'    ua is empty')
		else:
			print(url+'    '+ua)

		proxy_flg = False
		for i in pathList:
			if i == self.path:
				proxy_flg = True
				break
		if proxy_flg == False and (proxy_reg == None or proxy_reg.strip() == '') == False:
			if re.search(proxy_reg, self.path) != None:
				proxy_flg = True

		if proxy_flg == True:
			# 构造请求对象,并添加请求头
			if user_agent != None:
				headers = {
					'User-Agent': user_agent
				}
				req = request.Request(url=url, headers=headers)
			elif ua != None:
				headers = {
					'User-Agent': ua
				}
				req = request.Request(url=url, headers=headers)
			else:
				req = request.Request(url=url)
			# 发起请求
			resp = request.urlopen(req)
			# print(resp.getcode())
			# print(resp.getheaders())
			# print(resp)
			self.send_response(resp.getcode())
			for header in resp.getheaders():
				self.send_header(header[0], header[1])
				# print(header)

			# self.send_header('Content-type', 'text/html')
			self.end_headers()
			self.wfile.write(resp.read())

			# html = 'not found'
			# self.send_response(404)
			# self.send_header('Content-type', 'text/html')
			# self.end_headers()
			# self.wfile.write(html.encode('utf-8'))
			return

		html = getSourceCode(url, ua)
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		self.wfile.write(html.encode('utf-8'))

def testDomain(domain, ip):
	print(ip+'    '+domain, end="\t")
	if ip == None or ip == '':
		print('ip is empty')
		return
	qtype = 'A'
	ans = dns.resolver.resolve(qname=domain, rdtype=qtype, )
	ansip = ''
	for i in ans.response.answer:
		for j in i.items:
			if j.rdtype == 1:
				print (j.address, end="\t")
				ansip = j.address
	if re.search(ip, ansip) != None:
		print('hosts is ok')
		return
	if platform.system() == 'Linux':
		fo = open('/etc/hosts', "a", encoding = 'utf8')
		fo.write(ip+'    '+domain+'\n')
		fo.close()
		print('hosts is update')

def setBoolen(value: str = True, default: bool = True) -> bool:
	if value == None:
		value = default
	else:
		if value.strip() == '':
			value = default
		else:
			value = int(value)
			if value == 1:
				value = True
			elif value == 0:
				value = False
			else:
				value = default
	return value

if __name__ == '__main__':

	config = 'config.ini'
	opts, args = getopt.getopt(sys.argv[1:], '', ['config='])
	for opt, arg in opts:
		if opt in ('--config'):
			if os.path.isfile(arg):
				config = arg

	# 创建配置文件对象
	con = configparser.ConfigParser()
	# 读取文件
	con.read(config, encoding='utf-8')
	# 获取所有section
	# sections = con.sections()
	# ['url', 'email']
	# 获取特定section
	items = con.items('target') # 返回结果为元组
	items = dict(items)
	ip = items.get('ip')
	ip = ip.strip()
	port = items.get('port')
	port = port.strip()
	hostUrl = items.get('hosturl')
	hostUrl = hostUrl.strip()
	user_agent = items.get('user_agent')
	ua = None
	# executablePath = items.get('executable_path')
	# if executablePath != None:
	# 	executablePath = executablePath.strip()

	pc_window_size = items.get('pc_window_size')
	pc_window_w = 1920
	pc_window_h = 1200
	if pc_window_size != None:
		pc_window = pc_window_size.split(',')
		if len(pc_window) >= 2 and pc_window[0].strip() != '' and pc_window[1].strip() != '':
			pc_window_w = int(pc_window[0])
			pc_window_h = int(pc_window[1])

	mobile_window_size = items.get('mobile_window_size')
	mobile_window_w = 414
	mobile_window_h = 736
	if pc_window_size != None:
		mobile_window = mobile_window_size.split(',')
		if len(mobile_window) >= 2 and mobile_window[0].strip() != '' and mobile_window[1].strip() != '':
			mobile_window_w = int(mobile_window[0])
			mobile_window_h = int(mobile_window[1])

	load_script = items.get('load_script')
	if os.path.isfile(load_script):
		with open(load_script, 'r', encoding='utf-8') as file_object:
			contents = file_object.read()
			file_object.close()
			load_script = contents
	else:
		load_script = None

	after_script = items.get('after_script')
	if os.path.isfile(after_script):
		with open(after_script, 'r', encoding='utf-8') as file_object:
			contents = file_object.read()
			file_object.close()
			after_script = contents
	else:
		after_script = None

	images_enabled = items.get('images_enabled')
	images_enabled = setBoolen(images_enabled, True)

	headless = items.get('headless')
	headless = setBoolen(headless, True)

	devtools = items.get('devtools')
	devtools = setBoolen(devtools, True)

	mobile_reg = items.get('mobile_reg')
	if mobile_reg == None or mobile_reg.strip() == '':
		mobile_reg = r'AdsBot-Google-Mobile|AdsBot-Google-Mobile|Mediapartners-Google|AdsBot-Google-Mobile-Apps|googleweblight|Android|iPhone'
	waittime = items.get('waittime')
	if waittime == None:
		waittime = 1
	else:
		waittime = float(waittime)

	if ip == '0.0.0.0':
		ip = '127.0.0.1'
	url = 'http://' + ip + ':' + port
	port = int(port)
	server_address = ('', port)
	httpd = ThreadingHttpServer(server_address, myHTTPServerRequestHandler)

	items = con.items('proxy') # 返回结果为元组
	items = dict(items)
	proxy_reg = items.get('reg')
	pathList = items.get('path')
	if pathList != None:
		pathList = pathList.split(',')
	else:
		pathList = []
	# print(pathList)
	items = con.items('hosts') # 返回结果为元组
	items = dict(items)
	# print(items)
	num = items.get('num')
	for index in range(int(num)):
		domain2ipIndex = 'domain2ip'+str(index)
		domain2ip = items.get(domain2ipIndex)
		domain2ip = domain2ip.split(',')
		testDomain(domain2ip[0], domain2ip[1])

	print('running server... use <Ctrl-C> to stop')
	print('target URL \t' + hostUrl)
	print('Please use your browser to open this URL \t' + url)
	del con
	del items
	del config
	del opts
	del args
	del ip
	del url
	del port
	httpd.serve_forever()

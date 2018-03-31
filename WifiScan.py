#!/usr/bin/env python3
import re, logging
import subprocess as sp

FIX='* \t\n'
bFIX=b'* \t\n'

class WifiScan:
	'''WifiScan docstring'''
	def __init__(self, iface='wlan0'):
		assert(isinstance(iface, str))
		self.iface = iface
		self.raw_result = bytes()
		self.scan_result = list()
		pass

	def get_raw_scan(self):
		ret = sp.run(["/sbin/iw", "dev", self.iface, "scan"], 
			stdout=sp.PIPE)
		
		if ret.returncode==0:
			self.raw_result = ret.stdout
			return True
		else:
			logging.error('[Scan Failed] Please try execution as ROOT.')
			return False
		pass
	
	def parse_raw_scan(self):
		raw_lines = self.raw_result.split(b'\n')

		m_stack = list()
		for line in raw_lines:
			print(line)
			try:
				k,v = line.split(b':', 1)	#get (key, value) pair
			except Exception as e:
				k,v = b'Array', line
			ind = k.rfind(b'\t')		#check indent level
			level = len(m_stack)		#get current level

			if len(m_stack)==0:			#begin of one item
				k = line
				m_stack.append({'MAC', k[k.index(b' ')+1 : k.index(b'(')].decode()})
				pass
			elif len(m_stack)==ind:		#begin of the content
				m_stack.append({k.decode().strip(FIX) : v.decode().strip(FIX)})
				pass
			elif len(m_stack)>ind:		#end of the content
				#recursive add up
				while len(m_stack)>ind:
					tmp = m_stack.pop()
					if len(m_stack)==0:
						self.scan_result.append(tmp)
					else:
						for key in m_stack[-1]:
							if isinstance(m_stack[-1][key], dict):
								m_stack[-1][key].update(tmp)
							elif key=='Array':
								m_stack[-1][key].append(tmp['Array'])
							else:
								m_stack[-1][key] = tmp
						pass
					pass
				#append next
				m_stack.append({k.decode().strip(FIX) : v.decode().strip(FIX)})
				pass
			pass
		pass

	def update_scan_result(self):
		if self.get_raw_scan():
			self.parse_raw_scan()
			return True
		else:
			return False
		pass

	def freq2channel(freq):
		pass

	pass

def main():
	iws = WifiScan('wlp6s0')
	iws.get_raw_scan()
	iws.parse_raw_scan()
	pass

if __name__ == '__main__':
	main()

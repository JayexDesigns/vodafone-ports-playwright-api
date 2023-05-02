from playwright.sync_api import sync_playwright
from tabulate import tabulate
from decouple import config
from copy import deepcopy
from time import sleep

class PortHandler:
	def __init__(self, headless=True):
		self.headless = headless
		self.ports = []
		self.browserGetOpenPorts()

	def openBrowser(func):
		def performAction(self, *args):
			with sync_playwright() as p:
				browser = p.firefox.launch(headless=self.headless) # With Firefox The Headless Browser Is Not Detected
				page = browser.new_page()
				page.goto("http://192.168.0.1/login.html")

				# Login
				page.fill("xpath=//html/body/div/div/div[2]/div/div[2]/div[2]/div[2]/div/input", config("V_USERNAME"))
				page.fill("xpath=//html/body/div/div/div[2]/div/div[2]/div[2]/div[3]/div[1]/input", config("V_PASSWORD"))
				page.click("xpath=//html/body/div/div/div[2]/div/div[2]/div[2]/div[3]/div[2]/input")

				# Expert Mode
				page.click("xpath=//html/body/div/div/div[1]/div/div[1]/div/div/div/div[1]/div[2]/a")
				page.click("xpath=//html/body/div/div/div[1]/div/div[1]/div/div/div/div[1]/div[2]/div/ul/li[2]")

				return func(self, page, *args)

		return performAction

	@openBrowser
	def browserGetOpenPorts(self, page, *args):
		# Internet Tab
		page.click("xpath=//html/body/div/div/div[1]/div/div[2]/div/div/ul/li[3]/a")

		# Port Mapping
		page.click("xpath=//html/body/div/div/div[6]/div[2]/div[3]/ul/li[2]/a")

		# List Of Open Ports
		page.is_visible("xpath=//html/body/div/div/div[6]/div[3]/div/div/div[1]/div[4]/div/input")
		sleep(4)
		elements = page.locator(".port-mapping .table-row").all()
		self.ports = [["Service", "Local IP Address", "Protocol", "LAN Port", "Public Port"]]
		for i in range(1, len(elements)):
			port = []
			element = elements[i].element_handle().query_selector_all('> *')
			for j in range(0, len(element) - 3):
				data = element[j].inner_html()
				port.append(data)
			self.ports.append(port)

	def printOpenPorts(self):
		print(tabulate(self.ports, headers="firstrow"))

	def indexOfPort(self, port):
		for i in range(len(self.ports)):
			p = self.ports[i]
			if p[4] == port:
				return i
		return -1

	def openPort(self, protocol, ip, publicPort, lanPort):
		index = self.indexOfPort(publicPort)
		if index != -1:
			return False

		try:
			self.browserOpenPort(protocol, ip, publicPort, lanPort)
		except Exception as e:
			raise e

		self.ports.append([protocol, ip, protocol, lanPort, publicPort])
		return True

	@openBrowser
	def browserOpenPort(self, page, *args):
		protocol = args[0]
		ip = args[1]
		publicPort = args[2]
		lanPort = args[3]

		# Internet Tab
		page.click("xpath=//html/body/div/div/div[1]/div/div[2]/div/div/ul/li[3]/a")

		# Port Mapping
		page.click("xpath=//html/body/div/div/div[6]/div[2]/div[3]/ul/li[2]/a")

		# List Of Open Ports
		page.is_visible("xpath=//html/body/div/div/div[6]/div[3]/div/div/div[1]/div[4]/div/input")
		sleep(4)

		# Click Add Port
		page.click("xpath=//html/body/div/div/div[6]/div[3]/div/div/div[1]/div[4]/div/input")

		# Change Protocol
		sleep(1)
		steps = 1 if protocol == "TCP" else 2 if protocol == "UDP" else 3
		page.focus("#selectServiceProtocol_chosen > div > div > input[type=text]")
		for i in range(steps):
			page.keyboard.press("ArrowDown")
		page.keyboard.press("Enter")

		# Change IP
		ip = ip.split(".")
		page.focus("#content > div.popup.big > div:nth-child(3) > div:nth-child(3) > div.right > input:nth-child(1)")
		page.keyboard.type(ip[0])
		page.focus("#content > div.popup.big > div:nth-child(3) > div:nth-child(3) > div.right > input:nth-child(2)")
		page.keyboard.type(ip[1])
		page.focus("#content > div.popup.big > div:nth-child(3) > div:nth-child(3) > div.right > input:nth-child(3)")
		page.keyboard.type(ip[2])
		page.focus("#content > div.popup.big > div:nth-child(3) > div:nth-child(3) > div.right > input:nth-child(4)")
		page.keyboard.type(ip[3])

		# Chage Public Port
		page.focus("#publicSinglePort")
		page.keyboard.type(publicPort)

		# Chage LAN Port
		page.focus("#lanSinglePort")
		page.keyboard.type(lanPort)

		# Save
		page.click("#saveButton")
		sleep(2)

		# Cancel If Error
		if page.query_selector('#content > div.popup.big > div.scm_error_msg.message.message-error') is not None:
			error = page.locator("#content > div.popup.big > div.scm_error_msg.message.message-error").inner_html()
			page.locator(".button-cancel").all()[2].click()
			page.locator(".button-cancel").all()[0].click()
			raise Exception(error)

		# Apply
		page.click("#applyButton")
		sleep(4)

		return True

	def closePort(self, index):
		if type(index) != int or index <= 0 or index >= len(self.ports):
			return False
		if self.browserClosePort(index):
			self.ports.pop(index)
			return True
		return False

	@openBrowser
	def browserClosePort(self, page, *args):
		index = args[0]

		# Internet Tab
		page.click("xpath=//html/body/div/div/div[1]/div/div[2]/div/div/ul/li[3]/a")

		# Port Mapping
		page.click("xpath=//html/body/div/div/div[6]/div[2]/div[3]/ul/li[2]/a")

		# List Of Open Ports
		page.is_visible("xpath=//html/body/div/div/div[6]/div[3]/div/div/div[1]/div[4]/div/input")
		sleep(4)

		# Close Port
		table = page.locator(".port-mapping .table-row").all()
		trashButton = table[index].element_handle().query_selector_all('> *')[6]
		trashButton.click()

		# Apply
		page.click("#applyButton")
		sleep(4)

		return True

	def userInputHandler(self):
		while True:
			entry = input("\nSelect an option:\n\t- l (list of open ports)\n\t- o (open port)\n\t- c (close port)\n\t- g (get ports again)\n\t- e (exit)\n-> ")
			if (entry == "l"):
				self.printOpenPorts()

			elif (entry == "o"):
				protocol = input("Select protocol:\n\t[0] \"TCP/UDP\"\n\t[1] \"TCP\"\n\t[2] \"UDP\"\n-> ")
				if (protocol != "0" and protocol != "1" and protocol != "2"):
					print("Wrong option")
					continue
				protocol = "TCP/UDP" if protocol == "0" else "TCP" if protocol == "1" else "UDP"

				ip = input("Input the ip of the host\n-> ")
				if (len(ip.split(".")) != 4):
					print("Wrong IP format")
					continue

				publicPort = input("Input the public port\n-> ")
				lanPort = input("Input the LAN port\n-> ")

				try:
					if self.openPort(protocol, ip, publicPort, lanPort):
						print("Port opened successfully")
					else:
						print("Port is already open")
				except Exception as e:
					print(e.args[0])
					continue

			elif (entry == "c"):
				ports = deepcopy(self.ports)
				for i in range(0, len(ports)):
					if i == 0:
						ports[i].insert(0, "Index")
					else:
						ports[i].insert(0, f"[{i-1}]")
				print(tabulate(ports, headers="firstrow"))
				index = input("\nInput the index of the port you want to close\n-> ")
				try:
					index = int(index)
				except:
					print("The index must be a number")
					continue
				if not self.closePort(index + 1):
					print("The input is incorrect")
				else:
					print("Port closed successfully")

			elif (entry == "g"):
				self.browserGetOpenPorts()
				self.printOpenPorts()

			elif (entry == "e"):
				break
			else:
				print("Wrong option")

if __name__ == "__main__":
	portHandler = PortHandler()
	portHandler.userInputHandler()

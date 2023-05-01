from playwright.sync_api import sync_playwright
from tabulate import tabulate
from decouple import config
from time import sleep

class PortHandler:
	def __init__(self, headless=True):
		self.headless = headless
		self.ports = [["Service", "Local IP Address", "Protocol", "LAN Port", "Public Port"]]
		self.getOpenPorts()

	def openBrowser(func):
		def performAction(self):
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

				return func(self, page)

		return performAction

	@openBrowser
	def getOpenPorts(self, page):
		# Internet Tab
		page.click("xpath=//html/body/div/div/div[1]/div/div[2]/div/div/ul/li[3]/a")

		# Port Mapping
		page.click("xpath=//html/body/div/div/div[6]/div[2]/div[3]/ul/li[2]/a")

		# List Of Open Ports
		page.is_visible("xpath=//html/body/div/div/div[6]/div[3]/div/div/div[1]/div[4]/div/input")
		sleep(4)
		elements = page.locator(".port-mapping .table-row").all()
		for i in range(1, len(elements)):
			port = []
			element = elements[i].element_handle().query_selector_all('> *')
			for j in range(0, len(element) - 3):
				data = element[j].inner_html()
				port.append(data)
			self.ports.append(port)

	def printOpenPorts(self):
		print(tabulate(self.ports, headers="firstrow"))

	def portIsOpen(self, port):
		for p in self.ports:
			if p["public_port"] == str(port):
				return True
		return False

	def userInputHandler(self):
		while True:
			entry = input("\nSelect an option:\n\t- l (list of open ports)\n\t- o (open port)\n\t- c (close port)\n\t- e (exit)\n-> ")
			if (entry == "l"):
				self.printOpenPorts()
			elif (entry == "o"):
				self.printOpenPorts()
			elif (entry == "c"):
				self.printOpenPorts()
			elif (entry == "e"):
				break
			else:
				print("Wrong option")

if __name__ == "__main__":
	portHandler = PortHandler()
	portHandler.userInputHandler()

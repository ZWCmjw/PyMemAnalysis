import  os,sys,linecache,codecs
import tkinter as tk
from tkinter.filedialog import  askopenfilename
import tkinter.messagebox
import re

global fileNvm
global filetarget
global filecref
global filemap

global flashline
global flashcnt
global ramline
global ramcnt

filecref = None
filetarget = None
filemap = None
fileNvm = None

flashline = None
flashcnt = None
ramline = None
ramcnt = None
global mapflag
mapflag= False
# filemask = 'C:/Users/Administrator/Desktop/JavaCOS 空间修改器/c/mask.c'



		
def cur_file_dir():
	#获取脚本路径
	path = sys.path[0]
	#判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
	if os.path.isdir(path):
		return path
	elif os.path.isfile(path):
		return os.path.dirname(path)

# returndata = [g_ConfigSize,
# 1			  JC_EEPROM_BASE, EEPROM_LIMIT, EEPAGE_SIZE, ROMBase,
# 5			  NVMBase, OS_PARA_DATA_FIELD_START, OS_PARA_DATA_FIELD_SIZE, OS_VARIABLE_FIELD_START,
# 9			  OS_VARIABLE_FIELD_SIZE, E2P_IMAGE_START, EEP_BACKUP_AREA, EEP_BACKUP_AREA_SIZE,
# 13		  JC_RAM_BASE, RAM_LIMIT, RAMBase, RAMSize
# 17          g_ConfigSize
# 			  ]
#	getmap(file,self.datalist[1],self.datalist[2],self.datalist[5],self.datalist[13],self.datalist[14], self.datalist[15], self.datalist[16]):
def getmap(file):
	flashlineaddr = None
	flashlinesize = None
	ramlineaddr = None
	ramlinesize = None

	global flashline
	global flashcnt
	global ramline
	global ramcnt

	fline = open(file).readlines()
	if "ARM" in fline[0]:
		MAPflag = "keil"
	elif "Archive" in fline[0]:
		MAPflag = "eclipse"

	cnt = 0
	for msm in fline:
		if MAPflag is "keil":
			if flashline in msm:
				maincontext = fline[cnt - int(flashcnt)]
				index0 = maincontext.find("0x")
				index1 = maincontext.find(" ", index0)
				flashlineaddr = maincontext[index0+2:index1]
				flashlineaddr = int(flashlineaddr,16)
				endindex = len(maincontext)
				times = endindex - index1
				while times:
					times -=1
					index0 = maincontext.find(" ", index1+1)
					index1 = maincontext.find(" ", index0+1)
					if (index1- index0) >1:
						try:
							flashlinesize  = maincontext[index0+1:index1]
							flashlinesize  = int(flashlinesize)
							times = 0
						except:
							flashlinesize = 0
			if ramline in msm:
				maincontext = fline[cnt - int(ramcnt)]
				index0 = maincontext.find("0x")
				index1 = maincontext.find(" ", index0)
				ramlineaddr = maincontext[index0 + 2:index1]
				ramlineaddr = int(ramlineaddr,16)
				endindex = len(maincontext)
				times = endindex - index1
				while times:
					times -= 1
					index0 = maincontext.find(" ", index1 + 1)
					index1 = maincontext.find(" ", index0 + 1)
					if (index1 - index0) > 1:
						try:
							ramlinesize  = maincontext[index0+1:index1]
							ramlinesize  = int(ramlinesize)
							times = 0
						except:
							ramlinesize = 0

		elif MAPflag is "eclipse":
			pass

		cnt += 1


	return [flashlineaddr, flashlinesize,ramlineaddr,ramlinesize]


# getjavaMSM(filecref,"0x10032000","0x10063A00")
def getjavaMSM(file, rombase, e2base):
	getROMBASE = None
	getE2BASE = None
	fline = open(file).readlines()
	cnt = 0
	for msm in fline:
		if "ROMBASE=" in msm:
			if rombase is not None:
				fline[cnt] = "ROMBASE=" + rombase + "\n"
			getROMBASE = fline[cnt]
		elif "E2BASE=" in msm:
			if e2base is not None:
				fline[cnt] = "E2BASE=" + e2base + "\n"
			getE2BASE = fline[cnt]
		if getE2BASE and getROMBASE is not None:
			break
		cnt += 1

	if rombase or e2base is not None:
		fb = open(file, "w")
		for l in fline:
			fb.write(l)
		fb.close()

	return getROMBASE, getE2BASE


# getcmaskMSM(filemask)
def getcmaskMSM(file):
	with codecs.open(file, 'r', 'gbk') as handle:
		getROMSIZE = None
		getPEEPROM_IMAGE_SIZE = None
		for msm in handle:
			# define ROMSIZE 175399
			# define EEPROM_IMAGE_SIZE 12364
			fileline = msm.replace(" ", "").replace("	", "").replace("\n", "").replace("\r", "")
			if "#defineROMSIZE" in fileline:
				getROMSIZE = fileline.replace("#defineROMSIZE","")
			elif "#defineEEPROM_IMAGE_SIZE" in fileline:
				getPEEPROM_IMAGE_SIZE = fileline.replace("#defineEEPROM_IMAGE_SIZE","")
			if getROMSIZE and getPEEPROM_IMAGE_SIZE is not None:
				break
	handle.close()
	return getROMSIZE, getPEEPROM_IMAGE_SIZE





def ModifycnvmMSM(file, newsize):
	fline = open(file).readlines()
	cnt = 0
	for msm in fline:
		fileline = msm
		if "/*E2P_CONFIG_SIZE " in fileline:
			index1 = fileline.upper().find("0X")
			index2 = fileline.upper().find("0X", index1 + 1)
			index3 = fileline.upper().find("0X", index2 + 1)
			index4 = fileline.upper().find("0X", index3 + 1)
			index5 = fileline.upper().find(",", index4 + 1)
			if newsize is not None:
				t = msm[:index1] + newsize[0] + "," + newsize[1] + "," + newsize[2] + "," + newsize[3] + msm[index5:]
			else:
				t = [fileline[index1:index2 - 1], fileline[index2:index3 - 1], fileline[index3:index4 - 1],
					 fileline[index4:index5]]
			break
		cnt += 1

	if newsize is not None:
		fline[cnt] = t
		fb = open(file, "w")
		for l in fline:
			fb.write(l)
		fb.close()
		return None
	else:
		return t


def ALIGN_UP_OF(x, y):
	return ((x + y - 1) & ~(y - 1))


def getctarget(file, rombase, nvmbase, rambase, ramsize):
	# flash起始地址   JC_EEPROM_BASE
	# flash结束地址   EEPROM_LIMIT
	# flash页大小     EEPAGE_SIZE
	#
	# ram 起始地址    JC_RAM_BASE
	# ram 结束地址    RAM_LIMIT
	#

	# flash起始
	# ROM_AREA_START            ----java层的 ROMBASE
	# NVMBase                   ----平台起始地址
	# OS_PARA_DATA_FIELD_START  ----平台配置区的起始地址
	# OS_VARIABLE_FIELD_START   ----平台变量区的起始地址
	# E2P_IMAGE_START           ----E2P表起始地址
	# E2PBase                   ----用户可用的E2P起始地址
	# EEP_BACKUP_AREA
	# flash结束


	# ram起始                   ----ram的起始地址
	# DTR地址                   ----DTR起始地址以及大小
	# RTR地址                   ----RTR起始地址以及大小
	# ram结束                   ----ram的结束地址
	returndata = []
	fline = open(file).readlines()
	cnt = 0
	for msm in fline:
		fileline = msm.replace(" ", "").replace("	", "").replace("\r", "").replace("\n", "").upper()

		if "#DEFINENVMBASE" in fileline:
			index0 = fileline.find("0X")
			index1 = fileline.find(")", index0)
			if index1 != -1:
				index4 = index1
			else:
				index4 = index0 + 10
			NVMBase = fileline[index0:index4].replace("UL", "")
			if nvmbase is not None:
				fline[cnt] = fline[cnt].replace(NVMBase[2:], nvmbase[2:])
				NVMBase = int(nvmbase[2:], 16)
			else:
				NVMBase = int(NVMBase[2:], 16)
		elif "#DEFINEROM_AREA_START" in fileline:  # rombase
			index0 = fileline.find("0X")
			index1 = fileline.find(")", index0)
			if index1 != -1:
				index4 = index1
			else:
				index4 = index0 + 10
			ROMBase = fileline[index0:index4].replace("UL", "")
			if rombase is not None:
				fline[cnt] = fline[cnt].replace(ROMBase[2:], rombase[2:])
				ROMBase = int(rombase[2:], 16)
			else:
				ROMBase = int(ROMBase[2:], 16)
		elif "#DEFINERAMBASE" in fileline:  # RAMBase
			index0 = fileline.find("0X")
			index1 = fileline.find(")", index0)
			if index1 != -1:
				index4 = index1
			else:
				index4 = index0 + 10
			RAMBase = fileline[index0:index4].replace("UL", "")
			if rambase is not None:
				fline[cnt] = fline[cnt].replace(RAMBase[2:], rambase[2:])
				RAMBase = int(rambase[2:], 16)
			else:
				RAMBase = int(RAMBase[2:], 16)
		elif "#DEFINERAMSIZE" in fileline:  # RAMSize
			index0 = fileline.find("0X")
			index1 = fileline.find(")", index0)
			if index1 != -1:
				index4 = index1
			else:
				index4 = index0 + 6
			RAMSize = fileline[index0:index4].replace("UL", "")
			if ramsize is not None:
				fline[cnt] = fline[cnt].replace(RAMSize[2:], ramsize[2:])
				RAMSize = int(ramsize[2:], 16)
			else:
				RAMSize = int(RAMSize[2:], 16)
		elif "#DEFINEJC_RAM_BASE" in fileline:  # JC_RAM_BASE
			index0 = fileline.find("0X")
			index1 = fileline.find(")", index0)
			if index1 != -1:
				index4 = index1
			else:
				index4 = index0 + 10
			JC_RAM_BASE = fileline[index0:index4].replace("UL", "")
			JC_RAM_BASE = int(JC_RAM_BASE[2:], 16)
		elif "#DEFINERAM_LIMIT" in fileline:  # RAM_LIMIT
			index0 = fileline.find("0X")
			index1 = fileline.find(")", index0)
			if index1 != -1:
				index4 = index1
			else:
				index4 = index0 + 10
			RAM_LIMIT = fileline[index0:index4].replace("UL", "")
			RAM_LIMIT = int(RAM_LIMIT[2:], 16)
		elif "#DEFINEEEPAGE_SIZE0X" in fileline:  # 页大小
			EEPAGE_SIZE = int(fileline[20:23], 16)
		elif "#DEFINEBACKUP_BLOCK_NUM" in fileline:  # 备份页数 32
			BACKUP_BLOCK_NUM = int(fileline[23:25], 10)
		elif "#DEFINETF_ADDR_CELL_SZIE" in fileline:  # 6
			TF_ADDR_CELL_SZIE = int(fileline[24:25], 10)
		elif "#DEFINETF_CELL_SZIE" in fileline:  # 2
			TF_CELL_SZIE = int(fileline[19:20], 10)
		elif "#DEFINEOS_PARA_DATA_FIELD_SIZE" in fileline:  # 0x400+0x200 = 0x600
			index = fileline.find("0X")
			OS_PARA_DATA_FIELD_SIZE = int(fileline[index + 2:], 16)
		elif "#DEFINEOS_VARIABLE_FIELD_SIZE" in fileline:  # 0xF00
			index = fileline.find("0X")
			OS_VARIABLE_FIELD_SIZE = int(fileline[index + 2:], 16)
		elif "#DEFINEJC_EEPROM_BASE" in fileline:
			index0 = fileline.find("0X")
			index1 = fileline.find(")", index0)
			if index1 != -1:
				index4 = index1
			else:
				index4 = index0 + 10
			JC_EEPROM_BASE = fileline[index0:index4].replace("UL", "")
			JC_EEPROM_BASE = int(JC_EEPROM_BASE[2:], 16)
		elif "#DEFINEEEPROM_LIMIT" in fileline:
			index0 = fileline.find("0X")
			index1 = fileline.find(")", index0)
			if index1 != -1:
				index4 = index1
			else:
				index4 = index0 + 10
			EEPROM_LIMIT = fileline[index0:index4].replace("UL", "")
			EEPROM_LIMIT = int(EEPROM_LIMIT[2:], 16)
		elif "#DEFINEEFCFG_FIELD_SIZE" in fileline:
			index = fileline.find("0X")
			EFCFG_FIELD_SIZE = int(fileline[index + 2:], 16)
		elif "#DEFINEEEP_BACKUP_AREA_SIZE" in fileline:
			index = fileline.find("0X")
			EEP_BACKUP_AREA_SIZE = int(fileline[index + 2:], 16)

		cnt += 1

	TF_SIZE = BACKUP_BLOCK_NUM * TF_CELL_SZIE
	RECORD_BUFFER_SIZE = BACKUP_BLOCK_NUM * TF_ADDR_CELL_SZIE
	RECORD_BUFFER_TOTAL_SIZE = RECORD_BUFFER_SIZE + TF_SIZE
	TRANSACTION_BUFFER_SIZE = ((BACKUP_BLOCK_NUM + 1) * EEPAGE_SIZE + RECORD_BUFFER_TOTAL_SIZE)
	RECORD_PAGE_START = NVMBase
	TRANSACTION_BUFFER_START = RECORD_PAGE_START + ALIGN_UP_OF(RECORD_BUFFER_TOTAL_SIZE, EEPAGE_SIZE)
	BACKUP_RECORD_PAGE_AREA = (TRANSACTION_BUFFER_START + (BACKUP_BLOCK_NUM + 2) * EEPAGE_SIZE)
	OS_PARA_DATA_FIELD_START = (BACKUP_RECORD_PAGE_AREA + EEPAGE_SIZE * 2)
	OS_VARIABLE_FIELD_START = OS_PARA_DATA_FIELD_START + OS_PARA_DATA_FIELD_SIZE
	OS_CONFIG_SIZE = (ALIGN_UP_OF(RECORD_BUFFER_TOTAL_SIZE, EEPAGE_SIZE) + (
	BACKUP_BLOCK_NUM + 2 + 2) * EEPAGE_SIZE + OS_PARA_DATA_FIELD_SIZE + OS_VARIABLE_FIELD_SIZE)
	E2P_IMAGE_START = NVMBase + OS_CONFIG_SIZE
	EECFG1_ADDR = EEPROM_LIMIT - EFCFG_FIELD_SIZE + 1
	EEP_BACKUP_AREA = EECFG1_ADDR - EEP_BACKUP_AREA_SIZE
	g_ConfigSize = EEP_BACKUP_AREA - OS_VARIABLE_FIELD_START
	# E2PBase = E2P_IMAGE_START + EEPROM_IMAGE_SIZE
	# print(hex(g_ConfigSize))
	if rombase or nvmbase or rambase or ramsize is not None:
		fb = open(file, "w")
		for l in fline:
			fb.write(l)
		fb.close()

	returndata = [g_ConfigSize,
				  JC_EEPROM_BASE, EEPROM_LIMIT, EEPAGE_SIZE, ROMBase,
				  NVMBase,OS_PARA_DATA_FIELD_START, OS_PARA_DATA_FIELD_SIZE, OS_VARIABLE_FIELD_START,
				  OS_VARIABLE_FIELD_SIZE, E2P_IMAGE_START, EEP_BACKUP_AREA,EEP_BACKUP_AREA_SIZE,
				  JC_RAM_BASE, RAM_LIMIT, RAMBase,RAMSize
				  ]
	return returndata


# print(getctarget(filetarget,None,None,None,None))
# print(getctarget(filetarget,"0X10032000","0X10060000","0x20003000","0X3C00"))
# print(getctarget(filetarget,"0X10033000","0X10061000","0x20003300","0X3A00"))
# a = getctarget(filetarget,None,None,None,None)
# for s in a:
# 	print(hex(s))


class Application(tk.Frame):
	def __init__(self, master=None):
		super().__init__(master)
		self.pack()
		self.datalist = []
		self.create_Mainwidgets()
		self.create_Canvas(None,None)
		self.Basic_infor(None,None)
		self.filelist = [None,None,None,None,None,None,None,None]
		self.loadconfg()


	def loadconfg(self):
		path = cur_file_dir()
		try:
			paths = open(path + '\confg.txt').readlines()
			for file in paths:
				if "target" in file:
					global filetarget
					filetarget = file.strip('\n')
				elif "NvmDefaultData" in file:
					global fileNvm
					fileNvm = file.strip('\n')
				elif ".cfg" in file:
					global filecref
					filecref = file.strip('\n')
				elif ".map" in file:
					global filemap
					filemap = file.strip('\n')
				elif "flashline:" in file:
					global flashline
					flashline = file.strip('\n').replace("flashline:", "")
				elif "flashcnt:" in file:
					global flashcnt
					flashcnt =int( file.strip('\n').replace("flashcnt:", ""))
				elif "ramline:" in file:
					global ramline
					ramline = file.strip('\n').replace("ramline:", "")
				elif "ramcnt:" in file:
					global ramcnt
					ramcnt =int( file.strip('\n').replace("ramcnt:", ""))

		except:
			pass



	def create_Mainwidgets(self):
		self.ProPath = tk.Button(self)
		self.ProPath["text"] = "工程路径"
		self.ProPath["command"] = self.SetProPath
		self.ProPath.grid(row=0, column=0, sticky='ew')

		self.Analysis = tk.Button(self)
		self.Analysis["text"] = "开始分析"
		self.Analysis["command"] = self.MemAnalysis
		self.Analysis.grid(row=0, column=1, sticky='ew')

		self.CheckMAP = tk.Button(self)
		self.CheckMAP["text"] = "检查Map "
		self.CheckMAP["command"] = self.CheckMap
		self.CheckMAP.grid(row=0, column=2, sticky='ew')

		self.TextMSM = tk.Label(self,text ="基本信息 " ,width=30,height=1,relief ='flat')
		self.TextMSM.grid(row=0, column=3,columnspan = 6,sticky='ew')

		# self.cvs1 = tk.Canvas(self, width=280, height=150, bg='white', relief='groove')
		# self.cvs1.grid(row=7, column=3, rowspan=5, columnspan=6, padx=8, pady=4, sticky='ewn')
		# self.cvs1.create_rectangle(2, 2, 280, 150, fill="white")

		romlab = tk.Label(self, text="ROMBase")
		romlab.grid(row=11, column=3,sticky='ew')

		self.romstr = tk.StringVar()
		self.roment = tk.Entry(self, textvariable=self.romstr, width=15)
		self.roment.grid(row=11, column=4, columnspan=2,sticky='w')

		self.subit1 = tk.Button(self)
		self.subit1["text"] = "提交"
		self.subit1["command"] = self.Modifyrom
		self.subit1.grid(row=11, column=7, sticky='e')

		nvmlab = tk.Label(self, text="NVMBase")
		nvmlab.grid(row=12, column=3,sticky='ew')

		self.nvmstr = tk.StringVar()
		self.nvment = tk.Entry(self, textvariable=self.nvmstr, width=15)
		self.nvment.grid(row=12, column=4, columnspan=2,sticky='w')

		self.subit1 = tk.Button(self)
		self.subit1["text"] = "提交"
		self.subit1["command"] = self.Modifynvm
		self.subit1.grid(row=12, column=7, sticky='e')

		ramlab = tk.Label(self, text="RAMBase")
		ramlab.grid(row=13, column=3,sticky='ew')


		self.ramstr = tk.StringVar()
		self.rament = tk.Entry(self, textvariable=self.ramstr, width=15)
		self.rament.grid(row=13, column=4, columnspan=2,sticky='w')


		self.subit2 = tk.Button(self)
		self.subit2["text"] = "提交"
		self.subit2["command"] = self.Modifyram
		self.subit2.grid(row=13, column=7, sticky='e')

		ramsizelab = tk.Label(self, text="RAMSize")
		ramsizelab.grid(row=14, column=3,sticky='ew')
		self.ramsizestr = tk.StringVar()
		self.ramsizeent = tk.Entry(self, textvariable=self.ramsizestr, width=15)
		self.ramsizeent.grid(row=14, column=4, columnspan=2,sticky='w')

		self.subit3 = tk.Button(self)
		self.subit3["text"] = "提交"
		self.subit3["command"] = self.Modifyramsize
		self.subit3.grid(row=14, column=7, sticky='e')


		sizelab = tk.Label(self, text="E2P_CONFIG_SIZE")
		sizelab.grid(row=15, column=3,sticky='ew')

		self.sizestr = tk.StringVar()
		self.sizeent = tk.Entry(self, textvariable=self.sizestr, width=15)
		self.sizeent.grid(row=15, column=4, columnspan=2,sticky='w')

		self.size1str = tk.StringVar()
		self.size1ent = tk.Entry(self, textvariable=self.size1str, width=15)
		self.size1ent.grid(row=16, column=4, columnspan=2,sticky='w')

		self.size = tk.Button(self)
		self.size["text"] = "更正"
		self.size["command"] = self.Modifysize
		self.size.grid(row=16, column=7, sticky='e')

	def Modifyrom(self):
		rombase = self.romstr.get()

		global mapflag
		if mapflag:
			list = getctarget(filetarget, rombase.upper(),None, None, None)
			getjavaMSM(filecref, rombase, None)

	def Modifynvm(self):
		# print(getctarget(filetarget,"0X10032000","0X10060000","0x20003000","0X3C00"))
		# getjavaMSM(filecref,"0x10032000","0x10063A00")
		nvmbase = self.nvmstr.get()

		global mapflag
		if mapflag:
			list = getctarget(filetarget, None, nvmbase.upper(), None, None)
			getjavaMSM(filecref, None, hex(list[10]))

	def Modifyram(self):
		rambase = self.ramstr.get()
		global mapflag
		if mapflag:
			getctarget(filetarget, None,None, rambase.upper(), None)

	def Modifyramsize(self):
		ramsize = self.ramsizestr.get()
		global mapflag
		if mapflag:
			getctarget(filetarget, None,None, None, ramsize.upper())
	def Modifysize(self):
		global mapflag
		if mapflag:
			if self.sizestr.get() != self.size1str.get() :
				# print(self.sizestr.get())
				size = self.sizestr.get()
				size =  "00000000" +  size[2:]
				newsize = ["0x"+size[-8:-6],"0x"+ size[-6:-4], "0x"+size[-4:-2], "0x"+size[-2:]]
				ModifycnvmMSM(fileNvm, newsize)
				self.size1str.set(self.sizestr.get())

	def create_Canvas(self,data,map):
		# flat, groove, raised, ridge, solid, or sunken
		cvs = tk.Canvas(self,width=200, height=600,bg = 'white',relief ='groove')
		cvs.grid(row=1, column=0,rowspan=20 ,columnspan=3, padx= 8,pady= 4, sticky='ew')
		cvs.create_rectangle(2, 2, 200, 600, fill="white")


		if data is not None:
			maxsize = 600
			if data[1] > data[13]:
				ramy1 = maxsize
				ramy2 = maxsize - 100
				nvmy1 = maxsize - 150
				nvmy2 = 15

			else:
				nvmy1 = maxsize
				nvmy2 = 165
				ramy1 = 115
				ramy2 = 15
			fg = int((ramy1 + nvmy2) / 2)
			cvs.create_text(100, nvmy1 - 5,  text="JC_EEPROM_BASE  " + hex(data[1]))
			cvs.create_text(100, nvmy2 - 5 , text="EEPROM_LIMIT    " + hex(data[2]))
			cvs.create_line(0,nvmy1, 200, nvmy1, fill='red')
			cvs.create_line(0,nvmy2, 200, nvmy2, fill='red')

			cvs.create_text(100, ramy1 - 5,  text="JC_RAM_BASE     " + hex(data[13]))
			cvs.create_text(100, ramy2 - 5,  text="RAM_LIMIT       " + hex(data[14]))
			cvs.create_line(0, ramy1, 200, ramy1, fill='red')
			cvs.create_line(0, ramy2, 200, ramy2, fill='red')

			cvs.create_line(0, fg-3 , 200, fg-3, fill='black', dash=(4, 4))
			cvs.create_line(0, fg+3 , 200, fg+3, fill='black', dash=(4, 4))

			romt = data[2] - data[1] +1

			#画ROMBase
			t = nvmy1 - int(((data[4]-data[1] +1) /romt)*(nvmy1 - nvmy2))
			cvs.create_line(0,t , 200, t , fill='blue')
			cvs.create_text(100, t - 5,  text="ROMBase    " + hex(data[4]))
			# rommask  staticinit
			# t0 = int(((data[17]) /romt)*(nvmy1 - nvmy2))
			# t1 = t - int(t0/2)
			# t2 = t - t0
			# cvs.create_line(0,t2 , 200, t2 , fill='red', dash=(4, 4))
			# cvs.create_text(100, t1 - 5,  text="rommask    " + hex(data[17]))
			# cvs.create_text(100, t2 - 5,  text="staticinit " + hex(data[18]))



			#画 NVMBase
			t = nvmy1 - int(((data[5]-data[1] +1) /romt)*(nvmy1 - nvmy2))
			cvs.create_line(0,t , 200, t , fill='blue')
			cvs.create_text(100, t + 5,  text="NVMBase    " + hex(data[5]))


			# 画 OS_PARA_DATA_FIELD_START
			t = nvmy1 - int(((data[6] - data[1] + 1) / romt) * (nvmy1 - nvmy2))
			cvs.create_line(0, t, 200, t, fill='red')
			cvs.create_text(100, t -20, text="平台配置区(红色)" + hex(data[6]))

			# 画 OS_VARIABLE_FIELD_START
			t = nvmy1 - int(((data[8] - data[1] + 1) / romt) * (nvmy1 - nvmy2))
			cvs.create_line(0, t, 200, t, fill='purple')
			cvs.create_text(100, t - 30, text="平台变量区(紫色)" + hex(data[8]))

			# 画 E2P_IMAGE_START
			t = nvmy1 - int(((data[10] - data[1] + 1) / romt) * (nvmy1 - nvmy2))
			cvs.create_line(0, t, 200, t, fill='yellow')
			cvs.create_text(100, t - 40, text="E2P表起始地址(黄色)" + hex(data[10]))

			# 画 EEP_BACKUP_AREA
			t = nvmy1 - int(((data[11] - data[1] + 1) / romt) * (nvmy1 - nvmy2))
			cvs.create_line(0, t, 200, t, fill='blue')
			cvs.create_text(100, t + 5, text="EEP_BACKUP_AREA " + hex(data[11]))

			# 画  RAMBase
			t = int((ramy1 + ramy2)/2)
			cvs.create_line(0, t+20, 200, t+20, fill='blue')
			cvs.create_text(100, t + 15, text="RAMBase " + hex(data[15]))
			cvs.create_line(0, t - 20, 200, t-20, fill='blue')
			cvs.create_text(100, t - 25, text="RAMend " + hex(data[15] + data[16]))
			cvs.create_text(100, t-5, text="RAMSize " + str(int(data[16]/1024))+"K")

	def showfileerror(self,file):
		tk.messagebox.showinfo(title='错误', message=file + '错误!')

	def openfile(self,flag,frame):
		titlelist = ['请选择target.h','请选择NvmDefaultData.c','请选择.cfg','请选择.map']
		dirlist = ['C:/','C:/','C:/','C:/']
		if self.filelist[0] is not None:
			dirlist[1] = self.filelist[0].replace("target.h","")
			dirlist[2] = self.filelist[0][:2]
			dirlist[3] = self.filelist[0][:2]

		self.filelist[flag] = askopenfilename(title=titlelist[flag],initialdir = dirlist[flag])

		if self.filelist[flag] == "":
			self.filelist[flag] = None
		if self.filelist[0] is not None:
			if "target.h" not in self.filelist[0]:
				self.showfileerror("请选择target.h")
			else:
				target = tk.StringVar()
				targetent = tk.Entry(frame, textvariable=target,width =50)
				targetent.grid(row=0, column=1, sticky='w', columnspan=5)
				target.set(self.filelist[0])
				global filetarget
				filetarget = self.filelist[0]

		if self.filelist[1] is not None:
			if "NvmDefaultData.c" not in self.filelist[1]:
				self.showfileerror("请选择NvmDefaultData.c")
			else:
				nvm = tk.StringVar()
				nvment = tk.Entry(frame, textvariable=nvm, width=50)
				nvment.grid(row=1, column=1, sticky='w', columnspan=5)
				nvm.set(self.filelist[1])
				global fileNvm
				fileNvm = self.filelist[1]
		if self.filelist[2] is not None:
			if ".cfg" not in self.filelist[2]:
				self.showfileerror("请选择.cfg")
			else:
				cref = tk.StringVar()
				crefent = tk.Entry(frame, textvariable=cref, width=50)
				crefent.grid(row=2, column=1, sticky='w', columnspan=5)
				cref.set(self.filelist[2])
				global filecref
				filecref = self.filelist[2]
		if self.filelist[3] is not None:
			if ".map" not in self.filelist[3]:
				self.showfileerror("请选择.map")
			else:
				map = tk.StringVar()
				mapent = tk.Entry(frame, textvariable=map, width=50)
				mapent.grid(row=3, column=1, sticky='w', columnspan=5)
				map.set(self.filelist[3])
				global filemap
				filemap = self.filelist[3]

	def savepath(self,flashlines,flashcnts,ramlines,ramcnts):
		global fileNvm
		global filetarget
		global filecref
		global filemap
		global flashline
		global flashcnt
		global ramline
		global ramcnt

		flashline = flashlines.get()
		ramline = ramlines.get()

		flashcnt = flashcnts.get()
		ramcnt = ramcnts.get()

		list = [filetarget,fileNvm,filecref,filemap,"flashline:" +flashline,"flashcnt:" +flashcnt,"ramline:" + ramline,"ramcnt:" + ramcnt]

		path = cur_file_dir()
		try:
			fb = open(path + '\confg.txt', 'w')
			for l in list:
				pathtext = l + "\n"
				fb.write(pathtext)
			fb.close()
		except:
			pass
		self.loadconfg()


	def SetProPath(self):
		color1 = '#B01415'
		global fileNvm
		global filetarget
		global filecref
		global filemap
		global flashline
		global flashcnt
		global ramline
		global ramcnt
		self.loadconfg()

		SetPath = tk.Toplevel()
		# SetPath.wm_attributes('-topmost', 1)  # 置顶
		global xx
		global yy
		SetPath.geometry("+%d+%d" % (xx/2, yy/2))
		SetPathB0 =  tk.Button(SetPath,text="选择C层target",command=lambda:self.openfile(0,SetPath))
		SetPathB0.grid(row=0, column=0, padx= 8,pady= 4, sticky='ew')

		if filetarget is not None:
			target = tk.StringVar()
			targetent = tk.Entry(SetPath, textvariable=target,width =50)
			targetent.grid(row=0, column=1, sticky='w', columnspan=5)
			target.set(filetarget)

		SetPathB1 =  tk.Button(SetPath,text="选择C层NvmDefaultData",command=lambda:self.openfile(1,SetPath))
		SetPathB1.grid(row=1, column=0, padx= 8,pady= 4, sticky='ew')
		if fileNvm is not None:
			nvm = tk.StringVar()
			nvment = tk.Entry(SetPath, textvariable=nvm,width =50)
			nvment.grid(row=1, column=1, sticky='w', columnspan=5)
			nvm.set(fileNvm)
		SetPathB2 = tk.Button(SetPath, text="选择JAVA层cfg",command=lambda:self.openfile(2,SetPath))
		SetPathB2.grid(row=2, column=0, padx=8, pady=4, sticky='ew')
		if filecref is not None:
			cref = tk.StringVar()
			crefent = tk.Entry(SetPath, textvariable=cref,width =50)
			crefent.grid(row=2, column=1, sticky='w', columnspan=5)
			cref.set(filecref)

		SetPathB3 =  tk.Button(SetPath,text="选择C层map",command=lambda:self.openfile(3,SetPath))
		SetPathB3.grid(row=3, column=0, padx= 8,pady= 4, sticky='ew')
		if filemap is not None:
			map = tk.StringVar()
			mapent = tk.Entry(SetPath, textvariable=map,width =50)
			mapent.grid(row=3, column=1, sticky='w', columnspan=5)
			map.set(filemap)

		flashlinelab = tk.Label(SetPath, text="Flash指定参考内容和偏移")
		flashlinelab.grid(row=4, column=0, padx=8, pady=4, sticky='ew')
		flashlines = tk.StringVar()
		flashlineent = tk.Entry(SetPath, textvariable=flashlines, width=40)
		flashlineent.grid(row=4, column=1, sticky='w', columnspan=4)
		flashlines.set(flashline)
		flashcnts = tk.StringVar()
		flashcntent = tk.Entry(SetPath, textvariable=flashcnts, width=10)
		flashcntent.grid(row=4, column=5, sticky='w')
		flashcnts.set(flashcnt)

		ramlinelab = tk.Label(SetPath, text="RAM指定参考内容和偏移")
		ramlinelab.grid(row=5, column=0, padx=8, pady=4, sticky='ew')
		ramlines = tk.StringVar()
		ramlineent = tk.Entry(SetPath, textvariable=ramlines, width=40)
		ramlineent.grid(row=5, column=1, sticky='w', columnspan=4)
		ramlines.set(ramline)
		ramcnts = tk.StringVar()
		ramcntent = tk.Entry(SetPath, textvariable=ramcnts, width=10)
		ramcntent.grid(row=5, column=5, sticky='w')
		ramcnts.set(ramcnt)
		savetext = tk.Button(SetPath, text="保存",
							 command=lambda: self.savepath(flashlines, flashcnts, ramlines, ramcnts))
		savetext.grid(row=6, column=0, padx= 8,pady= 4, sticky='ew')


	def MemAnalysis(self):
		# ROMSIZE, PEEPROM_IMAGE_SIZE = getcmaskMSM(filemask)
		ROMBASE, E2BASE = getjavaMSM(filecref,None,None)
		try:
			self.datalist = getctarget(filetarget,None,None,None,None)
			t = ModifycnvmMSM(fileNvm,None)
			ConfigSize = t[0][2:]+t[1][2:]+t[2][2:]+t[3][2:]
			ConfigSize = int(ConfigSize,16)
			# datalist.append(int(ROMSIZE,10))
			# datalist.append(int(PEEPROM_IMAGE_SIZE,10))
			self.datalist.append(ConfigSize)
			# for s in datalist:
			# 	print(hex(s))
			self.Basic_infor(self.datalist,None)
			self.create_Canvas(self.datalist,None)
			self.romstr.set(hex(self.datalist[4]))
			self.nvmstr.set(hex(self.datalist[5]))
			self.ramstr.set(hex(self.datalist[15]))
			self.ramsizestr.set(hex(self.datalist[16]))
			self.sizestr.set(hex(self.datalist[0]))
			self.size1str.set(hex(self.datalist[17]))
			global  mapflag
			mapflag = True

		except ValueError:
			tk.messagebox.showinfo(title='错误', message="target.h中宏定义大小 XX_SIZE 为 0x200形式，不要写成0x100+0x100或0x200UL，"+
													   "宏定义地址为 JC_RAM_BASE 	((memref)0x20000000UL)")




	def CheckMap(self):
		global filemap

		if mapflag is  True:
			rlist = getmap(filemap)
			self.datalist = self.datalist + rlist
			self.Basic_infor(self.datalist,True)
			self.create_Canvas(self.datalist,True)
		else:
			tk.messagebox.showinfo(title='错误', message="请先执行分析")





	def Basic_infor(self,data,map):
		Basic_infor = tk.Text(self, width=20, height=15, bg="lightblue")
		Basic_infor.grid(row=1, column=3,rowspan = 6,columnspan = 6, padx= 2,pady= 4, sticky='ewn')
		if data is not None:
			Basic_infor.insert(1.0, "NVM 页大小："+hex(data[3])+" （"+str(data[3])+"） " +"\n" )
			Basic_infor.insert(2.0, "NVM 总空间：" + str(int((data[2] - data[1] +1)/1024)) +"K"+ "\n")
			Basic_infor.insert(3.0, "RAM 总空间：" + str(int((data[14] - data[13] + 1) / 1024)) + "K" + "\n")
			Basic_infor.insert(4.0, "JAVA分配RAM空间：" + str(int((data[16]) / 1024)) + "K" + "\n")
			Basic_infor.insert(5.0, "平台占用NVM空间：" + str(int((data[10] - data[5] + 1) / 1024)) + "K" + "\n")
			if data[17] != data[0]:
				Basic_infor.insert(6.0, "警告："+ "\n" )
				Basic_infor.insert(7.0, "NvmDefaultData中的E2P_CONFIG_SIZE有误！"+"\n")
			else:
				Basic_infor.insert(6.0, "\n")
				Basic_infor.insert(7.0, "\n")
		if map is True:
			Basic_infor.insert(8.0, "\n")
			Basic_infor.insert(9.0, "     编译结果信息"  + "\n")
			if data[5] >= ( data[18] +data[19]):
				Basic_infor.insert(10.0, "NVMBase前可以利用空间：" +  hex(data[5] - (data[18] +data[19])) + "\n")
				if data[15] >= (data[20] + data[21]):
					Basic_infor.insert(11.0, "RAMBase前可以利用空间：" + hex(data[15] - (data[20] + data[21])) + "\n")
				else:
					Basic_infor.insert(11.0, "警告：" + "\n")
					Basic_infor.insert(12.0, "JAVA RAM空间分配重叠!" + "\n")
					Basic_infor.insert(13.0, "RAMBase地址至少需要向后移动" + hex((data[20] + data[21]) - data[15]) + "\n")
			else:
				if data[15] >= (data[20] + data[21]):
					Basic_infor.insert(10.0, "RAMBase前可以利用空间：" + hex(data[15] - (data[20] + data[21])) + "\n")
				else:
					Basic_infor.insert(10.0, "警告：" + "\n")
					Basic_infor.insert(11.0, "JAVA RAM空间分配重叠! " + "\n")
					Basic_infor.insert(12.0, "RAMBase地址至少需要向后移动" + hex((data[20] + data[21]) - data[15]) + "\n")
					Basic_infor.insert(13.0, "平台起始地址与C层代码重叠!" + "\n")
					Basic_infor.insert(14.0, "NVMBase地址至少需要向后移动"+hex((data[18] +data[19]) - data[5])+"\n")


root = tk.Tk()
root.title('Rongcard')
global xx
global yy
xx = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
yy = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
root.geometry("+%d+%d" % (xx,yy))
root.maxsize(500, 700)
path = cur_file_dir()
try:
    root.iconbitmap(path + '\ico\card.ico')
except:
    pass
app = Application(master=root)
app.mainloop()


# returndata = [g_ConfigSize,
# 1			  JC_EEPROM_BASE, EEPROM_LIMIT, EEPAGE_SIZE, ROMBase,
# 5			  NVMBase, OS_PARA_DATA_FIELD_START, OS_PARA_DATA_FIELD_SIZE, OS_VARIABLE_FIELD_START,
# 9			  OS_VARIABLE_FIELD_SIZE, E2P_IMAGE_START, EEP_BACKUP_AREA, EEP_BACKUP_AREA_SIZE,
# 13		  JC_RAM_BASE, RAM_LIMIT, RAMBase, RAMSize
# 17          g_ConfigSize ,flashlineaddr, flashlinesize,ramlineaddr,
# 21          ramlinesize
# 			  ]


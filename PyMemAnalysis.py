import  os,sys,linecache,codecs
import tkinter as tk

filemask = 'C:/Users/Administrator/Desktop/JavaCOS 空间修改器/c/mask.c'
fileNvm = 'C:/Users/Administrator/Desktop/JavaCOS 空间修改器/c/NvmDefaultData.c'
filetarget = 'C:/Users/Administrator/Desktop/JavaCOS 空间修改器/c/target.h'
filecref =  'C:/Users/Administrator/Desktop/JavaCOS 空间修改器/java/cref_mask.cfg'


		
def cur_file_dir():
	#获取脚本路径
	path = sys.path[0]
	#判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
	if os.path.isdir(path):
		return path
	elif os.path.isfile(path):
		return os.path.dirname(path)

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


newsize1 = ["0x00", "0x09", "0xA7", "0x00"]


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
		self.create_Mainwidgets()
		self.create_Canvas(None)
		self.Basic_infor(None,None)

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




	def create_Canvas(self,data):
		# flat, groove, raised, ridge, solid, or sunken  
		cvs = tk.Canvas(self,width=200, height=600,bg = 'white',relief ='groove')
		cvs.grid(row=1, column=0,rowspan=16 ,columnspan=3, padx= 8,pady= 4, sticky='ew')
		if data is not None:
			cvs1 = tk.Canvas(self,width=200, height=300,bg = 'white',relief ='groove')
			cvs1.grid(row=7, column=3,rowspan=10 ,columnspan=6, padx= 8,pady= 4, sticky='ewn')

			Modify = tk.Button(self)
			Modify["text"] = "  修改  "
			Modify["command"] = self.MemModify
			Modify.grid(row=16, column=8, sticky='ew')

			if data[1] > data[13]:
				ramy1 = 600
				ramy2 = 500
				nvmy1 = 450
				nvmy2 = 15
				fg    = 475
			else:
				nvmy1 = 600
				nvmy2 = 165
				ramy1 = 115
				ramy2 = 15
				fg    = 140
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
			t0 = int(((data[17]) /romt)*(nvmy1 - nvmy2))	
			t1 = t - int(t0/2)
			t2 = t - t0
			cvs.create_line(0,t2 , 200, t2 , fill='red', dash=(4, 4)) 
			cvs.create_text(100, t1 - 5,  text="rommask    " + hex(data[17]))	
			cvs.create_text(100, t2 - 5,  text="staticinit " + hex(data[18]))			
			
			#画NVMBase
			t = nvmy1 - int(((data[5]-data[1] +1) /romt)*(nvmy1 - nvmy2)) 			
			cvs.create_line(0,t , 200, t , fill='blue')
			cvs.create_text(100, t - 5,  text="NVMBase    " + hex(data[5]))


			# cvs.create_rectangle(0, 0, 200, 300, fill="grey") #white
			# cvs.create_rectangle(200, 0,300, 50, fill="red")
			# cvs.create_line(0, nvmy - 1, 200, nvmy - 1, fill='red', dash=(4, 4))  # 虚线



	def SetProPath(self):
		pass
	def MemAnalysis(self):
		ROMSIZE, PEEPROM_IMAGE_SIZE = getcmaskMSM(filemask)
		ROMBASE, E2BASE = getjavaMSM(filecref,None,None)
		datalist = getctarget(filetarget,None,None,None,None)
		t = ModifycnvmMSM(fileNvm,None)
		ConfigSize = t[0][2:]+t[1][2:]+t[2][2:]+t[3][2:]
		ConfigSize = int(ConfigSize,16)
		datalist.append(int(ROMSIZE,10))
		datalist.append(int(PEEPROM_IMAGE_SIZE,10))
		datalist.append(ConfigSize)
		for s in datalist:
			print(hex(s))
		self.Basic_infor(datalist,None)
		self.create_Canvas(datalist)
		# for s in datalist:
		# 	print(hex(s))
		# getctarget(filetarget)
			
	def MemModify(self):
		pass
			

	def CheckMap(self):
		self.create_Canvas(1)

	def Basic_infor(self,data,map):
		Basic_infor = tk.Text(self, width=20, height=15, bg="lightblue")
		Basic_infor.grid(row=1, column=3,rowspan = 6,columnspan = 6, padx= 2,pady= 4, sticky='ewn')
		if data is not None:
			Basic_infor.insert(1.0, "NVM 页大小："+hex(data[3])+" （"+str(data[3])+"） " +"\n" )
			Basic_infor.insert(2.0, "NVM 总空间：" + str(int((data[2] - data[1] +1)/1024)) +"K"+ "\n")
			Basic_infor.insert(3.0, "RAM 总空间：" + str(int((data[14] - data[13] + 1) / 1024)) + "K" + "\n")
			Basic_infor.insert(4.0, "JAVA占用NVM空间：" + str(int((data[17] + data[18]) / 1024)) + "K" + "\n")
			Basic_infor.insert(5.0, "JAVA分配RAM空间：" + str(int((data[16]) / 1024)) + "K" + "\n")
			Basic_infor.insert(6.0, "平台占用NVM空间：" + str(int((data[10] - data[5] + 1) / 1024)) + "K" + "\n")
			if data[19] != data[0]:
				Basic_infor.insert(7.0, "警告："+ "\n" )
				Basic_infor.insert(8.0, "NvmDefaultData中的E2P_CONFIG_SIZE有误！"+"\n")
			else:
				Basic_infor.insert(7.0, "\n")
				Basic_infor.insert(8.0, "\n")
		if map is not None:
			Basic_infor.insert(9.0, "\n")
			Basic_infor.insert(10.0, "     编译结果信息"  + "\n")
			Basic_infor.insert(11.0, "\n")
			Basic_infor.insert(12.0, "ROMBase前可以利用空间：" + "\n")
			Basic_infor.insert(13.0, "警告："+ "\n" )
			Basic_infor.insert(14.0, "平台起始地址与mask.c重叠!" + "\n")

root = tk.Tk()
app = Application(master=root)
app.mainloop()



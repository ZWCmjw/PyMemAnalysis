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



class Application(tk.Frame):
	def __init__(self, master=None):
		super().__init__(master)
		self.pack()
		self.create_Mainwidgets()
		self.create_Canvas()


	def create_Mainwidgets(self):
		self.ProPath = tk.Button(self)
		self.ProPath["text"] = "工程路径"
		self.ProPath["command"] = self.SetProPath
		self.ProPath.grid(row=0, column=0, sticky='ew')

		self.Analysis = tk.Button(self)
		self.Analysis["text"] = "开始分析"
		self.Analysis["command"] = self.MemAnalysis
		self.Analysis.grid(row=0, column=1, sticky='ew')

		self.Modify = tk.Button(self)
		self.Modify["text"] = "  修改  "
		self.Modify["command"] = self.MemModify
		self.Modify.grid(row=0, column=2, sticky='ew')

		self.Recovery = tk.Button(self)
		self.Recovery["text"] = "  恢复  "
		self.Recovery["command"] = self.Recovery
		self.Recovery.grid(row=0, column=3, sticky='ew')

		self.Submit = tk.Button(self)
		self.Submit["text"] = "  提交  "
		self.Submit["command"] = self.Submit
		self.Submit.grid(row=0, column=4, sticky='ew')

		self.CheckMAP = tk.Button(self)
		self.CheckMAP["text"] = "检查Map "
		self.CheckMAP["command"] = self.Submit
		self.CheckMAP.grid(row=0, column=5, sticky='ew')


	def create_Addr(self):
		Addr_text = tk.Text(self,width=10, height=50,bg="lightgrey")
		Addr_text.grid(row=1, column=0, sticky='ew')

	def create_Canvas(self):
		# flat, groove, raised, ridge, solid, or sunken  
		cvs = tk.Canvas(self,width=60, height=600,bg = 'white',relief ='groove')
		cvs.grid(row=1, column=0,columnspan=2, padx= 8,pady= 4, sticky='ew')
		cvs.create_text(60,500,text = "12345")
		# cvs.create_rectangle(0, 0, 147, 300, fill="gray")
		# cvs.create_rectangle(200, 0,300, 50, fill="red")


	def SetProPath(self):
		pass
	def MemAnalysis(self):
		pass
			
	def MemModify(self):
		pass
			

	def Recovery(self):
		pass
	def Submit(self):
		pass


# root = tk.Tk()
# app = Application(master=root)
# app.mainloop()


# getjavaMSM(filecref,"0x10032000","0x10063A00")
def getjavaMSM(file,rombase,e2base):
	getROMBASE = None
	getE2BASE  = None
	fline = open(file).readlines()
	cnt = 0
	for msm in fline: 
		if "ROMBASE=" in msm:
			if rombase is not None:
				fline[cnt] =  "ROMBASE=" + rombase + "\n"
			getROMBASE = fline[cnt]
		elif "E2BASE=" in msm:
			if e2base is not None:
				fline[cnt] =  "E2BASE=" + e2base + "\n"
			getE2BASE  = fline[cnt]
		if getE2BASE and getROMBASE is not None:
			break
		cnt+=1


	if rombase or e2base is not None:	
		fb = open(file,"w")
		for l in fline:
		    fb.write(l)
		fb.close()

	return getROMBASE, getE2BASE

# getcmaskMSM(filemask)
def getcmaskMSM(file):
	with codecs.open(file, 'r', 'gbk') as handle:
		getROMSIZE = None
		getPEEPROM_IMAGE_SIZE  = None
		for msm in handle: 
		#define ROMSIZE 175399
		#define EEPROM_IMAGE_SIZE 12364
			fileline = msm.replace(" ","").replace("	","").replace("\n","").replace("\r","")
			if "#defineROMSIZE" in fileline:
				getROMSIZE = fileline
				print(getROMSIZE)
			elif "#defineEEPROM_IMAGE_SIZE" in fileline:
				getPEEPROM_IMAGE_SIZE  = fileline
				print(getPEEPROM_IMAGE_SIZE)
			if getROMSIZE and getPEEPROM_IMAGE_SIZE is not None:
				break
	handle.close()
	return 	getROMSIZE, getPEEPROM_IMAGE_SIZE

newsize1 = ["0x00","0x09","0xA7","0x00"]
def ModifycnvmMSM(file,newsize):
	fline = open(file).readlines()
	cnt = 0
	for msm in fline: 
		fileline = msm
		if "/*E2P_CONFIG_SIZE " in fileline:
			index1 = fileline.upper().find("0X")
			index2 = fileline.upper().find("0X",index1+1)
			index3 = fileline.upper().find("0X",index2+1)
			index4 = fileline.upper().find("0X",index3+1)
			index5 = fileline.upper().find(",",index4+1)
			if newsize is not None:
				t = msm[:index1] + newsize[0] +"," + newsize[1]  +"," + newsize[2]  +"," + newsize[3]  +msm[index5:]
			else:
				t =[fileline[index1:index2-1], fileline[index2:index3-1], fileline[index3:index4-1], fileline[index4:index5]]
			break 
		cnt +=1

	if newsize is not None:	
		fline[cnt] = t
		fb = open(file,"w")
		for l in fline:
		    fb.write(l)
		fb.close()
		return None
	else:
		return t

def getctarget(file,rombase,nvmbase, rambase,ramsize):
#flash起始地址   JC_EEPROM_BASE
#flash结束地址   EEPROM_LIMIT
#flash页大小     EEPAGE_SIZE 
# 
#ram 起始地址    JC_RAM_BASE 
#ram 结束地址    RAM_LIMIT 
# 

#flash起始
#ROM_AREA_START            ----java层的 ROMBASE
#NVMBase                   ----平台起始地址
#OS_PARA_DATA_FIELD_START  ----平台配置区的起始地址
#OS_VARIABLE_FIELD_START   ----平台变量区的起始地址
#E2P_IMAGE_START           ----E2P表起始地址
#E2PBase                   ----用户可用的E2P起始地址 
# EEP_BACKUP_AREA 
# flash结束


#ram起始                   ----ram的起始地址
#DTR地址                   ----DTR起始地址以及大小
#RTR地址                   ----RTR起始地址以及大小
#ram结束                   ----ram的结束地址
	
	fline = open(file).readlines()
	cnt = 0
	for msm in fline: 
		fileline = msm.replace(" ","").replace("	","").upper()
		
		if "#DEFINENVMBASE" in fileline:
			index0 = fileline.find("0X")
			index1 = fileline.find(")",index0)
			index2 = fileline.find("UL",index0)
			index3 = fileline.find("U",index0)
			index4 = min(index1,index2,index3)
			print(index0,index1,index2,index3,index4)
			# print(fileline[index:])
		elif "#DEFINEEEPAGE_SIZE0X" in fileline:# 页大小
			EEPAGE_SIZE = int(fileline[20:23],16)
		elif "#DEFINEBACKUP_BLOCK_NUM"in fileline:# 备份页数 32
			BACKUP_BLOCK_NUM = int(fileline[23:25],10)
		elif "#DEFINETF_ADDR_CELL_SZIE"in fileline:# 6
			TF_ADDR_CELL_SZIE = int(fileline[24:25],10)
		elif "#DEFINETF_CELL_SZIE"in fileline:# 2
			TF_CELL_SZIE = int(fileline[19:20],10) 



		cnt +=1

	TF_SIZE= BACKUP_BLOCK_NUM * TF_CELL_SZIE
	RECORD_BUFFER_SIZE  = BACKUP_BLOCK_NUM * TF_ADDR_CELL_SZIE
	RECORD_BUFFER_TOTAL_SIZE = RECORD_BUFFER_SIZE + TF_SIZE
	TRANSACTION_BUFFER_SIZE = ((BACKUP_BLOCK_NUM + 1)  * EEPAGE_SIZE + RECORD_BUFFER_TOTAL_SIZE) 

	# if RECORD_BUFFER_TOTAL_SIZE > EEPAGE_SIZE:
	# 	TRANSACTION_BUFFER_START =  


	# if newsize is not None:	
	# 	fline[cnt] = t
	# 	fb = open(file,"w")
	# 	for l in fline:
	# 	    fb.write(l)
	# 	fb.close()
	# 	return None
	# else:
	# 	return t
	print(hex(TRANSACTION_BUFFER_SIZE))


print(getctarget(filetarget,None,None,None,None))
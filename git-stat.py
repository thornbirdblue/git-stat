#!/usr/bin/env python
#########################################################################################################
#	CopyRight	(C)	VIVO,2025		All Right Reserved!
#
#	Module:		git repo and scan log of author commit
#
#	File:		git-stat.py
#
#	Author:		liuchangjian
#
#	Date:		2015-10-15
#
#	E-mail:		liuchangjian@vivo.com.cn
#
###########################################################################################################

##########################################################################################################
#	Abstract:
#			1. select git branch
#			2. git log
#			3. author commit count
#			4. author commit info
#			5. save file
###########################################################################################################

###########################################################################################################
#	Recorder:
#			1. total: repo,total cnt;
#					  prople,totl cnt;
#			2. repo: branch people cnt,commit info		
#
##########################################################################################################

###########################################################################################################
#
#	History:
#
#	Name		Date		Ver		Act
#----------------------------------------------------------------------------------------------------------
#	liuchangjian	2015-10-15	v0.1		create
#	liuchangjian	2015-10-16	v0.1		git log function is ok!
#	liuchangjian	2015-10-16	v0.1		log statistics is ok
#	liuchangjian	2015-10-17	v0.1		Add xlsx file save
#	liuchangjian	2015-10-19	v0.1		Add repos stat output
#	liuchangjian	2015-10-19	v0.1		Add sheet chart
#	liuchangjian	2015-10-19	v0.9		Release test version 0.9
#	liuchangjian	2015-10-19	v1.0		Release ver 1.0 for camera system group!!!
#
###########################################################################################################

import sys,os,string,subprocess,re,xlsxwriter
from xlsxwriter.utility import xl_range_abs

reload(sys)
sys.setdefaultencoding('utf8')
# select branch
repo_select="vivo_"

# authors
group_authors=("liuchangjian")
authors_ci_count=dict.fromkeys(group_authors)

ScanPath=""
fileName = "ccsg_week_commit.xlsx"
weeks=""
remote_branch=""
select_author=""

# log var
debugLog = 0
debugLogLevel=(0,1,2,3)	# 0:no log; 1:op logic; 2:op; 3:verbose

#file format
branch_interval_lines=2
charts_interval_row=15

# git rec info
class GitRecInfo:
	RepoCntSum={}
	RepoBraCntSum={}
	AuthorCiSum={}
	ReposBranches={}

	__RepoBranchTitle=("Branches","Author","Commit Num","Commit info")
	
	def __GitLogCnt(self,info):
		patten = re.compile(r"\w{39}\s")
		commit = re.findall(patten,info)
		if debugLog >= debugLogLevel[-1]:
			print "parse list is ",commit
			print "Num is ",len(commit)
		return len(commit)		

	def __UpdateNum(self,rep,bra,aut,num):
		if debugLog >= debugLogLevel[-1]:
			print "Repo: ",rep,"Author: ",aut,"Num: ",num

		if self.RepoCntSum.has_key(rep):
			RCnt=self.RepoCntSum.get(rep)
			RCnt+=num
			self.RepoCntSum[rep]=RCnt
		else:
			self.RepoCntSum[rep]=num
		
		if debugLog >= debugLogLevel[-1]:
			print rep," Num: ",self.RepoCntSum[rep]

		if self.RepoBraCntSum.has_key(rep):
			bras=self.RepoBraCntSum.get(rep)

			if bras.has_key(bra):
				BCnt=bras.get(bra)
				BCnt+=num
				bras[bra]=BCnt
			else:
				bras[bra]=num
		else:
			bras={}
			bras[bra]=num
			self.RepoBraCntSum[rep]=bras

		if self.AuthorCiSum.has_key(aut):
			ACnt=self.AuthorCiSum.get(aut)
			ACnt+=num
			self.AuthorCiSum[aut]=ACnt
		else:
			self.AuthorCiSum[aut]=num
		
		if debugLog >= debugLogLevel[-1]:
			print aut," Num: ",self.AuthorCiSum[aut]

	# repo branch author log
	def AddOneRec(self,rep,bra,aut,info):
		if debugLog >= debugLogLevel[-1]:
			print "branch is ",bra,"author is ",aut
			print "info is:"
			print info

		self.__UpdateNum(rep,bra,aut,self.__GitLogCnt(info))
		
		dic={}
		dic[aut]=info
		if self.ReposBranches.has_key(rep):
			Branches=self.ReposBranches.get(rep)	
			if debugLog >= debugLogLevel[2]:
				print "Branches:",Branches.keys()

			if Branches.has_key(bra):
				data=Branches.get(bra)
				data.append(dic)
				if debugLog >= debugLogLevel[2]:
					print "Add Data:",dic
					print "Data data is ",data,"\n"
				
				Branches[bra]=data
			else:
				data=[]
				
				if debugLog >= debugLogLevel[2]:
					print "Add NEW branch: ",bra
					print "Add NEW Data:",dic

				data.append(dic)
				Branches[bra]=data

		else:
			Branches={}
			data=[]
			
			if debugLog >= debugLogLevel[2]:
				print "Add NEW Repo:",rep
			if debugLog >= debugLogLevel[-1]:
				print "NEW Branch: ",bra
				print "New Data is ",dic
			
			data.append(dic)

			Branches[bra]=data
			self.ReposBranches[rep]=Branches
	
	def SaveRepoStat(self,wb,ws_repo):
		row_num=0
		col_num=0

		#Save All repos
		if debugLog >= debugLogLevel[-1]:
			print "Repos:"
			print self.RepoCntSum
			
		repo_list = self.RepoCntSum.keys()
		for i in range(0,len(repo_list)):
			ws_repo.set_column(row_num,col_num,len(repo_list[i]))
			ws_repo.write(row_num,col_num,repo_list[i])
			col_num += 1

		row_num += 1												#!!!row + 1  counte save to next row
		col_num = 0
		repo_values = self.RepoCntSum.values()
		for i in range(0,len(repo_values)):
			ws_repo.write(row_num,col_num,repo_values[i])
			col_num += 1
		
		row_num += 1												#!!!row + 1 
		
		# Repos chart
		chart_repo = wb.add_chart({"type":"column"})
		chart_repo.set_style(11)

		repo_x_abs = xl_range_abs(0,0,0,len(repo_list)-1)
		repo_y_abs = xl_range_abs(1,0,1,len(repo_list)-1)
		rep_cat="="+ws_repo.get_name()+"!"+repo_x_abs
		rep_val="="+ws_repo.get_name()+"!"+repo_y_abs
		chart_repo.add_series({
			"categories":rep_cat,
			"values":rep_val
		})

		ws_repo.insert_chart(row_num,1,chart_repo)
		row_num += charts_interval_row

		row_num += 2
		col_num = 0
		
		#Save every repo branches info
		for x in self.RepoBraCntSum.items():
			if debugLog >= debugLogLevel[1]:
				print "Stat: Repo Branch:"
				print x
			ws_repo.write(row_num,col_num,x[0])
			col_num += 1
			
			branches_list = x[1].keys()
			for i in range(0,len(branches_list)):
				ws_repo.set_column(row_num,col_num,len(branches_list[i]))
				ws_repo.write(row_num,col_num,branches_list[i])
				col_num += 1

			row_num += 1											# counte save to next row
			col_num -= len(branches_list)

			branches_values = x[1].values()
			for i in range(0,len(branches_values)):
				ws_repo.write(row_num,col_num,branches_values[i])
				col_num += 1
			
			row_num += 1											# !!!row + 1

			# Save Branch Chart
			chart_branch = wb.add_chart({"type":"column"})
			chart_branch.set_style(11)
			bran_x_abs = xl_range_abs(row_num-2,1,row_num-2,len(branches_list))
			bran_y_abs = xl_range_abs(row_num-1,1,row_num-1,len(branches_values))
			bran_cat="="+ws_repo.get_name()+"!"+bran_x_abs
			bran_val="="+ws_repo.get_name()+"!"+bran_y_abs
			chart_branch.add_series({
				"categories":bran_cat,
				"values":bran_val
			})
		
			ws_repo.insert_chart(row_num,1,chart_branch)
			row_num += charts_interval_row

		row_num += 2
		col_num = 0

		# Save Author commit num info
		ws_repo.write(row_num,col_num,"Author:")
		row_num += 1
		ws_repo.write(row_num,col_num,"Commit Num:")
		row_num -= 1

		col_num += 1
		auth_list = self.AuthorCiSum.keys()
		for i in range(0,len(auth_list)):
			ws_repo.write(row_num,col_num,auth_list[i])
			col_num += 1

		row_num += 1												# counte save to next row
		col_num -= len(auth_list)
		auth_values = self.AuthorCiSum.values()
		for i in range(0,len(auth_values)):
			ws_repo.write(row_num,col_num,auth_values[i])
			col_num += 1

		row_num += 1												#!!! row + 1
		
		# Save Author Chart
		chart_author = wb.add_chart({"type":"column"})
		chart_author.set_style(11)
		
		auth_x_abs = xl_range_abs(row_num-2,1,row_num-2,len(auth_list))
		auth_y_abs = xl_range_abs(row_num-1,1,row_num-1,len(auth_values))
		auth_cat="="+ws_repo.get_name()+"!"+auth_x_abs
		auth_val="="+ws_repo.get_name()+"!"+auth_y_abs
		chart_author.add_series({
			"categories":auth_cat,
			"values":auth_val
		})
		
		ws_repo.insert_chart(row_num,1,chart_author)
		row_num += charts_interval_row

	def SaveRepo(self,wb,rep):
		if self.ReposBranches.has_key(rep):
			# add new sheet
			if len(rep)<=31:
				SheetName=rep
			else:	
				SheetName=rep[8:]		#del android_
				if len(SheetName)>31:
					SheetName=SheetName[0:30]

			if debugLog >= debugLogLevel[2]:
				print "Add worksheet:",rep,"Save sheet is:",SheetName
			ws = wb.add_worksheet(SheetName)	
		
			# get Repo info
			Repo=self.ReposBranches.get(rep)
			if Repo:
				row_num=0
				col_num=0
				BraAutCiCnt={}
			
				if debugLog >= debugLogLevel[2]:
					print "Repo info:"
					print Repo

				for i in self.__RepoBranchTitle:
					ws.write(row_num,col_num,self.__RepoBranchTitle[col_num])
					col_num+=1
				
				row_num+=1									#!!! row + 1
				col_num=0

				BranchesInfos = Repo.items()				#!!!Info!!!:Tuple(branch,list[dict])
				if debugLog >= debugLogLevel[-2]:
					print "Branches info:"
					print BranchesInfos,"\n"				#list

				for BraInfo in BranchesInfos:				
					if debugLog >= debugLogLevel[-2]:
						print "Branch info: "
						print BraInfo						#Tupple
			
					for Info in BraInfo:					# string and list
						if type(Info) is str:
							Branch=Info
							if debugLog >= debugLogLevel[2]:
								print "Sheet(",SheetName,")","Branch:",Branch
							ws.set_column(row_num,col_num,len(Branch))
							ws.write(row_num,col_num,Branch)
							col_num+=1

						elif type(Info) is list:
							cur_col=col_num
							for AutInfo in Info:			# -->dict
								author=AutInfo.keys()		# -->list	
								
								if debugLog >= debugLogLevel[-2]:
									print "Author Name: ",author

								ws.set_column(row_num,cur_col,len(author[0]))
								ws.write(row_num,cur_col,author[0])	# Save Author Name 
								cur_col+=1
								
								CiLog = AutInfo.values()
								patten = re.compile(r"\w{39}\s")
								CiInfo = re.findall(patten,CiLog[0])
								CiCnt = len(CiInfo)
						
								ws.write(row_num,cur_col,CiCnt)		# Save Ci Num
								cur_col+=1
								
								for x in CiLog:
									if debugLog >= debugLogLevel[-2]:
										print " Commit info: "
										print x
									ws.write(row_num,cur_col,x)			# Save Ci Log
									row_num += 1						#!!! Row + 1!!!
									cur_col += 1

								cur_col=col_num
							
							# Save Author Commit Num Chart
							chart_author_ci = wb.add_chart({"type":"column"})
							chart_author_ci.set_style(11)
		
							auth_x_abs = xl_range_abs(row_num-len(Info),col_num,row_num,col_num)
							auth_y_abs = xl_range_abs(row_num-len(Info),col_num+1,row_num,col_num+1)
							auth_cat="="+ws.get_name()+"!"+auth_x_abs
							auth_val="="+ws.get_name()+"!"+auth_y_abs
							chart_author_ci.add_series({
								"categories":auth_cat,
								"values":auth_val
							})
		
							ws.insert_chart(row_num,col_num,chart_author_ci)
							row_num += charts_interval_row
						else:
							print "ERROR: Branches info in not Branch name and Author commit info:"
							print Info
							print "Type is ",type(Info)

					col_num = 0
					row_num += branch_interval_lines		# Add lines interval


		else:
			print "WARNING: NO repo",rep," info"
		
# abstract log of one branch
def deal_branch(repo,branch_list,GitR):
	if debugLog >= debugLogLevel[-1]:
		print "Cur Repo: ",repo

	for branch in branch_list:
		if debugLog >= debugLogLevel[-2]:
			print "Branch is "+branch
		try:
			os.system('git checkout -q -f ' + branch)
			os.system('git pull -q ')
		except Exception, error:
			print error
	   
		if select_author:
			global group_authors
			group_authors=[select_author]
			if debugLog >= debugLogLevel[-1]:
				print "group authors is",group_authors

		for author in group_authors:
			cmd_git_log=["git","log","--pretty=oneline"]
			
			cmd_git_log.append("--author="+author)

			if weeks:												#add sinc weeks
				cmd_git_log.append("--since="+str(weeks)+".weeks")
			
			if debugLog >= debugLogLevel[-1]:
				print cmd_git_log
	
			proc = subprocess.Popen(cmd_git_log,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			stdout, stderr = proc.communicate()
			if stdout:
				if debugLog >= debugLogLevel[-1]:
					print "git log is :"
					print stdout
				
				GitR.AddOneRec(repo,branch,author,stdout)

# get all branches of a project
def get_branches():
    branch_list = []
    branches = []
    tmp_str = ''
    try:
        cmd_git_remote = 'git remote show origin'
        proc = subprocess.Popen(cmd_git_remote.split(),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if debugLog >= debugLogLevel[-2]:
			print stdout
        tmp_str = stdout.split('Local branches configured')[0]
        try:
            tmp_str = tmp_str.split('Remote branches:\n')[1]
        except:
            tmp_str = tmp_str.split('Remote branch:\n')[1]
        branches = tmp_str.split('\n')
        for branch in branches[0:-1]:
            if re.search(' tracked', branch) is not None:
                branch = branch.replace('tracked', '').strip(' ')
                if remote_branch:
                    if branch == remote_branch:
                        branch_list.append(branch)
                else:
                    if re.match(repo_select,branch) is not None:
	                	branch_list.append(branch)

    except Exception, error:
        if branch_list == []:
            print "Can not get any branch!"
    return branch_list


def GoToDir(path):
	GitRec=GitRecInfo()
		
	workbook=xlsxwriter.Workbook(fileName)

	ws_repo=workbook.add_worksheet("Repo")
		
	for file in os.listdir(path):
		if os.path.isdir(file):
			if debugLog >= debugLogLevel[-2]:
				print "Dir is "+file
			
			os.chdir(file)
				
			branch_list = get_branches()

			if branch_list:
				if debugLog >= debugLogLevel[-2]:
					print "Branches is ",branch_list
					
				deal_branch(file,branch_list,GitRec)

			# save repo
			GitRec.SaveRepo(workbook,file)

	#Save Repo stat
	GitRec.SaveRepoStat(workbook,ws_repo)

	#!!! change to cur dir
	os.chdir(path)
	
	# save xlsx file
	workbook.close()

def ParseArgv():
	if not len(sys.argv):
		return

	for i in range(1,len(sys.argv)):
		if sys.argv[i] == '-h':
			Usage()
			sys.exit()
		elif sys.argv[i] == '-d':
			if sys.argv[i+1]:
				debug = string.atoi(sys.argv[i+1],10)
				if type(debug) == int:
					global debugLog
					debugLog = debug						
					print 'Log level is: '+str(debugLog)
				else:
					print 'cmd para ERROR: '+sys.argv[i+1]+' is not int num!!!'
			else:
				CameraOpenKPIHelp()
				sys.exit()
		elif sys.argv[i] == '-w':
			if sys.argv[i+1]:
				w_num = string.atoi(sys.argv[i+1],10)
				if type(w_num) == int:
					global weeks
					weeks = w_num						
					print 'Statistics weeks: '+str(weeks)
				else:
					print 'cmd para ERROR: '+sys.argv[i+1]+' is not int num!!!'
			else:
				CameraOpenKPIHelp()
				sys.exit()
		elif sys.argv[i] == '-o':
			if sys.argv[i+1]:
				global fileName
				fileName = sys.argv[i+1]
				print 'OutFileName is '+fileName
			else:
				Usage()
				sys.exit()
		elif sys.argv[i] == '-a':
			if sys.argv[i+1]:
				global select_author
				select_author = sys.argv[i+1]
				print 'stat author is '+select_author
			else:
				Usage()
				sys.exit()
		elif sys.argv[i] == '-b':
			if sys.argv[i+1]:
				global remote_branch
				remote_branch = sys.argv[i+1]
				print 'stat remote branch is '+remote_branch
			else:
				Usage()
				sys.exit()
		elif sys.argv[i] == '-p':
			if sys.argv[i+1]:
				global ScanPath
				ScanPath = sys.argv[i+1]
				print 'Scan dir path is '+ScanPath
			else:
				Usage()
				sys.exit()
					

def Usage():
	print 'Command Format :'
	print '		git-stat [-d 1/2/3] [-o outputfile] [-p path] [-w weeks] [-a author] [-b remote_branch]| [-h]'


if __name__ == '__main__':
	ParseArgv()

	if not ScanPath.strip():
		spath = os.getcwd()
	else:
		spath = ScanPath
	
	print 'Scan DIR: '+spath+'\n'

	GoToDir(spath)

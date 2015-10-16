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
#
###########################################################################################################

import sys,os,string,subprocess,re

# select branch
repo_select="vivo_"

# authors
group_authors=("xiongchen","wangkangkang")
authors_ci_count=dict.fromkeys(group_authors)

ScanPath=""
fileName = "ccsg_week_commit.xls"
weeks=1
remote_branch=""
select_author=""

# log var
debugLog = 0
debugLogLevel=(0,1,2,3)	# 0:no log; 1:op logic; 2:op; 3:verbose

# git rec info
class GitRecInfo:
	RepoCntSum={}
	AuthorCiSum={}
	ReposBranches={}
	
	def __GitLogCnt(self,info):
		patten = re.compile(r"\w{39}\s")
		commit = re.findall(patten,info)
		if debugLog >= debugLogLevel[-1]:
			print "parse list is ",commit
			print "Num is ",len(commit)
		return len(commit)		

	def __UpdateNum(self,rep,aut,num):
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

		if self.AuthorCiSum.has_key(aut):
			ACnt=self.AuthorCiSum.get(aut)
			ACnt+=num
			self.AuthorCiSum[aut]=ACnt
		else:
			self.AuthorCiSum[aut]=num
		
		if debugLog >= debugLogLevel[-1]:
			print aut," Num: ",self.AuthorCiSum[aut]

	def AddOneRec(self,rep,bra,aut,info):
		if debugLog >= debugLogLevel[-1]:
			print "branch is ",bra,"author is ",aut
			print "info is:"
			print info

		self.__UpdateNum(rep,aut,self.__GitLogCnt(info))
		
		dic={aut:info}
		if self.ReposBranches.has_key(rep):
			Branches=self.ReposBranches.get(rep)	
			if debugLog >= debugLogLevel[-1]:
				print "Branch data is ",Branches

			if Branches.has_key(bra):
				data=Branches.get(bra)
				if debugLog >= debugLogLevel[-2]:
					print "Data data is ",data,"\n"
				data.append(dic)
			
				Branches[bra]=data
				self.ReposBranches[rep]=Branches
			else:
				Branch={}
				data=[]
				
				if debugLog >= debugLogLevel[1]:
					print "Add NEW branch: ",bra

				data.append(dic)
				Branch[bra]=data
				self.ReposBranches[rep]=Branch

		else:
			Branches={}
			data=[]
			
			if debugLog >= debugLogLevel[1]:
				print "Add NEW Repo:",rep,"NEW Branch: ",bra
			
			data.append(dic)

			Branches[bra]=data
			self.ReposBranches[rep]=Branches

# abstract log of one branch
def deal_branch(repo,branch_list,GitR):
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
			cmd_git_log=["git","log","--pretty=oneline"]#,"--since="+str(weeks)+".weeks"]
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

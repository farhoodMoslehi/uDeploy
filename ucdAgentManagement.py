'''
Created on May 01, 2018

@author: Farhood Moslehi

Version 1.0
'''


import os
import sys
import fnmatch
import subprocess
import time
import platform
if platform.system() != "Windows":
    
    import pwd
    import grp 
   
    
staticVariable=False

def setGlobal(varBoolean):
    global staticVariable
    staticVariable=varBoolean
def getGlobal():
    return staticVariable

'''
This method is used to find out the OS being used
'''

def checkplatform():
    wsubstring='Window'
    lsubstring='Linux'
    varos=platform.system()
    if (wsubstring in varos):
        pForm='Windows'
    elif (lsubstring in varos):
        pForm='Linux'
    else:
        pForm='neither'
           
    return pForm

'''
This is the main class for the agent management operation. It searches and finds all instances of the agents given the parameters
'''
    
class AgentManagement(object):
    
    
    cVar=''
    commandDict ={}
    commandList=[]
    installs=[]
    var=''
    StartFolderW=''
    
    def __init__(self, cVar):
        
        self.cVar= cVar
        
        return

    def parseCommand(self):
        
        self.commandList=self.cVar.split(',')
        
        for var in self.commandList:
            varTemp=var.split('==')
            '''
            print (varTemp[0],varTemp[1])
            '''
            self.commandDict.update({varTemp[0]:varTemp[1]})
       
        return 
    
    def getcommandDict(self):
        
        return self.commandDict

    def getInstalls(self):
        
        return self.installs
    
    def FindAllPathsW(self,StartFolderW):
        
        '''
        This method is used by Windows to look for all installed.properties files
        The method returns a list of all the files with their respective full paths
        '''
    
        self.StartFolderW=[StartFolderW]
    
                
        for self.folder in self.StartFolderW:
            self.StartFolder=self.folder
            
            self.rootdir=self.StartFolder
      
    
            for self.root, self.subFolders, self.files in os.walk(self.rootdir):
            
                for self.file in fnmatch.filter(self.files,'installed.properties'):
                    self.var=os.path.join(self.root,self.file)
                    #print ('file',self.file)
                    #print self.var
                    self.installs.append(self.var)
                
    
        return self.installs  
        
    def getLogclass(self,dirPath): 
        
        
        self.ldirpath=dirPath
        print (self.ldirPath)
        
        return 

'''
This method is used by the get log method to read the contents of a file
'''    
        
def ReadDataFromFile(filename):
#---------------------------------------------------------------------------------------------------
# method to read data from a file
#---------------------------------------------------------------------------------------------------
    
    fileData=[]
    
    try:

        f = open(filename)

        for line in f:

            fileData.append(line)

        f.close()

    except IOError:
        print('File '+ filename +' Could not be found')
    
    return fileData

#---------------------------------------------------------------------------------------------------

def printfile(fileName):
#---------------------------------------------------------------------------------------------------
# method to print to the screen any list that is passed to it
#---------------------------------------------------------------------------------------------------
    outputfile=[]
    print('---------------------------------------------------')
    print(fileName)
    print('---------------------------------------------------')
       
    
    try:

        f = open(fileName)

        for line in f:

            outputfile.append(line)

        f.close()

    except IOError:
        print('File '+ fileName +' Could not be found')
    
    NumberOfLines=len(outputfile)
    
    
    if NumberOfLines < 50:
        for line in outputfile:
            print line
    else:
        for LineCounter in range(NumberOfLines-50,NumberOfLines):
            print outputfile[LineCounter]
    return

'''
This method is the main method for getting and displaying the agent.out and installed.properties logs.
if the agent.out log is more than 50 lines, the method only displays the last 50 lines
'''

def getLog(ucdAgent):  
    
    #print ('getlog ',ucdAgent.getcommandDict().get('directory'))
    
    
    if ucdAgent.getcommandDict().get('directory') =='':
        print ('no parent directory name was passed')
         
    else:
        #print ('getlog and going to find paths')
        ucdAgent.FindAllPathsW(ucdAgent.getcommandDict().get('directory'))
        #print (ucdAgent.getInstalls())
        #print(ucdAgent.getInstalls()[0])
        for agentHome in ucdAgent.getInstalls():
            printfile(agentHome)
            agentOutLogT=agentHome.split('conf')
            agentOutLog=agentOutLogT[0]+'var/log/agent.out'
            printfile(agentOutLog)
        
    
    return

'''
This method finds the user accounts of the installed.properties file for linux
'''

def ugIds(filename):

    resultArray=[]
    st=os.stat(filename)
    userinfo = pwd.getpwuid(st.st_uid)
    ownername = pwd.getpwuid(st.st_uid).pw_name
    resultArray.append(ownername)
    gid=pwd.getpwnam(ownername).pw_gid
    group=grp.getgrgid(gid).gr_name
    resultArray.append(group)

    return resultArray

'''
This method is used my the main linux restart platform to start a linux agent
'''

def StartLinuxAgent(agentDirectory,startId):
    
    
    AgentCode=0
    ReturnCode1=True
    
    try:
        os.chdir(agentDirectory)
        os.chdir('../..')
        os.chdir('bin')
        manageAgent=os.getcwd()+"/agent "
        actionStop=manageAgent+"stop"
        AgentCode= subprocess.call(["su", "-", startId, "-c", actionStop])
        time.sleep(5)
        actionStart=manageAgent+"start"
        AgentCode= subprocess.call(["su", "-", startId, "-c", actionStart])
        setGlobal(True)
    except:
        ReturnCode1=False
    if AgentCode==1:
        ReturnCode1=False    
    
    return ReturnCode1

'''
This method is the main method to start a Linux agent, it uses the StartLinuxAgent to start the agent
'''

def restartLinuxPlatform(ucdAgent): 
    
    if ucdAgent.getcommandDict().get('directory') =='':
        print ('no parent directory name was passed')
         
    else:
        ucdAgent.FindAllPathsW(ucdAgent.getcommandDict().get('directory'))
        if len(ucdAgent.getInstalls()) != 0: 
            
            for agentHome in ucdAgent.getInstalls():
                print (agentHome)
                usernameId=ugIds(agentHome)[0]
                groupnameId=ugIds(agentHome)[1]
                cmdStr='chown '+usernameId+':'+groupnameId+' '+agentHome
                os.system(cmdStr) 
                AgentDirectory=agentHome.split('/installed.properties')
                ReturnValueStartLinuxAgent=StartLinuxAgent(AgentDirectory[0],usernameId)
                if ReturnValueStartLinuxAgent == False:
                    print "There was a problem with the Agent start"
            
        else:
            print ('no installed.properties file exist on this server')
               
    return 'Return from Linux' 

'''
This method will start the windows service using the service name extracted from the installed.properties file
'''
def StartWindowsService(ServiceName):
    ReturnCode1=False
    
    CommandArg='sc stop '+ServiceName
    os.system(CommandArg)
    time.sleep(5)
    CommandArg='sc start '+ServiceName
    os.system(CommandArg)
    setGlobal(True)
    return ReturnCode1

'''
This method finds teh service name for windows from the installed.properties file
'''

def ReturnServiceNameForWindows(filename):
    
    ReturnCode1=False
    
    f = open(filename,'r')
    LocalServiceName=''
    for line in f:
    
        if 'service.name' in line:
            servicename=line.split("=")
            
            LocalServiceName=servicename[1].rstrip()
            ReturnCode1=True
    f.close
    return LocalServiceName, ReturnCode1
'''
This is the main method to restart a windows agent. It calls the Return ServiceNmeFor Windows method and StartWindowsService method
'''

def restartWindowsPlatform(ucdAgent):
    
    if ucdAgent.getcommandDict().get('directory') =='':
        print ('no parent directory name was passed')
         
    else:
        ucdAgent.FindAllPathsW(ucdAgent.getcommandDict().get('directory'))
        if len(ucdAgent.getInstalls()) != 0:     
    
            for agentHome in ucdAgent.getInstalls():
                          
                ReturnValuesServiceNameForWindows=ReturnServiceNameForWindows(agentHome)
               
                if (ReturnValuesServiceNameForWindows[1]):
                    StartWindowsService(ReturnValuesServiceNameForWindows[0])
                else:
                    print "No Service name was found in the installed.properties file"
              
        
    return 'Return from windows'

'''
This method is used by both Linux and windows to replace a string within installed.properties file
'''
def replaceString(filename,lvarString):
    
    mResult=True
    try:
        
        '''
        print(filename)
        print(lvarString[0],lvarString[1])
        '''
        f = open(filename,'r')
        filedata=f.read()
        f.close
        print(filedata)
        
        newdata=filedata.replace(lvarString[0],lvarString[1])
        f=open(filename,'w')
        f.write(newdata)
        f.close()
            
        if (filedata.find(lvarString[0]) == -1):
            print ('For file ',filename, '   ', lvarString[0], 'not found')
            mResult=False
        else:
            f=open(filename + '_relaybackup','w+')
            f.write(filedata)
            f.close() 
        
    
        
        
    except:
        print('the replace string provided is not in the correct format')
    
    return mResult

'''
This is the main method to replace any part of the installed.properties file.
This method calls replaceString method 
'''

def mainReplace(ucdAgent):
    
    lvarString=ucdAgent.getcommandDict().get('replace').split('--')
    print(lvarString[0],lvarString[1])
    try:
        lvarString=ucdAgent.getcommandDict().get('replace').split('--')
        print(lvarString[0],lvarString[1])
        ucdAgent.FindAllPathsW(ucdAgent.getcommandDict().get('directory'))
        
        for agentHome in ucdAgent.getInstalls():
            replaceString(agentHome,lvarString) 
            
            if checkplatform() !='Windows' :
                usernameId=ugIds(agentHome)[0]
                groupnameId=ugIds(agentHome)[1]
                cmdStr='chown '+usernameId+':'+groupnameId+' '+agentHome
                os.system(cmdStr)
                   
    except:
        print('the replace string provided is not in the correct format or the installed.properties file has an incorrect format')
    
    
    return

'''
This is the main method, program execution begins here
'''
def main(lVarCommand):

    
    print (lVarCommand)
    
    ucdAgent=AgentManagement(lVarCommand)
    #print('class variable  ',ucdAgent.cVar)
    
    
    try:
        ucdAgent.parseCommand()
        
        #print ('here    ',ucdAgent.getcommandDict().get('log'))
        #print ('here    ',ucdAgent.getcommandDict().get('directory'))
        
        if 'log' in ucdAgent.getcommandDict():
            if ucdAgent.getcommandDict().get('log') == 'yes':
                getLog(ucdAgent)
                #FindAllPathsW('c:/temp')
                #ucdAgent.FindAllPathsW('C:/temp')
        if 'restart' in ucdAgent.getcommandDict():
            if ucdAgent.getcommandDict().get('restart') =='yes':
                if checkplatform() !='Windows' :
                    restartLinuxPlatform(ucdAgent)
                else:
                    restartWindowsPlatform(ucdAgent)
        if 'replace' in ucdAgent.getcommandDict():
            if ucdAgent.getcommandDict().get('replace') != '':
            #replaceString (ucdAgent.getcommandDict().get('replace'))
                mainReplace(ucdAgent)
            else:
                print('the replace string provided is blank')
    except:
        print('the format of the input is not correct, please refer to the documentation for the correct format')
    
       
    return




if __name__ == '__main__':
    
    try:
        args=sys.argv[1:]
    
        print len(args)
        varCommand=''
        '''
        if len(args)>1:
            print('You need to pass your input data without any blank characters')
            break
        ''' 
        for x in args:
            varCommand +=str(x)
            
    except:
    
        print 'Input error'
       
        sys.exit()
        
    
    print(varCommand)
    main(varCommand)

    '''
    varCommand='log==no,restart==no,directory==/apps/udeploy/agent_udeploy,replace==UCD_ILT']--UCD_ILT'
    main(varCommand)
    '''
   

print('program terminated as expected')





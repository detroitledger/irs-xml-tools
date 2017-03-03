import json
import requests
import xmltodict
import pandas 
import re
import csv


def ListFromIRSIndex(pathOfIndex):
	#Given a local path to an IRS 990 index json file, output its entries as a list
	infile = open(pathOfIndex,'r')
	dic = json.loads(infile.read())
	Year=dic.keys()[0]
	infile.close()
	lis=dic[Year]
	return lis

def GetEinFromOrg(pathOfCsv):
	#Given a local path to organizations.csv file, output a dictionary, with id as key,org_name and EIN as values
	infile=pandas.read_csv(pathOfCsv,dtype={'EIN': str})
	df =  infile.loc[:,['Id','EIN','Org_name']].dropna()
	dicOrgEIN= df.set_index('Id').T.to_dict()
	return dicOrgEIN


def GetEINfromDic(dic):
	#Input:a dictionary, with id as key,org_name and EIN as values from organizations.csv
	#Output: set of 'EIN'
	listEIN=[]
	for n in dic.keys():
		listEIN.append(dic[n]['EIN'])
	return set(listEIN)

	

set2= GetEINfromDic(GetEinFromOrg('organizations.csv'))


def FliterList(list1,set2):
#	Given a IRS 990 index list and a set of EINs (numbers), output a list only the entries that match those given EINs.
	seq=filter(lambda x:(x['EIN'] in set2),list1)
	return seq

# finalFilterAllYear={}
# for n in range(2011,2018):
# 	finalFilterAllYear[n] = FliterList(ListFromIRSIndex('index_'+str(n)+'.json'),set2)
# 	outfile=open('finalFilterYear'+str(n)+'.json','w')
# 	outfile.write(json.dumps(finalFilterAllYear[n]))
# 	outfile.close()
	


def GetEINwXML(jsonlist):
	#Take a local path of Json List of all filtered organizations and return the a list of dictionay, of EIN and their XML file link
	#return [{EIN:"1234", 'URL':'https....XML'} , {EIN:"2345", 'URL':'https'} ]

	# infile = open(jsonlist,'r')
	# JsonListOfOrg=json.loads(infile.read())
	# reducedInfoListOfOrg=[]

	JsonListOfOrg=jsonlist
	reducedInfoListOfOrg=[]
	for n in JsonListOfOrg:
		dicOrg={}
		dicOrg["EIN"]=n["EIN"]
		dicOrg["URL"]=n["URL"]
		reducedInfoListOfOrg.append(dicOrg)
	
	#infile.close()
	return reducedInfoListOfOrg

 

def GetScheduleI(lis,year):
	lsScheduleI=[]
	count = 1
	lsVersion=[]
	versionXMLInstance=[]
	for n in lis:
		baseurl =n[u'URL']
		req = requests.get(baseurl)
		req2 = req.content.decode("utf-8-sig").encode("utf-8")
		
		if req2.find('IRS990ScheduleI') == -1: #Check if there is IRS990ScheduleI. if not, skip that EIN
			continue
		
		try:
			pattern = re.compile(ur'returnVersion.*(20[01][0-9]v[0-9.]+)', re.UNICODE)
			version= pattern.search(req2).group(1)
		except:
			print "Didn't find the return Version from XML : "+baseurl
			# Check the url link and modify the reg expression

		d = xmltodict.parse(req2)		
		dicInstance={}



		VersionSet=set(['2009v1.2', '2009v1.3', '2009v1.7', '2009v1.4', '2012v2.1', '2012v2.0', '2012v2.3', '2012v2.2', '2011v1.5', '2011v1.3', '2011v1.2', '2010v3.6', '2010v3.7', '2010v3.4', '2010v3.2'])
			
		try:
			dicInstance['EIN']=d['Return']['ReturnHeader']['Filer']['EIN']
			dicInstance['RecipientDic']=d['Return']['ReturnData']['IRS990ScheduleI']
		 	if version in VersionSet:
		 		dicInstance['OrgName']=d['Return']['ReturnHeader']['Filer']['Name']['BusinessNameLine1']
		 		dicInstance['TaxPeriodBeginDt']=d['Return']['ReturnHeader']['TaxPeriodBeginDate']
		 		dicInstance['TaxPeriodEndDt']=d['Return']['ReturnHeader']['TaxPeriodEndDate']
		 		
		 	elif version in ['2013v3.1','2013v3.0','2013v4.0']:
				dicInstance['OrgName']=d['Return']['ReturnHeader']['Filer']['BusinessName']['BusinessNameLine1']
				dicInstance['TaxPeriodBeginDt']=d['Return']['ReturnHeader']['TaxPeriodBeginDt']
				dicInstance['TaxPeriodEndDt']=d['Return']['ReturnHeader']['TaxPeriodEndDt']
				
			elif version in ['2014v5.0','2014v6.0','2015v2.1']:
				dicInstance['OrgName']=d['Return']['ReturnHeader']['Filer']['BusinessName']['BusinessNameLine1Txt']
				dicInstance['TaxPeriodBeginDt']=d['Return']['ReturnHeader']['TaxPeriodBeginDt']
				dicInstance['TaxPeriodEndDt']=d['Return']['ReturnHeader']['TaxPeriodEndDt']
				
			
			else:
		 		dicInstance['OrgName']=d['Return']['ReturnHeader']['Filer']['BusinessName']['BusinessNameLine1']
		 		dicInstance['TaxPeriodBeginDt']=d['Return']['ReturnHeader']['TaxPeriodBeginDate']
		 		dicInstance['TaxPeriodEndDt']=d['Return']['ReturnHeader']['TaxPeriodEndDate']
		 		
			

		except:
		 	print 'No parser for version: '+ version
		 	print "It's corresponding baseurl is " + baseurl
		lsScheduleI.append(dicInstance)


	return lsScheduleI
	#return a list of dictionary: ['EIN': ,  ''RecipientDic'': , 'OrgName': , 'TaxPeriodBeginDt': , ''TaxPeriodEndDt']
	# with open('lsScheduleI'+str(year)+'.json', 'w') as f:
	# 	f.write(json.dumps(lsScheduleI))



def FinalCsv(listJson,year):
	GrantId = int(str(year)+str(1000))
	lsGrant=[]

	re3=json.dumps(listJson)
	re3=re3.replace('BusinessNameLine1Txt','BusinessNameLine1').replace('RecipientBusinessName', 'RecipientNameBusiness').replace('RecipientEIN', 'EINOfRecipient').replace('CashGrantAmt','AmountOfCashGrant').replace('CashGrantAmt','AmountOfCashGrant').replace('PurposeOfGrantTxt','PurposeOfGrant')
	lis=json.loads(re3)

	for Org in lis:
		fromName=Org['OrgName']
		fromEIN = Org['EIN']
		stratYear=Org['TaxPeriodBeginDt']
		endYear=Org['TaxPeriodEndDt']

		
		try:
			if type(Org['RecipientDic']['RecipientTable'])==list:
				for Grant in Org['RecipientDic']['RecipientTable']:
			
					toName=Grant['RecipientNameBusiness']['BusinessNameLine1']
					toEIN=Grant['EINOfRecipient']
					amount=Grant['AmountOfCashGrant']
					description =Grant['PurposeOfGrant']
					oneGrant=[GrantId,toName,fromName,amount,toEIN,fromEIN,stratYear,endYear,description]
					GrantId+=1
					lsGrant.append(oneGrant)
			elif type(Org['RecipientDic']['RecipientTable'])==dict:
				Grant = Org['RecipientDic']['RecipientTable']
				toName=Grant['RecipientNameBusiness']['BusinessNameLine1']
				toEIN=Grant['EINOfRecipient']
				amount=Grant['AmountOfCashGrant']
				description =Grant['PurposeOfGrant']
				oneGrant=[GrantId,toName,fromName,amount,toEIN,fromEIN,stratYear,endYear,description]
				GrantId+=1
				lsGrant.append(oneGrant)
		except:
			#There are some entries in ScheduleI we don't catch right now:
			# a. NonCashAssistance
			# b. Assistance to individuals without EIN
			# This command will print them out.
			print json.dumps(Org,indent =2)

	with open("finalResult"+str(year)+".csv", 'w') as f:
		writer = csv.writer(f)
		writer.writerow(['GrantId','toName','fromName','amount','toEIN','fromEIN','stratYear','endYear','description'])
		for oneGrant in lsGrant:
	 		writer.writerow(oneGrant)
    	


#for n in range(2017,2018):
for n in range(2011,2018):
	finalFilterAllYear = FliterList(ListFromIRSIndex('index_'+str(n)+'.json'),set2)
	afile = GetScheduleI(GetEINwXML(finalFilterAllYear),n)
	FinalCsv(afile,n)





#All different version for 
#2017 ['2015v2.1']
#2016 ['2014v5.0', '2013v4.0', '2014v6.0', '2015v2.1']
#2015 ['2014v5.0', '2013v4.0']
#2014 ['2013v3.1', '2013v3.0', '2012v2.1', '2012v2.3', '2012v2.0', '2011v1.5']
#2013 ['2011v1.5', '2011v1.2', '2012v2.1', '2012v2.0', '2012v2.2', '2012v2.3']
#2012 ['2011v1.2', '2011v1.3', '2010v3.4', '2009v1.7', '2010v3.6', '2010v3.2', '2010v3.7']
#2011 ['2010v3.4', '2009v1.4', '2009v1.7', '2009v1.3', '2009v1.2', '2010v3.2']

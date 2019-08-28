from flask import Flask,render_template,request,send_from_directory,session,redirect,url_for,json,jsonify
import mysql.connector
import numpy as np
from mysql.connector import Error
import os,sys
from datetime import datetime
app=Flask(__name__)

mypath=app.root_path
newpath = mypath+"/dbpy"
sys.path.insert(0, newpath)

newpath = mypath+"/pyfiles"
sys.path.insert(0, newpath)

newpath = mypath+"/pyfiles/REGISTRATION"
sys.path.insert(0, newpath)
newpath = mypath+"/pyfiles/outpatient"
sys.path.insert(0, newpath)
newpath = mypath+"/pyfiles/inpatient"
sys.path.insert(0, newpath)
newpath = mypath+"/pyfiles/Helper"
sys.path.insert(0, newpath)
newpath = mypath+"/pyfiles/admin"
sys.path.insert(0, newpath)
newpath = mypath+"/pyfiles/Lab"
sys.path.insert(0, newpath)
newpath = mypath+"/pyfiles/ward"
sys.path.insert(0, newpath)
newpath = mypath+"/pyfiles/chartdata"
sys.path.insert(0, newpath)
newpath = mypath+"/pyfiles/medicine"
sys.path.insert(0, newpath)
newpath = mypath+"/pyfiles/Billing"
sys.path.insert(0, newpath)
newpath = mypath+"/pyfiles/Xray"
sys.path.insert(0, newpath)
newpath = mypath+"/pyfiles/ANC"
sys.path.insert(0,newpath)
newpath = mypath+"/pyfiles/portal"
sys.path.insert(0,newpath)



import registration as reg
import outvisit as opd
import ipd as ipd
import adminstuff as adm
import lab as lab
import wardstuff as wrd
import myHelper as hm,db_conf as con
import chartdata as chart
import medicine as med
import medbilling as mbill
import xray
import opdbilling as obill
import anc
import patientPortal as pp




#access to database connection
db=con.db
#prepare cursor object using cursor() method
cursor=db.cursor()

app.config['SECRET_KEY'] = 'my details secret!'
app.config['UPLOAD_FOLDER_OPD']=app.root_path+'/static/docuploads/'
app.config['DLOAD_FOLDER']=app.root_path+'/static/docuploads/'
app.config['UPLOAD_FOLDER_XRAY']=app.root_path+'/static/XrayUploads/'
app.config['DLOAD_FOLDER_XRAY']=app.root_path+'/static/XrayUploads/'
app.config['UPLOAD_FOLDER_ANC']=app.root_path+'/static/ANCUploads/'
app.config['DLOAD_FOLDER_ANC']=app.root_path+'/static/ANCUploads/'
app.config['UPLOAD_FOLDER_EXRAY']=app.root_path+'/static/XrayExcel/'
app.config['DLOAD_FOLDER_EXRAY']=app.root_path+'/static/XrayExcel/'
app.config['UPLOAD_FOLDER_MEDICINE']=app.root_path+'/static/MedicineUploads/'
app.config['DPLOAD_FOLDER_MEDICINE']=app.root_path+'/static/MedicineUploads/'
app.config['UPLOAD_FOLDER_DEL']=app.root_path+'/static/DeliveryUploads/'
app.config['DLOAD_FOLDER']=app.root_path+'/static/DeliveryUploads/'
app.config['UPLOAD_FOLDER_OPD']=app.root_path+'/static/OpdUploads/'
app.config['DLOAD_FOLDER']=app.root_path+'/static/OpdUploads/'
app.config['UPLOAD_FOLDER_IPD']=app.root_path+'/static/IpdUploads/'
app.config['DLOAD_FOLDER']=app.root_path+'/static/IpdUploads/'
app.config['UPLOAD_FOLDER_LAB']=app.root_path+'/static/LabUploads/'
app.config['DLOAD_FOLDER']=app.root_path+'/static/LabUploads/'
app.config['UPLOAD_FOLDER_SURG']=app.root_path+'/static/SurgeryUploads/'
app.config['DLOAD_FOLDER']=app.root_path+'/static/SurgeryUploads/'


@app.route('/uploads/<filename>',methods=['GET'])
def view_attachment(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER_OPD'],filename)

@app.route('/excel/<filename>',methods=['GET'])
def view_attachment2(filename):
	return send_from_directory(app.config['DLOAD_FOLDER'],filename)

    #default route
    #This method redirects to homepage of corresponding usertype if user is already logged in, else render 'login.html' page.
    #This may also get a error code.

@app.route('/',methods=['GET'])
def login():
	errorcode=request.args.get('error')
	page='login/login.html'
	if session.get('logged_in')==True:
		page=hm.getUserHomePage(session)
	return render_template(page,error=errorcode,alerMsg="You Already Loged in",pa='pas')

@app.route('/home', methods=['GET','POST'])
def home():
	if session.get('logged_in')==True:
		alerMsg="You Already Loged in"
		page=hm.getUserHomePage(session)
		return render_template(page,alerMsg=alerMsg,pa='pas',msg1=' ',msg='main' )
	if request.method=='POST':
		username=request.form['username']
		password=request.form['password']
		try:
			sql="SELECT eid from users where username='{}' and password='{}'".format(username,password)
			cursor.execute(sql)
			data=cursor.fetchall()
			if(len(data)==0):
				return redirect(url_for('login',error='1'))
			else:
				sql = "select ename,emptype from employee where eid='{}'".format(data[0][0])
				print(sql)
				cursor.execute(sql)
				edata = cursor.fetchone()
				session['logged_in']=True
				session['name'] = str(edata[0]).upper()
				session['usertype'] = str(edata[1]).upper()
				page=hm.getUserHomePage(session)
				msg1=' '
				usr=edata[0]
				return render_template(page,msg1=msg1,usr=usr,pa='test',msg='main')
		except Error as e:
			print(e)
			return redirect(url_for('login',error='2'))
	return redirect(url_for('login'))

@app.route('/logout')
def logout():
	#unsetting session variables
	session.pop('name',None)
	session.pop('username',None)
	session.pop('usertype',None)
	session.pop('logged_in',None)
	return render_template('login/login.html',error='3')

##--------------GENERAL CODE-------------------

##---------Patient Portal------------------

@app.route('/patientPortal_Redir',methods=['GET','POST'])
def patientPortal_Redir():
	return render_template('/mainpage/patientPortal_Redir.html',ack='')

@app.route('/patientPortal',methods=['GET','POST'])
def patientPortal():
	regno=request.form['regno']
	pinfo=pp.getPatient_DataForPortal(regno)#FileName = pyfile/portal/patientPortal.py
	if len(pinfo)>0:
		wmid=pp.getWardMainId(regno)#FileName = pyfile/portal/patientPortal.py
		mdata=ipd.getAdmitPatientMedicineDataForBill(wmid[0][0])#FileName=/pyfile/inpatient/ipd.py.
		idata=ipd.getAdmitPatientIntakeDataForBill(wmid[0][0])#FileName=/pyfile/inpatient/ipd.py.
		insudata=ipd.getAdmitPatientInsulineDataForBill(wmid[0][0])#FileName=/pyfile/inpatient/ipd.py.
		podata=ipd.getAdmitPatientPoisonDataForBill(wmid[0][0])#FileName=/pyfile/inpatient/ipd.py.

		invdata = ipd.getLabPatientForDischarge(regno,wmid[0][1])#FileName=/pyfile/inpatient/ipd.py.
		print("i am invdata1=",invdata)
		testdata = ''
		sdata=''
		if len(invdata)>0:
			testdata=ipd.getTestForDischarge(regno,wmid[0][1])
			sdata=[]
			samdata=[]
			for s in range(len(testdata)):
				sdata.append(testdata[s][1])
			for x in sdata:
				if x not in samdata:
					samdata.append(x)
				else:
					samdata.append('')
			for s in range(len(testdata)):
				sdata[s]= list(testdata[s][:]) + [samdata[s]]
		xinfo=pp.getXraysData(wmid[0][0])#FileName = pyfile/portal/patientPortal.py
		dinfo=pp.getDocsData(regno)#FileName = pyfile/portal/patientPortal.py
		return render_template('/mainpage/patientportal.html',pinfo=pinfo,mdata=mdata,idata=idata,insudata=insudata,podata=podata,invdata=invdata,testdata=sdata,xinfo=xinfo,dinfo=dinfo)
	else:
		disinfo=pp.getPatient_DischargeInfo(regno)#FileName = pyfile/portal/patientPortal.py
		return render_template('/mainpage/patientPortal_Redir.html',disinfo=disinfo,ack='DISCHARGED')



##---------Patient Portal------------------



##--------------NEW PATIENT REGISTRATION NPR_START -----------------------


@app.route('/newpatient_Redir',methods=['GET','POST'])
def newpatient_Redir():
	disname=adm.getAllDistrict() #FileName = pyfile/admin/adminstuff.py
	cname=adm.getAllCompany()#FileName = pyfile/admin/adminstuff.py
	return render_template('/registration/patient_reg.html',disname = disname,cname=cname)

@app.route('/Insertnewpatient',methods=['GET','POST'])
def Insertnewpatient():
	result = reg.newRegistration() #FileName = pyfile/REGISTRATION/registration.py
	tablename = "patient_registration"
	print("RESULT",result)
	if "SHD" in str(result) :
		return redirect(url_for('blank_Insertnewpatient',regno=result,tbname=tablename))
	else:
		return render_template('/registration/patient_reg.html',ack=result)

@app.route('/blank_Insertnewpatient',methods=['GET','POST'])
def blank_Insertnewpatient():
	regno =request.args['regno']
	tablename = request.args['tbname']
	dataset = reg.getPatient_Registration_All(regno) #FileName = pyfile/REGISTRATION/registration.py
	print("adsadafgfg",dataset)
	return render_template('/opdvisit/opdvisit.html',data=dataset,ptype="NEW")


##-------------NEW PATIENT UPDATION NPU_START---------------------------
@app.route('/updatepatient_Redir',methods=['GET','POST'])
def updatepatient_Redir():
	return render_template('/registration/patientUpdate.html',ds='')

@app.route('/getUpdatePatient',methods=['GET','POST'])
def getUpdatePatient():
	regno = request.form['regno']
	dataset = reg.getPatient_Registration_All(regno)  #FileName = pyfile/REGISTRATION/registration.py
	disname=adm.getAllDistrict() #FileName = pyfile/admin/adminstuff.py
	cname=adm.getAllCompany() #FileName = pyfile/admin/adminstuff.py
	if len(dataset) > 0:
		return render_template('/registration/update_patient_reg.html',ds=dataset,disname=disname,cname=cname)
	else:
		return render_template('/registration/patientUpdate.html',ack="NO DATA FOUND")

@app.route('/UpdatePatientRecord',methods=['GET','POST'])
def UpdatePatientRecord():
	result = reg.updateRegistration() #FileName = pyfile/REGISTRATION/registration.py
	if result==1:
		return render_template('/registration/update_patient_reg.html',ack="DATA UPDATED SUCCESSFULLY!")
	else:
		return render_template('/registration/update_patient_reg.html',ack=result)

##-------------NEW PATIENT UPDATION NPU_END---------------------------


#================District Admin Section================
@app.route('/registrationAddRemove',methods=['GET','POST'])
def registrationAddRemove():
	return render_template('/registration/reg_add_remove.html',flag = 0)

@app.route('/newdistrictRedir',methods=['GET','POST'])
def newdistrictRedir():
	return render_template('/registration/reg_add_remove.html',flag = 1)

@app.route('/Viewnewdistrict',methods=['GET','POST'])
def Viewnewdistrict():
	data = adm.getAllDistrict()#FileName=/pyfile/ward/wardstuff.py.
	return render_template('/registration/reg_add_remove.html',data=data,flag = 2)

@app.route('/Insertnewdistrict',methods=['GET','POST'])
def Insertnewdistrict():
	result = adm.InsertNewDistrict()#FileName=/pyfile/ward/wardstuff.py.
	if result == 1:
		return redirect(url_for('blank_Insertnewdistrict'))
	else:
		return render_template('/registration/reg_add_remove.html',flag = 1,ack=result)

@app.route('/blank_Insertnewdistrict',methods=['GET','POST'])
def blank_Insertnewdistrict():
	return render_template('/registration/reg_add_remove.html',flag = 1,ack="DATA INSERTED SUCCESSFULLY!")

@app.route('/UpdateNewDistrict',methods=['GET','POST'])
def UpdateNewDistrict():
	result = adm.UpdateDistrict()#FileName=/pyfile/ward/wardstuff.py.
	if result == 1:
		return render_template('/registration/reg_add_remove.html',flag = 2,ack="DATA UPDATED SUCCESSFULLY!")
	else:
		return render_template('/registration/reg_add_remove.html',flag = 2,ack=result)

#================District Admin Section================


#================COMPANY Admin Section================


@app.route('/insertCompanyRedir',methods=['GET','POST'])
def insertCompanyRedir():
	return render_template('/registration/reg_add_remove.html',flag = 0,cflag=1)

@app.route('/ViewAllCompany',methods=['GET','POST'])
def ViewAllCompany():
	data = adm.getAllCompany()#FileName=/pyfile/ward/wardstuff.py.
	return render_template('/registration/reg_add_remove.html',data=data,flag = 0,cflag = 2)

@app.route('/InsertNewCompany',methods=['GET','POST'])
def InsertNewCompany():
	result = adm.InsertNewCompany()#FileName=/pyfile/ward/wardstuff.py.
	if result == 1:
		return redirect(url_for('blank_InsertNewCompany'))
	else:
		return render_template('/registration/reg_add_remove.html',flag = 1,ack=result)

@app.route('/blank_InsertNewCompany',methods=['GET','POST'])
def blank_InsertNewCompany():
	return render_template('/registration/reg_add_remove.html',flag = 0,cflag = 1,ack="DATA INSERTED SUCCESSFULLY!")

@app.route('/UpdateNewCompany',methods=['GET','POST'])
def UpdateNewCompany():
	result = adm.UpdateCompany()#FileName=/pyfile/ward/wardstuff.py.
	if result == 1:
		return render_template('/registration/reg_add_remove.html',flag = 0,cflag = 2,ack="DATA UPDATED SUCCESSFULLY!")
	else:
		return render_template('/registration/reg_add_remove.html',flag = 0,cflag = 2,ack=result)


#================COMPANY Admin Section================
#================GENERAL MESSAGE Admin Section================+++++++++++++++================================
@app.route('/insertGenMsgRedir',methods=['GET','POST'])
def insertGenMsgRedir():
	return render_template('/registration/reg_add_remove.html',flag = 0,cflag=0,flag2=1)


@app.route('/InsertnewGenMsg',methods=['GET','POST'])
def InsertnewGenMsg():
	result = adm.InsertNewGeneralMsg()#FileName=/pyfile/ward/wardstuff.py.
	if result == 1:
		return redirect(url_for('blank_InsertnewGenMsg'))
	else:
		return render_template('/registration/reg_add_remove.html',flag2 =1 ,ack=result)

@app.route('/blank_InsertnewGenMsg',methods=['GET','POST'])
def blank_InsertnewGenMsg():
	return render_template('/registration/reg_add_remove.html',flag2 = 1,ack="DATA INSERTED SUCCESSFULLY!")


@app.route('/ViewGenMsg',methods=['GET','POST'])
def ViewGenMsg():
	data=adm.getAllGenMsg()
	return render_template('/registration/reg_add_remove.html',flag = 0,cflag = 0,flag2=2,data=data)


@app.route('/UpdateGenMsg',methods=['GET','POST'])
def UpdateGenMsg():
	result = adm.UpdateGeneralMsg()#FileName=/pyfile/ward/wardstuff.py.
	if result == 1:
		return render_template('/registration/reg_add_remove.html',flag = 0,cflag = 0,flag2=2,ack="DATA UPDATED SUCCESSFULLY!")
	else:
		return render_template('/registration/reg_add_remove.html',flag = 0,cflag = 0,flag2=2,ack=result)

#################################=====GENERAL MESSAGE Admin Section ENDS=====######################################
####++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++##########
#################################=====Delivery MESSAGE Admin Section=====######################################


@app.route('/insertDelMsgRedir',methods=['GET','POST'])
def insertDelMsgRedir():
	return render_template('/registration/reg_add_remove.html',flag = 0,cflag=0,flag2=0,flag3=1)

@app.route('/InsertnewDelMsg',methods=['GET','POST'])
def InsertnewDelMsg():
	result = adm.InsertNewDeliveryMsg()#FileName=/pyfile/ward/wardstuff.py.
	if result == 1:
		return redirect(url_for('blank_InsertnewDelMsgRedir'))
	else:
		return render_template('/registration/reg_add_remove.html',flag3 =1 ,ack=result)

@app.route('/blank_InsertnewDelMsgRedir',methods=['GET','POST'])
def blank_InsertnewDelMsgRedir():
	return render_template('/registration/reg_add_remove.html',flag3 = 1,ack="DATA INSERTED SUCCESSFULLY!")


@app.route('/ViewDeliveryMsg',methods=['GET','POST'])
def ViewDeliveryMsg():
	data=adm.getAllDeliveryMsg()
	return render_template('/registration/reg_add_remove.html',flag = 0,cflag=0,flag2=0,flag3=2,data=data)

@app.route('/UpdateDelMsg',methods=['GET','POST'])
def UpdateDelMsg():
	result = adm.UpdateDeliveryMsg()#FileName=/pyfile/ward/wardstuff.py.
	if result == 1:
		return render_template('/registration/reg_add_remove.html',flag = 0,cflag = 0,flag2=0,flag3=2,ack="DATA UPDATED SUCCESSFULLY!")
	else:
		return render_template('/registration/reg_add_remove.html',flag = 0,cflag = 0,flag2=0,flag3=2,ack=result)

##--------------OLD PATIENT VISIT OPV_START ----------------------------

@app.route('/oldpatient_Redir',methods=['GET','POST'])
def oldpatient_Redir():
	return render_template('/registration/oldpatient.html')

@app.route('/oldpatientregno',methods=['GET','POST'])
def oldpatientregno():
	dataset = reg.getOldPatientRegno() #FileName=/pyfile/opdvisit/outvisit.py
	return render_template('/registration/oldpatient.html',ds=dataset)

@app.route('/oldpatientfname',methods=['GET','POST'])
def oldpatientfname():
	dataset = reg.getOldPatientFName() #FileName=/pyfile/opdvisit/outvisit.py
	return render_template('/registration/oldpatient.html',ds=dataset)

@app.route('/oldpatientcontact',methods=['GET','POST'])
def oldpatientcontact():
	dataset = reg.getOldPatientContact() #FileName=/pyfile/opdvisit/outvisit.py
	return render_template('/registration/oldpatient.html',ds=dataset)

@app.route('/oldpatientaadhar',methods=['GET','POST'])
def oldpatientaadhar():
	dataset = reg.getOldPatientAadhar() #FileName=/pyfile/opdvisit/outvisit.py
	return render_template('/registration/oldpatient.html',ds=dataset)

@app.route('/oldpatientaddress',methods=['GET','POST'])
def oldpatientaddress():
	dataset = reg.getOldPatientAddress() #FileName=/pyfile/opdvisit/outvisit.py
	return render_template('/registration/oldpatient.html',ds=dataset)

##--------------OLD PATIENT VISIT OPV_END ----------------------------
##--------------OLD PATIENT PRINT START-------------------------------
@app.route('/opdPrint',methods=['GET','POST'])
def opdPrint():
	return "I am PRINT UNDER COUNTRUCTION"



#####++++++++++++++++OPDVIEW STARTS FROM HERE+++++++++++++++++++############

@app.route('/opdSearch_Redir',methods=['GET','POST'])
def opdSearch_Redir():
	return render_template('/opdvisit/oldpatientview.html')

##===================Search FOR TODAY==================#
@app.route('/opdSearchPatientViewToday',methods=['GET','POST'])
def opdSearchPatientViewToday():
	dataset = opd.getopdSearchPatientToday() #FileName=/pyfile/opdvisit/outvisit.py
	return render_template('/opdvisit/oldpatientview.html',ds=dataset)


##===================Search FOR DATE ==================#
@app.route('/opdSearchPatientViewdate',methods=['GET','POST'])
def opdSearchPatientViewdate():
	dataset = opd.getopdSearchPatientViewDateData(app.config['UPLOAD_FOLDER_OPD']) #FileName=/pyfile/opdvisit/outvisit.py
	if len(dataset)>0:
		return render_template('/opdvisit/oldpatientview.html',ds=dataset,msg="Excel Sheet Generated Successfully!")
	else:
		return render_template('/opdvisit/oldpatientview.html',msg="Sorry! No Data Found")



##===================Search FOR DATE NAME==================#
@app.route('/opdSearchPatientViewNameDate',methods=['GET','POST'])
def opdSearchPatientViewNameDate():
	dataset = opd.getopdSearchPatientNameDateData() #FileName=/pyfile/opdvisit/outvisit.py
	return render_template('/opdvisit/oldpatientview.html',ds=dataset)

##===================Search By REGNO==================#
@app.route('/opdSearchPatientViewregno',methods=['GET','POST'])
def opdSearchPatientViewregno():
	dataset = opd.getOpdSearchPatientRegno() #FileName=/pyfile/opdvisit/outvisit.py
	return render_template('/opdvisit/oldpatientview.html',ds=dataset)

##===================Search By FName==================#

@app.route('/opdSearchPatientViewfname',methods=['GET','POST'])
def opdSearchPatientViewfname():
	dataset = opd.getopdSearchPatientFName() #FileName=/pyfile/opdvisit/outvisit.py
	return render_template('/opdvisit/oldpatientview.html',ds=dataset)


@app.route('/opdSearchPatientViewcontact',methods=['GET','POST'])
def opdSearchPatientViewcontact():
	dataset = opd.getopdSearchPatientViewContact() #FileName=/pyfile/opdvisit/outvisit.py
	return render_template('/opdvisit/oldpatientview.html',ds=dataset)


@app.route('/opdSearchPatientViewAddress',methods=['GET','POST'])
def opdSearchPatientViewAddress():
	dataset = opd.getopdSearchPatientViewAddressData() #FileName=/pyfile/opdvisit/outvisit.py
	return render_template('/opdvisit/oldpatientview.html',ds=dataset)


@app.route('/outPatientPrint',methods=['GET','POST'])
def outPatientPrint():
	page=request.form['page']
	if page =='VISITPAGE':
		dataset = opd.getPatientDataPrintVisit() #FileName=/pyfile/opdvisit/outvisit.py
		dataset2=adm.getRandomGeneralMsg()
		dataset3=adm.getRandomDeliveryMsg()
	elif page =='SEARCHPAGE':
		dataset = opd.getPatientDataPrintSearch() #FileName=/pyfile/opdvisit/outvisit.py
		dataset2=adm.getRandomGeneralMsg()
		dataset3=adm.getRandomDeliveryMsg()
		#print("i am ds3",dataset3)

	return render_template('/opdvisit/outpatientPrint.html',ds=dataset,ds2=dataset2,ds3=dataset3)

############### autocomplete function for complaint######Sanjay#######################
@app.route('/getOpdComplaint',methods=['GET','POST'])
def getOpdComplaint():
	dataset = opd.getallcomplaint() #FileName=/pyfile/opdvisit/outvisit.py
	#print("i am cmplt",dataset)
	if dataset != 0:
		return jsonify(dataset)
	else:
		return jsonify(dataset)




########################################################################################

##--------------OLD PATIENT PRINT START-------------------------------
##-------------PATIENT VITAL PVIT_START-------------------------------
@app.route('/opdVisit_redir',methods=['GET','POST'])
def opdVisit_redir():
	regno =request.form['regno']
	dataset = reg.getPatient_Registration_All(regno) #FileName = pyfile/REGISTRATION/registration.py
	return render_template('/opdvisit/opdvisit.html',data=dataset,ptype="OLD")

@app.route('/opdVisit',methods=['GET','POST'])
def opdVisit():
	result = opd.visitOpdInsert() #FileName=/pyfile/opdvisit/outvisit.py
	regno = request.form['regno']
	vdate = request.form['vdate']
	if result==1:
		return redirect(url_for('blank_opdVisit',regno=regno,vd=vdate))
	else:
		return render_template('/opdvisit/opdvisit.html',ack=result)

@app.route('/blank_opdVisit',methods=['GET','POST'])
def blank_opdVisit():
	regno = request.args['regno']
	vdate = request.args['vd']
	return render_template('/opdvisit/opdvisit.html',ack="DATA STORED SUCCESSFULLY!",regno=regno,vd=vdate)

##-------------PATIENT VITAL PVIT_END--------------------------------

##-------------OLD PATIENT VISIT UPDATE START OPVU_START--------------

@app.route('/opdViewUpdate_Redir',methods=['GET','POST'])
def opdViewUpdate_Redir():
	return render_template('/opdvisit/opdView_Update_Redir.html',ds1='',ds2='')

# This function will serve two module first is opdView_Update_Redir and second is opdConsultViewUpdate_Redir.
#It will identify the module on the basis of psource variable value.
@app.route('/getOpdViewUpdate',methods=['GET','POST'])
def getOpdViewUpdate():
	regno=request.form['regno']
	psource =request.form['source'] #not using this variable
	dataset1 = reg.getPatient_Registration_All(regno) #FileName = pyfile/REGISTRATION/registration.py
	if len(dataset1)>0:
		dataset2 = opd.getPatientVisitData(regno) #FileName=/pyfile/opdvisit/outvisit.py
		if len(dataset1)>0 and len(dataset2)>0:
			return render_template('/opdvisit/opdView_Update_Redir.html',ds1=dataset1,ds2=dataset2)
		else:
			return render_template('/opdvisit/opdView_Update_Redir.html',ds1=dataset1,ds2='',ack2="NO VISIT IS RECORDED YET!")
	else:
		return render_template('/opdvisit/opdView_Update_Redir.html',ds1='',ack1="INVALID REGNO!")

@app.route('/OpdViewUpdateShow',methods=['GET','POST'])
def OpdViewUpdateShow():
	opdid = request.form['opdid']
	regno = request.form['regno']
	print(request.form['regno'],request.form['opdid'])
	dataset1 = reg.getPatient_Registration_All(regno) #FileName = pyfile/REGISTRATION/registration.py
	dataset2 = opd.getAllPatientVisitData(opdid) #FileName=/pyfile/opdvisit/outvisit.py
	return render_template('/opdvisit/opdView_Update.html',data1=dataset1,data2=dataset2)

@app.route('/OpdViewUpdate',methods=['GET','POST'])
def OpdViewUpdate():
	result = opd.opdVisitUpdate() #FileName=/pyfile/opdvisit/outvisit.py
	if result==1:
		return render_template('/opdvisit/opdView_Update.html',ack="DATA UPDATED SUCCESSFULLY!",regno=request.form['regno'])
	else:
		return render_template('/opdvisit/opdView_Update.html',ack=result)



##-------------OLD PATIENT VISIT UPDATE START OPVU_END------------------

##-------------OLD PATIENT VISIT ACKNOWLEDGE START OPVACK_START---------

@app.route('/opdAcknowledgement_Redir',methods=['GET','POST'])
def opdAcknowledgement_Redir():
	return render_template('/opdvisit/opdAcknowledge.html',flag1=0,flag2=0)


@app.route('/getOpdAcknowledge',methods=['GET','POST'])
def getOpdAcknowledge():
	fildate = request.form['fildate']
	ptypeack=opd.getPtypeTodayAck(fildate) #FileName = pyfile/outpatient/outvisit.py
	pcatack=opd.getPcatTodayAck(fildate) #FileName = pyfile/outpatient/outvisit.py
	comack=opd.getCompanyDetail(fildate) #FileName = pyfile/outpatient/outvisit.py
	genptype=opd.getGeneralPtype(fildate) #FileName = pyfile/outpatient/outvisit.py
	return render_template('/opdvisit/opdAcknowledge.html',ptype=ptypeack,pack=pcatack,comp=comack,flag1=1,flag2=0,fdate=datetime.strptime(fildate, '%Y-%m-%d'),gn=genptype)


@app.route('/getOpdAcknowledgeRange',methods=['GET','POST'])
def getOpdAcknowledgeRange():
	fdate = request.form['fdate']
	tdate = request.form['tdate']
	ptypeack=opd.getPtypeRangeAck(fdate,tdate) #FileName = pyfile/outpatient/outvisit.py
	ptypetot=opd.getTotalPtypeRangeAck(fdate,tdate) #FileName = pyfile/outpatient/outvisit.py
	pcatack=opd.getPcatRangeAck(fdate,tdate) #FileName = pyfile/outpatient/outvisit.py
	pcattot=opd.getTotalPcatRangeAck(fdate,tdate) #FileName = pyfile/outpatient/outvisit.py
	return render_template('/opdvisit/opdAcknowledge.html',ptype=ptypeack,ptypetot=ptypetot,pack=pcatack,pcattot=pcattot,flag1=0,flag2=1,fdate=datetime.strptime(fdate, '%Y-%m-%d'),tdate=datetime.strptime(tdate,'%Y-%m-%d'))

##-------------OLD PATIENT VISIT ACKNOWLEDGE START OPVACK_START---------

##-------------OLD PATIENT VISIT REPORT START OPVR_START----------------

@app.route('/opdReport_Redir',methods=['GET','POST'])
def opdReport_Redir():
	return render_template('/opdvisit/opdReport.html')

##-------------OLD PATIENT VISIT REPORT START OPVR_END-----------------

##-------------PATIENT CONSULT START OPC_START-----------------

@app.route('/opdConsult_Redir',methods=['GET','POST'])
def opdConsult_Redir():
	return render_template('/opdvisit/opdconsult_Redir.html',ack1='',ack2='')

@app.route('/getOpdConsult',methods=['GET','POST'])
def getOpdConsult():
	regno=request.form['regno']
	todaydate=request.form['tdate']
	dataset1 = reg.getPatient_Registration_All(regno) #FileName = pyfile/REGISTRATION/registration.py
	if len(dataset1)>0:
		dataset2 = opd.getTodayPatientVisitData(regno,todaydate) #FileName=/pyfile/opdvisit/outvisit.py
		if len(dataset1)>0 and len(dataset2)>0:
			return render_template('/opdvisit/opdconsult.html',ds1=dataset1,ds2=dataset2,ack1='',ack2='',vital='ON',his='',ref='',med='',dia='',up='')
		else:
			return render_template('/opdvisit/opdconsult_Redir.html',ack1="NO VISIT IS RECORDED FOR TODAY YET!")
	else:
		return render_template('/opdvisit/opdconsult_Redir.html',ack2="INVALID REGNO!")

##-------------PATIENT REFER START OPDR_START---------------

@app.route('/opdConsultRefer',methods=['GET','POST'])
def opdConsultRefer():
	result = opd.insertOpdConsultRefer() #FileName=/pyfile/opdvisit/outvisit.py
	if result == 1:
		return jsonify({"ack":"DATA SUCCESSFULLY STORED!"})
	else:
		return jsonify({"ack":result})

##-------------PATIENT REFER START OPDR_END---------------


##-------------PATIENT HISTORY START OPDH_START---------------
@app.route('/opdConsultHistory',methods=['GET','POST'])
def opdConsultHistory():
	result = opd.insertOpdConsultHistory() #FileName=/pyfile/opdvisit/outvisit.py
	if result == 1:
		return jsonify({"ack":"DATA SUCCESSFULLY STORED!"})
	else:
		return jsonify({"ack":result})

##-------------PATIENT HISTORY START OPDH_END---------------

##-------------PATIENT DIAGNOSIS START OPD_START---------------
@app.route('/getOpdDiagnosis',methods=['GET','POSt'])
def getOpdDiagnosis():
	dataset = opd.getDiagnosis() #FileName=/pyfile/opdvisit/outvisit.py
	if dataset != 0:
		return jsonify(dataset)
	else:
		return jsonify(dataset)

@app.route('/opdDiagnosis',methods=['GET','POST'])
def opdDiagnosis():
	result=opd.insertOpdDiagnosis()#FileName=/pyfile/opdvisit/outvisit.py
	print(result,"i am diagno")
	if result == 1:
		return jsonify({"ack":"DATA SUCCESSFULLY STORED!"})
	else:
		return jsonify({"ack":result})

##-------------PATIENT DIAGNOSIS START OPD_END---------------

##-------------PATIENT DOCUMENTS UPLOAD START OPDDOCUP_START---------------

@app.route('/opdUpDoc_Redir',methods=['GET','POSt'])
def opdUpDoc_Redir():
	return render_template('/opdvisit/opduploaddoc_Redir.html')

@app.route('/getOpdDocUp',methods=['GET','POST'])
def getOpdDocUp():
	regno=request.form['regno']
	dataset = reg.getPatient_Registration_All(regno) #FileName = pyfile/REGISTRATION/registration.py
	if len(dataset)>0:
		return render_template('/opdvisit/opdUpload.html',ds=dataset)
	else:
		return render_template('/opdvisit/opduploaddoc_Redir.html',ack="INVALID REGNO!")

@app.route('/opdDocUpload',methods=['GET','POST'])
def opdDocUpload():
	print(request.form['regno'],request.form['entrydate'])
	result=opd.insertOpdDocUpload(app.config['UPLOAD_FOLDER_OPD'])#FileName=/pyfile/opdvisit/outvisit.py
	if result==1:
		return redirect(url_for('blank_opdDocUpload'))
	else:
		return render_template('/opdvisit/opdUpload.html',ack=result)

@app.route('/blank_opdDocUpload',methods=['GET','POST'])
def blank_opdDocUpload():
	return render_template('/opdvisit/opdUpload.html',ack="DOCUMENT(S) UPLOADED SUCCESSFULLY!")

##-------------PATIENT DOCUMENTS UPLOAD END OPDDOCUP_END---------------

##-------------PATIENT CONSULT START OPC_END-----------------------------


##--------------PATIENT CONSULT UPDATION STARTOPCU_START-----------------

@app.route('/opdConsultViewUpdate_Redir',methods=['GET','POST'])
def opdConsultViewUpdate_Redir():
	return render_template('/opdvisit/opdconsultViewUpdate_Redir.html',ds1='',ds2='')

@app.route('/opdConsultViewUpdateList',methods=['GET','POST'])
def opdConsultViewUpdateList():
	regno=request.form['regno']
	dataset1 = reg.getPatient_Registration_All(regno) #FileName = pyfile/REGISTRATION/registration.py
	if(len(dataset1)>0):
		opddata = opd.getPatientConsultData(regno)#FileName=/pyfile/opdvisit/outvisit.py
		if(len(opddata)>0):
			return render_template('/opdvisit/opdconsultViewUpdate_Redir.html',ds1=dataset1,ds2=opddata)
		else:
			return render_template('/opdvisit/opdconsultViewUpdate_Redir.html',ds1=dataset1,ack='NO CONSULT IS RECORDED YET.')
	else:
		return render_template('/opdvisit/opdconsultViewUpdate_Redir.html',ds1='',ds2='',ack="INVALID REGNO.")

@app.route('/opdConsultViewUpdate',methods=['GET','POST'])
def opdConsultViewUpdate():
	regno = request.form['regno']
	dataset1 = reg.getPatient_Registration_All(regno) #FileName = pyfile/REGISTRATION/registration.py
	conid = request.form['conid']
	conhis = opd.getOpdConsultHistory(conid)#FileName=/pyfile/opdvisit/outvisit.py
	condia = opd.getOpdConsultDiagnosis(conid)#FileName=/pyfile/opdvisit/outvisit.py
	conref = opd.getOpdConsultRefer(conid)#FileName=/pyfile/opdvisit/outvisit.py
	#conmed =opd.getOpdConsultMedicine(opddata[0][0])#FileName=/pyfile/opdvisit/outvisit.py
	return render_template('/opdvisit/opdconsultViewUpdate.html',ds1=dataset1,chis=conhis,cdia=condia,cref=conref)

@app.route('/deleteDianosis',methods=['GET','POST'])
def deleteDianosis():
	result = opd.opdConsultDeleteDiagnosis(request.form['did'])#FileName=/pyfile/opdvisit/outvisit.py

	return json.dumps({'data':result})


@app.route('/updateOpdConsultHistory',methods=['GET','POST'])
def updateOpdConsultHistory():
	result=opd.opdConsultUpdateHistory()#FileName=/pyfile/opdvisit/outvisit.py
	return jsonify({"ack":"DATA SUCCESSFULLY UPDATED!"})

@app.route('/updateOpdConsultRefer',methods=['GET','POST'])
def updateOpdConsultRefer():
	result=opd.opdConsultUpdateRefer()#FileName=/pyfile/opdvisit/outvisit.py
	return jsonify({"ack":"DATA SUCCESSFULLY UPDATED!"})

@app.route('/updateOpdConsultDiagnosis',methods=['GET','POST'])
def updateOpdConsultDiagnosis():
	result=opd.opdConsultUpdateDiagnosis()#FileName=/pyfile/opdvisit/outvisit.py
	return jsonify({"ack":"DATA SUCCESSFULLY UPDATED!"})

@app.route('/opdConsultUpInDiagnosis',methods=['GET','POST'])
def opdConsultUpInDiagnosis():
	result=opd.insertUpdateOpdDiagnosis()#FileName=/pyfile/opdvisit/outvisit.py
	if result == 1:
		return jsonify({"ack":"DATA SUCCESSFULLY STORED!"})
	else:
		return jsonify({"ack":result})


################################################################################
##################################Diagnosis Admin START#########################
################################################################################

@app.route('/diagnosisRedir',methods=['GET','POST'])
def diagnosisRedir():
	return render_template('/opdvisit/diagnosis_add_remove.html',flag = 0)

@app.route('/InsertDiagnosisRedir',methods=['GET','POST'])
def InsertDiagnosisRedir():
	return render_template('/opdvisit/diagnosis_add_remove.html',flag = 1)

@app.route('/ViewDiagnosis',methods=['GET','POST'])
def ViewDiagnosis():
	data = adm.getAllDiagnosis()#FileName=/pyfile/admin/adminstuff.py.
	return render_template('/opdvisit/diagnosis_add_remove.html',data=data,flag = 2)

@app.route('/InsertNewDiagnosis',methods=['GET','POST'])
def InsertNewDiagnosis():
	result = adm.InsertNewDiagnosisData()#FileName=/pyfile/admin/adminstuff.py.
	if result == 1:
		return redirect(url_for('blank_InsertNewDiagnosis'))
	else:
		return render_template('/opdvisit/diagnosis_add_remove.html',flag = 1,ack=result)

@app.route('/blank_InsertNewDiagnosis',methods=['GET','POST'])
def blank_InsertNewDiagnosis():
	return render_template('/opdvisit/diagnosis_add_remove.html',flag = 1,ack="DATA INSERTED SUCCESSFULLY!")

@app.route('/UpdateDiagnosis',methods=['GET','POST'])
def UpdateDiagnosis():
	result = adm.UpdateDiagnosisData()#FileName=/pyfile/admin/adminstuff.py.
	if result == 1:
		return render_template('/opdvisit/diagnosis_add_remove.html',flag = 2,ack="DATA UPDATED SUCCESSFULLY!")
	else:
		return render_template('/opdvisit/diagnosis_add_remove.html',flag = 2,ack=result)


################################################################################
##################################Diagnosis Admin END###########################
################################################################################




'''
@app.route('/getOpdConsultData',methods=['GET','POST'])
def getOpdConsultData():
	regno=request.form['regno']
	opdid=request.form['opdid']
	dataset1 = reg.getPatient_Registration_All(regno) #FileName = pyfile/REGISTRATION/registration.py
	hisdataset = opd.getOpdConsultHistory(opdid) #FileName=/pyfile/opdvisit/outvisit.py
	refdataset = opd.getOpdConsultRefer(opdid) #FileName=/pyfile/opdvisit/outvisit.py
	diadataset = opd.getOpdConsultDiagnosis(opdid) #FileName=/pyfile/opdvisit/outvisit.py
	if len(dataset1)>0:
		return render_template('/opdvisit/opdconsultViewUpdate.html',ds1=dataset1,hds=hisdataset,rds=refdataset,dds=diadataset)
	else:
		return render_template('/opdvisit/opdconsultViewUpdate.html',ack="No Record Found For Given Regno!")
'''



##--------------PATIENT CONSULT UPDATION END OPCU_END-----------------



##--------------ADMIT PATIENT START AP_START-----------------

@app.route('/admit_Redir',methods=['GET','POST'])
def admit_Redir():
	return render_template('/ipdvisit/admit.html')

@app.route('/admitPatient',methods=['GET','POST'])
def admitPatient():
	regno =request.form['regno']
	dataset = ipd.getLatestAdmitPatientData(regno) #FileName=/pyfile/inpatient/ipd.py.
	if len(dataset)>0:
		wardname = wrd.getAvalableWardData()#FileName=/pyfile/ward/wardstuff.py.
		gscheme = adm.getAllGovScheme()#FileName=/pyfile/admin/adminstuff.py.
		return render_template('/ipdvisit/ipdvisit.html',ds=dataset,wname=wardname,gsch=gscheme)
	else:
		return render_template('/ipdvisit/admit.html',ack="PATIENT NOT YET REGISTERED OR OPD RECEIPT IS NOT GENERATED!")

@app.route('/ipdvisit',methods=['GET','POST'])
def ipdvisit():
	regno=request.form['regno']
	ipddate=request.form['ipddate']
	result = ipd.visitIpd() #FileName=/pyfile/inpatient/ipd.py.
	if result==1:
		return redirect(url_for('blank_ipdvisit',regno=regno,vd=ipddate))
	else:
		return render_template('/ipdvisit/ipdvisit.html',ack=result)

@app.route('/blank_ipdvisit',methods=['GET','POST'])
def blank_ipdvisit():
	regno = request.args['regno']
	vdate = request.args['vd']
	return render_template('/ipdvisit/ipdvisit.html',ack="DATA STORED SUCCESSFULLY!",regno=regno,vd=vdate)

##-------------------------IPD PRINT---------------------

@app.route('/inpatientPrint',methods=['GET','POST'])
def inpatientPrint():
	page=request.form['page']
	if page =='ADMIT':
		admitdata = ipd.getAdmitPatientDataForPrint(request.form['regno'],request.form['vdate'])
		dataset2=adm.getRandomGeneralMsg()
	elif page =='OLDADMIT':
		admitdata = ipd.getOldAdmitPatientDataForPrint(request.form['ipdid'])
		dataset2=adm.getRandomGeneralMsg()
	return render_template('/ipdvisit/ipdPrint.html',admitdata=admitdata,ds2=dataset2)
	##-------------------------IPD PRINT---------------------


@app.route('/ipdViewUpdate_Redir',methods=['GET','POST'])
def ipdViewUpdate_Redir():
	return render_template('/ipdvisit/ipdView_Update_Redir.html',ds1='',ds2='')

@app.route('/getIpdViewUpdate',methods=['GET','POST'])
def getIpdViewUpdate():
	regno = request.form['regno']
	dataset1 = reg.getPatient_Registration_All(regno) #FileName = pyfile/REGISTRATION/registration.py
	if len(dataset1)>0:
		dataset2 = ipd.getAllAdmitPatientData(regno)#FileName=/pyfile/inpatient/ipd.py.
		if len(dataset1)>0 and len(dataset2)>0:
			return render_template('/ipdvisit/ipdView_Update_Redir.html',ds1=dataset1,ds2=dataset2,ack1='',ack2='')
		else:
			return render_template('/ipdvisit/ipdView_Update_Redir.html',ds1=dataset1,ds2='',ack2="NO VISIT IS RECORDED YET!")
	else:
		return render_template('/ipdvisit/ipdView_Update_Redir.html',ds1='',ack1="INVALID REGNO!")


@app.route('/IpdViewUpdateShow',methods=['GET','POST'])
def IpdViewUpdateShow():
	ipdid = request.form['ipdid']
	regno = request.form['regno']
	dataset1 = reg.getPatient_Registration_All(regno) #FileName = pyfile/REGISTRATION/registration.py
	dataset2 = ipd.getAdmitPatientData(ipdid) #FileName=/pyfile/inpatient/ipd.py.
	wardname = wrd.getAvalableWardData()#FileName=/pyfile/ward/wardstuff.py.
	gscheme = adm.getAllGovScheme()#FileName=/pyfile/admin/adminstuff.py.
	return render_template('/ipdvisit/ipdView_Update.html',data1=dataset1,data2=dataset2,wname=wardname,gsch=gscheme)

@app.route('/IpdViewUpdate',methods=['GET','POST'])
def IpdViewUpdate():
		result = ipd.visitIpdUpdate() #FileName=/pyfile/inpatient/ipd.py.
		if result==1:
			return render_template('/ipdvisit/ipdView_Update.html',ack="DATA UPDATED SUCCESSFULLY!",regno=request.form['regno'])
		else:
			return render_template('/ipdvisit/ipdView_Update.html',ack=result)

@app.route('/ipdAck_Redir',methods=['GET','POST'])
def ipdAck_Redir():
	return render_template('/ipdvisit/ipdAcknowledge.html')

@app.route('/getIpdAcknowledge',methods=['GET','POST'])
def getIpdAcknowledge():
	fildate = request.form['fildate']
	ptypeack=ipd.getPtypeTodayAckIpd(fildate) #FileName = pyfile/inpatient/ipd.py
	genptype=ipd.getGeneralPtypeIpd(fildate) #FileName = pyfile/inpatient/ipd.py
	pcatack=ipd.getPcatTodayAckIpd(fildate) #FileName = pyfile/inpatient/ipd.py
	comack=ipd.getCompanyDetailIpd(fildate) #FileName = pyfile/inpatient/ipd.py
	gsch = ipd.getGovSchemeDetailIpd(fildate)#FileName = pyfile/inpatient/ipd.py
	return render_template('/ipdvisit/ipdAcknowledge.html',ptype=ptypeack,gn=genptype,pack=pcatack,comp=comack,gs=gsch,flag1=1,flag2=0,fdate=datetime.strptime(fildate, '%Y-%m-%d'))


@app.route('/getIpdAcknowledgeRange',methods=['GET','POST'])
def getIpdAcknowledgeRange():
	fdate = request.form['fdate']
	tdate = request.form['tdate']
	ptypeack=ipd.getPtypeRangeAckIpd(fdate,tdate)  #FileName = pyfile/inpatient/ipd.py
	ptypetot=ipd.getTotalPtypeRangeAckIpd(fdate,tdate)  #FileName = pyfile/inpatient/ipd.py
	pcatack=ipd.getPcatRangeAckIpd(fdate,tdate)  #FileName = pyfile/inpatient/ipd.py
	pcattot=ipd.getTotalPcatRangeAckIpd(fdate,tdate)  #FileName = pyfile/inpatient/ipd.py
	return render_template('/ipdvisit/ipdAcknowledge.html',ptype=ptypeack,ptypetot=ptypetot,pack=pcatack,pcattot=pcattot,flag1=0,flag2=1,fdate=datetime.strptime(fdate, '%Y-%m-%d'),tdate=datetime.strptime(tdate, '%Y-%m-%d'))

##-------------------INPATIENT SEARCH START---------------

@app.route('/ipdSearch_Redir',methods=['GET','POST'])
def ipdSearch_Redir():
	return render_template('/ipdvisit/oldipdpatientsearch.html')

@app.route('/ipdoldpatientviewToday',methods=['GET','POST'])
def ipdoldpatientviewToday():
	ipddata=ipd.getipdoldpatientviewToday()#FileName = pyfile/inpatient/ipd.py
	return render_template('/ipdvisit/oldipdpatientsearch.html',adata=ipddata)

@app.route('/ipdoldpatientviewdate',methods=['GET','POST'])
def ipdoldpatientviewdate():
	ipddata=ipd.getipdoldpatientviewdate(app.config['UPLOAD_FOLDER_IPD'])#FileName = pyfile/inpatient/ipd.py
	if len(ipddata)>0:
		return render_template('/ipdvisit/oldipdpatientsearch.html',adata=ipddata,msg="Excel Sheet Generated Successfully!")
	else:
		return render_template('/ipdvisit/oldipdpatientsearch.html',msg1="No Data Found")


@app.route('/ipdoldpatientviewnamedate',methods=['GET','POST'])
def ipdoldpatientviewnamedate():
	ipddata=ipd.getipdoldpatientviewnamedate()#FileName = pyfile/inpatient/ipd.py
	return render_template('/ipdvisit/oldipdpatientsearch.html',adata=ipddata)

@app.route('/ipdoldpatientviewregno',methods=['GET','POST'])
def ipdoldpatientviewregno():
	ipddata=ipd.getipdoldpatientviewregno()#FileName = pyfile/inpatient/ipd.py
	return render_template('/ipdvisit/oldipdpatientsearch.html',adata=ipddata)

@app.route('/ipdoldpatientviewfname',methods=['GET','POST'])
def ipdoldpatientviewfname():
	ipddata=ipd.getipdoldpatientviewfname()#FileName = pyfile/inpatient/ipd.py
	return render_template('/ipdvisit/oldipdpatientsearch.html',adata=ipddata)


@app.route('/ipdoldpatientviewcontact',methods=['GET','POST'])
def ipdoldpatientviewcontact():
	ipddata=ipd.getipdoldpatientviewcontact()#FileName = pyfile/inpatient/ipd.py
	return render_template('/ipdvisit/oldipdpatientsearch.html',adata=ipddata)

@app.route('/ipdoldpatientviewAddress',methods=['GET','POST'])
def ipdoldpatientviewAddress():
	ipddata=ipd.getipdoldpatientviewAddress()#FileName = pyfile/inpatient/ipd.py
	return render_template('/ipdvisit/oldipdpatientsearch.html',adata=ipddata)
##-------------------INPATIENT SEARCH END---------------

#################################################
###DISCHARGE START###############################
################################################
@app.route('/ipd_discharge_Redir',methods=['GET','POST'])
def ipd_discharge_Redir():
	ddata = ipd.getDischargeRequestedPatientData()#FileName = pyfile/inpatient/ipd.py
	if len(ddata)>0:
		return render_template('/ipdvisit/discharge_Redir.html',ddata=ddata,ack="")
	else:
		return render_template('/ipdvisit/discharge_Redir.html',ack="No Discharge Request(s) Is Generated By Ward(s).")


@app.route('/requestForDischarge',methods=['GET','POST'])
def requestForDischarge():
	wmid=request.form['wmid']
	wid=request.form['wid']
	wname=request.form['wname']
	result = ipd.dischargeMeRequest(wmid)
	if result==1:
		showdata=wrd.showWardAdmitPatient(wid)#FileName=/pyfile/ward/wardstuff.py.
		return render_template('/wards/reginward.html',wname=wname,wid=wid,showdata=showdata)

@app.route('/cancelRequestForDischarge',methods=['GET','POST'])
def cancelRequestForDischarge():
	wmid=request.form['wmid']
	wid=request.form['wid']
	wname=request.form['wname']
	result = ipd.cancelDischargeMeRequest(wmid)
	if result==1:
		showdata=wrd.showWardAdmitPatient(wid)#FileName=/pyfile/ward/wardstuff.py.
		return render_template('/wards/reginward.html',wname=wname,wid=wid,showdata=showdata)


@app.route('/fillAdvice_Redir',methods=['GET','POST'])
def fillAdvice_Redir():
	wmid=request.form['wmid']
	adata = ipd.getPatientDataForAdvice(wmid)#FileName=/pyfile/ward/wardstuff.py.
	return render_template('/ipdvisit/filladvice.html',adata=adata)

@app.route('/insertAdvice',methods=['GET','POST'])
def insertAdvice():
	result = ipd.updatePatientAdvice()#FileName=/pyfile/ward/wardstuff.py.
	if result == 1:
		ddata = ipd.getDischargeRequestedPatientData()#FileName = pyfile/inpatient/ipd.py
		return render_template('/ipdvisit/discharge_Redir.html',ddata=ddata)
	else:
		return render_template('/ipdvisit/filladvice.html',ack=result)

@app.route('/ipdbilling',methods=['GET','POST'])
def ipdbilling():
	ipdid=request.form['ipdid']
	wmid=request.form['wmid']
	regno=request.form['regno']
	dataset = ipd.getAdmitPatientDataForBill(ipdid) #FileName=/pyfile/inpatient/ipd.py.

	mdata = ipd.getAdmitPatientMedicineDataForBill(wmid)#FileName=/pyfile/inpatient/ipd.py.
	mtotal=ipd.getAdmitPatientMedicineTotalAmount(wmid)#FileName=/pyfile/inpatient/ipd.py.

	isdata = ipd.getAdmitPatientIntakeDataForBill(wmid)#FileName=/pyfile/inpatient/ipd.py.
	istotal=ipd.getAdmitPatientIntakeTotalAmount(wmid)#FileName=/pyfile/inpatient/ipd.py.

	isudata = ipd.getAdmitPatientInsulineDataForBill(wmid)#FileName=/pyfile/inpatient/ipd.py.
	isutotal=ipd.getAdmitPatientInsulineTotalAmount(wmid)#FileName=/pyfile/inpatient/ipd.py.

	poidata = ipd.getAdmitPatientPoisonDataForBill(wmid)#FileName=/pyfile/inpatient/ipd.py.
	poitotal=ipd.getAdmitPatientPoisonTotalAmount(wmid)#FileName=/pyfile/inpatient/ipd.py.

	condata = ipd.getAdmitPatientConsumeDataForBill(wmid)#FileName=/pyfile/inpatient/ipd.py.
	contotal=ipd.getAdmitPatientConsumeTotalAmount(wmid)#FileName=/pyfile/inpatient/ipd.py.

	surdata = ipd.getAdmitPatientSurgeryDataForBill(wmid)#FileName=/pyfile/inpatient/ipd.py.
	surtotal=ipd.getAdmitPatientSurgeryTotalAmount(wmid)#FileName=/pyfile/inpatient/ipd.py.

	ldata = ipd.getAdmitPatientLabDataForBill(regno,ipdid)#FileName=/pyfile/inpatient/ipd.py.
	ltotal=ipd.getAdmitPatientLabToatalAmount(regno,ipdid)#FileName=/pyfile/inpatient/ipd.py.

	xdata=ipd.getAdmitPatientXrayDataForBill(regno,wmid)#FileName=/pyfile/inpatient/ipd.py.
	xtotal=ipd.getAdmitPatientXrayTotalAmount(regno,wmid)#FileName=/pyfile/inpatient/ipd.py.

	ecgdata='No'
	ecgtotal=0

	dredata=ipd.getAdmitPatientDressingDataForBill(wmid)#FileName=/pyfile/inpatient/ipd.py.
	dretotal=ipd.getAdmitPatientDressingTotalAmount(wmid)#FileName=/pyfile/inpatient/ipd.py.

	phydata=ipd.getAdmitPatientPhyDataForBill(wmid)#FileName=/pyfile/inpatient/ipd.py.
	phytotal=ipd.getAdmitPatientPhyTotalAmount(wmid)#FileName=/pyfile/inpatient/ipd.py.

	thedata='No'
	thetotal=0
	return render_template('/ipdvisit/ipdbilling_main.html',ack='',ds=dataset,mdata=mdata,mtotal=mtotal,isdata=isdata,istotal=istotal,isudata=isudata,isutotal=isutotal,poidata=poidata,poitotal=poitotal,condata=condata,contotal=contotal,surdata=surdata,stotal=surtotal,ldata=ldata,ltotal=ltotal,xdata=xdata,xtotal=xtotal,ecgdata=ecgdata,ecgtotal=ecgtotal,dredata=dredata,dretotal=dretotal,phydata=phydata,phytotal=phytotal,thedata=thedata,thetotal=thetotal)

@app.route('/keepIpdBilling',methods=['GET','POST'])
def keepIpdBilling():
	ac = ipd.keepIpdBillingData()#FileName=/pyfile/inpatient/ipd.py.
	if ac==1:
		return redirect(url_for('blank_keepIpdBilling',wrd_id=request.form['wrd_id'],regno=request.form['regno'],ipdid=request.form['ipdid']))
	else:
		return render_template('/ipdvisit/ipdbilling_main.html',ack=ac)

@app.route('/blank_keepIpdBilling',methods=['GET','POST'])
def blank_keepIpdBilling():
	wmid = request.args['wrd_id']
	regno = request.args['regno']
	ipdid = request.args['ipdid']
	return render_template('/ipdvisit/ipdbillingprint_Redir.html',ack="DATA SUCCESSFULLY STORED!",wmid=wmid,regno=regno,ipdid=ipdid)

@app.route('/printDischarge',methods=['GET','POST'])
def printDischarge():
	wmid = request.args['wmid']
	regno=request.args['regno']
	ipdid=request.args['ipdid']
	pdata=ipd.getPatientDetailForDischarge(wmid)#FileName=/pyfile/inpatient/ipd.py.
	print(pdata[0][11])
	if int(pdata[0][11]) == int(5) :
		delidata=wrd.getPatientMotherDetailsForDischarge(wmid) #FileName=/pyfile/ward/wardstuff.py.
		dchilddata=wrd.getDeliveryChildDetailsForDischarge(delidata[0][0])#FileName=/pyfile/ward/wardstuff.py.
		print("I AM IF",dchilddata)
	else:
		print("I AM ELSE")
		delidata=''
		dchilddata=''
	wdata=ipd.getWardDetailForDischarge(wmid)#FileName=/pyfile/inpatient/ipd.py.
	mdata=ipd.getAdmitPatientMedicineDataForBill(wmid)#FileName=/pyfile/inpatient/ipd.py.
	idata=ipd.getAdmitPatientIntakeDataForBill(wmid)#FileName=/pyfile/inpatient/ipd.py.
	insudata=ipd.getAdmitPatientInsulineDataForBill(wmid)#FileName=/pyfile/inpatient/ipd.py.
	podata=ipd.getAdmitPatientPoisonDataForBill(wmid)#FileName=/pyfile/inpatient/ipd.py.

	invdata = ipd.getLabPatientForDischarge(regno,ipdid)#FileName=/pyfile/inpatient/ipd.py.
	testdata = ''
	sdata=''
	if len(invdata)>0:
		testdata=ipd.getTestForDischarge(regno,ipdid)
		sdata=[]
		samdata=[]
		for s in range(len(testdata)):
			sdata.append(testdata[s][1])
		for x in sdata:
			if x not in samdata:
				samdata.append(x)
			else:
				samdata.append('')

		for s in range(len(testdata)):
			sdata[s]= list(testdata[s][:]) + [samdata[s]]
		print("SDDD=",sdata)
	return render_template('/ipdvisit/printdischargesummary.html',pdata=pdata,wdata=wdata,invdata=invdata,testdata=sdata,mdata=mdata,idata=idata,insudata=insudata,podata=podata,ds3=delidata,ds4=dchilddata)

@app.route('/printNormalBill',methods=['GET','POST'])
def printNormalBill():
	wmid = request.args['wmid']
	pdata=ipd.getPatientDetailForIpdBill(wmid)#FileName=/pyfile/inpatient/ipd.py.
	print("DATATA",pdata)
	return render_template('/ipdvisit/printnormalipdbill.html',pdata=pdata)

@app.route('/printDetailBill',methods=['GET','POST'])
def printDetailBill():
	wmid = request.args['wmid']
	regno=request.args['regno']
	ipdid=request.args['ipdid']
	pdata=ipd.getPatientDetailForIpdBill(wmid)#FileName=/pyfile/inpatient/ipd.py.
	print("DATATA",pdata)
	mdata = ipd.getAdmitPatientMedicineDataForBill(wmid)#FileName=/pyfile/inpatient/ipd.py.
	mtotal=ipd.getAdmitPatientMedicineTotalAmount(wmid)#FileName=/pyfile/inpatient/ipd.py.

	isdata = ipd.getAdmitPatientIntakeDataForBill(wmid)#FileName=/pyfile/inpatient/ipd.py.
	istotal=ipd.getAdmitPatientIntakeTotalAmount(wmid)#FileName=/pyfile/inpatient/ipd.py.

	isudata = ipd.getAdmitPatientInsulineDataForBill(wmid)#FileName=/pyfile/inpatient/ipd.py.
	isutotal=ipd.getAdmitPatientInsulineTotalAmount(wmid)#FileName=/pyfile/inpatient/ipd.py.

	poidata = ipd.getAdmitPatientPoisonDataForBill(wmid)#FileName=/pyfile/inpatient/ipd.py.
	poitotal=ipd.getAdmitPatientPoisonTotalAmount(wmid)#FileName=/pyfile/inpatient/ipd.py.

	condata = ipd.getAdmitPatientConsumeDataForBill(wmid)#FileName=/pyfile/inpatient/ipd.py.
	contotal=ipd.getAdmitPatientConsumeTotalAmount(wmid)#FileName=/pyfile/inpatient/ipd.py.

	surdata = ipd.getAdmitPatientSurgeryDataForBill(wmid)#FileName=/pyfile/inpatient/ipd.py.
	surtotal=ipd.getAdmitPatientSurgeryTotalAmount(wmid)#FileName=/pyfile/inpatient/ipd.py.

	ldata = ipd.getAdmitPatientLabDataForBill(regno,ipdid)#FileName=/pyfile/inpatient/ipd.py.
	ltotal=ipd.getAdmitPatientLabToatalAmount(regno,ipdid)#FileName=/pyfile/inpatient/ipd.py.

	xdata=ipd.getAdmitPatientXrayDataForBill(regno,wmid)#FileName=/pyfile/inpatient/ipd.py.
	xtotal=ipd.getAdmitPatientXrayTotalAmount(regno,wmid)#FileName=/pyfile/inpatient/ipd.py.

	ecgdata='No'
	ecgtotal=0

	dredata=ipd.getAdmitPatientDressingDataForBill(wmid)#FileName=/pyfile/inpatient/ipd.py.
	dretotal=ipd.getAdmitPatientDressingTotalAmount(wmid)#FileName=/pyfile/inpatient/ipd.py.

	phydata=ipd.getAdmitPatientPhyDataForBill(wmid)#FileName=/pyfile/inpatient/ipd.py.
	phytotal=ipd.getAdmitPatientPhyTotalAmount(wmid)#FileName=/pyfile/inpatient/ipd.py.

	thedata='No'
	thetotal=0
	return render_template('/ipdvisit/printdetailipdbill.html',ack='',pdata=pdata,mdata=mdata,mtotal=mtotal,isdata=isdata,istotal=istotal,isudata=isudata,isutotal=isutotal,poidata=poidata,poitotal=poitotal,condata=condata,contotal=contotal,surdata=surdata,stotal=surtotal,ldata=ldata,ltotal=ltotal,xdata=xdata,xtotal=xtotal,ecgdata=ecgdata,ecgtotal=ecgtotal,dredata=dredata,dretotal=dretotal,phydata=phydata,phytotal=phytotal,thedata=thedata,thetotal=thetotal)

@app.route('/ipdBillingSearch_Redir',methods=['GET','POST'])
def ipdBillingSearch_Redir():
	return render_template('/ipdvisit/ipd_billing_search.html',flag = 0,gflag=0)

@app.route('/ipdBillingSearchByToday',methods=['GET','POST'])
def ipdBillingSearchByToday():
	bdata=ipd.getipdBillingSearchByTodayData()#FileName=/pyfile/inpatient/ipd.py.
	return render_template('/ipdvisit/ipd_billing_search.html',bdata=bdata)

@app.route('/ipdBillingSearchByDate',methods=['GET','POST'])
def ipdBillingSearchByDate():
	bdata=ipd.getipdBillingSearchByDateData()#FileName=/pyfile/inpatient/ipd.py.
	return render_template('/ipdvisit/ipd_billing_search.html',bdata=bdata)

@app.route('/ipdBillingSearchByRegno',methods=['GET','POST'])
def ipdBillingSearchByRegno():
	bdata=ipd.getipdBillingSearchByRegnoData()#FileName=/pyfile/inpatient/ipd.py.
	print("DDD ",bdata)
	return render_template('/ipdvisit/ipd_billing_search.html',bdata=bdata)



#################################################
###DISCHARGE END###############################
################################################


################################################################################
##################################DEATH REASON Admin START#########################
################################################################################

@app.route('/deathReasonRedir',methods=['GET','POST'])
def deathReasonRedir():
	return render_template('/ipdvisit/ipdadmin_add_remove.html',flag = 0,gflag=0)

@app.route('/InsertDeathReasonRedir',methods=['GET','POST'])
def InsertDeathReasonRedir():
	return render_template('/ipdvisit/ipdadmin_add_remove.html',flag = 1,gflag=0)

@app.route('/ViewDeathReason',methods=['GET','POST'])
def ViewDeathReason():
	data = adm.getAllDeathReason()#FileName=/pyfile/admin/adminstuff.py.
	return render_template('/ipdvisit/ipdadmin_add_remove.html',data=data,flag = 2,gflag=0)

@app.route('/InsertNewDeathReason',methods=['GET','POST'])
def InsertNewDeathReason():
	result = adm.InsertNewDeathReasonData()#FileName=/pyfile/admin/adminstuff.py.
	if result == 1:
		return redirect(url_for('blank_InsertNewDeathReason'))
	else:
		return render_template('/ipdvisit/ipdadmin_add_remove.html',flag = 1,gflag=0,ack=result)

@app.route('/blank_InsertNewDeathReason',methods=['GET','POST'])
def blank_InsertNewDeathReason():
	return render_template('/ipdvisit/ipdadmin_add_remove.html',flag = 1,gflag=0,ack="DATA INSERTED SUCCESSFULLY!")

@app.route('/UpdateDeathReason',methods=['GET','POST'])
def UpdateDeathReason():
	result = adm.UpdateDeathReasonData()#FileName=/pyfile/admin/adminstuff.py.
	if result == 1:
		return render_template('/ipdvisit/ipdadmin_add_remove.html',flag = 2,gflag=0,ack="DATA UPDATED SUCCESSFULLY!")
	else:
		return render_template('/ipdvisit/ipdadmin_add_remove.html',flag = 2,gflag=0,ack=result)


################################################################################
##################################DEATH REASON Admin END###########################
################################################################################

################################################################################
##################################Government Scheme  Admin START#########################
################################################################################

@app.route('/govSchemeRedir',methods=['GET','POST'])
def govSchemeRedir():
	return render_template('/ipdvisit/ipdadmin_add_remove.html',flag = 0,gflag=0)

@app.route('/InsertGovSchemeRedir',methods=['GET','POST'])
def InsertGovSchemeRedir():
	return render_template('/ipdvisit/ipdadmin_add_remove.html',flag = 0,gflag=1)

@app.route('/ViewGovScheme',methods=['GET','POST'])
def ViewGovScheme():
	data = adm.getAllGovScheme()#FileName=/pyfile/admin/adminstuff.py.
	return render_template('/ipdvisit/ipdadmin_add_remove.html',data=data,flag = 0,gflag=2)

@app.route('/InsertNewGovScheme',methods=['GET','POST'])
def InsertNewGovScheme():
	result = adm.InsertNewGovSchemeData()#FileName=/pyfile/admin/adminstuff.py.
	if result == 1:
		return redirect(url_for('blank_InsertNewGovScheme'))
	else:
		return render_template('/ipdvisit/ipdadmin_add_remove.html',flag = 0,gflag=1,ack=result)

@app.route('/blank_InsertNewGovScheme',methods=['GET','POST'])
def blank_InsertNewGovScheme():
	return render_template('/ipdvisit/ipdadmin_add_remove.html',flag = 0,gflag=1,ack="DATA INSERTED SUCCESSFULLY!")

@app.route('/UpdateGovScheme',methods=['GET','POST'])
def UpdateGovScheme():
	result = adm.UpdateGovSchemeData()#FileName=/pyfile/admin/adminstuff.py.
	if result == 1:
		return render_template('/ipdvisit/ipdadmin_add_remove.html',flag = 0,gflag=2,ack="DATA UPDATED SUCCESSFULLY!")
	else:
		return render_template('/ipdvisit/ipdadmin_add_remove.html',flag = 0,gflag=2,ack=result)

@app.route('/DeactivateGovScheme',methods=['GET','POST'])
def DeactivateGovScheme():
	result = adm.DeactivateGovSchemeData()#FileName=/pyfile/admin/adminstuff.py.
	if result == 1:
		return render_template('/ipdvisit/ipdadmin_add_remove.html',flag = 0,gflag=2,ack="Scheme Has Deactivated Successfully!")
	else:
		return render_template('/ipdvisit/ipdadmin_add_remove.html',flag = 0,gflag=2,ack=result)


################################################################################
##################################Government Scheme Admin END###########################
################################################################################






##--------------ADMIT PATIENT END AP_END-----------------

##--------------LAB--------------------------------------

@app.route('/Insertnewsample',methods=['GET','POST'])
def Insertnewsample():
	result = lab.newSample() #FileName = pyfile/lab/lab.py
	if request.method == 'GET':
		return render_template('/lab/add_sample.html',ack="")
	if result==1:
		return redirect(url_for('blank_Insertnewsample'))
	else:
		return render_template('/lab/add_sample.html',ack=result)

@app.route('/blank_Insertnewsample',methods=['GET','POST'])
def blank_Insertnewsample():
	return render_template('/lab/add_sample.html',ack="DATA SUCCESSFULLY STORED!")

	#return render_template('/lab/update_sample.html',data=data,ack=str(data[1]))
@app.route('/Updatesample',methods=['GET','POST'])
def Updatesample():
	result = lab.updateSample()
	data = lab.get_all_samples() #data from database
	if result==1:
		return render_template('/lab/view_samples.html',ack="DATA SUCCESSFULLY UPDATED!",value=data)
	else:
		return render_template('/lab/view_samples.html',ack=result)



@app.route('/Insertnewpanel',methods=['GET','POST'])
def Insertnewpanel():
	data = lab.get_all_samples() #data from database
	if request.method == 'GET':
		return render_template('/lab/add_panel.html',ack="",value=data)
	result = lab.newPanel() #FileName = pyfile/lab/lab.py
	if result==1:
		return redirect(url_for('blank_Insertnewpanel'))
	else:
		return render_template('/lab/add_panel.html',ack=result,value=data)

@app.route('/blank_Insertnewpanel',methods=['GET','POST'])
def blank_Insertnewpanel():
	data = lab.get_all_samples() #data from database
	return render_template('/lab/add_panel.html',ack="DATA SUCCESSFULLY STORED!",value=data)

@app.route('/Updatepanel',methods=['GET'])
def Updatepanel():
	pid=request.args['pid']
	data1 = lab.get_panel_from_id(pid)
	value = lab.get_all_samples()
	return render_template('/lab/update_panel.html',pdata=data1,value=value)


	#return render_template('/lab/update_sample.html',data=data,ack=str(data[1]))
@app.route('/Updatepanel2',methods=['GET','POST'])
def Updatepanel2():
	result = lab.updatePanel()
	value = lab.get_all_samples()
	if result==1:
		return render_template('/lab/view_panels.html',sdata=value,ack="DATA SUCCESSFULLY UPDATE!")
	else:
		return render_template('/lab/update_panel.html',ack=result)


@app.route('/Insertnewtest',methods=['GET','POST'])
def Insertnewtest():
	data1 = lab.get_all_samples() #data from database
	if request.method == 'GET':
		return render_template('/lab/add_test.html',ack="",value1=data1)
	result = lab.newTest() #FileName = pyfile/lab/lab.py
	if result==1:
		return redirect(url_for('blank_Insertnewtest'))
	else:
		return render_template('/lab/add_test.html',ack=result,value1=data1)

@app.route('/blank_Insertnewtest',methods=['GET','POST'])
def blank_Insertnewtest():
	data1 = lab.get_all_samples() #data from database
	return render_template('/lab/add_test.html',ack="DATA SUCCESSFULLY STORED!",value1=data1)


@app.route('/Updatetest',methods=['GET'])
def Updatetest():
	tid = request.args['tid']
	pid = request.args['pid']
	if pid=='0':
		data1 = lab.get_test_from_id_Nopanel(tid)
	else:
		data1 = lab.get_test_from_id(tid)
	value = lab.get_all_samples()
	print("HEHEH",data1)
	return render_template('/lab/update_test.html',data=data1,value1=value)


	#return render_template('/lab/update_sample.html',data=data,ack=str(data[1]))
@app.route('/Updatetest2',methods=['GET','POST'])
def Updatetest2():
	result = lab.updateTest()
	value = lab.get_all_samples()
	if result==1:
		return render_template('/lab/view_tests.html',sdata=value)
	else:
		return render_template('/lab/update_test.html',ack=result)





@app.route('/getpanel',methods=['POST'])
def getpanel():
    sname = request.form['sname']
    rows = lab.getpanel_1(sname)
    return json.dumps({'data' : rows})


@app.route('/Viewsample',methods=['GET','POST'])
def Viewsample():
	data = lab.get_all_samples() #data from database
	return render_template('/lab/view_samples.html',value=data)

@app.route('/Viewpanel',methods=['GET','POST'])
def Viewpanel():
	sdata = lab.get_all_samples() #data from database
	return render_template('/lab/view_panels.html',sdata=sdata)

@app.route('/ViewpanelById',methods=['GET','POST'])
def ViewpanelById():
	sdata = lab.get_all_samples() #data from database
	data = lab.get_panel_from_id_forSample(request.form['samplename']) #data from database
	print("qwewretry",data)
	return render_template('/lab/view_panels.html',data=data,sdata=sdata)

@app.route('/getPanelInfo',methods=['GET','POST'])
def getPanelInfo():
	data = lab.get_panel_from_id_forSample(request.form['sname']) #data from database
	return json.dumps({'data':data})


@app.route('/Viewtest',methods=['GET','POST'])
def Viewtest():
	sdata = lab.get_all_samples() #data from database
	return render_template('/lab/view_tests.html',sdata=sdata)

@app.route('/ViewtestByFilter',methods=['GET','POST'])
def ViewtestByFilter():
	sid = request.form['sampleid']
	pid = request.form['panelid']
	print("SID",sid)
	print("PID",pid)
	sdata = lab.get_all_samples() #data from database
	if pid == '0':
		print("I AM IF")
		data = lab.get_test_by_samid(sid)
	else:
		print("I AM ELSE")
		data = lab.get_test_by_samid_pid(sid,pid)
	return render_template('/lab/view_tests.html',data=data,sdata=sdata,pid=pid)


@app.route('/labadmin',methods=['GET','POST'])
def lab_admin():
	return render_template('/lab/lab_admin.html')

@app.route('/labtesttest',methods=['GET','POST'])
def testtest():
	sam = lab.get_all_samples()
	return render_template('/lab/collectsample.html',sam=sam)


@app.route('/getSampleDetails',methods=['POST','GET'])
def getSampleDetails():
    sampleid=request.form['sample']
    panel=lab.getSampleDetails_1(sampleid)
    test=lab.getSampleDetails_2(sampleid)
    return json.dumps({'panel':panel,'test':test})

@app.route('/getPanelTest',methods=['GET','POST'])
def getPanelTest():
    panelid=request.form['panelid']
    paneltest=lab.getPanelTest_1(panelid)
    return json.dumps({'paneltest':paneltest})


@app.route('/collectsample',methods=['GET','POST'])
def collectsample():
	acno = lab.getTadayLabPatient()  #FileName = pyfile/lab/lab.py
	tname = lab.getTadayTest() #FileName = pyfile/lab/lab.py
	return render_template("lab/collectsamplemain.html",acno=acno,tname=tname)


@app.route('/getpatientdatafromsource',methods=['GET','POST'])
def getpatientdatafromsource():
	regno=request.form['regno']
	location=request.form['location']
	sam = lab.get_all_samples()
	#xname=lab.get_ptdata() #FileName = pyfile/admin/adminstuff.py
	#subname=adm.getAllSubXray() #FileName = pyfile/admin/adminstuff.py
	#dataset1 = reg.getPatient_Registration_All(regno)
	if location=="OPD":
		locdata = lab.getOpdPatientdata(regno) #FileName = pyfile/Xray/xray.py
		if (len(locdata) > 0):
			return render_template('/lab/collectsample.html',ds1=locdata,ack1='',sam=sam)
		else:
			return render_template('/lab/collectsamplemain.html',ack1="INVALID REGISTRATION NUMBER!")
	elif location=="Ward":
		locdata = lab.getWardPatientdata(regno) #FileName = pyfile/Xray/xray.py
		if (len(locdata) > 0):
			return render_template('/lab/collectsample.html',ds1=locdata,ack1='',sam=sam)
		else:
			return render_template('/lab/collectsamplemain.html',ack1="INVALID REGISTRATION NUMBER!")
	else:
		return render_template('/lab/collectsamplemain.html',ack1="INVALID REGISTRATION NUMBER!")
'''
	if len(locdata)>0:
		return render_template('/lab/collectsample.html',ds1=locdata,loc=location,ack1='')
'''

@app.route('/test_id_collect',methods=['GET','POST'])
def test_id_collect():
	listt = (request.form.getlist('testid'))
	#print("LIST",listt)
	a = []
	for i in listt:
		if i.isdigit():
			a.append(i)
	#print ("WITHOUT ",a)
	'''
	regno = request.form['regno']
	source = request.form['source']
	source_id = request.form['source_id']
	tdate = request.form['tdate']
	#print(regno+'/'+source+'/'+source_id+'/'+tdate)
	'''
	result = lab.new_sample_collect()
	if result == 1:
		res = lab.save_test_data(a)
		if res == 1:
			return redirect(url_for('blank_test_id_collect'))
	else:
		return str(a)

@app.route('/blank_test_id_collect',methods=['GET','POST'])
def blank_test_id_collect():
	acno = lab.getTadayLabPatient()  #FileName = pyfile/lab/lab.py
	tname = lab.getTadayTest() #FileName = pyfile/lab/lab.py
	return render_template('/lab/collectsamplemain.html',ack1="Data Successfully Saved!",acno=acno,tname=tname)


@app.route('/editSample_Redir',methods=['GET','POST'])
def editSample_Redir():
	return render_template('/lab/viewcollectsample.html')

@app.route('/editSample',methods=['GET','POST'])
def editSample():
	pname = request.form['page']
	acno = request.form['accession_no']
	ldata = lab.getLabPatientByAcno(acno,"0")#FileName = pyfile/lab/lab.py
	tdata = lab.get_all_tests_with_panel_sampleByAcc(acno)#FileName = pyfile/lab/lab.py
	tname = lab.get_all_tests()#FileName = pyfile/lab/lab.py
	return render_template('/lab/updatesamplecollect.html',ldata=ldata,tdata=tdata,pname=pname,tname=tname)

@app.route('/getTestbySample',methods=['GET','POST'])
def getTestbySample():
	tname = lab.get_all_testsBySampleId(request.form['sid'])
	return json.dumps({'data':tname})

@app.route('/updateSampleCollect',methods=['GET','POST'])
def updateSampleCollect():
	pname = request.form['pname']
	result = lab.updateTestSampleCollect()#FileName = pyfile/lab/lab.py
	if result == 1:
		if pname=="Fpage":
			return redirect(url_for('collectsample'))
		elif pname=="Spage":
			return redirect(url_for('editSample_Redir'))
	else:
		return render_template('/lab/updatesamplecollect.html',ack=result)


@app.route('/getSampleByAccNo',methods=['GET','POST'])
def getSampleByAccNo():
	testdata = ''
	labdata = lab.getLabPatientByAcno(request.form['acno'],"0")  #FileName = pyfile/lab/lab.py
	if len(labdata)>0:
		testdata= lab.getTestByAcno(labdata[0][0]) #FileName = pyfile/lab/lab.py
		return render_template('/lab/viewcollectsample.html',labdata=labdata,testdata=testdata,ack="")
	else:
		return render_template('/lab/viewcollectsample.html',ack="No Data Found")

@app.route('/getSampleByRegNo',methods=['GET','POST'])
def getSampleByRegNo():
	testdata=''
	labdata = lab.getLabPatientByRegno(request.form['regno'],"0")  #FileName = pyfile/lab/lab.py
	if len(labdata)>0:
		testdata = lab.getTestByRegno(labdata[0][0]) #FileName = pyfile/lab/lab.py
		return render_template('/lab/viewcollectsample.html',labdata=labdata,testdata=testdata,ack="")
	else:
		return render_template('/lab/viewcollectsample.html',ack="No Data Found")

@app.route('/getSampleByDate',methods=['GET','POST'])
def getSampleByDate():
	testdata=''
	labdata= lab.getLabPatientByDate(request.form['fdate'],request.form['tdate'])  #FileName = pyfile/lab/lab.py
	if len(labdata)>0:
		testdata= lab.getTestByDate(labdata[0][0],request.form['fdate'],request.form['tdate']) #FileName = pyfile/lab/lab.py
		return render_template('/lab/viewcollectsample.html',labdata=labdata,testdata=testdata,ack="")
	else:
		return render_template('/lab/viewcollectsample.html',ack="No Data Found")

@app.route('/validate_sample_Redir',methods=['GET','POST'])
def validate_sample_Redir():
	acno = lab.getTadayLabValidationPatient()#FileName = pyfile/lab/lab.py
	vdata= lab.getTadayValidationTest()#FileName = pyfile/lab/lab.py
	notval= lab.getLabNotValidationPatient()#FileName = pyfile/lab/lab.py
	nvaltest = lab.getNotValidationTest()#FileName = pyfile/lab/lab.py
	return render_template('/lab/validate_sample_Redir.html',acno=acno,vdata=vdata,notval=notval,nvaltest=nvaltest)

'''
@app.route('/validate_sample',methods=['GET','POST'])
def validate_sample():
	#smp_name = []
	kk = []
	accession_no = request.form['accession_no']
	sql = 'select regno,date,source,source_id from lab_sample_collect where accession_no ='+str(accession_no)
	cursor.execute(sql)
	smp_data = cursor.fetchall()
	#print(smp_data)
	sqll="select regno,pfname,pmname,psname,sex,age from patient_registration where regno = '" + str(smp_data[0][0])+"'"
	cursor.execute(sqll)
	pat_data = cursor.fetchall()
	sqlll = "select tid from lab_test_data where accession_no = "+str(accession_no)
	cursor.execute(sqlll)
	test_data = cursor.fetchall()
	for i in test_data:
		test_detail = lab.get_test_from_id(i[0])
		print((test_detail[0]))
		test_detail1 = list(test_detail[0])
		smp_detail = lab.get_sample_from_id(test_detail[0][1])
		test_detail1.append((smp_detail[0][1]))
		kk.append(test_detail1)

	print(kk)
	if len(smp_data) > 0 and len(pat_data) > 0:
		return render_template('/lab/validate_sample.html',smp_data = smp_data,pat_data= pat_data,test_data=test_data,test_detail=kk)
	else:
		return render_template('/lab/validate_sample_Redir.html', ack1 = "Accession no is Invalid!")
'''

@app.route('/validate_sample',methods=['GET','POST'])
def validate_sample():
	accession_no = str(request.form['accession_no'])
	print("acccc",accession_no)
	pat_data = lab.validateSamplePatientDetails(accession_no)#FileName = pyfile/lab/lab.py
	data = lab.validateSampleTestDetails(accession_no)#FileName = pyfile/lab/lab.py
	if len(data) > 0 and len(pat_data) > 0:
		return render_template('lab/validate_sample.html',data=data,pat_data=pat_data)
	else:
		return render_template('/lab/validate_sample_Redir.html', ack1 = "Accession no is Invalid!")


@app.route('/save_test_values',methods=['GET','POST'])
def save_test_values():
	listt1 = (request.form.getlist('textvalue'))
	listt2 = (request.form.getlist('ltd_id'))
	res = lab.update_testvalues(listt1,listt2)
	if res == 1:
		return jsonify({"ack":"DATA SUCCESSFULLY UPDATED!"})
	else:
		return jsonify({"ack":res})
'''
@app.route('/blank_save_test_values',methods=['GET','POST'])
def blank_save_test_values():
	acno = lab.getTadayLabValidationPatient()#FileName = pyfile/lab/lab.py
	vdata= lab.getTadayValidationTest()#FileName = pyfile/lab/lab.py
	return render_template('/lab/validate_sample.html',ack1="Data Successfully Updated!",acno=acno,vdata=vdata)
'''

@app.route('/lab_report_Redir',methods=['GET','POST'])
def lab_report_Redir():
	return render_template('/lab/viewvalidatesample.html')

@app.route('/getValSampleByAccNo',methods=['GET','POST'])
def getValSampleByAccNo():
	testdata = ''
	labdata = lab.getLabPatientByAcno(request.form['acno'],"1")  #FileName = pyfile/lab/lab.py
	if len(labdata)>0:
		testdata= lab.getTestByAcno(labdata[0][0]) #FileName = pyfile/lab/lab.py
		return render_template('/lab/viewvalidatesample.html',labdata=labdata,testdata=testdata,ack="")
	else:
		return render_template('/lab/viewvalidatesample.html',ack="No Data Found")

@app.route('/getValSampleByRegNo',methods=['GET','POST'])
def getValSampleByRegNo():
	testdata=''
	labdata = lab.getLabPatientByRegno(request.form['regno'],"1")  #FileName = pyfile/lab/lab.py
	if len(labdata)>0:
		testdata = lab.getTestByRegno(labdata[0][0]) #FileName = pyfile/lab/lab.py
		return render_template('/lab/viewvalidatesample.html',labdata=labdata,testdata=testdata,ack="")
	else:
		return render_template('/lab/viewvalidatesample.html',ack="No Data Found")

@app.route('/getValSampleByDate',methods=['GET','POST'])
def getValSampleByDate():
	testdata=''
	labdata= lab.getValidateLabPatientByDate(request.form['fdate'],request.form['tdate'])#FileName = pyfile/lab/lab.py
	if len(labdata)>0:
		testdata= lab.getValidateTestByDate(labdata[0][0],request.form['fdate'],request.form['tdate']) #FileName = pyfile/lab/lab.py
		return render_template('/lab/viewvalidatesample.html',labdata=labdata,testdata=testdata,ack="")
	else:
		return render_template('/lab/viewvalidatesample.html',ack="No Data Found")

@app.route('/printLabReport',methods=['GET','POST'])
def printLabReport():
	testdata = ''
	labdata = lab.getLabPatientForPrint(request.form['acno'])  #FileName = pyfile/lab/lab.py
	print("LABABA",labdata)
	if len(labdata)>0:
		testdata= lab.getTestForPrint(labdata[0][0]) #FileName = pyfile/lab/lab.py
		print("FIRST dsfsdfds",type(testdata))
		sdata=[]
		samdata=[]
		for s in range(len(testdata)):
			sdata.append(testdata[s][1])
		for x in sdata:
			if x not in samdata:
				samdata.append(x)
			else:
				samdata.append('')

		for s in range(len(testdata)):
			sdata[s]= list(testdata[s][:]) + [samdata[s]]
		return render_template('/lab/printlabreport.html',labdata=labdata,testdata=sdata,ack="")
	else:
		return render_template('/lab/validate_sample.html',ack="No Data Found")

@app.route('/lab_report',methods=['GET','POST'])
def lab_report():
	accession_no = request.form['accession_no']
	sqll="select p.regno,p.pfname,p.pmname,p.psname,p.age,p.sex,l.date,l.source,l.source_id from lab_sample_collect l, patient_registration p where l.regno = p.regno and accession_no = "+str(accession_no)
	cursor.execute(sqll)
	pat_data = cursor.fetchall()
	sql = "select s.sample_name,t.test_name,t.Unit,t.Male_Range_min,t.Male_Range_max,t.Female_Range_min,t.Female_Range_max,lt.tid,lt.test_value from admin_addsample s, admin_addtest t,lab_sample_collect l,lab_test_data lt where  s.id = t.sid and lt.tid = t.id and l.accession_no = lt.accession_no and lt.accession_no = "+str(accession_no) +" order by s.sample_name desc ;"
	cursor.execute(sql)
	data = cursor.fetchall()
	if len(data) > 0 and len(pat_data) > 0:
		return render_template('lab/lab_report.html',data=data,pat_data=pat_data)
	else:
		return render_template('/lab/lab_report_Redir.html', ack1 = "Accession no is Invalid!")



##################=========Lab Data Search===========########################################

@app.route('/labacknowlegeRedir',methods=['GET','POST'])
def labacknowlegeRedir():
	dataset1=lab.get_all_samples()
	dataset2=lab.get_all_tests()
	return render_template('/lab/labacknowledge.html',ds1=dataset1,ds2=dataset2)

@app.route('/getAllTestDataForReport',methods=['GET','POST'])
def getAllTestDataForReport():
	sname=request.form['sname']
	print("i am sm",sname)
	ds1=lab.getAllTestBySample(sname)
	print("testname",ds1)
	return json.dumps({'data' : ds1});

@app.route('/getLabAllData',methods=['GET','POST'])
def getLabAllData():
	fdate=request.form['fdate']
	tdate=request.form['tdate']
	testname=request.form['testname']
	dataset1=lab.get_all_samples()
	dataset2=lab.get_all_tests()
	dataset5=lab.getAllTestDataAck(fdate,tdate,testname,app.config['UPLOAD_FOLDER_LAB'])
	if len(dataset5)>0:
		return render_template('/lab/labacknowledge.html',ds1=dataset1,ds2=dataset2,ds5=dataset5,msg="Excel Sheet Generated Successfully")
	else:
		return render_template('/lab/labacknowledge.html',ds1=dataset1,ds2=dataset2,msg="Sorry!No Data Found")



#-------------------END LAB--------------------------------------------------


###########################################################
###########################################################
######################## WARD START#########################
###########################################################
###########################################################

@app.route('/WardLogin',methods=['GET','POST'])
def WardLogin():
	wd=wrd.getAllWardData()#FileName=/pyfile/ward/wardstuff.py.
	return render_template('/wards/wardslogin.html',wd=wd)



@app.route('/reginward',methods=['GET','POST'])
def reginward():
	wardname= request.form['wardname']
	wid= request.form['wid']
	showdata=wrd.showWardAdmitPatient(wid)#FileName=/pyfile/ward/wardstuff.py.
	return render_template('/wards/reginward.html',wname=wardname,wid=wid,showdata=showdata)

@app.route('/patientregno',methods=['GET','POST'])
def patientregno():
	wid= request.form['wid']
	beds=wrd.getBeds(wid)
	regno=request.form['regno']
	pdetails=wrd.getPatientDetails(regno,wid)#FileName=/pyfile/ward/wardstuff.py.
	if len(pdetails) > 0:
		pwardstatus=wrd.getpatientWardStatus(regno)#FileName=/pyfile/ward/wardstuff.py.
		if len(pwardstatus) == 0:
			return render_template('/wards/patient_regno.html',wname=request.form['wname'],wid=request.form['wid'],beds=beds,pdetails=pdetails)
		else:
			wardname=request.form['wname']
			wid= request.form['wid']
			showdata=wrd.showWardAdmitPatient(wid)#FileName=/pyfile/ward/wardstuff.py.
			return render_template('/wards/reginward.html',wname=wardname,wid=wid,showdata=showdata,ack1="This Patient IS Already Admitted in ",wn=pwardstatus[0][0])
	else:
		wardname=request.form['wname']
		wid= request.form['wid']
		showdata=wrd.showWardAdmitPatient(wid)#FileName=/pyfile/ward/wardstuff.py.
		return render_template('/wards/reginward.html',wname=wardname,wid=wid,showdata=showdata,ack1="IPD RECEIPT IS NOT GENERATED OR THIS PATIENT IS ADMITTED FOR DIFFERENT WARD BY COUNTER!")


@app.route('/insertInWard',methods=['GET','POST'])
def insertInWard():
	wardname= request.form['wardname']
	wid=request.form['wid']
	bedno=request.form['bedno']

	insertdata=wrd.insertWardMainData()#FileName=/pyfile/ward/wardstuff.py.
	if insertdata == 1:
		return redirect(url_for('blank_Insertwardmain',wardname=wardname,wid=wid,bedno=bedno))
	else:
		return render_template('/wards/patient_regno.html',wname=wardname,ack=insertdata)

@app.route('/blank_Insertwardmain',methods=['GET','POST'])
def blank_Insertwardmain():
	wid= request.args['wid']
	bedno= request.args['bedno']
	uresult = wrd.updateBedStatus(bedno)#FileName=/pyfile/ward/wardstuff.py.
	print("Uresy",uresult)
	if uresult == 1:
		showdata=wrd.showWardAdmitPatient(wid)#FileName=/pyfile/ward/wardstuff.py.
		return render_template('/wards/reginward.html',wname=request.args['wardname'],wid=request.args['wid'],ack="DATA SUCCESSFULLY STORED",showdata=showdata)
	else:
		return render_template('/wards/reginward.html',ack=uresult)


@app.route('/wardAdminRedir',methods=['GET','POST'])
def wardAdminRedir():
	wd=wrd.getAllWardData()#FileName=/pyfile/ward/wardstuff.py.
	return render_template('/wards/wardadmin.html',wd=wd)

@app.route('/InsertwardName',methods=['GET','POST'])
def InsertwardName():
	wname=request.form['wname']
	ins=wrd.insertWardData()#FileName=/pyfile/ward/wardstuff.py.
	if ins == 1:
		wd=wrd.getAllWardData()#FileName=/pyfile/ward/wardstuff.py.
		return redirect(url_for('blank_InsertwardName'))
	else:
		return render_template('/wards/wardadmin.html',ack=ins)

@app.route('/blank_InsertwardName',methods=['GET','POST'])
def blank_InsertwardName():
	wd=wrd.getAllWardData()#FileName=/pyfile/ward/wardstuff.py.
	return render_template('/wards/wardadmin.html',wd=wd)

@app.route('/editward',methods=['GET','POST'])
def editward():
	ewd=wrd.editWardData()#FileName=/pyfile/ward/wardstuff.py.
	wd=wrd.getAllWardData()#FileName=/pyfile/ward/wardstuff.py.
	return render_template('/wards/wardadmin.html',flag="edit",ewn=ewd,wd=wd)

@app.route('/updateward',methods=['GET','POST'])
def updateward():
	ewd=wrd.updateWardData()#FileName=/pyfile/ward/wardstuff.py.
	if ewd == 1:
		wd=wrd.getAllWardData()#FileName=/pyfile/ward/wardstuff.py.
		return render_template('/wards/wardadmin.html',wd=wd)
	else:
		return render_template('/wards/wardadmin.html',msg=ewd)

@app.route('/GetWardBedNoRedir',methods=['GET','POST'])
def GetWardBedNoRedir():
	wd=wrd.getAllWardData()#FileName=/pyfile/ward/wardstuff.py.
	return render_template('/wards/WardBedAdd.html',wd=wd)

@app.route('/SearchBed',methods=['GET','POST'])
def SearchBed():
	#ins=wrd.insertWardBed()#FileName=/pyfile/ward/wardstuff.py
	wb=wrd.getWardBeds(str(request.form['wid']))#FileName=/pyfile/ward/wardstuff.py.
	return json.dumps({'data' : wb})

@app.route('/InsertWardBeds',methods=['GET','POST'])
def InsertWardBeds():
	wid = request.form['wid']
	ins=wrd.insertWardBed()#FileName=/pyfile/ward/wardstuff.py.
	print("MSG",ins)
	if ins == 1:
		return redirect(url_for('blank_InsertBed',wid=wid))
	else:
		return render_template('/wards/WardBedAdd.html',ack=ins)

@app.route('/blank_InsertBed',methods=['GET','POST'])
def blank_InsertBed():
	wid=request.args['wid']
	wbd=wrd.getWardBeds(wid)#FileName=/pyfile/ward/wardstuff.py.
	wd=wrd.getAllWardData()#FileName=/pyfile/ward/wardstuff.py.
	return render_template('/wards/WardBedAdd.html',wbd=wbd,wd=wd)

@app.route('/Edit_Ward_Bed',methods=['GET','POST'])
def Edit_Ward_Bed():
	wid=request.args['wid']
	wbd=wrd.getWardBedNo(wid)#FileName=/pyfile/ward/wardstuff.py.
	wd=wrd.getAllWardData()#FileName=/pyfile/ward/wardsSurgeryWardRedirtuff.py.
	return render_template('/wards/WardBedAdd.html',flag="EditBed",wd=wd,wbd=wbd)

@app.route('/updateBedNo',methods=['GET','POST'])
def updateBedNo():
	ewd=wrd.updateWardBedData()#FileName=/pyfile/ward/wardstuff.py.
	if ewd == 1:
		wd=wrd.getAllWardData()#FileName=/pyfile/ward/wardstuff.py.
		return render_template('/wards/WardBedAdd.html',wd=wd,msg="DATA SUCCESSFULLY UPDATED!")
	else:
		return render_template('/wards/WardBedAdd.html',msg=ewd)

@app.route('/GetWardAdminRedir',methods=['GET','POST'])
def GetWardAdminRedir():
	return render_template('/wards/WardAdminPage.html')


@app.route('/PatientTranferFromWard',methods=['GET','POST'])
def PatientTranferFromWard():
	regno=request.args['regno']
	wrd_id=request.args['wrd_id']
	print(wrd_id,"wrd_id")
	wid=request.args['wid']
	print(wid,"wid")
	bid=request.args['bid']
	print(bid,"bid")
	pdetails=wrd.getTransferPatientDetails(wrd_id)#FileName=/pyfile/ward/wardstuff.py.
	wd=wrd.getAllWardData()#FileName=/pyfile/ward/wardstuff.py.
	return render_template('/wards/patientTransferFromWard.html',wd=wd,pdetails=pdetails,wrd_id=wrd_id,wid=wid,bid=bid)

@app.route('/patientTransferWardBed',methods=['GET','POST'])
def patientTransferWardBed():
	wid=request.form['wid']
	wb=wrd.getBeds(str(wid))#FileName=/pyfile/ward/wardstuff.py.
	return json.dumps({'data' : wb})

@app.route('/goTransferPatient',methods=['GET','POST'])
def goTransferPatient():
	tp=wrd.InsertPatientTransferData()#FileName=/pyfile/ward/wardstuff.py.
	if tp==1:
		wardname= request.form['wname']
		wid= request.form['wid']
		return redirect(url_for('blank_goTransferPatient',wname=wardname,wid=wid))
	else:
		return render_template('/wards/patientTransferFromWard.html',ack=tp)

@app.route('/blank_goTransferPatient',methods=['GET','POST'])
def blank_goTransferPatient():
	wid=request.args['wid']
	showdata=wrd.showWardAdmitPatient(wid)#FileName=/pyfile/ward/wardstuff.py.
	return render_template('/wards/reginward.html',wname=request.args['wname'],wid=wid,showdata=showdata,msg="Patient Transferred To Another Ward !")

@app.route('/GetTransferMed',methods=['GET','POST'])
def GetTransferMed():
	wd=wrd.getAllWardData()#FileName=/pyfile/ward/wardstuff.py.
	mdtype=med.GetMedType()#FileName=/pyfile/medicine/medicine.py.
	return render_template('/wards/medicineTransfer.html',wd=wd,mdtype=mdtype)

@app.route('/getDrugsFromWard',methods=['GET','POST'])
def getDrugsFromWard():
	wardnameid=request.form['wardnameid']
	drugtype=request.form['drugtype']
	drugname=request.form['drugname']
	warddrugs=wrd.getDrugsAvailableInWard(wardnameid,drugtype,drugname)
	print(warddrugs,"warddrugs")
	return json.dumps({'data' : warddrugs})

@app.route('/getSelectedWardNameId',methods=['GET','POST'])
def getSelectedWardNameId():
	wardnameid=wrd.getSelectedFromWard(request.form['wardnameid'])
	return json.dumps({'data' : wardnameid})

@app.route('/getWardNameId',methods=['GET','POST'])
def getWardNameId():
	updatemed=wrd.OutwardDetailUpdateFromWard()
	print(updatemed)
	if updatemed==1:
		return redirect(url_for('blank_getWardNameId'))
	else:
		wd=wrd.getAllWardData()#FileName=/pyfile/ward/wardstuff.py.
		mdtype=med.GetMedType()#FileName=/pyfile/medicine/medicine.py.
		return render_template('/wards/medicineTransfer.html',wd=wd,mdtype=mdtype,msg=updatemed)

@app.route('/blank_getWardNameId',methods=['GET','POST'])
def blank_getWardNameId():
	wd=wrd.getAllWardData()#FileName=/pyfile/ward/wardstuff.py.
	mdtype=med.GetMedType()#FileName=/pyfile/medicine/medicine.py.
	return render_template('/wards/medicineTransfer.html',wd=wd,mdtype=mdtype,msg1="DATA SUBMITTED SUCCESSFULLY...!")



######################################################## WARD CHARTS START #######################################################

@app.route('/chartlogin',methods=['GET','POST'])
def chartlogin():
	return render_template('/wards/chartlogin.html')

@app.route('/charts',methods=['GET','POST'])
def charts():
	if request.method=="GET":
		wmid=request.args['wmid']
		regno=request.args['regno']
		wname=request.args['wardname']
		#wid=request.form['wid']
		pdata=chart.getChartDataByRegno(regno)#FileName=/pyfile/ward/chartdata.py.
		drugtype=med.GetMedType()#FileName=/pyfile/medicine/medicine.py.
		dataset2=adm.getAllDressing()
		dataset3=adm.getAllPhy()
		return render_template('/wards/charts.html',pdata=pdata,drugtype=drugtype,wmid=wmid,wname=wname,wardid=request.args['wardid'],ds2=dataset2,ds3=dataset3)
	elif wid=='6':
		wmid=request.args['wmid']
		regno=request.args['regno']
		wname=request.args['wardname']
		wid=request.form['wid']
		pdata=chart.getChartDataByRegno(regno)#FileName=/pyfile/ward/chartdata.py.
		drugtype=med.GetMedType()#FileName=/pyfile/medicine/medicine.py.
		dataset2=adm.getAllDressing()
		dataset3=adm.getAllPhy()
		return render_template('/wards/Nursery_Charts.html',pdata=pdata,drugtype=drugtype,wid=wid,wname=wname,ds2=dataset2,ds3=dataset3)


@app.route('/InsertTPR',methods=['GET','POST'])
def InsertTPR():
	result=chart.insertTPRdata()#FileName=/pyfile/ward/chartdata.py.
	if result==1:
		return jsonify({"ack":"DATA SUCCESSFULLY STORED!"})
	else:
		return jsonify({"ack":result})


@app.route('/getMedicineWard',methods=['GET','POST'])
def getMedicineWard():
	drugname=request.form['drugname']
	medtype=request.form['medtype']
	wardid=request.form['wardid']
	mdata=chart.getMedicineForWard(drugname,medtype,wardid)
	print("hello",mdata)
	return jsonify(mdata)

@app.route('/insertWardMedicine',methods=['GET','POST'])
def insertWardMedicine():
	result=chart.insertWardMedicineData()#FileName=/pyfile/ward/chartdata.py.
	if result==1:
		return jsonify({"ack":"DATA SUCCESSFULLY STORED!"})
	else:
		return jsonify({"ack":result})

@app.route('/getMedicineWardIntake',methods=['GET','POST'])
def getMedicineWardIntake():
	print("I AM IN ")
	intakename=request.form['intake']
	wardid=request.form['wardid']
	mdata=chart.getMedicineForWardIntake(intakename,wardid)
	print("VALUESSSSSS",mdata)
	return jsonify(mdata)


@app.route('/InsertWardIntake',methods=['GET','POST'])
def InsertWardIntake():
	result=chart.insertWardIntakeData()#FileName=/pyfile/ward/chartdata.py.
	if result==1:
		return jsonify({"ack":"DATA SUCCESSFULLY STORED!"})
	else:
		return jsonify({"ack":result})

@app.route('/getMedicineWardConsume',methods=['GET','POST'])
def getMedicineWardConsume():
	print("I AM IN ")
	consume=request.form['consume']
	wardid=request.form['wardid']
	mdata=chart.getMedicineForWardConsume(consume,wardid)
	print("VALUESSSSSS",mdata)
	return jsonify(mdata)

@app.route('/insertWardConsume',methods=['GET','POST'])
def insertWardConsume():
	result=chart.insertWardConsumeData()#FileName=/pyfile/ward/chartdata.py.
	if result==1:
		return jsonify({"ack":"DATA SUCCESSFULLY STORED!"})
	else:
		return jsonify({"ack":result})


@app.route('/getMedicineWardSugar',methods=['GET','POST'])
def getMedicineWardSugar():
	print("I AM IN ")
	insuline=request.form['insuline']
	wardid=request.form['wardid']
	mdata=chart.getMedicineForWardSugar(insuline,wardid)
	print("VALUESSSSSS",mdata)
	return jsonify(mdata)

@app.route('/insertWardSugar',methods=['GET','POST'])
def insertWardSugar():
	result=chart.insertWardSugarData()#FileName=/pyfile/ward/chartdata.py.
	if result==1:
		return jsonify({"ack":"DATA SUCCESSFULLY STORED!"})
	else:
		return jsonify({"ack":result})

@app.route('/getMedicineWardPoison',methods=['GET','POST'])
def getMedicineWardPoison():
	print("I AM IN ")
	injection=request.form['injection']
	wardid=request.form['wardid']
	mdata=chart.getMedicineForWardPoison(injection,wardid)
	print("VALUESSSSSS",mdata)
	return jsonify(mdata)

@app.route('/insertWardPoison',methods=['GET','POST'])
def insertWardPoison():
	result=chart.insertWardPoisonData()#FileName=/pyfile/ward/chartdata.py.
	if result==1:
		return jsonify({"ack":"DATA SUCCESSFULLY STORED!"})
	else:
		return jsonify({"ack":result})


@app.route('/getDressing',methods=['GET','POST'])
def getDressing():
	dname=request.form['dname']
	ds1=chart.getAllDressingAmount(dname)  #FileName=/pyfile/ward/chartdata.py.
	return json.dumps({'data' : ds1});

@app.route('/insertWardDressing',methods=['GET','POST'])
def insertWardDressing():
	result=chart.insertWardDressingData()#FileName=/pyfile/ward/chartdata.py.
	if result==1:
		return jsonify({"ack":"DATA SUCCESSFULLY STORED!"})
	else:
		return jsonify({"ack":result})

@app.route('/getPhysiotherapy',methods=['GET','POST'])
def getPhysiotherapy():
	pname=request.form['pname']
	ds2=chart.getAllPhysiotherapyAmount(pname)  #FileName=/pyfile/ward/chartdata.py.
	return json.dumps({'data' : ds2});

@app.route('/insertWardPhysiotherapy',methods=['GET','POST'])
def insertWardPhysiotherapy():
	result=chart.insertWardPhysiotherapyData() #FileName=/pyfile/ward/chartdata.py.
	if result==1:
		return jsonify({"ack":"DATA SUCCESSFULLY STORED!"})
	else:
		return jsonify({"ack":result})

######################################################### WARD CHARTS UPDATE #####################################################

@app.route('/UpdateCharts',methods=['GET','POST'])
def UpdateCharts():
	wardname= request.args['wardname']
	wid= request.args['wardid']
	regno=request.args['regno']
	wmid=request.args['wmid']
	pdata=chart.getChartDataByRegno(regno)#FileName=/pyfile/ward/chartdata.py.
	tprd=chart.getPatientTPRData(wmid)#FileName=/pyfile/ward/chartdata.py.
	dresstype=adm.getAllDressing() #FileName=/pyfile/admin/adminstuff.py.
	pdressing=chart.getPatientDressingData(wmid)#FileName=/pyfile/ward/chartdata.py.
	physio=chart.getPatientPhysioData(wmid)#FileName=/pyfile/ward/chartdata.py.
	physiotype=adm.getAllPhy()#FileName=/pyfile/admin/adminstuff.py.
	poison=chart.getPatientPoisonData(wmid)#FileName=/pyfile/ward/chartdata.py.
	return render_template('/wards/chartUpdate.html',wname=wardname,wid=wid,pdata=pdata,wmid=wmid,tprd=tprd,pdressing=pdressing,dresstype=dresstype,physio=physio,physiotype=physiotype,poison=poison)

@app.route('/getPatientMedData',methods=['GET','POST'])
def getPatientMedData():
	return render_template('/wards/chartUpdate.html')

@app.route('/getPatientTPRData',methods=['GET','POST'])
def getPatientTPRData():
	return render_template('/wards/chartUpdate.html')

@app.route('/updatePatientTPR',methods=['GET','POST'])
def updatePatientTPR():
	result=chart.UpdatePatientTPRData() #FileName=/pyfiles/ward/chartdata.py
	if result==1:
		return jsonify({"ack":"DATA UPDATED SUCCESSFULLY!"})
	else:
		return jsonify({"ack":result})

@app.route('/updateWardPatientDressing',methods=['GET','POST'])
def updateWardPatientDressing():
	result=chart.UpdateWardDressing() #FileName=/pyfiles/ward/chartdata.py
	if result==1:
		return jsonify({"ack":"DATA UPDATED SUCCESSFULLY!"})
	else:
		return jsonify({"ack":result})

@app.route('/getPhysioAmount',methods=['GET','POST'])
def getPhysioAmount():
	physioname=request.form['physioname']
	phy=chart.getAllPhysioAmount(physioname)
	print("i am amount",phy)  #FileName=/pyfile/ward/chartdata.py.
	return json.dumps({'data' : phy})

@app.route('/updatePhysioData',methods=['GET','POST'])
def updatePhysioData():
	result=chart.updatePhysiotherepyData() #FileName=/pyfiles/ward/chartdata.py
	if result==1:
		return jsonify({"ack":"DATA UPDATED SUCCESSFULLY!"})
	else:
		return jsonify({"ack":result})


######################################################### WARD CHARTS UPDATE ENDS ################################################

##################################################################################################################################
######################################################## WARD CHARTS ENDS ########################################################
##################################################################################################################################

################################################################################################################################
############################################################# WARD END #########################################################
################################################################################################################################



###################################################################################################################################
################################################ SURGERY WARD START ###############################################################
###################################################################################################################################

@app.route('/SurgeryAdminRedir',methods=['GET','POST'])
def SurgeryAdminRedir():
	return render_template('/wards/SurgeryAdminRedir.html')

@app.route('/SurgeryRedir',methods=['GET','POST'])
def SurgeryRedir():
	getTodayList=wrd.getTodaySurgeryPatient()#FileName=/pyfile/ward/wardstuff.py.
	print(getTodayList,"oooooooooooooooooooooooooooooooooooooooooooooo")
	return render_template('/wards/surgerylogin.html',getTodayList=getTodayList)

@app.route('/InsertSDetails', methods=['GET','POST'])
def InsertSDetails():
	result=wrd.insertSurgeryDetails()#FileName=/pyfile/ward/wardstuff.py.
	if result==1:
		return redirect(url_for('blank_InsertSdetails'))
	else:
		return render_template('/wards/surgerylogin.html',ack1=result)

@app.route('/blank_InsertSdetails',methods=['GET','POST'])
def blank_InsertSdetails():
	getTodayList=wrd.getTodaySurgeryPatient()#FileName=/pyfile/ward/wardstuff.py.
	return render_template('/wards/surgerylogin.html',ack="Data Successfully Stored",getTodayList=getTodayList)

@app.route('/getSurgeryProAmount',methods=['GET','POST'])
def getSurgeryProAmount():
	result = wrd.getSurgerySPamount(request.form['psurgery'])
	return json.dumps({'adata':result})

@app.route('/Surgery',methods=['GET','POST'])
def Surgery():
	surgerylist=wrd.showSurgeryProcedureList()#FileName=/pyfile/ward/wardstuff.py.
	regno=request.form['regno']
	source = request.form['source']
	if source == "OUTPATIENT":
		surgerydetails=wrd.getSurgeryPatientDetailsOpd(regno)#FileName=/pyfile/ward/wardstuff.py.
	elif source == "INPATIENT":
		surgerydetails=wrd.getSurgeryPatientDetailsIpd(regno)#FileName=/pyfile/ward/wardstuff.py.
		print(surgerydetails,"roiht")
	return render_template('/wards/surgerydetails.html',surgerydetails=surgerydetails,surgerylist=surgerylist,source=source)

@app.route('/AddSurgeryProcedureRedir',methods=['GET','POST'])
def AddSurgeryProcedureRedir():
	surgerylist=wrd.showSurgeryProcedureList()#FileName=/pyfile/ward/wardstuff.py.
	return render_template('/wards/AddSurgeryProcedure.html',surgerylist=surgerylist)

@app.route('/EditeSurgeryType',methods=['GET','POST'])
def EditeSurgeryType():
	sid=request.args['sid']
	editspro=wrd.editSprocedure(sid)#FileName=/pyfile/ward/wardstuff.py.
	surgerylist=wrd.showSurgeryProcedureList()#FileName=/pyfile/ward/wardstuff.py.
	return render_template('/wards/AddSurgeryProcedure.html',surgerylist=surgerylist,flag="edit",editspro=editspro)

@app.route('/updateSprocedureType',methods=['GET','POST'])
def updateSprocedureType():
	spl=wrd.EditSurgeryName()#FileName=/pyfile/ward/wardstuff.py.
	if spl == 1:
		surgerylist=wrd.showSurgeryProcedureList()#FileName=/pyfile/ward/wardstuff.py.
		return render_template('/wards/AddSurgeryProcedure.html',surgerylist=surgerylist,ack1="Data Updated Successfully")
	else:
		return render_template('/wards/AddSurgeryProcedure.html',ack=spl)

@app.route('/InsertSprocedure',methods=['GET','POST'])
def InsertSprocedure():
	getspro=wrd.insertSurgeryProcedure()#FileName=/pyfile/ward/wardstuff.py.
	request.form
	if getspro==1:
		return redirect(url_for('blank_InsertSprocedure'))
	else:
		return render_template('/wards/AddSurgeryProcedure.html',ack1="Data Not Stored",getspro=getspro)

@app.route('/blank_InsertSprocedure',methods=['GET','POST'])
def blank_InsertSprocedure():
	surgerylist=wrd.showSurgeryProcedureList()#FileName=/pyfile/ward/wardstuff.py.
	return render_template('/wards/AddSurgeryProcedure.html',ack="Data Successfully Stored",surgerylist=surgerylist)

@app.route('/EditSurgeryDetails',methods=['GET','POST'])
def EditSurgeryDetails():
	surgerylist=wrd.showSurgeryProcedureList()#FileName=/pyfile/ward/wardstuff.py.
	sid=request.args['sid']
	print(sid,"aaaaaaaaaaaaaa")
	pfrom=request.args['pfrom']
	print(pfrom,"bbbbbbbbbbb")
	if pfrom=="OUTPATIENT":
		getSpatient=wrd.getCurrentSurgeryPatientOpd(sid)#FileName=/pyfile/ward/wardstuff.py.
	elif pfrom=="INPATIENT":
		getSpatient=wrd.getCurrentSurgeryPatientIpd(sid)#FileName=/pyfile/ward/wardstuff.py.
		print(getSpatient,"oooooooooooooooooooooooooooooooooooooooooooooo")
	return render_template('/wards/surgeryEdit.html',getSpatient=getSpatient,surgerylist=surgerylist,sid=sid)

@app.route('/UpdaetSurgeryDetails',methods=['GET','POST'])
def UpdaetSurgeryDetails():
	sid=request.form['sid']
	uSergery=wrd.UpdateSurgeryDetails(sid)#FileName=/pyfile/ward/wardstuff.py.
	getTodayList=wrd.getTodaySurgeryPatient()#FileName=/pyfile/ward/wardstuff.py.
	return render_template('/wards/surgerylogin.html',getTodayList=getTodayList,msg="Data Updated Successfully")

@app.route('/ViewSurgeryPatientRedir',methods=['GET','POST'])
def ViewSurgeryPatientRedir():
	sprocedure=wrd.showSurgeryProcedureList()#FileName=/pyfile/ward/wardstuff.py.
	return render_template('/wards/SurgeryPatientView.html',sprocedure=sprocedure)

@app.route('/ShowSurgeryPatientRedir',methods=['GET','POST'])
def ShowSurgeryPatientRedir():
	sprocedure=wrd.showSurgeryProcedureList()#FileName=/pyfile/ward/wardstuff.py.
	fdate=request.form['fdate']
	tdate=request.form['tdate']
	pfrom=request.form['pfrom']
	bydate=wrd.getAllSurgeryPatientByDate(app.config['UPLOAD_FOLDER_SURG'])
	if len(bydate)>0:
		return render_template('/wards/SurgeryPatientView.html',bydate=bydate,sprocedure=sprocedure,msg="Excel Sheet Generated Successfully")
	else:
		return render_template('/wards/SurgeryPatientView.html',msg1="Sorry! No Data Found")


@app.route('/ShowSurgeryPatientByTypes',methods=['GET','POST'])
def ShowSurgeryPatientByTypes():
		sprocedure=wrd.showSurgeryProcedureList()#FileName=/pyfile/ward/wardstuff.py.
		fdate=request.form['fdate']
		tdate=request.form['tdate']
		ksurgerytype=request.form['ksurgerytype']
		stype=request.form['stype']
		anstype=request.form['anstype']
		psurgery=request.form['psurgery']
		bydate=wrd.getSurgeryPatientSearchExcel(app.config['UPLOAD_FOLDER_SURG'])
		if len(bydate)>0:
			return render_template('/wards/SurgeryPatientView.html',sprocedure=sprocedure,bydate=bydate,msg2="Excel Sheet Generated Successfully")
		else:
			return render_template('/wards/SurgeryPatientView.html',msg1="Sorry! No Data Found")

@app.route('/EditSurgeryDetails1',methods=['GET','POST'])
def EditSurgeryDetails1():
	sprocedure=wrd.showSurgeryProcedureList()#FileName=/pyfile/ward/wardstuff.py.
	return render_template('/wards/surgeryEdit.html',sprocedure=sprocedure)

###################################################################################################################################
######################################################## SURGERY WARD CODES ENDS ##################################################
###################################################################################################################################


###########################################################
###########################################################
################### Delivery Starts#######################
###########################################################
###########################################################

#================Delivery Admin Section================

@app.route('/deliverytype',methods=['GET','POST'])
def deliverytype():
	return render_template('/wards/delivery_add_remove.html',flag = 0)

@app.route('/Insertnewdeliverytype',methods=['GET','POST'])
def Insertnewdeliverytype():
	return render_template('/wards/delivery_add_remove.html',flag = 1)

@app.route('/Viewdeliverytype',methods=['GET','POST'])
def Viewdeliverytype():
	data = wrd.getAllDelType()#FileName=/pyfile/ward/wardstuff.py.
	return render_template('/wards/delivery_add_remove.html',data=data,flag = 2)

@app.route('/InsertDelType',methods=['GET','POST'])
def InsertDelType():
	result = wrd.InsertNewDelType()#FileName=/pyfile/ward/wardstuff.py.
	if result == 1:
		return redirect(url_for('blank_InsertDelType'))
	else:
		return render_template('/wards/delivery_add_remove.html',flag = 1,ack=result)

@app.route('/blank_InsertDelType',methods=['GET','POST'])
def blank_InsertDelType():
	return render_template('/wards/delivery_add_remove.html',flag = 1,ack="DATA INSERTED SUCCESSFULLY!")

@app.route('/UpdateDelType',methods=['GET','POST'])
def UpdateDelType():
	result = wrd.UpdateDelType()#FileName=/pyfile/ward/wardstuff.py.
	if result == 1:
		return render_template('/wards/delivery_add_remove.html',flag = 2,ack="DATA UPDATED SUCCESSFULLY!")
	else:
		return render_template('/wards/delivery_add_remove.html',flag = 2,ack=result)


######################################################################################################################################################
#========================#################################Delivery Starts From Here########################################==========================#

#========================Delivery Starts From Here==========================#

@app.route('/GetdeliveryRedir',methods=['GET','POST'])
def GetdeliveryRedir():
	dataset2=wrd.getCurrentMonthDeliveryChildCount()
	dataset3=wrd.getCurrentYearDeliveryChildCount()
	dataset4=wrd.getPreviousYearDeliveryChildCount()

	return render_template('/wards/deliveryAdmin.html',ds2=dataset2,ds3=dataset3,ds4=dataset4)

@app.route('/deliverylogin',methods=['GET','POST'])
def deliverylogin():
	return render_template('/wards/deliverylogin.html',flag1=1,flag2=0)

@app.route('/delivery',methods=['GET','POST'])
def delivery():
	regno=request.form['regno']
	disdata=wrd.getDeliveryPatientDetail(regno)
	dataset2=wrd.getDeliveryCount()
	tydata = wrd.getAllDelType()
	if len(disdata) > 0:
		return render_template('/wards/delivery.html',ds1=disdata,tydata=tydata,ds2=dataset2)
	else:
		return render_template('/wards/deliverylogin.html',ack1="Invalid registration number",flag1=1)

##===============Delivery Insert==========================#

@app.route('/insertdeliverydetails',methods=['GET','POST'])
def insertdeliverydetails():
	wrd_id=request.form['wrd_id']
	regno=request.form['regno']
	dataset7 = wrd.insertdeliveryDetails() #FileName=/pyfile/ward/wardstuff.py
	print("i am ans",dataset7)

	if dataset7==1:
		return redirect(url_for('blank_InsertDelivery',ds1=dataset7,flag2=1,flag1=1))
	else:
		return render_template('/wards/delivery.html',ack1=dataset7)

@app.route('/blank_InsertDelivery',methods=['GET','POST'])

def blank_InsertDelivery():
	dataset1=wrd.getDeliveryId()
	return render_template('/wards/deliverylogin.html',ack1="DATA STORED SUCCESSFULLY!",flag1=1,flag2=1,ds1=dataset1)


@app.route('/deliveryPrintPage',methods=['GET','POST'])
def deliveryPrintPage():
	dataset3=wrd.getPatientMotherDetails(request.form['delivery_id'])
	dataset4=wrd.getDeliveryChildDetails(request.form['delivery_id'])
	f=0
	for i in range(len(dataset4)):
		if dataset4[i][6]=='Asphyxiated':
			f=f+1
	return render_template('/wards/deliveryPatientPrint.html',ds3=dataset3,ds4=dataset4,flag=f)


#===============================delivery Insert ends==========================#


###==========================Delivery Update Starts============================#
@app.route('/EditDeliveryDetails',methods=['GET','POST'])
def EditDeliveryDetails():
	regno=request.args['regno']
	delivery_id=request.args['delivery_id']
	disdata=wrd.getDeliveryPatientDetail(regno)  			#display ppl details
	disdata2=wrd.getDeliveryData(delivery_id) 				#display mother data
	disdata3=wrd.getDeliveryChildData(delivery_id)				#child data
	tydata = wrd.getAllDelType()
	return render_template('/wards/deliveryUpdate.html',ds1=disdata,ds2=disdata2,ds3=disdata3,tydata=tydata)

@app.route('/deliveryUpdate',methods=['GET','POST'])
def deliveryUpdate():
	return render_template('/wards/deliveryUpdateRedir.html')

@app.route('/deliveryviewregno',methods=['GET','POST'])
def deliveryviewregno():
	dataset = wrd.getDeliveryDetailsbyReg() #FileName=/pyfile/ward/wardstuff.py
	return render_template('/wards/deliveryUpdateRedir.html',ds1=dataset)

@app.route('/deliveryviewfname',methods=['GET','POST'])
def deliveryviewfname():
	dataset = wrd.getDeliveryDetailsbyName() #FileName=/pyfile/ward/wardstuff.py
	return render_template('/wards/deliveryUpdateRedir.html',ds1=dataset)

@app.route('/deliveryviewdate',methods=['GET','POST'])
def deliveryviewdate():
	dataset = wrd.getDeliveryDetailsbyDate() #FileName=/pyfile/ward/wardstuff.py
	return render_template('/wards/deliveryUpdateRedir.html',ds1=dataset)

@app.route('/deliveryviewbwdate',methods=['GET','POST'])
def deliveryviewbwdate():
	fdate=request.form['fdate']
	tdate=request.form['tdate']
	dataset = wrd.getDeliveryDetailsbtdate(fdate,tdate) #FileName=/pyfile/ward/wardstuff.py
	return render_template('/wards/deliveryUpdateRedir.html',ds1=dataset)


@app.route('/updateDeliveryData',methods=['GET','POST'])
def updateDeliveryData():
	result = wrd.UpdatedeliveryDetails() #FileName=/pyfile/ward/wardstuff.py
	if result==1:
		return render_template('/wards/deliveryUpdateRedir.html',ack1="DATA UPDATED SUCCESSFULLY!")
	else:
		return render_template('/wards/deliveryUpdate.html',ack1=result)

@app.route('/getDeliveryAmount',methods=['GET','POST'])
def getDeliveryAmount():
	result = wrd.getFilterDelType(request.form['amount'])
	return json.dumps({'adata':result})




###==========================Delivery Update ENd============================#

###==================Delivery View Starts From Here=======================#
@app.route('/deliveryViewDetail',methods=['GET','POST'])
def deliveryViewDetail():
	return render_template('/wards/deliveryViewDetails.html')


@app.route('/deliveryViewDetailsByregno',methods=['GET','POST'])
def deliveryViewDetailsByregno():
	dataset = wrd.getDeliveryAllDataRegno() #FileName=/pyfile/ward/wardstuff.py
	return render_template('/wards/deliveryViewDetails.html',ds1=dataset)


@app.route('/deliveryviewDetailsByfname',methods=['GET','POST'])
def deliveryviewDetailsByfname():
	dataset = wrd.getDeliveryAllDataName() #FileName=/pyfile/ward/wardstuff.py
	return render_template('/wards/deliveryViewDetails.html',ds1=dataset)

@app.route('/deliveryviewDetailsBydate',methods=['GET','POST'])
def deliveryviewDetailsBydate():
	dataset = wrd.getDeliveryAllDataByDate() #FileName=/pyfile/ward/wardstuff.py
	return render_template('/wards/deliveryViewDetails.html',ds1=dataset)


@app.route('/deliveryviewDetailsbwdate',methods=['GET','POST'])
def deliveryviewDetailsbwdate():
	fdate=request.form['fdate']
	tdate=request.form['tdate']
	dataset = wrd.getDeliveryAllDataBTDate(fdate,tdate,app.config['UPLOAD_FOLDER_DEL']) #FileName=/pyfile/ward/wardstuff.py
	return render_template('/wards/deliveryViewDetails.html',ds1=dataset,msg="Excel Sheet Generated Successfully")

###===============Delivery View & Delivery Final End====================#

###########################################################
###########################################################
################### Delivery End#######################
###########################################################
###########################################################





###################################################################################################################################
##########################################################  MEDICINE START #############################################################
###################################################################################################################################

##---------------------MEDICINE INVENTORY ------------------------------##


###-------adding new medicines-----

@app.route('/inventory',methods=['GET','POST'])
def inventory():
	return render_template('/medicine/frame.html')

##-------admin page for medicine
@app.route('/medicineAdmin',methods=['GET','POST'])
def medicineAdmin():
	return render_template('/medicine/addmedicinemainpage.html')


@app.route('/new_med_Redir',methods=['GET','POST'])
def new_med_Redir():
	result1=med.GetMedType()
	return render_template('/medicine/add_medicine.html',ack=" ",result1=result1)

@app.route('/new_medupadte_Redir',methods=['GET','POST'])
def new_medupadte_Redir():
	return render_template('/medicine/addmedicineupdate.html',ack=" ")


@app.route('/new_med_Insert',methods=['GET','POST'])
def new_med_Insert():
	result = med.AddNewMedicne() #FileName=/pyfile/medicine/newmedicine.py
	if result==1:
		return redirect(url_for('blank_new_med_Insert'))
	else:
		return render_template('/medicine/add_medicine.html',ack=result)

@app.route('/blank_new_med_Insert',methods=['GET','POST'])
def blank_new_med_Insert():
	return render_template('/medicine/add_medicine.html',ack="DATA SUCCESSFULLY STORED!")

@app.route('/UpdateMedicineNameMedtype',methods=['GET','POST'])
def UpdateMedicineNameMedtype():
	getdata1=med.GetMedType()
	result=med.UpdateDrugNameDrugType()
	if request.method=="GET":
		return render_template('/medicine/addmedicineupdate.html',getdata1=getdata1)
	elif request.method=="POST":
		return render_template('/medicine/addmedicineupdate.html',getdata1=getdata1,ack="DATA UPDATED SUCCESSFULLY!")

@app.route('/ViewAllDrugName',methods=['GET','POST'])
def ViewAllDrugName():
	getdata1=med.GetMedType()
	return render_template('/medicine/viewalldrugname.html',getdata1=getdata1)

@app.route('/ShowDrugnames',methods=['GET','POST'])
def ShowDrugnames():
	getdata1=med.GetMedType()
	getdata=med.ShowAllDrugName(app.config['UPLOAD_FOLDER_MEDICINE'])
	if len(getdata)>0:
		return render_template('/medicine/viewalldrugname.html',getdata=getdata,getdata1=getdata1,ack1='Excel Sheet Generated Successfully')
	else:
		return render_template('/medicine/viewalldrugname.html',ack1='Sorry! No Data Found')





@app.route('/UpdateMedicineAdmin',methods=['GET','POST'])
def UpdateMedicineAdmin():
	outdata=med.GetAlldata()
	return jsonify(outdata)


##------------------distributorInsert-----------------##


@app.route('/new_distributor_Redir',methods=['GET','POST'])
def new_distributor_Redir():
	disdata=med.GetAllDistributorType()
	if len(disdata)>0:
		return render_template('/medicine/distributor.html',ack=" ",disdata=disdata)
	else:
		return render_template('/medicine/distributor.html',ack="result")

@app.route('/new_distributor_Insert',methods=['GET','POST'])
def new_distributor_Insert():
	result = med.AddNewDistributor() #FileName=/pyfile/medicine/newmedicine.py
	if result ==1:
		return redirect(url_for('blank_new_distributor_Insert'))
	else:
		return render_template('/medicine/distributor.html',ack=result)

@app.route('/blank_new_distributor_Insert',methods=['GET','POST'])
def blank_new_distributor_Insert():
	disdata=med.GetAllDistributorType()
	if len(disdata)>0:
		return render_template('/medicine/distributor.html',disdata=disdata,ack="Data Stored Successfully!")

###-----------------Update Distributor------------

@app.route('/update_distributor_Redir',methods=['GET','POST'])
def update_distributor_Redir():
	disdata=med.GetAllDistributorType()
	if  len(disdata)>0:
		return render_template('/medicine/updatedistributor.html',ack=" ",disdata=disdata)
	else:
		return render_template('/medicine/updatedistributor.html',ack="result")

@app.route('/new_distributor_update',methods=['GET','POST'])
def new_distributor_update():
	result = med.UpdateDistributor() #FileName=/pyfile/medicine/newmedicine.py
	if result ==1 :
		disdata=med.GetAllDistributorType()
		return render_template('/medicine/updatedistributor.html',disdata=disdata,ack="DATA UPDATED SUCCESSFULLY!")
	else:
		return render_template('/medicine/updatedistributor.html',ack=result)


@app.route('/getDistributorName',methods=['GET','POST'])
def getDistributorName():
	disdata=med.GetAll_DistributorName(request.form['dist_type_id'])
	return json.dumps({'data' : disdata});

@app.route('/getUpdateDistributor',methods=['GET','POST'])
def getUpdateDistributor():
	disname=med.getDistributorAllData(request.form['distributor_id'])
	distype=med.GetAllDistributorType()
	return json.dumps({'disname' : disname,'distype':distype});


##------------Delete Distributor-----------
@app.route('/delete_distributor_Redir',methods=['GET','POST'])
def delete_distributor_Redir():
	disdata=med.GetAllDistributorType()
	if  len(disdata)>0:
		return render_template('/medicine/deletedistributor.html',ack=" ",disdata=disdata)
	else:
		return render_template('/medicine/deletedistributor.html',ack="result")



##----------------inventory insert-----------##

@app.route('/new_inventory_Redir',methods=['GET','POST'])
def new_inventory_Redir():
	disdata=med.GetAllDistributorType()
	if  len(disdata)>0:
		return render_template('/medicine/inventory.html',ack=" ",disdata=disdata)
	else:
		return render_template('/medicine/inventory.html',ack="result")

@app.route('/new_inventory_Insert',methods=['GET','POST'])
def new_inventory_Insert():
	result = med.New_Inventory() #FileName=/pyfile/medicine/newmedicine.py
	if result ==1:
		return redirect(url_for('blank_new_inventory_Insert'))
	else:
		return render_template('/medicine/inventory.html',ack=result)

@app.route('/blank_new_inventory_Insert',methods=['GET','POST'])
def blank_new_inventory_Insert():
	disdata=med.GetAllDistributorType()
	if len(disdata)>0:
		return render_template('/medicine/inventory.html',disdata=disdata,ack="Data Stored Successfully!")


@app.route('/getAllDrugname',methods=['GET','POST']) ##---getting all drug name
def getAllDrugname():
	result=med.getDrugname()
	return jsonify(result)

@app.route('/getSelectedDrug',methods=['GET','POST']) ##---getting all drug name
def getSelectedDrug():
	result=med.getDrugTypeName(request.form['drugtype'])
	print("RESULT",result)
	return json.dumps({'drugdata' : result})


#-----INVENTORY UPDATE----
@app.route('/inventory_search',methods=['GET','POST'])
def inventory_search():
	result=med.GetDrugDeptType()
	print(result)
	return render_template('/medicine/inventory_search.html',result=result)


@app.route('/update_inventory_Redir',methods=['GET','POST'])
def update_inventory_Redir():
	disdata=med.GetAllDistributorType()
	if  len(disdata)>0:
		return render_template('/medicine/updateinventory.html',ack=" ",disdata=disdata)
	else:
		return render_template('/medicine/updateinventory.html',ack="result")

@app.route('/getUpdateInventory',methods=['GET','POST'])
def getUpdateInventory():
	getdata=med.GetAllInventoryDetail()
	disdata=med.GetAllDistributorType()
	#print(getdata)
	return render_template('/medicine/updateinventory.html',getdata=getdata,disdata=disdata)


@app.route('/ViewUpdateInventory',methods=['GET','POST'])
def ViewUpdateInventory():
	getdata1=med.ShowInventoryUpadte()# i changed
	disdata=med.GetAllDistributorType()
	print(getdata1)
	print(disdata)
	return render_template('/medicine/updateinventoryshow.html',getdata1=getdata1,disdata=disdata)


@app.route('/UpdateInventory',methods=['GET','POST'])
def UpdateInventory():
	disdata=med.GetAllDistributorType()
	getdata1=med.UpdateInventory()
	print(getdata1)
	return render_template('/medicine/updateinventory.html',ack="DATA UPDATED SUCCESSFULLY!",disdata=disdata,getdata=' ')


##--------------Add Distributor Type-----------


@app.route('/add_distributorType_Redir',methods=['GET','POST'])
def add_distributorType_Redir():
	return render_template('/medicine/adddistributortype.html',ack=" ")

@app.route('/add_distributorType',methods=['GET','POST'])
def add_distributorType():
	result = med.AddDistributorType() #FileName=/pyfile/medicine/newmedicine.py
	#result1=med.GetAllDistributorName()
	if result ==1:
		return redirect(url_for('blank_add_distributorType'))
	else:
		return render_template('/medicine/adddistributortype.html',ack=result)

@app.route('/blank_add_distributorType',methods=['GET','POST'])
def blank_add_distributorType():
	return render_template('/medicine/adddistributortype.html',ack="DISTRIBUTOR TYPE ADDED SUCCESSFULLY!")


##-----------------------outward---------------------------------------##



##------------ medicine outward main page-------------##
@app.route('/medicine_outward_redir',methods=['GET','POST'])
def medicine_outward_redir():
	return render_template('/medicine/medicineoutwardmainpage.html')


@app.route('/outward_Redir',methods=['GET','POST'])
def outward_Redir():
	result=med.GetAllWardName()
	result1=med.GetMedType()
	print(result1);
	if  len(result)>0:
		return render_template('/medicine/medicineoutward.html',ack="",result=result,result1=result1)
	else:
		return render_template('/medicine/medicineoutward.html',ack=result)

@app.route('/getDrugList',methods=['GET','POST'])
def getDrugList():
	result=med.GetDrugDetailList()
	print(result)
	return json.dumps({'data' : result})

@app.route('/ShowMedicineOutwardDetail',methods=['GET','POST'])
def ShowMedicineOutwardDetail():
	outmeddet=med.Outward_detail_Insert()
	if outmeddet == 1:
		#print("hello everyone");
		invup=med.MedicineOutwardInventoryUpdate()
		#print(invup);
		return redirect(url_for('blank_new_outward_Insert'))
	else:
		return render_template('/medicine/medicineoutward.html',ack=outmeddet,ack1=invup)


@app.route('/blank_new_outward_Insert',methods=['GET','POST'])
def blank_new_outward_Insert():
	outmeddet=med.Outward_detail_Insert()
	result=med.GetAllWardName()
	result1=med.GetMedType()
	return render_template('/medicine/medicineoutward.html',ack="DATA SUCCESSFULLY STORED!",result=result,result1=result1)

@app.route('/UpdateOutwardDetail',methods=['GET','POST'])
def UpdateOutwardDetail():
	result=med.GetAllWardName()
	return render_template('/medicine/updatemedicineoutward.html',result=result)

@app.route('/ViewUpdateOutwardByWard',methods=['GET','POST'])
def ViewUpdateOutwardByWard():
	result=med.GetAllWardName()
	getupdtward=med.ViewUpdateOutwardWard()
	##print(result)
	if len(result)>0:
		return render_template('/medicine/updatemedicineoutward.html',result=result,getdata=getupdtward)

@app.route('/ViewUpdateOutwardByDate',methods=['GET','POST'])
def ViewUpdateOutwardByDate():
	result=med.GetAllWardName()
	print(result)
	getupdtdate=med.ViewUpdateOutwardDate()
	#print(getupdt)
	return render_template('/medicine/updatemedicineoutward.html',result=result,getdata=getupdtdate)

@app.route('/ViewUpdateOutwardByDrugname',methods=['GET','POST'])
def ViewUpdateOutwardByDrugname():
	result=med.GetAllWardName()
	getupdtdrug=med.ViewUpdateOutwardDrugname()
	return render_template('/medicine/updatemedicineoutward.html',result=result,getdata=getupdtdrug)

@app.route('/ViewUpdateOutward',methods=['GET','POST'])
def ViewUpdateOutward():
	result=med.GetAllWardName()
	getdata=med.getViewUpdateOutward()
	return render_template('/medicine/updatemedicineoutwardshow.html',result=result,getdata=getdata)

@app.route('/UpdateOutwardMedicine',methods=['GET','POST'])
def UpdateOutwardMedicine():
	result1=med.GetAllWardName()
	result=med.UpdateOutwardMedicineDetail()
	if result ==1:
		return render_template('/medicine/updatemedicineoutward.html',ack="DATA UPDATED SUCCESSFULLY!",result1=result1)
	else:
		return render_template('/medicine/updatemedicineoutward.html',ack=result)


@app.route('/getMedDetailsOutwardUpdate',methods=['GET','POST'])
def getMedDetailsOutwardUpdate():
	outdata = med.getAllMedicineNoFilter()
	return jsonify(outdata)

#------------GENERAL SEARCH  FOR MEDICNE OUTWARD------------


@app.route('/MedicineOutwardSearch',methods=['GET','POST'])
def MedicineOutwardSearch():
	result=med.GetDrugDeptType()
	result1=med.GetMedType()
	result2=med.GetAllWardName()
	return render_template('/medicine/MedicineOutwardSearch.html',result=result,result1=result1,result2=result2)

@app.route('/ViewByIssuedDate',methods=['GET','POST'])
def ViewByIssuedDate():
	getdata=med.ShowByIssuedDate(app.config['UPLOAD_FOLDER_MEDICINE'])
	result=med.GetDrugDeptType()
	result1=med.GetMedType()
	result2=med.GetAllWardName()
	if len(getdata)>0:
		return render_template('/medicine/MedicineOutwardSearch.html',getdata=getdata,result=result,result1=result1,result2=result2,ack1="Excel Sheet Generated Successfully")
	else:
		return render_template('/medicine/MedicineOutwardSearch.html',ack="No Data Found")



@app.route('/ViewByDrugName',methods=['GET','POST'])
def ViewByDrugName():
	getdata=med.ShowByDrugName(app.config['UPLOAD_FOLDER_MEDICINE'])
	result=med.GetDrugDeptType()
	result1=med.GetMedType()
	result2=med.GetAllWardName()
	if len(getdata)>0:
		return render_template('/medicine/MedicineOutwardSearch.html',getdata=getdata,result=result,result1=result1,result2=result2,ack2="Excel Sheet Generated Successfully")
	else:
		return render_template('/medicine/MedicineOutwardSearch.html',ack2="Sorry! No Data Found")


@app.route('/ViewByDrugType',methods=['GET','POST'])
def ViewByDrugType():
	getdata=med.ShowByDrugType(app.config['UPLOAD_FOLDER_MEDICINE'])
	result=med.GetDrugDeptType()
	result1=med.GetMedType()
	result2=med.GetAllWardName()
	return render_template('/medicine/MedicineOutwardSearch.html',getdata=getdata,result=result,result1=result1,result2=result2,ack3="Excel Sheet Generated Successfully")

@app.route('/ViewByWardNameIssuedDateFromTo',methods=['GET','POST'])
def ViewByWardNameIssuedDateFromTo():
	getdata=med.ShowWardIssuedDate(app.config['UPLOAD_FOLDER_MEDICINE'])
	result=med.GetDrugDeptType()
	result1=med.GetMedType()
	result2=med.GetAllWardName()
	print(result)
	if len(getdata)>0:
		return render_template('/medicine/MedicineOutwardSearch.html',getdata=getdata,result=result,result1=result1,result2=result2,ack4="Excel Sheet Generated Successfully")
	else:
		return render_template('/medicine/MedicineOutwardSearch.html',result2=result2,ack4="Sorry! No Data Found")



@app.route('/ViewDetailsByGeneralSearchMedcineOutward',methods=['GET','POST'])
def ViewDetailsByGeneralSearchMedcineOutward():
	getdata=med.ShowDetailsByGeneralSearchMedcineOutward()
	result=med.GetDrugDeptType()
	result1=med.GetMedType()
	result2=med.GetAllWardName()
	return render_template('/medicine/MedicineOutwardSearch.html',getdata=getdata,result=result,result1=result1,result2=result2)

#------------GENERAL SEARCH  FOR INVENTORY------------
@app.route('/ViewFullDetails',methods=['GET','POST'])
def ViewFullDetails():
	getdata=med.ShowFullDetails(app.config['UPLOAD_FOLDER_MEDICINE'])
	result=med.GetDrugDeptType()
	if len(getdata)>0:
		return render_template('/medicine/inventory_search.html',flag1=2,getdata=getdata,result=result,ack4="Excel Sheet Generated Successfully")
	else:
		return render_template('/medicine/inventory_search.html',flag1=2,ack4="Sorry! No Data Found")



@app.route('/ViewByEntryDate',methods=['GET','POST'])
def ViewByEntryDate():
	getdata=med.ShowByEntryDate(app.config['UPLOAD_FOLDER_MEDICINE'])
	result=med.GetDrugDeptType()
	if len(getdata)>0:
		return render_template('/medicine/inventory_search.html',flag1=1,getdata=getdata,result=result,ack1="Excel Sheet Generated Successfully")
	else:
		return render_template('/medicine/inventory_search.html',flag1=1,ack1="Sorry! No Data Found")



@app.route('/ViewByExpiry',methods=['GET','POST'])
def ViewByExpiry():
	getdata=med.ShowByExpiry(app.config['UPLOAD_FOLDER_MEDICINE'])
	result=med.GetDrugDeptType()
	print("expiry",result)
	#result1=med.GetMedType()
	#result2=med.GetAllWardName()
	if len(getdata)>0:
		return render_template('/medicine/inventory_search.html',flag1=2,getdata=getdata,result=result,ack2="Excel Sheet Generated Successfully")
	else:
		return render_template('/medicine/inventory_search.html',flag1=2,ack2="Sorry! No Data Found")


@app.route('/ViewByDeptNameExpiry',methods=['GET','POST'])
def ViewByDeptNameExpiry():
	getdata=med.ShowByDeptNameExpiry(app.config['UPLOAD_FOLDER_MEDICINE'])
	print("i am data",getdata)
	result=med.GetDrugDeptType()
	print("deptexpiry",result)
	if len(getdata)>0:
		return render_template('/medicine/inventory_search.html',flag1=2,getdata=getdata,result=result,ack3="Excel Sheet Generated Successfully")
	else:
		return render_template('/medicine/inventory_search.html',flag1=2,ack3="Sorry! No Data Found")


@app.route('/ViewDetailsByGeneralSearchInventory',methods=['GET','POST'])
def ViewDetailsByGeneralSearchInventory():
	getdata=med.ShowDetailsByGeneralSearchInventory()
	result=med.GetDrugDeptType()
	return render_template('/medicine/inventory_search.html',flag1=2,getdata=getdata,result=result)

##------------medicine return by ward-----
@app.route('/medicine_return',methods=['GET','POST'])
def medicine_return():
	result1=med.GetAllWardName()
	result=med.MedicineReturnByWard()
	#print("final med return",result);
	return render_template('/medicine/medicinereturnmainpage.html',result1=result1,result=result)

@app.route('/MedicineReturnDetailInsert',methods=['GET','POST'])
def MedicineReturnDetailInsert():
	result1=med.GetAllWardName()
	result=med.MedicineReturnByWard()
	if request.method=="GET":
		return render_template('/medicine/medicinereturn.html',result1=result1,result=result)
	elif request.method=="POST":
		return render_template('/medicine/medicinereturn.html',ack="DATA STORED SUCCESSFULLY!")

	#print("final",result);
	#return render_template('/medicine/medicinereturn.html',result1=result1,result=result,ack="DATA STORED SUCCESSFULLY!")

@app.route('/GetDataForMedicicneReturn',methods=['GET','POST'])
def GetDataForMedicicneReturn():
	outdata=med.RetrieveData()
	return jsonify(outdata)

###-------------GENERAL SEARCH FOR MEDICINE RETURN-------#####
@app.route('/medicineReturnSearch',methods=['GET','POST'])
def medicineReturnSearch():
	result1=med.GetAllWardName()
	return render_template('/medicine/medicinereturnsearch.html',result1=result1)


@app.route('/viewByReturnDate',methods=['GET','POST'])
def viewByReturnDate():
	result1=med.GetAllWardName()
	result=med.MedicineReturnByDateSearch(app.config['UPLOAD_FOLDER_MEDICINE'])
	#print("final",result);
	if len(result)>0:
		return render_template('/medicine/medicinereturnsearch.html',result1=result1,result=result,ack1="Excel Sheet Generated Successfully")
	else:
		return render_template('/medicine/medicinereturnsearch.html',ack1="Sorry! No data Found")


@app.route('/viewByReturnDateWardName',methods=['GET','POST'])
def viewByReturnDateWardName():
	result1=med.GetAllWardName()
	result=med.MedicineReturnByWardDateSearch(app.config['UPLOAD_FOLDER_MEDICINE'])
	#print("final",result);
	if len(result)>0:
		return render_template('/medicine/medicinereturnsearch.html',result1=result1,result=result,ack2="Excel Sheet Generated Successfully")
	else:
		return render_template('/medicine/medicinereturnsearch.html',ack2="Sorry! No data Found")


@app.route('/ViewDetailsByGeneralSearchMedicineReturn',methods=['GET','POST'])
def ViewDetailsByGeneralSearchMedicineReturn():
	result1=med.GetAllWardName()
	result=med.showDetailsByGeneralSearchMedicineReturn()
	#print("final",result);
	return render_template('/medicine/medicinereturnsearch.html',result1=result1,result=result)


#----Notification page-------

@app.route('/Notificationpage',methods=['GET','POST'])
def Notificationpage():
	a=med.checkForExpiry()
	getdata=med.getDataNotificationPageExpiry(app.config['UPLOAD_FOLDER_MEDICINE'])
	result=med.getDataNotificationPageMinValue(app.config['UPLOAD_FOLDER_MEDICINE'])
	result1=med.getDataNotificationPageMaxValue(app.config['UPLOAD_FOLDER_MEDICINE'])
	result2=med.getMedicineExpiryCount(app.config['UPLOAD_FOLDER_MEDICINE'])
	return render_template('/medicine/notificationpage.html',a=a,getdata=getdata,result=result,result1=result1,result2=result2)

@app.route('/ViewBy3MonthExpiry',methods=['GET','POST'])
def ViewBy3MonthExpiry():
	getdata=med.getDataNotificationPageExpiry(app.config['UPLOAD_FOLDER_MEDICINE'])
	aw = wrd.getAllWardData()
	if len(getdata)>0:
		return render_template('/medicine/ViewNotificationDetail.html',getdata=getdata,flag1=1,allward=aw,ack1="Excel Sheet Generated Successfully")
	else:
		return render_template('/medicine/ViewNotificationDetail.html',flag1=1,ack1="Sorry! No data Found")


@app.route('/ViewBy3MonthExpiryOnlyInMedicineStore',methods=['GET','POST'])
def ViewBy3MonthExpiryOnlyInMedicineStore():
	getdata=med.getMedicineExpiryCount(app.config['UPLOAD_FOLDER_MEDICINE'])
	if len(getdata)>0:
		return render_template('/medicine/ViewNotificationDetail.html',getdata=getdata,flag1=2,ack2="Excel Sheet Generated Successfully")
	else:
		return render_template('/medicine/ViewNotificationDetail.html',flag1=2,ack2="Sorry! No data Found")



@app.route('/ViewBy3MonthMinValue',methods=['GET','POST'])
def ViewBy3MonthMinValue():
	getdata=med.getDataNotificationPageMinValue(app.config['UPLOAD_FOLDER_MEDICINE'])
	if len(getdata)>0:
		return render_template('/medicine/ViewNotificationDetail.html',getdata=getdata,flag1=3,ack3="Excel Sheet Generated Successfully")
	else:
		return render_template('/medicine/ViewNotificationDetail.html',flag1=3,ack3="Sorry! No data Found")


@app.route('/ViewBy3MonthMaxValue',methods=['GET','POST'])
def ViewBy3MonthMaxValue():
	getdata=med.getDataNotificationPageMaxValue(app.config['UPLOAD_FOLDER_MEDICINE'])
	if len(getdata)>0:
		return render_template('/medicine/ViewNotificationDetail.html',getdata=getdata,flag1=4,ack4="Excel Sheet Generated Successfully")
	else:
		return render_template('/medicine/ViewNotificationDetail.html',flag1=4,ack4="Sorry! No data Found")


###################################################################################################################################
##########################################################  MEDICINE ENDS #############################################################
###################################################################################################################################


#================Billing Admin Section==================================

@app.route('/billingMain',methods=['GET','POST'])
def billingMain():
	return render_template('/Billing/billing_add_remove.html',dflag=0,pflag=0,tflag=0)


#=====================Dressing=====================================

@app.route('/InsertDressingRedir',methods=['GET','POST'])
def InsertDressingRedir():
	return render_template('/Billing/billing_add_remove.html',dflag=1,pflag=0,tflag=0)

@app.route('/InsertNewDressing',methods=['GET','POST'])
def InsertNewDressing():
	result = adm.InsertNewDressingData()#FileName=/pyfile/admin/adminstuff.py.
	if result == 1:
		return redirect(url_for('blank_InsertNewDressing'))
	else:
		return render_template('/Billing/billing_add_remove.html',dflag=1,pflag=0,tflag=0,ack=result)

@app.route('/blank_InsertNewDressing',methods=['GET','POST'])
def blank_InsertNewDressing():
	return render_template('/Billing/billing_add_remove.html',dflag=1,pflag=0,tflag=0,ack="DATA INSERTED SUCCESSFULLY!")

@app.route('/ViewDressing',methods=['GET','POST'])
def ViewDressing():
	data = adm.getAllDressing()#FileName=/pyfile/admin/adminstuff.py.
	return render_template('/Billing/billing_add_remove.html',dflag=2,pflag=0,tflag=0,data=data)

@app.route('/UpdateDressing',methods=['GET','POST'])
def UpdateDressing():
	result = adm.UpdateDressingData()#FileName=/pyfile/admin/adminstuff.py.
	if result == 1:
		return render_template('/Billing/billing_add_remove.html',dflag=2,pflag=0,tflag=0,ack="DATA UPDATED SUCCESSFULLY!")
	else:
		return render_template('/Billing/billing_add_remove.html',dflag=2,pflag=0,tflag=0,ack=result)

#=====================Dressing=====================================



#=====================Physiotherapy=====================================

@app.route('/InsertPhyRedir',methods=['GET','POST'])
def InsertPhyRedir():
	return render_template('/Billing/billing_add_remove.html',dflag=0,pflag=1,tflag=0)

@app.route('/InsertNewPhy',methods=['GET','POST'])
def InsertNewPhy():
	result = adm.InsertNewPhyData()#FileName=/pyfile/admin/adminstuff.py.
	if result == 1:
		return redirect(url_for('blank_InsertNewPhy'))
	else:
		return render_template('/Billing/billing_add_remove.html',dflag=0,pflag=1,tflag=0,ack=result)

@app.route('/blank_InsertNewPhy',methods=['GET','POST'])
def blank_InsertNewPhy():
	return render_template('/Billing/billing_add_remove.html',dflag=0,pflag=1,tflag=0,ack="DATA INSERTED SUCCESSFULLY!")

@app.route('/ViewPhy',methods=['GET','POST'])
def ViewPhy():
	data = adm.getAllPhy()#FileName=/pyfile/admin/adminstuff.py.
	return render_template('/Billing/billing_add_remove.html',dflag=0,pflag=2,tflag=0,data=data)

@app.route('/UpdatePhy',methods=['GET','POST'])
def UpdatePhy():
	result = adm.UpdatePhyData()#FileName=/pyfile/admin/adminstuff.py.
	if result == 1:
		return render_template('/Billing/billing_add_remove.html',dflag=0,pflag=2,tflag=0,ack="DATA UPDATED SUCCESSFULLY!")
	else:
		return render_template('/Billing/billing_add_remove.html',dflag=0,pflag=2,tflag=0,ack=result)

#=====================Physiotherapy=====================================

#======================= Therapy ==============================================#

@app.route('/InsertTherapyRedir',methods=['GET','POST'])
def InsertTherapyRedir():
	return render_template('/Billing/billing_add_remove.html',dflag=0,pflag=0,tflag=1)

@app.route('/InsertNewTherapy',methods=['GET','POST'])
def InsertNewTherapy():
	result = adm.InsertNewTherapyData()#FileName=/pyfile/admin/adminstuff.py.
	if result == 1:
		return redirect(url_for('blank_InsertNewTherapy'))
	else:
		return render_template('/Billing/billing_add_remove.html',dflag=0,pflag=0,tflag=1,ack=result)

@app.route('/blank_InsertNewTherapy',methods=['GET','POST'])
def blank_InsertNewTherapy():
	return render_template('/Billing/billing_add_remove.html',dflag=0,pflag=0,tflag=1,ack="DATA INSERTED SUCCESSFULLY!")

@app.route('/ViewTherapy',methods=['GET','POST'])
def ViewTherapy():
	data = adm.getAllTherapy()#FileName=/pyfile/admin/adminstuff.py.
	return render_template('/Billing/billing_add_remove.html',dflag=0,pflag=0,tflag=2,data=data)

@app.route('/UpdateTherapy',methods=['GET','POST'])
def UpdateTherapy():
	result = adm.UpdateTherapyData()#FileName=/pyfile/admin/adminstuff.py.
	if result == 1:
		return render_template('/Billing/billing_add_remove.html',dflag=0,pflag=0,tflag=2,ack="DATA UPDATED SUCCESSFULLY!")
	else:
		return render_template('/Billing/billing_add_remove.html',dflag=0,pflag=0,tflag=2,ack=result)

#========================= Therapy ============================================#




############################################BILLING STARTS #############################################################
########################################################################################################################
@app.route("/billmedicinemain",methods=['GET','POST'])
def billmedicinemain():
	return render_template('/Billing/medicinemain.html')

@app.route("/billmedicineRedir",methods=['GET','POST'])
def billmedicineRedir():
	result=mbill.getDocMedicineDetail()
	return render_template('/Billing/newbill.html',data=result)

@app.route("/getPatientDetailBilling",methods=['GET','POST'])
def getPatientDetailBilling():
	user = request.form['user']
	result = mbill.getBillPatientData()#FileName=/pyfile/medicine Billing/medbilling.py.
	if user =='pharmacy':
		if len(result)>0:
			return render_template('/Billing/makepatientbill.html',data=result,ack=' ',user="pharmacy")
		else:
			return render_template('/Billing/newbill.html',ack="NO DATA FOUND")
	elif user == 'doctor':
		bmid=request.form['bmid']
		mresult = mbill.getMedDetails(bmid)
		return render_template('/Billing/makepatientbill.html',data=result,data1=mresult,ack=' ',user="doctor")

@app.route('/getMedicinePharmacy',methods=['GET','POST'])
def getMedicinePharmacy():
	drugname=request.form['drugname']
	mdata=mbill.getMedicineForPharmacy(drugname)
	print("VALUESSSSSS",mdata)
	return jsonify(mdata)

@app.route('/insertPatientDetailBilling',methods=['GET','POST'])
def insertPatientDetailBilling():
	result=mbill.insertPatientDetailBillingData()
	#result=1
	if result==1:
		return jsonify({"ack":"DATA SUCCESSFULLY STORED!"})
	else:
		return jsonify({"ack":result})

@app.route('/updatePatientDetailBilling',methods=['GET','POST'])
def updatePatientDetailBilling():
	result=mbill.updateBillingDetail()
	#result=1
	if result==1:
		return jsonify({"ack":"DATA SUCCESSFULLY UPDATED!"})
	else:
		return jsonify({"ack":result})

@app.route('/generateBill',methods=['GET','POST'])
def generateBill():
	result = mbill.getBillPatientData()#FileName=/pyfile/medicine Billing/medbilling.py.
	return render_template('/Billing/makepatientbill.html',data=result,ack=' ')


@app.route('/opdbillprint',methods=['GET','POST'])
def opdbillprint():
	rfrom =request.args['rfrom']
	if rfrom == 'pharmacy':
		result = mbill.getPatientDetailsPharmacy()
		print("RETRE",result[0][0])
		meddetail = mbill.getPharDetailsForBilling(result[0][0])
	elif rfrom == 'doctor':
		bmid =request.args['bmid']
		result = mbill.getPatientDetailsDoctor(bmid)
		meddetail = mbill.getDocDetailsForBilling(bmid)
		update = mbill.updatePrintStatus(bmid)
	return render_template('/Billing/opdbillprint.html',pdet = result,mdet=meddetail)


@app.route("/opdBillingSearch_Redir",methods=['GET','POST'])
def opdBillingSearch_Redir():
	return render_template('/Billing/opd_billing_search.html')

############################################BILLING ENDS ########################################################
#################################################################################################################
################################OPD Investigation& Services BILLING STARTS ######################################

@app.route("/opdbillingRedir",methods=['GET','POST'])
def opdbillingRedir():
	return render_template('/Billing/opdbillingRedir.html')

@app.route("/opdbillinglogin",methods=['GET','POST'])
def opdbillinglogin():
	return render_template('/Billing/opdBillingInsertRedir.html')

@app.route("/opdibillingupdate",methods=['GET','POST'])
def opdibillingupdate():
	return render_template('Billing/opdbillingEditRedir.html')

@app.route("/opdbillingview",methods=['GET','POST'])
def opdbillingview():
	return render_template('/Billing/opdBillingViewRedir.html')

@app.route("/opdBillingInsertRedir",methods=['GET','POST'])
def opdBillingInsertRedir():
	regno=request.form['regno']
	dataset1=obill.getPatientRegnoBilling()


	if len(dataset1)>0:
		return render_template('/Billing/opdbillingInsert.html',ds1=dataset1)
	else:
		return render_template('/Billing/opdBillingInsertRedir.html',ack1="Invalid Registration Number!")


########################OPD BILLING Ajax AutoSelect code ####################################

@app.route('/getInvestigationName',methods=['GET','POST'])
def getInvestigationName():
	invname=request.form['invname']
	if invname=='Xray':
		ds1=obill.getAllSubXrayName()
	elif invname=='Physiotherapy':
		ds1=obill.getAllPhyName()
	elif invname=='LAB':
		ds1=obill.getAllTestName()
	elif invname=='Dressing':
		ds1=obill.getAllDressingName()
	return json.dumps({'data' : ds1});

@app.route('/getInvestigationAmount',methods=['GET','POST'])
def getInvestigationAmount():
	invid=request.form['invid']
	invtype=request.form['invtype']
	if invtype=='Xray':
		ds1=obill.getsubXrayAmount(invid)
	elif invtype=='Physiotherapy':
		ds1=obill.getphyAmount(invid)
	elif invtype=='LAB':
		ds1=obill.getLabTestAmount(invid)
	elif invtype=='Dressing':
		ds1=obill.getDressingAmount(invid)
	return json.dumps({'data' : ds1});


########################OPD BILLING INSERT STARTS ####################################

@app.route('/insertOpdBilling',methods=['GET','POST'])
def insertOpdBilling():
	regno=request.form['regno']
	opdid=request.form['opdid']
	dataset7 = obill.insertopdbillingmain() #FileName=/pyfile/ward/wardstuff.py

	if dataset7==1:
		return redirect(url_for('blank_InsertOpdBillingMain'))
	else:
		return render_template('/Billing/opdbillingInsert.html',ack1=dataset7)


@app.route('/blank_InsertOpdBillingMain',methods=['GET','POST'])
def blank_InsertOpdBillingMain():
	dataset3=obill.getopmidMain()
	print("kyu",dataset3)
	return render_template('/Billing/opdbillingInsert.html',ack1="DATA STORED SUCCESSFULLY!",ds3=dataset3)


@app.route("/opdDetailsPrint",methods=['GET','POST'])
def opdDetailsPrint():
	dataset1=obill.getOpdPrintMain()
	print("hi",dataset1)
	dataset2=obill.getOpdPrintDetails()
	print("bye",dataset2)

	return render_template('/Billing/opdinvestigationprint.html',ds1=dataset1,ds2=dataset2)


################################OPD Investigation& Services BILLING End ######################################

#####################################################################################################################

#----------------------------------XRAY_STARTS FROM HERE-------------------------------------------#
#--------------------------------------------------------------------------------------------------#


@app.route('/xray_Redir',methods=['GET','POST'])
def xray_Redir():
	return render_template('/X-Ray/xray_Redir.html',ack1='')

@app.route('/xray',methods=['GET','POST'])
def collect():
	loc=' '
	regno=request.form['regno']
	location=request.form['location']
	xname=adm.getAllXray() #FileName = pyfile/admin/adminstuff.py
	subname=adm.getAllSubXray() #FileName = pyfile/admin/adminstuff.py

	if location=="OPD":
		locdata = xray.getOpdPatientXray(regno) #FileName = pyfile/Xray/xray.py
		loc=location
	elif location=="WARD":
		locdata = xray.getWardPatientXray(regno) #FileName = pyfile/Xray/xray.py
	if len(locdata)>0:
		loc=locdata[0][6]
		return render_template('/X-Ray/collect.html',ds1=locdata,loc=loc,ack1='',xname = xname,subname = subname)
	else:
		return render_template('/X-Ray/xray_Redir.html',ack1="INVALID REGISTRATION NUMBER!")


#+++++++++++++++++++++++++++X-Ray Insert Start+++++++++++++++++++++++++++++#


@app.route('/insertXray',methods=['GET','POST'])
def insertXray():
    result=xray.insertXrayDetail(app.config['UPLOAD_FOLDER_XRAY']) #FileName = pyfile/Xray/xray.py
    if result == 1:

        return redirect(url_for('blank_xrayInsert'))
    else:
        return render_template('/X-Ray/collect.html',ack1=result)


@app.route('/blank_xrayInsert',methods=['GET','POST'])
def blank_xrayInsert():
    return render_template('/X-Ray/xray_Redir.html',ack1="DATA STORED SUCCESSFULLY!")



#++++++++++++++++++++++++++++++Insert Xray Ajax Code++++++++++++++++++++++++++#

@app.route('/getAllXraylist',methods=['GET','POST'])
def getAllXraylist():
    xraytype=request.form['xraytype']
    ds1=xray.getAllXray(xraytype)  #FileName = pyfile/Xray/xray.py

    return json.dumps({'data' : ds1});


@app.route('/getAllXraySublist',methods=['GET','POST'])
def getAllXraySublist():
	subxray=request.form['subxray']
	print("i am sub",subxray)
	ds1=xray.getAllSubXray(subxray)  #FileName = pyfile/Xray/xray.py
	print("i am ds",ds1)
	return json.dumps({'data' : ds1});

#++++++++++++++++++++++X-Ray Display Started++++++++++++++++++++++++++++#


@app.route('/xray_displayRedir',methods=['GET','POST'])
def xray_displayRedir():

	return render_template('/X-Ray/xray_AckRedir.html',flag1=0,flag2=0,flag3=0)


#=====================Search BY Registration Number======================#


@app.route('/getXrayDetails',methods=['GET','POST'])
def getXrayDetails():
	regno=request.form['regno']
	ds1=xray.getPatientNameDetails(regno)
	ds2=xray.getPatientXrayDetailXray(regno) #FileName = pyfile/Xray/xray.py

	if len(ds1)>0:
		return render_template('/X-Ray/xray_AckRedir.html',ds2=ds2,ds1=ds1,flag1=1,ack1='',imgpath=app.config['UPLOAD_FOLDER_XRAY'])
	else:
		return render_template('/X-Ray/xray_AckRedir.html',ack1="invalid registration number")



#=====================Search ACK Per Day==============================#

@app.route('/getXrayAcknowledgeByDate',methods=['GET','POST'])
def getXrayAcknowledgeByDate():
	filldate =request.form['filldate']
	dataset = xray.getPatientXrayByDate(filldate)
	dataset2 = xray.getTotalPatientByDate(filldate)
	return render_template('/X-Ray/xray_AckRedir.html',ds4=dataset2,ds3=dataset,flag2=1)




#=============================Search Between Date Monthly=========================#


@app.route('/getXrayAckRange',methods=['GET','POST'])
def getXrayAckRange():
	allxray = adm.getAllXray()
	ackdata = xray.monthlyXrayReport(app.config['UPLOAD_FOLDER_EXRAY'])
	print("nope",ackdata)
	return render_template('/X-Ray/xray_AckRedir.html',allx=allxray,ackdata = ackdata,count=len(allxray),flag3=1,msg="Excel Sheet Generated Successfully")

#==========================Patient Details Xray between dates###############
@app.route('/getXrayPatientDetails',methods=['GET','POST'])
def getXrayPatientDetails():
	Fdate =request.form['Fdate']
	Tdate =request.form['Tdate']
	ds5 = xray.getAllXrayData(Fdate,Tdate)

	return render_template('/X-Ray/xray_AckRedir.html',ds5=ds5,flag4=1)


#++++++++++++++++++++++++++++++UPDATE Xray Ajax Code+++++++++++++++++++++++++++#

@app.route('/getAllXrayList',methods=['GET','POST'])
def getAllXrayList():
    xraytype=request.form['xraytype']
    ds1=xray.getAllXray(xraytype)  #FileName = pyfile/Xray/xray.py
    print(ds1,"ssss")
    return json.dumps({'data' : ds1});

@app.route('/getAllXraySubList',methods=['GET','POST'])
def getAllXraySubist():
	subxray=request.form['subxray']
	#print("i am sub",subxray)
	ds1=xray.getAllSubXray(subxray)  #FileName = pyfile/Xray/xray.py
	#print("i am ds",ds1)
	return json.dumps({'data' : ds1});





#=========================X-Ray Update Started================================#

@app.route('/updateRedir',methods=['GET','POST'])
def updateRedir():
	return render_template('/X-Ray/xray_updateRedir.html')

@app.route('/getxrayupdate',methods=['GET','POST'])
def getxrayupdate():
	loc=' '
	regno=request.form['regno']
	location=request.form['location']
	xname=adm.getAllXray() #FileName = pyfile/admin/adminstuff.py
	subname=adm.getAllSubXray() #FileName = pyfile/admin/adminstuff.py

	if location=="OPD":
		print("I AM OPD")
		locdata=xray.getPatientDetail(regno)   #FileName = pyfile/Xray/xray.py
		print("i am locdatefirst",locdata)
		ds1=xray.getOpdUpdateXray(regno)   #FileName = pyfile/Xray/xray.py
		loc=location

	elif location=="WARD":
		print("I AM WARD")
		locdata = xray.getWardPatientDetail(regno) #FileName = pyfile/Xray/xray.py
		print("i am locdata",locdata)
		ds1=xray.getWardUpdateXray(regno)   #FileName = pyfile/Xray/xray.py
	if len(locdata)>0:
		loc=locdata[0][6]
		return render_template('/X-Ray/update_xray.html',ds1=ds1,ds2=locdata,loc=loc,ack1='',xname = xname,subname = subname,count=len(ds1),imgpath=app.config['UPLOAD_FOLDER_XRAY'])
	else:
		return render_template('/X-Ray/xray_updateRedir.html',ack1="Sorry,No data Found,Check the Regno again!")

@app.route('/update_xray',methods=['GET','POST'])
def update_xray():
	result = xray.updateXrayDetail(app.config['UPLOAD_FOLDER_XRAY']) #FileName = pyfile/Xray/xray.py
	print("i am rs3",result)
	if result==1:
		return redirect(url_for('blank_xrayUpdate'))
	else:
		return render_template('/X-Ray/update_xray.html',ack="ERROR"+result)


@app.route('/blank_xrayUpdate',methods=['GET','POST'])
def blank_xrayUpdate():
    return render_template('/X-Ray/xray_updateRedir.html',ack1="DATA UPDATED SUCCESSFULLY!")





#===========================+X-Ray Admin Starts from Here+=====================#

#===========================+X-Ray Admin Starts from Here+=====================#
@app.route('/xray_partRedir',methods=['GET','POST'])
def xray_partRedir():
    return render_template('/X-Ray/xray_admin.html',flag1=0,flag2=0,flag3=0,flag4=0)

@app.route('/InsertNewXrayRedir',methods=['GET','POST'])
def InsertNewXrayRedir():
    return render_template('/X-Ray/xray_admin.html',flag1=1,flag2=0,flag3=0,flag4=0)

@app.route('/InsertPartType',methods=['GET','POST'])
def InsertPartType():
	xdata=xray.newXrayPart()
	print("i am me",xdata)
	if xdata==1:
		return redirect(url_for('blank_xrayAdminPart'))
	else:
		return render_template('/X-Ray/xray_admin.html',ack=xdata,flag1=1)

@app.route('/blank_xrayAdminPart',methods=['GET','POST'])
def blank_xrayAdminPart():
    return render_template('/X-Ray/xray_admin.html',ack="DATA STORED SUCCESSFULLY!",flag1=1,flag2=0,flag3=0,flag4=0)


@app.route('/ViewXrayTypeRedir',methods=['GET','POST'])
def ViewXrayTypeRedir():
	dataset1=adm.getAllXray()  #FileName = pyfile/admin/adminstuff.py
	print("i am part",dataset1)
	return render_template('/X-Ray/xray_admin.html',flag1=0,flag2=1,flag3=0,flag4=0,ds1=dataset1)

@app.route('/UpdatePartType',methods=['GET','POST'])
def UpdatePartType():
	result = xray.updatepartname() #FileName = pyfile/Xray/xray.py
	print("i am up",result)
	if result == 1:
		return render_template('/X-Ray/xray_admin.html',flag1=0,flag2=1,flag3=0,flag4=0,ack="DATA UPDATED SUCCESSFULLY!")
	else:
		return render_template('/X-Ray/xray_admin.html',flag1=0,flag2=1,flag3=0,flag4=0,ack=result)

###################################################################################################

@app.route('/InsertNewSubXrayRedir',methods=['GET','POST'])
def InsertNewSubXrayRedir():
	dataset1=adm.getAllXray()  #FileName = pyfile/admin/adminstuff.py
	return render_template('/X-Ray/xray_admin.html',flag1=0,flag2=0,flag3=1,flag4=0,ds1=dataset1)

@app.route('/InsertSubPartType',methods=['GET','POST'])
def InsertSubPartType():
	dataset3=xray.newSubXray()  #FileName = pyfile/Xray/xray.py
	if dataset3==1:
		return redirect(url_for('blank_xrayAdminSub'))
	else:
		return render_template('/X-Ray/xray_admin.html',ack=dataset3,flag3=1)

@app.route('/blank_xrayAdminSub',methods=['GET','POST'])
def blank_xrayAdminSub():
	dataset1=adm.getAllXray()  #FileName = pyfile/admin/adminstuff.py
	return render_template('/X-Ray/xray_admin.html',ack="DATA STORED SUCCESSFULLY!",flag1=0,flag2=0,flag3=1,flag4=0,ds1=dataset1)


@app.route('/ViewSubXrayRedir',methods=['GET','POST'])
def ViewSubXrayRedir():
	dataset1=adm.getAllXray()  #FileName = pyfile/admin/adminstuff.py
	dataset2=xray.getAllSubXrayList()  #FileName = pyfile/admin/adminstuff.py
	return render_template('/X-Ray/xray_admin.html',flag1=0,flag2=0,flag3=0,flag4=1,ds1=dataset1,ds2=dataset2)

@app.route('/UpdateSubPartType',methods=['GET','POST'])
def UpdateSubPartType():
	result = xray.updateSubPartName() #FileName = pyfile/Xray/xray.py
	print("i am up2",result)
	if result == 1:
		return render_template('/X-Ray/xray_admin.html',flag1=0,flag2=0,flag3=0,flag4=1,ack="DATA UPDATED SUCCESSFULLY!")
	else:
		return render_template('/X-Ray/xray_admin.html',flag1=0,flag2=0,flag3=0,flag4=1,ack=result)


################################################################################
############################### ++XRAY ENDS HERE++################################
################################################################################

#################################ANC STARTS FROM HERE##########################################################
##--------------------ANC Consult Starts-------------------------------------##



@app.route('/anc_Redir',methods=['GET','POST'])
def anc_Redir():
	return render_template('/ANC/anc_Redir.html',ack1='')

@app.route('/ANCConsult',methods=['GET','POST'])
def ANCConsult():
	regno=request.form['regno']
	dataset1 = anc.getNewPatientVisit(regno) #FileName = /pyfiles/ANC/anc.py
	if len(dataset1)>0:
		checkancreg = anc.getANCMainData(regno) #FileName = /pyfiles/ANC/anc.py
		checkancregold = anc.getFilterCountANCData(regno) #FileName = /pyfiles/ANC/anc.
		print(checkancregold)
		if checkancreg[0][0]==0 and checkancreg[0][1]=='NONE':
			print("I am 1ST")
			insertnew = anc.insertNewANCData()  #FileName = /pyfiles/ANC/anc.py
			return redirect(url_for('blank_ANCConsult',regno=regno))
		elif checkancregold[0][0]==0:
			print("I am 2ND")
			getdata = anc.getFilterAllANCData(regno) #FileName = /pyfiles/ANC/anc.py
			insertnew = anc.insertNewANCData()  #FileName = /pyfiles/ANC/anc.py
			return redirect(url_for('blank_ANCConsultAgain',regno=regno))
			#getph=	anc.getAllPhCount(getdata[0][0])  #FileName = /pyfiles/ANC/anc.py
			#getgh= anc.getAllGhCount(getdata[0][0])   #FileName = /pyfiles/ANC/anc.py
			#getfiv= anc.getAllFiVCount(getdata[0][0])  #FileName = /pyfiles/ANC/anc.py
			#getfov= anc.getAllFoVCount(getdata[0][0])  #FileName = /pyfiles/ANC/anc.py
			#getlc= anc.getAllLcCount(getdata[0][0])  #FileName = /pyfiles/ANC/anc.py
			#getusg= anc.getAllUsgCount(getdata[0][0])  #FileName = /pyfiles/ANC/anc.py
			#return render_template('/ANC/anc_mainpage.html',ds1=dataset1,gd=getdata)
		else:
			print("I am 3RD")
			getdata = anc.getAllANCData(regno) #FileName = /pyfiles/ANC/anc.py
			#getph=	anc.getAllPhCount(getdata[0][0])  #FileName = /pyfiles/ANC/anc.py
			#getgh= anc.getAllGhCount(getdata[0][0])   #FileName = /pyfiles/ANC/anc.py
			#getfiv= anc.getAllFiVCount(getdata[0][0])  #FileName = /pyfiles/ANC/anc.py
			#getfov= anc.getAllFoVCount(getdata[0][0])  #FileName = /pyfiles/ANC/anc.py
			#getlc= anc.getAllLcCount(getdata[0][0])  #FileName = /pyfiles/ANC/anc.py
			#getusg= anc.getAllUsgCount(getdata[0][0])  #FileName = /pyfiles/ANC/anc.py
			return render_template('/ANC/anc_Mainpage.html',ds1=dataset1,gd=getdata)
	else:
		return render_template('/ANC/anc_Redir.html',ds1='',ack1="INVALID REGNO!")


@app.route('/blank_ANCConsult',methods=['GET','POST'])
def blank_ANCConsult():
	regno=request.args['regno']
	dataset1 = anc.getNewPatientVisit(regno) #FileName = /pyfiles/ANC/anc.py
	getdata = anc.getAllANCData(regno) #FileName = /pyfiles/ANC/anc.py
	return render_template('/ANC/anc_Mainpage.html',ds1=dataset1,gd=getdata)

@app.route('/blank_ANCConsultAgain',methods=['GET','POST'])
def blank_ANCConsultAgain():
	regno=request.args['regno']
	dataset1 = anc.getNewPatientVisit(regno) #FileName = /pyfiles/ANC/anc.py
	getdata = anc.getAllANCData(regno) #FileName = /pyfiles/ANC/anc.py
	return render_template('/ANC/anc_Mainpage.html',ds1=dataset1,gd=getdata)

@app.route('/ANCMain',methods=['GET','POST'])
def ANCMain():
	anc_id=request.form['anc_id']
	regno=request.form['regno']
	dataset1=anc.getNewPatientVisit(regno)  #FileName = /pyfiles/ANC/anc.py
	getdata = anc.getFilterAllANCData(regno) #FileName = /pyfiles/ANC/anc.py
	#getph=	anc.getAllPhCount(getdata[0][0])  #FileName = /pyfiles/ANC/anc.py
	#getgh= anc.getAllGhCount(getdata[0][0])   #FileName = /pyfiles/ANC/anc.py
	#getfiv= anc.getAllFiVCount(getdata[0][0])  #FileName = /pyfiles/ANC/anc.py
	#getfov= anc.getAllFoVCount(getdata[0][0])  #FileName = /pyfiles/ANC/anc.py
	#getlc= anc.getAllLcCount(getdata[0][0])  #FileName = /pyfiles/ANC/anc.py
	#getusg= anc.getAllUsgCount(getdata[0][0])  #FileName = /pyfiles/ANC/anc.py
	return render_template('/ANC/anc.html',ds1=dataset1,gd=getdata)


##--------------ANC Patient History Starts------------------------------------##

@app.route('/ANCPatientHistory',methods=['GET','POST'])
def ANCPatientHistory():
	result=anc.insertANCPatientHistory() #FileName=/pyfiles/ANC/anc.py
	if result==1:
		return jsonify({"ack":"DATA SUCCESSFULLY STORED!"})
	else:
		return jsonify({"ack":result})
##--------------------ANC Patient History Ends----------------------------------##

##--------------ANC Gravida History Starts-------------------------------------##

@app.route('/ANCGravidaHistory',methods=['GET','POST'])
def ANCGravidaHistory():
	result=anc.insertANCGravidaHistory() #FileName=/pyfiles/ANC/anc.py
	if result==1:
		return jsonify({"ack":"DATA SUCCESSFULLY STORED!"})
	else:
		return jsonify({"ack":result})

##-------------ANC Gravida History Ends----------------------------------------##

##------------ANC First Visit Starts-------------------------------------------##

@app.route('/ANCFirstVisit',methods=['GET','POST'])
def ANCFirstVisit():
	result=anc.insertANCFirstVisit() #FileName=/pyfiles/ANC/anc.py
	if result==1:
		return jsonify({"ack":"DATA SUCCESSFULLY STORED!"})
	else:
		return jsonify({"ack":result})

##-------------------ANC First Visit Ends-------------------------------------##

##---------------ANC Follow Up Visit Starts-----------------------------------##

@app.route('/ANCFollowUpVisit',methods=['GET','POST'])
def ANCFollowUpVisit():
	result=anc.insertANCFollowUpVisit() #FileName=/pyfiles/ANC/anc.py
	if result==1:
		return jsonify({"ack":"DATA SUCCESSFULLY STORED!"})
	else:
		return jsonify({"ack":result})

##---------------ANC Follow Up Visit Ends------------------------------------##

##---------------ANC Lab Check Up Starts--------------------------------------##

@app.route('/ANCLabCheckUp',methods=['GET','POST'])
def ANCLabCheckUp():
	result=anc.insertANCLabCheckUp() #FileName=/pyfiles/ANC/anc.py
	#dataset9=anc.GetANClcid() #FileName = /pyfiles/ANC/anc.py
	#print("i am dataset9",dataset9)
	if result==1:
		return jsonify({"ack":"DATA SUCCESSFULLY STORED!"})
	else:
		return jsonify({"ack":result})

##-----------------ANC Lab Check Up Ends--------------------------------------##

##---------------ANC USG Report Starts---------------------------------------##

@app.route('/ANCUsgReport',methods=['GET','POST'])
def ANCUsgReport():
	result=anc.insertANCUsgReport() #FileName=/pyfiles/ANC/anc.py
	if result==1:
		return jsonify({"ack":"DATA SUCCESSFULLY STORED!"})
	else:
		return jsonify({"ack":result})
##--------------------ANC USG Report Ends------------------------------------##


##-------------For Deactivating the Registration No in ANC Starts-------------##
@app.route('/ANCIdDeactivate',methods=['GET','POST'])
def ANCIdDeactivate():
	anc_id=request.form['anc_id']
	ds = anc.ANCIdDeactive(anc_id)     #FileName = /pyfiles/ANC/anc.py
	if ds==1:
		return render_template('/ANC/anc_Redir.html',ack1="This Registration No has been deactivated")
	else:
		print("ERRO",ds)
		return render_template('/ANC/anc_Redir.html',ack3=ds)

##-------------For Deactivating the Registration No in ANC Ends-------------##

##------------------ANC Lab Report Print Starts-------------------------------##

@app.route('/labreportsearch',methods=['GET','POST'])
def labreportsearch():
    return render_template('/ANC/anclabreportsearch.html',flag1=0)

@app.route('/GetAllLabDataSearch',methods=['GET','POST'])
def GetAllLabDataSearch():
	regno = request.form['regno']
	dataset1=anc.ANCSearchForLabData(regno) #FileName=/pyfiles/ANC/anc.py

	return render_template('/ANC/anclabreportsearch.html',ds1=dataset1,flag1=1,regno=regno)

@app.route('/ANCLabReportPrint',methods=['GET','POST'])
def ANCLabReportPrint():
	dataset2=anc.ANCLabPrint()  #FileName = /pyfiles/ANC/anc.py
	print("i am print data3",dataset2)
	return render_template('/ANC/ancLabReport.html',ds2=dataset2)

##---------------------ANC Lab Report Print Ends------------------------------##

##------------------ANC USG Report Print Starts-------------------------------##
@app.route('/ANCUsgReportPrint',methods=['GET','POST'])
def ANCUsgReportPrint():
	dataset1=anc.GetANCusgid() #FileName = /pyfiles/ANC/anc.py
	print("2",dataset1)
	usg_id=request.form['usg_id']
	print("1",usg_id)
	dataset2=anc.ANCUsgPrint(usg_id)  #FileName = /pyfiles/ANC/anc.py
	print("3",dataset2)
	return render_template('/ANC/ancUsgReport.html',ds1=dataset1,ds2=dataset2)




##---------------------ANC USG Report Print Ends------------------------------##
##-------------------ANC Consult Ends-----------------------------------------##

##----------------ANC Update Starts------------------------------------------##

@app.route('/ancView_Update_Redir',methods=['GET','POST'])
def ancView_Update_Redir():
	return render_template('/ANC/ancView_Update_Redir.html',ack1='')

@app.route('/ancView_Update',methods=['GET','POST'])
def ancView_Update():
	regno = request.form['regno']
	dataset1 = anc.getANCView_Update(regno) #FileName = /pyfiles/ANC/anc.py
	if len(dataset1)>0 and dataset1[0][10]>0 and dataset1[0][11]>0 and dataset1[0][12]>0 and dataset1[0][13]>0:
		dataset2 = anc.getANCPhView_Update(dataset1[0][9]) #FileName = /pyfiles/ANC/anc.py
		dataset3 = anc.getANCGhView_Update(dataset1[0][9]) #FileName = /pyfiles/ANC/anc.py
		dataset4 = anc.getANCFiVView_Update(dataset1[0][9]) #FileName = /pyfiles/ANC/anc.py
		dataset5 = anc.getANCFoVView_Update(dataset1[0][9]) #FileName = /pyfiles/ANC/anc.py
		dataset6 = anc.getANCLcView_Update(dataset1[0][9]) #FileName = /pyfiles/ANC/anc.py
		dataset7 = anc.getANCUsrView_Update(dataset1[0][9]) #FileName = /pyfiles/ANC/anc.py
		return render_template('/ANC/ancView_Update.html',ds1=dataset1,ds2=dataset2,ghdata=dataset3,FiVdata=dataset4,FoVdata=dataset5,lcdata=dataset6,usgdata=dataset7,ack1='')
	else:
		return render_template('/ANC/ancView_Update_Redir.html',ack1="DATA NOT RECORDED YET OR THIS REG NO HAS BEEN DEACTIVATED !")

##------------ANC Patient's History Update Starts-----------------------------##
@app.route('/ANCUpdatePatientHistory',methods=['GET','POST'])
def ANCUpdatePatientHistory():
	result=anc.updateANCPatientHistory() #FileName=/pyfiles/ANC/anc.py
	if result==1:
		return jsonify({"ack":"DATA UPDATED SUCCESSFULLY!"})
	else:
		return jsonify({"ack":result})


##------------ANC Patient's History Update Ends-------------------------------##

##------------ANC Gravida History Update Starts-------------------------------##
@app.route('/ANCUpdateGravidaHistory',methods=['GET','POST'])
def ANCUpdateGravidaHistory():
	result=anc.updateANCGravidaHistory() #FileName=/pyfiles/ANC/anc.py
	if result==1:
		return jsonify({"ack":"DATA UPDATED SUCCESSFULLY!"})
	else:
		return jsonify({"ack":result})


##------------ANC Gravida History Update Ends---------------------------------##

##-------------For Deleting row in ANC Gravida History Table Starts-----------##
@app.route('/GravidaDeleteRow',methods=['GET','POST'])
def GravidaDeleteRow():
	result = anc.ANCGravidaDeleteRow(request.form['gh_id']) #FileName=/pyfile/ANC/anc.py
	return json.dumps({'data':result})


##-------------For Deleting row in ANC Gravida History Table Ends-----------##


##------------ANC First Visit Update Starts-----------------------------------##
@app.route('/ANCUpdateFirstVisit',methods=['GET','POST'])
def ANCUpdateFirstVisit():
	result=anc.updateANCFirstVisit() #FileName=/pyfiles/ANC/anc.py
	if result==1:
		return jsonify({"ack":"DATA UPDATED SUCCESSFULLY!"})
	else:
		return jsonify({"ack":result})



##------------ANC First Visit Update Ends-------------------------------------##

##------------ANC Follow Up Visit Update Starts-------------------------------##

@app.route('/ANCUpdateFollowUpVisit',methods=['GET','POST'])
def ANCUpdateFollowUpVisit():
	result=anc.updateANCFollowupVisit() #FileName=/pyfiles/ANC/anc.py
	if result==1:
		return jsonify({"ack":"DATA UPDATED SUCCESSFULLY!"})
	else:
		return jsonify({"ack":result})
##------------ANC Follow Up Visit Update Ends---------------------------------##

##------------ANC Lab Check Up Update Starts-------------------------------##

@app.route('/ANCUpdateLabCheckUp',methods=['GET','POST'])
def ANCUpdateLabCheckUp():
	result=anc.updateANCLabCheckUpVisit() #FileName=/pyfiles/ANC/anc.py
	if result==1:
		return jsonify({"ack":"DATA UPDATED SUCCESSFULLY!"})
	else:
		return jsonify({"ack":result})
##------------ANC Lab Check Up Update Ends---------------------------------##

##------------ANC USG Report Update Starts-------------------------------##

@app.route('/ANCUpdateUsgReport',methods=['GET','POST'])
def ANCUpdateUsgReport():
	result=anc.updateANCUsgReportVisit() #FileName=/pyfiles/ANC/anc.py
	if result==1:
		return jsonify({"ack":"DATA UPDATED SUCCESSFULLY!"})
	else:
		return jsonify({"ack":result})
##------------ANC USG Report Update Ends---------------------------------##

##------------------ANC Search Starts-----------------------------------------##
@app.route('/anc_view_gen1',methods=['GET','POST'])
def anc_view_gen1():
	return render_template('/ANC/ancSearch.html',flag1=0,flag2=0,flag3=0,flag4=0,flag5=0)

##------------------ANC Search By Registration No Starts----------------------##
@app.route('/anc_view_gen',methods=['GET','POST'])
def anc_view_gen():
	regno = request.form['regno']
	dataset1=anc.ANCSearchReg(regno) #FileName=/pyfiles/ANC/anc.py
	getdata = anc.getFilterAllANCData(regno) #FileName = /pyfiles/ANC/anc.py
	#dataset8=anc.GetANClcid() #FileName = /pyfiles/ANC/anc.py

	return render_template('/ANC/ancSearch.html',ds1=dataset1,gd=getdata,flag1=1,regno=regno)
##------------------ANC Search By Registration No Ends------------------------##

##------------------ANC Search By Date Starts---------------------------------##
@app.route('/anc_view_date',methods=['GET','POST'])
def anc_view_date():
	frmdate=request.form['frmdate']
	todate=request.form['todate']
	dataset2=anc.ANCSearchDate(frmdate,todate,app.config['UPLOAD_FOLDER_ANC']) #FileName=/pyfiles/ANC/anc.py
	if len(dataset2)>0:
		return render_template('/ANC/ancSearch.html',ds2=dataset2,flag2=1,frmdate=datetime.strptime(frmdate,'%Y-%m-%d'),todate=datetime.strptime(todate,'%Y-%m-%d'),msg="Excel Sheet Generated Successfully")
	else:
		return render_template('/ANC/ancSearch.html',msg="Sorry! No Data Found")

##------------------ANC Search By Date Ends-----------------------------------##

##------------------ANC Search By Immunization Status Starts------------------##
@app.route('/anc_view_imm',methods=['GET','POST'])
def anc_view_imm():
	frmdate=request.form['frmdate']
	todate=request.form['todate']
	immustatus=request.form['immustatus']
	dataset3=anc.ANCSearchImmu(app.config['UPLOAD_FOLDER_ANC']) #FileName=/pyfiles/ANC/anc.py
	if len(dataset3)>0:
		return render_template('/ANC/ancSearch.html',ds3=dataset3,flag3=1,frmdate=datetime.strptime(frmdate,'%Y-%m-%d'),todate=datetime.strptime(todate,'%Y-%m-%d'),immustatus=immustatus,msg1="Excel Sheet Generated Successfully")
	else:
		return render_template('/ANC/ancSearch.html',msg1="Sorry! No Data Found")


##------------------ANC Search By Immunization Status Ends--------------------##

##------------------ANC Search By Haemoglobin Starts--------------------------##

@app.route('/anc_view_hb',methods=['GET','POST'])
def anc_view_hb():
	frmdate=request.form['frmdate']
	todate=request.form['todate']
	hb=request.form['hb']
	blood=request.form['blood']
	dataset4=anc.ANCSearchHb(app.config['UPLOAD_FOLDER_ANC']) #FileName=/pyfiles/ANC/anc.py
	if len(dataset4)>0:
		return render_template('/ANC/ancSearch.html',ds4=dataset4,flag4=1,frmdate=datetime.strptime(frmdate,'%Y-%m-%d'),todate=datetime.strptime(todate,'%Y-%m-%d'),hb=hb,blood=blood,msg2="Excel Sheet Generated Successfully")
	else:
		return render_template('/ANC/ancSearch.html',msg2="Sorry! No Data Found")



##------------------ANC Search By Haemoglobin Ends----------------------------##

##------------------ANC Search By Blood Pressure Starts-----------------------##

@app.route('/anc_view_bp',methods=['GET','POST'])
def anc_view_bp():
	frmdate=request.form['frmdate']
	todate=request.form['todate']
	sys=request.form['sys']
	dia=request.form['dia']
	pressure=request.form['pressure']
	dataset5=anc.ANCSearchBp(app.config['UPLOAD_FOLDER_ANC']) #FileName=/pyfiles/ANC/anc.py
	if len(dataset5)>0:
		return render_template('/ANC/ancSearch.html',ds5=dataset5,flag5=1,frmdate=datetime.strptime(frmdate,'%Y-%m-%d'),todate=datetime.strptime(todate,'%Y-%m-%d'),sys=sys,dia=dia,pressure=pressure,msg3="Excel Sheet Generated Successfully")
	else:
		return render_template('/ANC/ancSearch.html',msg3="Sorry! No Data Found")



##------------------ANC Search By Blood Pressure Ends-----------------------##

##------------------ANC Search Ends-------------------------------------------##

##------------------ANC Report Starts-----------------------------------------##
'''
@app.route('/ancPatientDetails',methods=['GET','POST'])
def ancPatientDetails():
	regno=request.args['regno']
	dataset1=anc.getANCView_Update(regno) #FileName = /pyfiles/ANC/anc.py
	getdata = anc.getFilterAllANCData(regno) #FileName = /pyfiles/ANC/anc.py
	return render_template('/ANC/anc_Mainpage.html',ds1=dataset1,gd=getdata)
'''


@app.route('/ancReport',methods=['GET','POST'])
def ancReport():
	anc_id=request.args['anc_id']
	dataset1=anc.getANCReport(anc_id) #FileName = /pyfiles/ANC/anc.py
	dataset2=anc.getANCPhReport(anc_id) #FileName = /pyfiles/ANC/anc.py
	dataset3=anc.getANCGhReport(anc_id) #FileName = /pyfiles/ANC/anc.py
	dataset4=anc.getANCFiVReport(anc_id) #FileName = /pyfiles/ANC/anc.py
	dataset5=anc.getANCFoVReport(anc_id) #FileName = /pyfiles/ANC/anc.py
	dataset6=anc.getANCLcReport(anc_id) #FileName = /pyfiles/ANC/anc.py
	dataset7=anc.getANCUsgReport(anc_id) #FileName = /pyfiles/ANC/anc.py
	return render_template('/ANC/ancPatientReport.html',ds1=dataset1,ds2=dataset2,ds3=dataset3,ds4=dataset4,ds5=dataset5,ds6=dataset6,ds7=dataset7)

##------------------ANC Report Ends-------------------------------------------##
##############################################################################


###################ANC FINAL END#############################################

###############################################################################

######################################Nursery Starts Here####################################################

@app.route('/insertNursery',methods=['GET','POST'])
def insertNursery():
	wardname= request.form['wardname']
	wid=request.form['wid']
	bedno = request.form['bedno']
	insertdata = wrd.insertNurseryDetails() #FileName=/pyfile/ward/wardstuff.py.
	if insertdata == 1:
		return redirect(url_for('blank_insertnurserymain',wardname=wardname,wid=wid,bedno=bedno))
	else:
		return render_template('/wards/patient_regno.html',wardname=wardname,ack=insertdata)

@app.route('/blank_insertnurserymain',methods=['GET','POST'])
def blank_insertnurserymain():
	wid = request.args['wid']
	bedno = request.args['bedno']
	uresult = wrd.updateBedStatus(bedno) #FileName=/pyfile/ward/wardstuff.py.
	if uresult == 1:
		showdata = wrd.showWardAdmitPatient(wid) #FileName=/pyfile/ward/wardstuff.py.
		return render_template('/wards/reginward.html',wname=request.args['wardname'],wid=request.args['wid'],ack1="DATA SUCCESSFULLY STORED",showdata=showdata)
	else:
		return render_template('/wards/reginward.html',ack=uresult)


@app.route('/Nursery_Charts',methods=['GET','POST'])
def Nursery_Charts():
	wmid=request.args['wmid']
	wardid=request.args['wardid']
	regno=request.args['regno']
	wname=request.args['wardname']
	pdata=chart.getChartDataByRegno(regno) #FileName=/pyfile/ward/chartdata.py.
	drugtype=med.GetMedType() #FileName=/pyfile/medicine/medicine.py.
	dataset2=adm.getAllDressing() #FileName=/pyfile/admin/adminstuff.py.
	dataset3=adm.getAllTherapy() #FileName=/pyfile/admin/adminstuff.py.
	return render_template('/wards/Nursery_Charts.html',pdata=pdata,drugtype=drugtype,wname=wname,wmid=wmid,wardid=wardid,ds2=dataset2,ds3=dataset3)


@app.route('/InsertNurTPR',methods=['GET','POST'])
def InsertNurTPR():
	result=chart.insertNurseryTPRChart()#FileName=/pyfile/ward/chartdata.py.
	if result==1:
		return jsonify({"ack":"DATA SUCCESSFULLY STORED!"})
	else:
		return jsonify({"ack":result})

@app.route('/getTherapy',methods=['GET','POST'])
def getTherapy():
	tname=request.form['tname']
	ds3=chart.getAllTherapyAmount(tname)  #FileName=/pyfile/ward/chartdata.py.
	return json.dumps({'data' : ds3});

@app.route('/insertNurTherapy',methods=['GET','POST'])
def insertNurTherapy():
	result=chart.insertNurseryTherapy() #FileName=/pyfile/ward/chartdata.py.
	if result==1:
		return jsonify({"ack":"DATA SUCCESSFULLY STORED!"})
	else:
		return jsonify({"ack":result})

####################### Nursery Charts Ends ####################################

##################### Nursery View Update Starts ###############################

@app.route('/Nursery_ViewUpdate_Redir',methods=['GET','POST'])
def Nursery_ViewUpdate_Redir():
	regno=request.args['regno']
	wrd_id=request.args['wrd_id']
	dataset1=wrd.getwardsViewUpdate(regno) #FileName=/pyfile/ward/wardstuff.py.
	dataset2=chart.getAllNurseryData(wrd_id) #FileName=/pyfile/ward/chartdata.py.
	dataset3=chart.getAllNurTPRChartData(wrd_id) #FileName=/pyfile/ward/chartdata.py.
	dataset4=chart.getAllDressingData(wrd_id) #FileName=/pyfile/ward/chartdata.py.
	dataset5=adm.getAllDressing() #FileName=/pyfile/admin/adminstuff.py.
	dataset6=chart.getAllTherapyData(wrd_id) #FileName=/pyfile/ward/chartdata.py.
	dataset7 = adm.getAllTherapy()#FileName=/pyfile/admin/adminstuff.py.
	return render_template('/wards/Nursery_ViewUpdate.html',ds1=dataset1,ds2=dataset2,ds3=dataset3,ds4=dataset4,ds5=dataset5,ds6=dataset6,ds7=dataset7,regno=regno,wrd_id=wrd_id)


@app.route('/updateNurSheet',methods=['GET','POST'])
def updateNurSheet():
	result=chart.UpdateNurSheetData() #FileName=/pyfiles/ward/chartdata.py
	if result==1:
		return jsonify({"ack":"DATA UPDATED SUCCESSFULLY!"})
	else:
		return jsonify({"ack":result})

@app.route('/updateNurTPR',methods=['GET','POST'])
def updateNurTPR():
	result=chart.UpdateNurTPRChartData() #FileName=/pyfiles/ward/chartdata.py
	if result==1:
		return jsonify({"ack":"DATA UPDATED SUCCESSFULLY!"})
	else:
		return jsonify({"ack":result})

@app.route('/updateWardDressing',methods=['GET','POST'])
def updateWardDressing():
	result=chart.UpdateWardDressingData() #FileName=/pyfiles/ward/chartdata.py
	if result==1:
		return jsonify({"ack":"DATA UPDATED SUCCESSFULLY!"})
	else:
		return jsonify({"ack":result})

@app.route('/updateNurTherapy',methods=['GET','POST'])
def updateNurTherapy():
	result=chart.UpdateNurseryTherapyData() #FileName=/pyfiles/ward/chartdata.py
	if result==1:
		return jsonify({"ack":"DATA UPDATED SUCCESSFULLY!"})
	else:
		return jsonify({"ack":result})









############################# Nursery Ends ################################################################################################################################################################################################################################################


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5030,debug=True)

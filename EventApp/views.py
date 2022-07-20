from importlib.metadata import metadata
import re
from django.urls import reverse
import json
import os
import datetime
from django.utils import timezone

from requests import request, session
import stripe
from pprint import pprint
from django.shortcuts import render,redirect
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponse
from .models import clsEventDetails, clsUser
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from django.http import JsonResponse
from django.template.loader import render_to_string


# Create your views here.
# Home
def index(request):
    #list all events
    lstAllEventLocationType = ['','Pysical venue','Online','Recorded Events']
    tbmItems = clsEventDetails.objects.filter(~Q(int_last_action = 0),Q(dat_event_start_date_time__gte = datetime.datetime.now()), Q(int_if_paid = 1)).order_by('dat_event_start_date_time')
    lstAllItems = []
    strOutputFormat = '%Y-%m-%d %H:%M:%S'
    for tbmEachItem in tbmItems:
        dctAllItems = {}
        dctAllItems['intPkEventId'] = tbmEachItem.pk_event_id
        dctAllItems['intFkUserId'] = tbmEachItem.fk_user_id
        dctAllItems['strEventStartDateTime'] = tbmEachItem.dat_event_start_date_time.strftime(strOutputFormat)
        dctAllItems['strEventEndDateTime'] = tbmEachItem.dat_event_end_date_time.strftime(strOutputFormat)
        dctAllItems['strEventVenue'] = tbmEachItem.vhr_event_venue
        dctAllItems['strEventDescription'] = tbmEachItem.vhr_event_description
        dctAllItems['strEventPoster'] = 'attachment/'+tbmEachItem.vhr_event_file_upload
        dctAllItems['strCreatedDateTime'] = tbmEachItem.dat_created_datetime.strftime(strOutputFormat)
        dctAllItems['intLastAction'] = tbmEachItem.int_last_action
        dctAllItems['intIfPaid'] = tbmEachItem.int_if_paid  
        dctAllItems['intEventLocation'] = tbmEachItem.int_event_location_type
        dctAllItems['strEventType'] = lstAllEventLocationType[tbmEachItem.int_event_location_type]
        dctAllItems['strEventName'] = tbmEachItem.vhr_event_name
        lstAllItems.append(dctAllItems)
    return render(request,'index.html',{'lstAllItems':lstAllItems})

# Login
def login(request):
    
    if request.method == 'POST':
        strEmail = request.POST.get('txtEmail')
        strPassword = request.POST.get('txtPassword')
        # // Check User Authentication
        tbmUser = clsUser.objects.filter(Q(vhr_email__iexact=strEmail),Q(vhr_password__iexact=strPassword))
        try:
            if tbmUser[0]:
                request.session['intLoginUserId'] = tbmUser[0].pk_user_id
                request.session['strLoginUserName'] = tbmUser[0].vhr_user_name
                request.session['strEmail'] = tbmUser[0].vhr_email
                messages.success(request,'Signin Success!')
                return redirect('eventsList')
        except Exception as err:
            messages.error(request,'Invalid Email Or Password.')
            return redirect('login')
    else:
        return render(request,'login.html')
#Logout
def logout(request):
    
    request.session['intLoginUserId'] = 0
    request.session['strLoginUserName'] = ''
    request.session['strEmail'] = ''
    # request.session.flush()
    return redirect('index')

# Login
def signup(request):
   
    if request.method == 'POST':
        jsnSignupData = request.POST.get('jsnSignupData')
        lstSignupData = json.loads(jsnSignupData)
        dctResponse = {'strStatus':''}
        try:
             # // Check Already Exists
            tbmUser = clsUser.objects.filter(Q(vhr_email__iexact=lstSignupData['strEmail']))
            if tbmUser[0]:
                
                # return redirect('signup')
                dctResponse['strStatus'] = 'ERROR'
                dctResponse['strMessage'] = 'User already exists!'

        except:
            tbmNewUser = clsUser()
            tbmNewUser.vhr_user_name = lstSignupData['strActualName']
            tbmNewUser.vhr_email = lstSignupData['strEmail']
            tbmNewUser.vhr_password = lstSignupData['strPassword']
            tbmNewUser.int_if_admin = 0 # Not Admin
            tbmNewUser.dat_created_datetime =datetime.datetime.now()
            tbmNewUser.int_last_action = 1
            tbmNewUser.save()
            dctResponse['strStatus'] = 'SUCCESS'
            dctResponse['strMessage'] = 'Sign up successfully!'
           
        jsnResponse = json.dumps(dctResponse)
        mimetype = 'application/json'
        return HttpResponse(jsnResponse, mimetype)            
    else:
        return render(request,'signup.html')
    pass

@csrf_exempt 
def addEvent(request):  
    
    if request.method == 'POST':
        jsnCreateEventData = request.POST.get('arrCreateEventData')
        lstCreateEventData = json.loads(jsnCreateEventData)
        strFileName = request.POST.get('strFileName')
        file = request.FILES['file']
        
        dctResponse = {'strStatus':''}    
        # // Event Already Exist Checking
        tbmEvent = clsEventDetails.objects.filter(Q(vhr_event_name__iexact=lstCreateEventData['strEventName']))
        try:
            if tbmEvent[0]:
                messages.error(request,'Event Already Exists.Please Choose Another Event Name!')
                dctResponse['strStatus'] = 'ERROR'
        except Exception as err:
            tbmEvent = clsEventDetails()
            tbmEvent.vhr_event_name = lstCreateEventData['strEventName']
            tbmEvent.fk_user_id = int(request.session['intLoginUserId'])
            tbmEvent.dat_event_start_date_time = lstCreateEventData['strEventStartTime']
            tbmEvent.dat_event_end_date_time = lstCreateEventData['strEventEndTime']
            tbmEvent.vhr_event_venue = lstCreateEventData['strEventLocation']
            tbmEvent.vhr_event_description = lstCreateEventData['strEventDescription']
            tbmEvent.vhr_event_file_upload = strFileName
            tbmEvent.int_last_action = int(lstCreateEventData['intLastAction']) + 1
            tbmEvent.int_event_location_type = int(lstCreateEventData['intEventLocation'])
            tbmEvent.int_if_paid = int(lstCreateEventData['intIfPaid'])
            tbmEvent.dat_created_datetime = datetime.datetime.now()
            tbmEvent.save()
            messages.success(request,'Event added successfully!')
            dctResponse['strStatus'] = 'SUCCESS'
        
        # //Checking File Exsist
        strFileDirName = os.path.join('EventApp','static','attachment',strFileName)
        default_storage.save(strFileDirName, ContentFile(file.read()))
        
        jsnResponse = json.dumps(dctResponse)
        mimetype = 'application/json'
        return HttpResponse(jsnResponse, mimetype)
    else:
        return render(request,'addEvent.html')
    pass
  
@csrf_exempt 
def updateEvent(request):
        
    if request.method == 'POST':
        jsnCreateEventData = request.POST.get('arrCreateEventData')
        lstCreateEventData = json.loads(jsnCreateEventData)
        strFileName = request.POST.get('strFileName')
        file = request.FILES['file']
        
        dctResponse = {'strStatus':''}
        # // Event Already Exist Checking
        tbmEvent = clsEventDetails.objects.filter(Q(vhr_event_name__iexact=lstCreateEventData['strEventName']),~Q(pk_event_id=lstCreateEventData['intPkEventsId']),~Q(int_last_action=0))
        try:
            if tbmEvent[0]:
                messages.error(request,'Event Already Exists.Please Choose Another Event Name!')
                dctResponse['strStatus'] = 'ERROR'
        except Exception as err:
            tbmEvent = clsEventDetails.objects.get(Q(pk_event_id = lstCreateEventData['intPkEventsId']))
            tbmEvent.vhr_event_name = lstCreateEventData['strEventName']
            tbmEvent.fk_user_id = int(request.session['intLoginUserId'])
            tbmEvent.dat_event_start_date_time = lstCreateEventData['strEventStartTime']
            tbmEvent.dat_event_end_date_time = lstCreateEventData['strEventEndTime']
            tbmEvent.vhr_event_venue = lstCreateEventData['strEventLocation']
            tbmEvent.vhr_event_description = lstCreateEventData['strEventDescription']
            tbmEvent.vhr_event_file_upload = strFileName
            tbmEvent.int_last_action = int(lstCreateEventData['intLastAction']) + 1
            tbmEvent.int_event_location_type = int(lstCreateEventData['intEventLocation'])
            tbmEvent.int_if_paid = int(lstCreateEventData['intIfPaid'])
            # tbmEvent.dat_created_datetime = datetime.datetime.now()
            tbmEvent.save()
            messages.success(request,'Event Updated successfully!')
            dctResponse['strStatus'] = 'SUCCESS'
        
        strFileDirName = os.path.join('EventApp','static','attachment',strFileName)
        default_storage.save(strFileDirName, ContentFile(file.read()))
        
        jsnResponse = json.dumps(dctResponse)
        mimetype = 'application/json'
        return HttpResponse(jsnResponse, mimetype)        
    else:
        return render(request,'addEvent.html')
    pass
  
def eventsList(request):
    
    tbmItems = clsEventDetails.objects.filter(~Q(int_last_action = 0),Q(fk_user_id = int(request.session['intLoginUserId'])))
    lstAllItems = []
    strOutputFormat = '%Y-%m-%d %H:%M:%S'
    for tbmEachItem in tbmItems:
        
        dctAllItems = {}
        dctAllItems['intPkEventId'] = tbmEachItem.pk_event_id
        dctAllItems['intFkUserId'] = tbmEachItem.fk_user_id
        dctAllItems['strEventStartDateTime'] = tbmEachItem.dat_event_start_date_time.strftime(strOutputFormat)
        dctAllItems['strEventEndDateTime'] = tbmEachItem.dat_event_end_date_time.strftime(strOutputFormat)
        dctAllItems['strEventName'] = tbmEachItem.vhr_event_name
        dctAllItems['strEventVenue'] = tbmEachItem.vhr_event_venue
        dctAllItems['strEventDescription'] = tbmEachItem.vhr_event_description.replace('\n','')
        dctAllItems['strEventPoster'] = tbmEachItem.vhr_event_file_upload
        dctAllItems['strCreatedDateTime'] = tbmEachItem.dat_created_datetime.strftime(strOutputFormat)
        dctAllItems['intLastAction'] = tbmEachItem.int_last_action
        dctAllItems['intIfPaid'] = tbmEachItem.int_if_paid  
        dctAllItems['intEventLocation'] = tbmEachItem.int_event_location_type
        lstAllItems.append(dctAllItems)
       
    return render(request,'eventsList.html',{'lstAllItems':lstAllItems})

def deleteEvent(request):
    if request.method == 'POST':
        jsnCreateEventData = request.POST.get('jsnEventDeleteData')
        lstCreateEventData = json.loads(jsnCreateEventData)
        dctResponse = {'strStatus':''}
        try:
            tbmEventData = clsEventDetails.objects.get(pk_event_id =lstCreateEventData['intPkEventId'] )
            tbmEventData.int_last_action = 0
            tbmEventData.save()
            dctResponse['strStatus'] = 'SUCCESS'
            dctResponse['strMessage'] = 'Event deleted successfully!'
            
        except:
            dctResponse['strStatus'] = 'ERROR'
            dctResponse['strMessage'] = 'Delete not Possible.Try Again'
        jsnResponse = json.dumps(dctResponse)
        mimetype = 'application/json'
        return HttpResponse(jsnResponse, mimetype)       
    else:
        return render(request,'eventsList.html')

@csrf_exempt 
def loadPaymentMethod(request):
   
    return render(request,'payment.html')

# This is your test secret API key.
stripe.api_key = settings.STRIPE_SECRET_KEY

def createCheckoutSession(request):
   
    IntEventId = request.POST.get('txtEventId')
    strEventName = request.POST.get('txtEventName')
    # lstSignupData = json.loads(IntEventId)
    
    host = request.get_host()
    checkout_session = stripe.checkout.Session.create(
    payment_method_types = ['card'],
    metadata = {'event_id' : IntEventId,'event_name': strEventName},
    line_items=[
        {
            'price_data' : {
                'currency': 'inr',
                'unit_amount':250000,
                'product_data':{
                    'name':'Publishing Fee',
                }     
            },
            'quantity': 1,
        },
    ],
    mode='payment',
    success_url="http://{}{}".format(host,reverse('payment-success')),
    cancel_url="http://{}{}".format(host,reverse('payment-cancel')),
    )
   
    return redirect(checkout_session.url, code=303)

def paymentSuccess(request):
    context = {
        'payment_status': 'success'
    }
    return render(request, 'confirmation.html', context)

def paymentCancel(request):
    context = {
        'payment_status': 'cancel'
    }
    return render(request, 'confirmation.html', context)

@csrf_exempt
def my_webhook_view(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        if session.payment_status == 'paid':
            #Update Events Data
            if session.metadata.event_id:
                try:
                    tbmEventData = clsEventDetails.objects.get(pk_event_id =int(session.metadata.event_id))
                    tbmEventData.int_if_paid = 1
                    tbmEventData.save()
                except:
                    pass
    # Passed signature verification
    return HttpResponse(status=200)


            
    
    


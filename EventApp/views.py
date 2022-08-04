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
from .forms import loginForm
from django.core.paginator import Paginator
from django.views import View


# Create your views here.
# Home
def index(request):
    #  list all events
    event_location_type_list = ['','Physical venue','Online','Recorded Events']
    database_items = clsEventDetails.objects.filter(~Q(int_last_action = 0),Q(dat_event_start_date_time__gte = datetime.datetime.now()), Q(int_if_paid = 1)).order_by('dat_event_start_date_time')
    all_items_list = []
    date_output_format = '%Y-%m-%d %H:%M:%S'
    for each_item in database_items:
        all_items_dict = dict()
        all_items_dict['intPkEventId'] = each_item.pk_event_id
        all_items_dict['intFkUserId'] = each_item.fk_user_id
        all_items_dict['strEventStartDateTime'] = each_item.dat_event_start_date_time.strftime(date_output_format)
        all_items_dict['strEventEndDateTime'] = each_item.dat_event_end_date_time.strftime(date_output_format)
        all_items_dict['strEventVenue'] = each_item.vhr_event_venue
        all_items_dict['strEventDescription'] = each_item.vhr_event_description
        all_items_dict['strEventPoster'] = 'attachment/'+each_item.vhr_event_file_upload
        all_items_dict['strCreatedDateTime'] = each_item.dat_created_datetime.strftime(date_output_format)
        all_items_dict['intLastAction'] = each_item.int_last_action
        all_items_dict['intIfPaid'] = each_item.int_if_paid
        all_items_dict['intEventLocation'] = each_item.int_event_location_type
        all_items_dict['strEventType'] = event_location_type_list[each_item.int_event_location_type]
        all_items_dict['strEventName'] = each_item.vhr_event_name
        all_items_list.append(all_items_dict)

    # Set up Pagination
    # database_items = all_items_list
    events = ''
    nums = ''
    if len(all_items_list):
        p = Paginator(all_items_list, 3)
        page = request.GET.get('page')
        events = p.get_page(page)
        nums = "a" * events.paginator.num_pages
    return render(request, 'index.html', {'lstAllItems': all_items_list, 'events': events, 'nums': nums})

# Login
# def login(request):
#     form = loginForm()
#     if request.method == 'POST':
#         form = loginForm(request.POST)
#         if form.is_valid():
#             database_user = clsUser.objects.filter(Q(vhr_email__iexact=form.cleaned_data['email']), Q(vhr_password__iexact=form.cleaned_data['password']))
#         # // Check User Authentication
#         try:
#             if database_user[0]:
#                 request.session['intLoginUserId'] = database_user[0].pk_user_id
#                 request.session['strLoginUserName'] = database_user[0].vhr_user_name
#                 request.session['strEmail'] = database_user[0].vhr_email
#                 messages.success(request,'Signin Success!')
#                 return redirect('events_list')
#         except Exception as err:
#             messages.error(request,'Invalid Email Or Password.')
#             return redirect('login')
#     else:
#         return render(request,'login.html',{'form':form})
#
#     return render(request,'login.html',{'form':form})


class LoginClass(View):
    form_class = loginForm

    def get(self, request):
        return render(request, 'login.html', {'form': self.form_class()})

    def post(self, request):
        form = loginForm(request.POST)
        if form.is_valid():
            database_user = clsUser.objects.filter(Q(vhr_email__iexact=form.cleaned_data['email']),
                                                   Q(vhr_password__iexact=form.cleaned_data['password']))
        # // Check User Authentication
        try:
            if database_user[0]:
                request.session['intLoginUserId'] = database_user[0].pk_user_id
                request.session['strLoginUserName'] = database_user[0].vhr_user_name
                request.session['strEmail'] = database_user[0].vhr_email
                messages.success(request, 'Signin Success!')
                return redirect('events_list')
        except Exception as err:
            messages.error(request,'Invalid Email Or Password.')
            return redirect('login')
    else:
        return render(request,'login.html',{'form':form})

    return render(request,'login.html',{'form':form})

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
        signup_data_json = request.POST.get('jsnSignupData')
        signup_data_list = json.loads(signup_data_json)
        response_dict = {'strStatus': ''}

        try:
             # // Check Already Exists
            tbmUser = clsUser.objects.filter(Q(vhr_email__iexact=lstSignupData['strEmail']))
            if tbmUser[0]:
                
                # return redirect('signup')
                dctResponse['strStatus'] = 'ERROR'
                dctResponse['strMessage'] = 'User already exists!'

        except:
            database_new_user_obj = clsUser()
            database_new_user_obj.vhr_user_name = signup_data_list['strActualName']
            database_new_user_obj.vhr_email = signup_data_list['strEmail']
            database_new_user_obj.vhr_password = signup_data_list['strPassword']
            database_new_user_obj.int_if_admin = 0 # Not Admin
            database_new_user_obj.dat_created_datetime =datetime.datetime.now()
            database_new_user_obj.int_last_action = 1
            database_new_user_obj.save()
            response_dict['strStatus'] = 'SUCCESS'
            response_dict['strMessage'] = 'Sign up successfully!'
            messages.success(request, 'Signup Successfully!')
           
        jsnResponse = json.dumps(dctResponse)
        mimetype = 'application/json'
        return HttpResponse(jsnResponse, mimetype)            
    else:
        return render(request,'signup.html')
    pass


@csrf_exempt
def add_event(request):
    
    if request.method == 'POST':
        jsnCreateEventData = request.POST.get('arrCreateEventData')
        lstCreateEventData = json.loads(jsnCreateEventData)
        strFileName = request.POST.get('strFileName')
        file = request.FILES['file']

        response_dict = {'strStatus': ''}
        response_dict = serverside_validation(request,create_event_data_list)
        if response_dict['strStatus'] == 'ERROR':
            response_json = json.dumps(response_dict)
            mimetype = 'application/json'
            return HttpResponse(response_json, mimetype)

        # // Event Already Exist Checking
        tbmEvent = clsEventDetails.objects.filter(Q(vhr_event_name__iexact=lstCreateEventData['strEventName']))
        try:
            if database_event_details[0]:
                messages.error(request, 'Event Already Exists.Please Choose Another Event Name!')
                response_dict['strStatus'] = 'ERROR'
        except Exception as err:
            database_event_details = clsEventDetails()
            database_event_details.vhr_event_name = create_event_data_list['strEventName']
            database_event_details.fk_user_id = int(request.session['intLoginUserId'])
            database_event_details.dat_event_start_date_time = create_event_data_list['strEventStartTime']
            database_event_details.dat_event_end_date_time = create_event_data_list['strEventEndTime']
            database_event_details.vhr_event_venue = create_event_data_list['strEventLocation']
            database_event_details.vhr_event_description = create_event_data_list['strEventDescription']
            database_event_details.vhr_event_file_upload = file_name
            database_event_details.int_last_action = int(create_event_data_list['intLastAction']) + 1
            database_event_details.int_event_location_type = int(create_event_data_list['intEventLocation'])
            database_event_details.int_if_paid = int(create_event_data_list['intIfPaid'])
            database_event_details.dat_created_datetime = datetime.datetime.now()
            database_event_details.save()
            messages.success(request, 'Event added successfully!')
            response_dict['strStatus'] = 'SUCCESS'
        
        # //Checking File Exist
        file_directory_name = os.path.join('EventApp', 'static', 'attachment', file_name)
        default_storage.save(file_directory_name, ContentFile(file.read()))
        
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
        
        response_dict = {'strStatus': ''}
        response_dict = serverside_validation(request, create_event_data_list)
        if response_dict['strStatus'] == 'ERROR':
            response_json = json.dumps(response_dict)
            mimetype = 'application/json'
            return HttpResponse(response_json, mimetype)
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


def events_list(request):

    event_location_type = ['', 'Physical venue', 'Online', 'Recorded Events']

    database_items = clsEventDetails.objects.filter(~Q(int_last_action = 0),Q(fk_user_id = int(request.session['intLoginUserId'])))
    all_items_list = []
    date_output_format = '%Y-%m-%d %H:%M:%S'
    for each_item in database_items:
        
        all_items_dict = dict()
        all_items_dict['intPkEventId'] = each_item.pk_event_id
        all_items_dict['intFkUserId'] = each_item.fk_user_id
        all_items_dict['strEventStartDateTime'] = each_item.dat_event_start_date_time.strftime(date_output_format)
        all_items_dict['strEventEndDateTime'] = each_item.dat_event_end_date_time.strftime(date_output_format)
        all_items_dict['strEventName'] = each_item.vhr_event_name
        all_items_dict['strEventVenue'] = each_item.vhr_event_venue
        all_items_dict['strEventDescription'] = each_item.vhr_event_description.replace('\n','')
        all_items_dict['strEventPoster'] = each_item.vhr_event_file_upload
        all_items_dict['strCreatedDateTime'] = each_item.dat_created_datetime.strftime(date_output_format)
        all_items_dict['intLastAction'] = each_item.int_last_action
        all_items_dict['intIfPaid'] = each_item.int_if_paid
        all_items_dict['intEventLocation'] = each_item.int_event_location_type
        all_items_dict['strEventLocation'] = event_location_type[each_item.int_event_location_type]
        all_items_dict['strPublicationDetails'] = 'Unpublished.Payment needed(₹100)'
        if each_item.int_if_paid:
            all_items_dict['strPublicationDetails'] = 'Published'
        all_items_list.append(all_items_dict)
    events = ''
    nums = ''
    if len(all_items_list):
        p = Paginator(all_items_list, 3)
        page = request.GET.get('page')
        events = p.get_page(page)
        nums = "a" * events.paginator.num_pages
    return render(request, 'eventsList.html', {'lstAllItems': all_items_list, 'events': events, 'nums': nums})


def delete_event(request):
    if request.method == 'POST':
        create_event_data_json = request.POST.get('jsnEventDeleteData')
        create_event_data_list = json.loads(create_event_data_json)

        response_dict = serverside_validation_delete(request, create_event_data_list)
        if response_dict['strStatus'] == 'ERROR':
            response_json = json.dumps(response_dict)
            mimetype = 'application/json'
            return HttpResponse(response_json, mimetype)
        try:
            database_event = clsEventDetails.objects.get(pk_event_id =create_event_data_list['intPkEventId'] )
            database_event.int_last_action = 0
            database_event.save()
            response_dict['strStatus'] = 'SUCCESS'
            response_dict['strMessage'] = 'Event deleted successfully!'
        except:
            dctResponse['strStatus'] = 'ERROR'
            dctResponse['strMessage'] = 'Delete not Possible.Try Again'
        jsnResponse = json.dumps(dctResponse)
        mimetype = 'application/json'
        return HttpResponse(jsnResponse, mimetype)       
    else:
        return render(request,'eventsList.html')


def serverside_validation(request, create_event_data_list):

    response_dict = {'strStatus': ''}
    if not create_event_data_list['strEventName']:
        response_dict['strMessage'] = 'Event Name is Required'
        response_dict['strStatus'] = 'ERROR'
        return response_dict

    if not create_event_data_list['strEventLocation']:
        response_dict['strMessage'] = 'Event Venue is Required'
        response_dict['strStatus'] = 'ERROR'
        return response_dict

    if not create_event_data_list['strEventStartTime']:
        response_dict['strMessage'] = 'Event Start date and time is Required'
        response_dict['strStatus'] = 'ERROR'
        return response_dict

    if not create_event_data_list['strEventEndTime']:
        response_dict['strMessage'] = 'Event end date and time is Required'
        response_dict['strStatus'] = 'ERROR'
        return response_dict
    if not create_event_data_list['strEventDescription']:
        response_dict['strMessage'] = 'Event description is Required'
        response_dict['strStatus'] = 'ERROR'
        return response_dict
    if not create_event_data_list['intEventLocation']:
        response_dict['strMessage'] = 'Event Location Type is Required'
        response_dict['strStatus'] = 'ERROR'
        return response_dict

    if create_event_data_list['intPkEventsId']:  # Update mode
        database_update_event = clsEventDetails.objects.get(pk_event_id=create_event_data_list['intPkEventsId'])
        if database_update_event.fk_user_id != request.session['intLoginUserId']:
            response_dict['strMessage'] = 'Update Not Possible.An event can be updated by the creator only.'
            response_dict['strStatus'] = 'ERROR'
            return response_dict
    return response_dict


def serverside_validation_delete(request, create_event_data_list):
    response_dict = {'strStatus': ''}
    if not create_event_data_list['intPkEventId']:
        response_dict['strMessage'] = 'Delete Not Possible'
        response_dict['strStatus'] = 'ERROR'
        return response_dict
    try:
        database_delete_event = clsEventDetails.objects.get(pk_event_id=create_event_data_list['intPkEventId'])
        if database_delete_event.fk_user_id != request.session['intLoginUserId']:
            response_dict['strMessage'] = 'Delete Not Possible.An event can be deleted by the creator only.'
            response_dict['strStatus'] = 'ERROR'
            return response_dict
    except:
        pass

    return response_dict


@csrf_exempt
def edit_event(request, key_id=''):
    if request.method == 'POST':
        create_event_data_json = request.POST.get('arrCreateEventData')
        create_event_data_list = json.loads(create_event_data_json)
        file_name = request.POST.get('strFileName')
        file = request.FILES['file']

        response_dict = {'strStatus': ''}
        response_dict = serverside_validation(create_event_data_list)
        if response_dict['strStatus'] == 'ERROR':
            response_json = json.dumps(response_dict)
            mimetype = 'application/json'
            return HttpResponse(response_json, mimetype)

        # // Event Already Exist Checking
        database_event_details = clsEventDetails.objects.filter(
            Q(vhr_event_name__iexact=create_event_data_list['strEventName']))
        try:
            if database_event_details[0]:
                messages.error(request, 'Event Already Exists.Please Choose Another Event Name!')
                response_dict['strStatus'] = 'ERROR'
        except Exception as err:
            database_event_details = clsEventDetails()
            database_event_details.vhr_event_name = create_event_data_list['strEventName']
            database_event_details.fk_user_id = int(request.session['intLoginUserId'])
            database_event_details.dat_event_start_date_time = create_event_data_list['strEventStartTime']
            database_event_details.dat_event_end_date_time = create_event_data_list['strEventEndTime']
            database_event_details.vhr_event_venue = create_event_data_list['strEventLocation']
            database_event_details.vhr_event_description = create_event_data_list['strEventDescription']
            database_event_details.vhr_event_file_upload = file_name
            database_event_details.int_last_action = int(create_event_data_list['intLastAction']) + 1
            database_event_details.int_event_location_type = int(create_event_data_list['intEventLocation'])
            database_event_details.int_if_paid = int(create_event_data_list['intIfPaid'])
            database_event_details.dat_created_datetime = datetime.datetime.now()
            database_event_details.save()
            messages.success(request, 'Event added successfully!')
            response_dict['strStatus'] = 'SUCCESS'

        # //Checking File Exist
        file_directory_name = os.path.join('EventApp', 'static', 'attachment', file_name)
        default_storage.save(file_directory_name, ContentFile(file.read()))

        response_json = json.dumps(response_dict)
        mimetype = 'application/json'
        return HttpResponse(response_json, mimetype)
    else:
        return render(request, 'addEvent.html')
    pass


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
                'unit_amount':100,
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


            
    
    


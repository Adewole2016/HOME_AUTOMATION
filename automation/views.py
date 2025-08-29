import json
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import Device, DeviceReport
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404



# --- Device Authentication ---
def _auth_device(request):
    token = request.headers.get('X-DEVICE-TOKEN') or request.GET.get('token')
    return token == settings.DEVICE_SHARED_TOKEN


@login_required(login_url='login')
def dashboard(request):
    device, _ = Device.objects.get_or_create(
        device_id='NODEMCU-01', defaults={'name': 'Home Devices Controller'}
    )
    reports = device.reports.all().order_by('-created_at')[:10]
    
    return render(request, 'dashboard.html', {
        'device': device,
        'reports': reports,
        'DEVICE_SHARED_TOKEN': settings.DEVICE_SHARED_TOKEN  # Pass token here
    })




@login_required
def toggle_channel(request, device_id, channel: int):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    device = get_object_or_404(Device, device_id=device_id)

    if channel == 1:
        device.desired_ch1 = not device.desired_ch1
    elif channel == 2:
        device.desired_ch2 = not device.desired_ch2
    elif channel == 3:
        device.desired_ch3 = not device.desired_ch3
    elif channel == 4:
        device.desired_ch4 = not device.desired_ch4

    device.save()
    return JsonResponse({
        'status': 'success',
        'channel': channel,
        'new_state': getattr(device, f'desired_ch{channel}')
    })


@login_required
def all_channels(request, device_id, action: str):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    device = get_object_or_404(Device, device_id=device_id)
    state = True if action.lower() == 'on' else False
    device.desired_ch1 = state
    device.desired_ch2 = state
    device.desired_ch3 = state
    device.desired_ch4 = state
    device.save()

    return JsonResponse({
        'status': 'success',
        'new_state': state
    })

# --- API: Get Desired State + Recent Reports ---
def api_desired_state(request, device_id: str):
    if not _auth_device(request):
        return JsonResponse({'error': 'unauthorized'}, status=401)

    device, _ = Device.objects.get_or_create(
        device_id=device_id, defaults={'name': device_id}
    )
    device.last_seen = timezone.now()
    device.save(update_fields=['last_seen'])

    # Last 10 reports
    reports = device.reports.all().order_by('-created_at')[:10]
    report_list = [
        {
            'created_at': r.created_at.isoformat(),
            'ch1': r.ch1,
            'ch2': r.ch2,
            'ch3': r.ch3,
            'ch4': r.ch4,
        }
        for r in reports
    ]

    data = {
        'device_id': device.device_id,
        'desired': {
            'ch1': device.desired_ch1,
            'ch2': device.desired_ch2,
            'ch3': device.desired_ch3,
            'ch4': device.desired_ch4,
        },
        'timestamp': timezone.now().isoformat(),
        'reports': report_list
    }

    return JsonResponse(data)


# --- API: Report Device State ---
@csrf_exempt
def api_report_state(request, device_id: str):
    if not _auth_device(request):
        return JsonResponse({'error': 'unauthorized'}, status=401)

    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    device = get_object_or_404(Device, device_id=device_id)
    rep = DeviceReport.objects.create(
        device=device,
        ch1=bool(payload.get('ch1')),
        ch2=bool(payload.get('ch2')),
        ch3=bool(payload.get('ch3')),
        ch4=bool(payload.get('ch4')),
    )
    return JsonResponse({'ok': True, 'created_at': rep.created_at.isoformat()})
    
    
   

def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

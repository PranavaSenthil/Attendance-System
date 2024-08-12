from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.utils import timezone
from .models import *

# Create your views here.


def admin_guard_details(request):
    if request.user.is_authenticated:
        try:
            user_type = UserType.objects.get(user=request.user)
            if user_type.is_admin:
                try:
                    admin = Admin.objects.get(admin_type=user_type)
                except Admin.DoesNotExist:
                    messages.error(request, "Admin profile not found.")
                    return redirect('login')
                guards = UserType.objects.filter(is_guard=True)
                current_date = timezone.now().date()
                
                # Prepare attendance status
                guard_details = []
                for guard in guards:
                    # Fetch the latest attendance for today
                    latest_attendance = Attendance.objects.filter(
                        guard=guard,
                        date=current_date
                    ).order_by('-timestamp').first()
                    
                    # Determine attendance status
                    status = 'Absent' if not latest_attendance else 'Present'
                    
                    guard_details.append({
                        'guard': guard,
                        'latest_attendance': latest_attendance,
                        'status': status
                    })
                print(guard_details)
                return render(request, 'admin.html', {'guard_details': guard_details})
            else:
                messages.error(request, "You are not authorized to view this page.")
                return redirect('login')
        except Admin.DoesNotExist:
            messages.error(request, "Admin profile not found.")
            return redirect('login')
    else:
        messages.error(request, "You must be logged in to view this page.")
        return redirect('login')

def user_guard(request):
    return render(request,'guard.html')

def upload_selfie(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            user_type = UserType.objects.get(user=request.user)
            if user_type.is_guard:
                current_timestamp = timezone.now()
                start_of_hour = current_timestamp.replace(minute=0, second=0, microsecond=0)
                end_of_hour = start_of_hour + timedelta(hours=1)
                print(f"Current Timestamp: {current_timestamp}")
                print(f"Start of Hour: {start_of_hour}")
                print(f"End of Hour: {end_of_hour}")
                attendance = Attendance.objects.filter(
                    guard=user_type,
                    timestamp__gte=start_of_hour,
                    timestamp__lt=end_of_hour
                )
                print(f"Attendance Query: {attendance}")
                if attendance.exists():
                    messages.error(request, "Selfie already uploaded for this hour.")
                else:
                    if 'selfie' in request.FILES:
                        selfie = request.FILES['selfie']
                        attendance = Attendance(guard=user_type, selfie=selfie)
                        attendance.save()
                        messages.success(request, "Selfie uploaded successfully.")
                    else:
                        messages.error(request, "No selfie uploaded. Please try again.")
            else:
                messages.error(request, "Only guards are allowed to upload selfies.")
        except UserType.DoesNotExist:
            messages.error(request, "User role not found.")
        except KeyError:
            messages.error(request, "Please upload a selfie.")
    else:
        messages.error(request, "You must be logged in to upload a selfie.")
    
    return redirect('user_guard')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            try:
                user_type = UserType.objects.get(user=user)
                if user_type.is_admin:
                    return redirect('admin_guard_details') 
                elif user_type.is_guard:
                    return redirect('user_guard') 
                else:
                    messages.error(request, 'Your account does not have the required role.')
                    return redirect('login')
            except UserType.DoesNotExist:
                messages.error(request, 'User role not found.')
                return redirect('login')
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('login')
    return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return redirect('login')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirmpassword = request.POST['confirmpassword']
        phoneno = request.POST['phoneno']
        gender = request.POST['gender']
        is_admin = request.POST.get('is_admin', False)
        is_guard = request.POST.get('is_guard', False)


        if password == confirmpassword:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, password=password, email=email)
                user.set_password(password)
                user.save()
                usertype = UserType.objects.create(user=user, phoneno=phoneno,gender=gender,is_admin=is_admin,is_guard=is_guard)
                messages.success(request, 'User created successfully')
                return redirect('login')
        else:
            messages.error(request, 'Password not matching')
            return redirect('register')
    else:
        return render(request, 'register.html')
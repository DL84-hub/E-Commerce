from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .serializers import UserSerializer, UserRegistrationSerializer, UserLoginSerializer, UserUpdateSerializer
from .forms import UserLoginForm, UserRegistrationForm, UserUpdateForm
from .utils import send_verification_email
from .models import User
import uuid

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.generate_verification_token()
        send_verification_email(user, request)
        return Response({
            'message': 'User registered successfully. Please check your email to verify your account.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(request, username=username, password=password)
        
        if user:
            if not user.email_verified:
                return Response({
                    'error': 'Please verify your email address before logging in.',
                    'resend_verification': True
                }, status=status.HTTP_403_FORBIDDEN)
            login(request, user)
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_email(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
        if user.email_verified:
            return Response({'error': 'Email is already verified'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.generate_verification_token()
        send_verification_email(user, request)
        return Response({'message': 'Verification email sent successfully'})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request, token):
    try:
        user = User.objects.get(email_verification_token=token)
        if not user.is_verification_token_valid():
            return Response({'error': 'Verification link has expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.email_verified = True
        user.save()
        return Response({'message': 'Email verified successfully'})
    except User.DoesNotExist:
        return Response({'error': 'Invalid verification token'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'message': 'Logout successful'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    return Response(UserSerializer(request.user).data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profile updated successfully',
            'user': UserSerializer(request.user).data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Frontend Views
def login_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user:
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'users/login.html', {'form': form})

def logout_page(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')

def register_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.generate_verification_token()
            send_verification_email(user, request)
            messages.success(request, 'Registration successful! Please check your email to verify your account.')
            return render(request, 'users/verify_email_sent.html', {'email': user.email})
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})

def verify_email_sent_page(request):
    return render(request, 'users/verify_email_sent.html')

def verify_email_page(request, token):
    try:
        user = User.objects.get(email_verification_token=token)
        if not user.is_verification_token_valid():
            messages.error(request, 'Verification link has expired.')
            return redirect('resend_verification')
        
        user.email_verified = True
        user.save()
        messages.success(request, 'Email verified successfully! You can now log in.')
        return redirect('login')
    except User.DoesNotExist:
        messages.error(request, 'Invalid verification token.')
        return redirect('login')

def resend_verification_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if user.email_verified:
                messages.error(request, 'Email is already verified.')
            else:
                user.generate_verification_token()
                send_verification_email(user, request)
                messages.success(request, 'Verification email sent successfully.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
        return redirect('login')
    
    return render(request, 'users/resend_verification.html')

def profile_page(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'users/profile.html', {'form': form})

from datetime import timedelta, timezone
import json
from django.http import Http404, JsonResponse
from django.views import View
import requests
from rest_framework import status,views,generics
from rest_framework.response import Response
import stripe
from .serializers import ArticleSerializer, EventSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Article, CustomUser, Order,Event
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth import authenticate, login,logout
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from backend import settings
from django.contrib.sessions.models import Session
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import permission_classes
from rest_framework.authentication import SessionAuthentication
from celery import shared_task
from django.views.decorators.csrf import csrf_exempt


stripe.api_key = settings.STRIPE_SECRET_KEY

class ProdigiOrderDetailsView(views.APIView):
    def get(self, request):
        order_ids = request.GET.get('order_ids').split(',')
        data = []
        for order_id in order_ids:
            response = requests.get(
                f'https://api.sandbox.prodigi.com/v4.0/orders/{order_id}',
                headers={'X-API-Key': 'ac6f8a4f-1bae-4826-a837-6e012b910651',
                         'Content-Type': 'application/json'}
            )
            data.append(response.json())
        return JsonResponse(data, safe=False)

class GetUserOrdersView( views.APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        # Get the currently logged-in user
        user = request.user

        # Get the orders associated with the currently logged-in user
        orders = Order.objects.filter(user=user)

        # Serialize the orders data
        data = []
        for order in orders:
            data.append({
                'id': order.id,
                'order_data': order.order_data,
                'prodigi_order_id':order.prodigi_order_id
            })

        # Return the serialized data as a JSON response
        return JsonResponse(data, safe=False)

class CreateCheckoutSessionView(views.APIView):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        amount = data['amount']

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Your product name',
                    },
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            # success_url='http://localhost:4200/#/order-complete?sessionId={CHECKOUT_SESSION_ID}',
            success_url='http://localhost:4200/#/donate',

            cancel_url='http://localhost:4200/home',
        )

        return JsonResponse({
            'sessionId': checkout_session['id']
        })

class CreatePaymentView(views.APIView):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        amount = data['amount']

        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
        )

        return JsonResponse({
            'clientSecret': payment_intent['client_secret']
        })

class ProdigiProductsAPIView(views.APIView):
    def get(self, request, product_id):
        # Set the URL and headers for the Prodigi API request
        url = f'https://api.sandbox.prodigi.com/v4.0/Products/{product_id}'
        headers = {
            'X-API-Key': 'ac6f8a4f-1bae-4826-a837-6e012b910651',
            'Content-Type': 'application/json'
        }

        # Send the request to the Prodigi API
        response = requests.get(url, headers=headers)

        # Return the response from the Prodigi API
        return Response(response.json())

class CancelOrderView(views.APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request, order_id):
        # Set the URL and headers for the Prodigi API request
        url = f'https://api.sandbox.prodigi.com/v4.0/Orders/{order_id}/'
        headers = {
            'X-API-Key': 'ac6f8a4f-1bae-4826-a837-6e012b910651',
            'Content-Type': 'application/json'
        }
        data = {
            'action': 'cancel'
        }

        # Send the request to the Prodigi API
        response = requests.post(url, headers=headers, json=data)

        # Update the status of the order in your database
        order = Order.objects.get(id=order_id)
        order.status = 'canceled'
        order.save()

        # Return the response from the Prodigi API
        return Response(response.json())




class ProdigiOrdersAPIView(views.APIView):
    def post(self, request):
        # Get the data from the request
        data = request.data
        # Set the URL and headers for the Prodigi API request
        url = 'https://api.sandbox.prodigi.com/v4.0/Orders'
        headers = {
            'X-API-Key': 'ac6f8a4f-1bae-4826-a837-6e012b910651',
            'Content-Type': 'application/json'
        }

        # Send the request to the Prodigi API
        response = requests.post(url, headers=headers, json=data)
        
        # Check if the response is empty
        if not response.text:
            # Handle the case where the response is empty
            return Response({'message': 'Empty response from the API.'}, status=500)

        try:
            # Try to parse the response as JSON
            json_data = response.json()
            # Process the JSON data as needed
            # ...

            # Return the response from the Prodigi API
            return Response(json_data)
        except ValueError:
            # Handle the case where the response is not valid JSON
            return Response({'message': 'Invalid JSON in the API response.'}, status=500)
        

class AddOrderDataAPIView(views.APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        # Get the data from the request
        data = request.data

        # Extract the order ID from the data
        order_id = data['order']['id']

        # Save the order data and ID to the database
        order = Order.objects.create(user=request.user, order_data=data, prodigi_order_id=order_id)

        # Return a success response
        return Response({'status': 'success'})


def send_verification_email(user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verification_url = f'http://localhost:4200/activate-account/{uid}/{token}/'
    subject = 'Verify your email address'
    message = f'Please click on the following link to verify your email address: {verification_url}'
    from_email = 'CRISTOCENTRIC <luca.stancu@gmail.com>'
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)

class RegisterView(generics.RetrieveAPIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user.save()
            send_verification_email(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def check_fields(request, email, username, phone_number):
    email_exists = CustomUser.objects.filter(email=email).exists()
    username_exists = CustomUser.objects.filter(username=username).exists()
    phone_number_exists = CustomUser.objects.filter(phone_number=phone_number).exists()

    data = {
        'email_exists': email_exists,
        'username_exists': username_exists,
        'phone_number_exists': phone_number_exists,
    }

    return JsonResponse(data)

class VerifyEmailView(views.APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'failure'}, status=status.HTTP_400_BAD_REQUEST)
        
class LoginView(views.APIView):
    def post(self, request):
        username_or_email = request.data.get('username')
        password = request.data.get('password')
        print(request.data)
        try:
            user = CustomUser.objects.get(email=username_or_email)
            username = user.username
        except CustomUser.DoesNotExist:
            username = username_or_email
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'failure'}, status=status.HTTP_400_BAD_REQUEST)
        
class GetAuthStatusView(LoginRequiredMixin, views.APIView):
    def get(self, request):
        return JsonResponse({'is_authenticated': request.user.is_authenticated})
    

class LogoutView(views.APIView):
    def post(self, request):
        logout(request)
        return JsonResponse({'status': 'success'})
    
class UserDataView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return JsonResponse(serializer.data)

class UpdateUserDataView(LoginRequiredMixin, View):
    def put(self, request):
        user = request.user
        data = json.loads(request.body)
        serializer = UserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        else:
            return JsonResponse(serializer.errors, status=400)


# class ArticleList(views.APIView):
#     def get(self, request):
#         articles = Article.objects.all()
#         serializer = ArticleSerializer(articles, many=True)
#         return Response(serializer.data)

class ArticleDetail(views.APIView):
    def get_object(self, pk):
        try:
            return Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        article = self.get_object(pk)
        serializer = ArticleSerializer(article)
        return Response(serializer.data)
    
class CreateArticle(views.APIView):
    def post(self, request):
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ArticleUpdate(views.APIView):
    def get_object(self, pk):
        try:
            return Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        article = self.get_object(pk)
        serializer = ArticleSerializer(article, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArticleDelete(views.APIView):
    def get_object(self, pk):
        try:
            return Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            raise Http404

    def delete(self, request, pk):
        article = self.get_object(pk)
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ArticleFileUploadView(views.APIView):
    def post(self, request, article_id):
        file = request.FILES['file']
        article = Article.objects.get(pk=article_id)
        article.main_image = file
        article.save()
        file_url = article.main_image.url
        return JsonResponse({'url': file_url})


class ArticleList(views.APIView):
    def get(self, request):
        articles = Article.objects.all()
        page_size = request.GET.get('pageSize', 10)
        paginator = Paginator(articles, page_size)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        serializer = ArticleSerializer(page_obj, many=True)
        return Response({
            'articles': serializer.data,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
        })
    

# EVENTS VIEWS 
class EventCreateView(views.APIView):
    permission_classes = [IsAuthenticated]  # Add the IsAuthenticated permission

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(organizer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request):
        events = Event.objects.all().order_by('created_at')
        page_size = int(request.GET.get('pageSize', 10))
        paginator = Paginator(events, page_size)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        serializer = EventSerializer(page_obj, many=True)
        return Response({
            'events': serializer.data,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
        })

class EventDetailView(views.APIView):
    def get_object(self, event_id):
        try:
            return Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            raise Http404

    def get(self, request, event_id):
        event = self.get_object(event_id)
        serializer = EventSerializer(event)
        return Response(serializer.data)

    def put(self, request, event_id):
        event = self.get_object(event_id)
        serializer = EventSerializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, event_id):
        event = self.get_object(event_id)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class   EventFileUploadView(views.APIView):
    def post(self, request, event_id):
        file = request.FILES['file']
        event = Event.objects.get(pk=event_id)
        event.image = file
        event.save()
        file_url = event.image.url
        return JsonResponse({'url': file_url})

class PublicEventListView(views.APIView):

    def get(self, request):
        events = Event.objects.filter(is_public=True)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)


class SaveEventView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.user.id
        event_id = request.data.get('eventId')

        user = CustomUser.objects.get(id=user_id)
        event = Event.objects.get(id=event_id)

        user.saved_events.add(event)

        return Response({'status': 'success'})
    
    def get(self, request):
        user = request.user
        saved_events = user.saved_events.all()
        data = []
        for event in saved_events:
            data.append({
                    'id': event.id,
                'title': event.title,
                'date': event.date,
                # Add other event fields here
                'location': event.location,
                'description': event.description,
                'general_location' : event.general_location,
            })
        return JsonResponse(data, safe=False)

class RemoveEventView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.user.id
        event_id = request.data.get('eventId')

        user = CustomUser.objects.get(id=user_id)
        event = Event.objects.get(id=event_id)

        user.saved_events.remove(event)

        return Response({'status': 'success'})


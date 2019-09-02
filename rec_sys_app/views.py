import json
import pandas as pd
import turicreate as tc
from utils.recommender import Recommender

from rec_sys_app.models import Transaction
from rec_sys_app.forms import UserForm, UserProfileInfoForm

from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django.contrib.auth import authenticate, login, logout


# Create your views here.
def index(request):
    return render(request, 'rec_sys_app/index.html')


def register(request):
    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            # Can't commit yet because we still need to manipulate
            profile = profile_form.save(commit=False)
            profile.user = user
            if "profile_pic" in request.FILES:
                print("found profile_pic")
                profile.profile_pic = request.FILES["profile_pic"]
            profile.save()
            print("user successfully registered.")
            # reference: https://stackoverflow.com/questions/5823464/django-httpresponseredirect
            # reverse(app_name:str_name)  ==> str_name is defined in `app_name's` `url.py`
            # ==> ```path(... name="str_name")```
            return HttpResponseRedirect(reverse("rec_sys_app:index"))
        else:
            print(user_form.errors, profile_form.errors)
            return HttpResponseRedirect("register")
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()
        return render(request, "rec_sys_app/register.html",
                      {
                          "user_form": user_form,
                          "profile_form": profile_form
                      })


'''
# this route is deprecated because it only support login functionality via HTTP request. It doesn't allow `GET` method, 
and won't render the Login form.
#  
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'}, status=HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'}, status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key}, status=HTTP_200_OK)
'''


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        # Django's built-in authentication function:
        user = authenticate(username=username, password=password)
        if user:
            # Check it the account is active
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('rec_sys_app:index'))
            else:
                return HttpResponse("Your account is not active.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username, password))
            return HttpResponseRedirect(reverse('rec_sys_app:user_login'))
    else:
        return render(request, "rec_sys_app/login.html")


def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse("rec_sys_app:index"))


def profile(request):
    return render(request, "rec_sys_app/profile.html")


def query(request):
    if request.user.is_authenticated:
        body = json.loads(request.body)
        users_to_recommend = [body["uid"]]
        n_rec = body["n_rec"]

        model = tc.load_model("static/model")
        recom = model.recommend(users=["uid"], k=n_rec)
        recom = pd.DataFrame(recom)
        recom = recom["productID"]
        # print(list(recom))
        return JsonResponse({"users_to_recommend": users_to_recommend, "recom": list(recom)})
    else:
        return HttpResponse("You need to login to do that.")


def train(request):
    if request.user.is_authenticated:
        user_id = 'customerID'
        item_id = 'productID'
        name = 'cosine'
        target = 'Purchase_Count'

        recommender = Recommender()

        # pull transactions from database
        transactions = recommender.pull_transactions()
        data = recommender.normalize_transaction_data(transactions, method=0)
        train_data, test_data = recommender.split_data(data, r=.2)

        model = recommender.train_model(train_data, name, user_id, item_id, target)
        model.save("static/model")
        return JsonResponse({"state": "retraining engine done!"})
    else:
        return HttpResponse("you need to login to do that.")


def newtransaction(request):
    if request.user.is_authenticated:
        body = json.loads(request.body)
        # print(type(body))  # dict
        # print(type(body["pid"]))
        # print(type(body['uid']))

        uid = body["uid"]
        pid = body["pid"]
        obj = Transaction(uid=uid, pid=pid)
        obj.save()
        # print(obj.id)
        return JsonResponse({"state": "transaction data uploaded to the recommendation engine!"})
    else:
        return HttpResponse("you need to login to do that.")

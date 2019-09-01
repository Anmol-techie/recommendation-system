import json
import pandas as pd
import turicreate as tc
from django.shortcuts import render
from utils.recommender import Recommender
from django.http import HttpResponse, JsonResponse
from rec_sys_app.models import Transaction


from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK)
from rest_framework.response import Response


# Create your views here.

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

@csrf_exempt
@api_view(["POST"])
def query(request):
    body = json.loads(request.body)
    users_to_recommend = [body["uid"]]
    n_rec = body["n_rec"]

    model = tc.load_model("static/model")
    recom = model.recommend(users=["uid"], k=n_rec)
    recom = pd.DataFrame(recom)
    recom = recom["productID"]
    # print(list(recom))
    return JsonResponse({"users_to_recommend": users_to_recommend, "recom": list(recom)})

@csrf_exempt
@api_view(["POST"])
def train(request):
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

@csrf_exempt
@api_view(["POST"])
def newtransaction(request):
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

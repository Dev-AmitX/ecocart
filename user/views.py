from wsgiref.util import request_uri

from django.http import HttpResponse
from django.shortcuts import render
from datetime import datetime
from django.db import connection
from django.utils.http import escape_leading_slashes
from unicodedata import category

from .models import *


# Create your views here.
def index(request):
    data=tbl_category.objects.all().order_by('-id')[0:6]
    pdata=tbl_product.objects.all().order_by('-discount_price')[0:12]
    sdata=tbl_slider.objects.all().order_by('-id')[0:3]
    md={"cdata":data,"productdata":pdata,"sliderdata":sdata}

    return render(request,'index.html',md)


def product(request):
    cid=request.GET.get('pid')
    pdata=""
    if cid is not  None:
        pdata = tbl_product.objects.all().filter(category=cid)
    else:
        pdata = tbl_product.objects.all().order_by('-id')

    cdata = tbl_category.objects.all().order_by('-id')

    mydict = {"categorydata": cdata,"productdata":pdata}
    return render(request,'product.html',mydict)


def about(request):
    return  render(request,'about.html',)

def contact(request):

    mydict={}
    if request.method=="POST":
        a=request.POST.get('name')
        b=request.POST.get('email')
        c=request.POST.get('mobile')
        d=request.POST.get('subject')
        e=request.POST.get('msg')
        contactus(Name=a,Email=b,Mobile=c,Subject=d,Message=e).save()
        return HttpResponse("<script>alert('Data Save Successfully'); location.href='/contact/';</script>")

        #mydict={"name":a,"email":b,"mobile":c,"subject":d,"message":e}

    return  render(request,'contact.html',mydict)

def faqs(request):
    return  render(request,'faqs.html')

def register(request):

    if request.method=="POST":
        name=request.POST.get('name')
        email=request.POST.get('email')
        passwd = request.POST.get('passwd')
        mobile=request.POST.get('mobile')
        address=request.POST.get('address')
        city=request.POST.get('city')
        pincode = request.POST.get('pincode')
        picture=request.FILES['fu']
        x=tbl_register.objects.all().filter(email=email).count()
        if x==1:
            return HttpResponse("<script>alert('You are already registered..');location.href='/register/';</script>")
        else:
            tbl_register(name=name,email=email,password=passwd,mobile=mobile,address=address,city=city,pincode=pincode,picture=picture).save()
            return HttpResponse("<script>alert('Thanks For register with Us....'); location.href='/register/';</script>")

    return  render(request,'register.html')

def login(request):
    if request.method=="POST":
        email=request.POST.get('userid')#aman@gmail.com
        passwd=request.POST.get('passwd')#45454
        x=tbl_register.objects.all().filter(email=email,password=passwd).count()
        if x==1:
            y=tbl_register.objects.all().filter(email=email)
            request.session['userpic']=str(y[0].picture)
            request.session['username']=str(y[0].name)
            request.session['user']=email
            cartitems=tbl_cart.objects.all().filter(userid=email).count()
            request.session['cartitems']=cartitems
            return HttpResponse("<script>alert('You are login successfully..');location.href='/../';</script>")
        else:
            return HttpResponse("<script>alert('Your userid or password is incorrect..');location.href='/login/';</script>")

    return  render(request,'login.html')

def logout(request):
    if request.session.get('user'):
        del request.session['user']
        return  HttpResponse("<script>alert('Now you are logout');location.href='/login';</script>")
    return  render(request,'logout.html')

def cart(request):
    user = request.session.get('user')
    if user:
        pid=request.GET.get('pid')
        pimage=request.GET.get('pimage')
        pprice=float(request.GET.get('pprice'))
        pname=request.GET.get('pname')
        pw=request.GET.get('pw')
        pquantity=int(request.GET.get('pquantity'))
        total_price=pprice*pquantity
        if pquantity>0:
            tbl_cart(userid=user,product_id=pid,product_image=pimage,product_price=pprice,quantity=pquantity,total_price=total_price,pw=pw,product_name=pname,added_date=datetime.now().date()).save()
            cartitems=tbl_cart.objects.all().filter(userid=user).count()
            request.session['cartitems']=cartitems
            return HttpResponse("<script>alert('Your item is added susseccfully in cart..');location.href='/home/';</script>")
        else:
            return HttpResponse("<script>alert('Please Increse your item  quantity');location.href='/home/';</script>")

    return render(request,'cart.html')

def orderhistory(request):
    oid=request.GET.get('oid')
    user=request.session.get('user')
    if user:
        data1=tbl_order.objects.all().filter(userid=user,status="Pending")
        data2=tbl_order.objects.all().filter(userid=user,status="Accepted")
        data3=tbl_order.objects.all().filter(userid=user,status="Delivered")
        if oid is not None:
            tbl_order.objects.all().filter(id=oid).delete()
            return HttpResponse("<script>alert('your order has been cancel');location.href='/history/';</script>")
        mydict={"porder":data1,"aorder":data2,"dorder":data3}

    return  render(request,'orderhistory.html',mydict)

def myprofile(request):
    user=request.session.get('user')
    uinfo=""
    if user:
        uinfo=tbl_register.objects.all().filter(email=user)
        if request.method=="POST":
            name=request.POST.get('name')
            mobile=request.POST.get('mobile')
            address=request.POST.get('address')
            city=request.POST.get('city')
            pincode=request.POST.get('pincode')
            passwd=request.POST.get('passwd')
            cpasswd=request.POST.get('cpasswd')
            picture=request.FILES['fu']
            if passwd==cpasswd:
                tbl_register(email=user,name=name,mobile=mobile,address=address,city=city,pincode=pincode,picture=picture,password=passwd).save()
                y = tbl_register.objects.all().filter(email=user)
                request.session['userpic'] = str(y[0].picture)
                request.session['username'] = str(y[0].name)
                return HttpResponse("<script>alert('Your profile is updated successfully..');location.href='/profile/'</script>")
            else:
                return HttpResponse("<script>alert('confirm password is not matched..');location.href='/profile/'</script>")
    mydict={"userinfo":uinfo}
    return render(request,'myprofile.html',mydict)

def showcart(request):
    user=request.session.get('user')
    cid=request.GET.get('cid')
    data=""
    if user:
        data=tbl_cart.objects.all().filter(userid=user).order_by('-id')
        if cid is not None:
            tbl_cart.objects.all().filter(id=cid).delete()
            cartitems=tbl_cart.objects.all().filter(userid=user).count()
            request.session['cartitems'] = cartitems
            return HttpResponse("<script>alert('Your item has been deleted from cart..');location.href='/showcart/'</script>")

    md={"cartdata":data}
    return render(request,'showcartitems.html',md)

def cartforproduct(request):
    user = request.session.get('user')
    if user:
        pid = request.GET.get('pid')
        pimage = request.GET.get('pimage')
        pprice = float(request.GET.get('pprice'))
        pname = request.GET.get('pname')
        pw = request.GET.get('pw')
        pquantity = int(request.GET.get('pquantity'))
        total_price = pprice * pquantity
        if pquantity > 0:
            tbl_cart(userid=user, product_id=pid, product_image=pimage, product_price=pprice, quantity=pquantity,total_price=total_price, pw=pw, product_name=pname, added_date=datetime.now().date()).save()
            cartitems = tbl_cart.objects.all().filter(userid=user).count()
            request.session['cartitems'] = cartitems
            return HttpResponse(
                "<script>alert('Your item is added susseccfully in cart..');location.href='/product/';</script>")
        else:
            return HttpResponse("<script>alert('Please Increse your item  quantity');location.href='/product/';</script>")

    return render(request,'pcart.html')

def order(request):
    user=request.session.get('user')
    msg=request.GET.get('msg')
    if user:
         if msg is not None:
            cursor=connection.cursor()
            cursor.execute("insert into user_tbl_order(userid,product_id, product_name,product_image,product_price,product_quantity, total_price,pw,status,order_date) select '"+str(user)+"',product_id, product_name,product_image,product_price,quantity,total_price,pw,'Pending','"+str(datetime.now().date())+"' from user_tbl_cart where userid='"+str(user)+"'")
            tbl_cart.objects.all().filter(userid=user).delete()
            cartitems = tbl_cart.objects.all().filter(userid=user).count()
            request.session['cartitems'] = cartitems
            return HttpResponse("<script>alert('Your order placed successfully..');location.href='/history/';</script>")

    return render(request,'order.html')

def portfolio(request):
    return  render(request,'portfolio.html')
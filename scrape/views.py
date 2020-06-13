from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from .forms import RequestForm
from django.views import generic
import uuid
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from .models import Request

def get_yahooauction(url):
    res = requests.get(url)
    soup = bs(res.content, "html.parser")
    items = soup.findAll("li", class_="Product")
    return[
        {
            "title": item.find("a",class_="product__titleLink"),
            "url": item.find("a",class_="Product__titleLink").get("href"),
            "picture": item.find("img").get("src")
        }
        for item in items
    ]

class GetData(generic.FormView):
    template_name = "scrape/index.html"
    form_class = RequestForm

    def form_valid(self, form):
        # uuidを生成
        _uuid = uuid.uuid4()
        gcs_bucket = "gs://yuw5296"
        # formオブジェクトを初期化
        f = form.save(commit=False)
        # formにuuidを代入       
        f.uuid = _uuid
        # formを保存
        f.save()
        url = form.cleaned_data["url"]
        # スクレイピング
        result = get_yahooauction(url)
        df = pd.DataFrame(result)
        # file名を定義
        filename = f"{gcs_bucket}/{_uuid}test.pkl"
        # save data
        df.to_pickle(filename)

        context = {
            "url": form.cleaned_data["url"],
            "form": self.form_class,
            "name": f"スクレイピング {datetime.today()}",
            "result": Request.objects.all().order_by("-date")
        }
        return render(
            self.request, 
            self.template_name,
            context
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name"] = f"スクレイピング {datetime.today()}"
        context["result"] = Request.objects.all().order_by("-date")
        return context

def downloader(request, uuid):
    gcs_bucket = "gs://yuw5296"
    filename = f"{gcs_bucket}/{uuid}test.pkl"
    df = pd.read_pickle(filename)

    res = HttpResponse(content_type="text/csv; charset=utf-8")
    file_name = f"{datetime.today()}_dj.csv"
    res["Content-Disposition"] = f"attachment; filename*=UTF-8\'\'{file_name}"
    df.to_csv(res, index=False)

    return res
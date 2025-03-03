from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from .codal_scraper import main
import threading
import json
from .models import Log


@csrf_exempt
def start_scrape(request):
    if request.method == "POST":
        # read json from request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"status": "Invalid JSON format"}, status=400)

        # get parameters form json data
        Audited = data.get("Audited", True)
        AuditorRef = data.get("AuditorRef", None)
        Category = data.get("Category", None)
        Childs = data.get("Childs", None)
        CompanyState = data.get("CompanyState", None)
        CompanyType = data.get("CompanyType", None)
        Consolidatable = data.get("Consolidatable", None)
        IndustryGroup = data.get("IndustryGroup", None)
        IsNotAudited = data.get("IsNotAudited", None)
        Length = data.get("Length", None)
        LetterCode = data.get("LetterCode", None)
        LetterType = data.get("LetterType", None)
        Mains = data.get("Mains", None)
        NotAudited = data.get("NotAudited", None)
        NotConsolidatable = data.get("NotConsolidatable", None)
        PageNumber = data.get("PageNumber", None)
        Publisher = data.get("Publisher", None)
        ReportingType = data.get("ReportingType", None)
        Symbol = data.get("Symbol", None)
        TracingNo = data.get("TracingNo", None)

        # get row and col
        row_names = data.get("row_names", [])
        col_names = data.get("col_names", [])

        if isinstance(row_names, str):
            try:
                row_names = json.loads(row_names)
            except json.JSONDecodeError:
                Log.objects.create(
                    log_detail=f"status : Invalid row_names format",
                    row=row_names,
                    col=col_names,
                )
                return JsonResponse({"status": "Invalid row_names format"}, status=400)

        if isinstance(col_names, str):
            try:
                col_names = json.loads(col_names)
            except json.JSONDecodeError:
                Log.objects.create(
                    log_detail=f"status : Invalid col_names format",
                    row=row_names,
                    col=col_names,
                )
                return JsonResponse({"status": "Invalid col_names format"}, status=400)

    def run_scrape():
        result = main(
            Audited=Audited,
            AuditorRef=AuditorRef,
            Category=Category,
            Childs=Childs,
            CompanyState=CompanyState,
            CompanyType=CompanyType,
            Consolidatable=Consolidatable,
            IndustryGroup=IndustryGroup,
            IsNotAudited=IsNotAudited,
            Length=Length,
            LetterCode=LetterCode,
            LetterType=LetterType,
            Mains=Mains,
            NotAudited=NotAudited,
            NotConsolidatable=NotConsolidatable,
            PageNumber=PageNumber,
            Publisher=Publisher,
            ReportingType=ReportingType,
            Symbol=Symbol,
            TracingNo=TracingNo,
            row_names=row_names,
            col_names=col_names,
        )

    # create thread
    scrape_thread = threading.Thread(target=run_scrape)
    scrape_thread.start()

    # return message that bot is working on task
    return JsonResponse({"status": "bot is tryin'"})

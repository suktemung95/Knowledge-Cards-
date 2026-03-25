from django.shortcuts import render, redirect
from .models import KnowledgeCard
from .utils import upload_to_s3
from .utils import generate_histogram
from .similarity import compare_image_similarity

from io import BytesIO

# Create your views here.
def home(request):
    query = request.GET.get('q')
    
    if query:
        cards = KnowledgeCard.objects.filter(title__icontains=query) | \
                KnowledgeCard.objects.filter(description__icontains=query)
    else:
        cards = KnowledgeCard.objects.all()

    return render(request, "home.html", {"cards": cards})

def upload_card(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        image = request.FILES.get("image")

        # Read file into memory
        image_bytes = image.read()

        # Upload to S3
        image_url = upload_to_s3(BytesIO(image_bytes), image.name)

        # Generate histogram
        histogram = generate_histogram(BytesIO(image_bytes))

        # Save to DB
        KnowledgeCard.objects.create(
            title=title,
            description=description,
            image_url=image_url,
            histogram=histogram
        )

        return redirect("/")

    return render(request, "upload.html")

def show_db(request):
    cards = KnowledgeCard.objects.all()
    return render(request, "db.html", {"cards": cards})

def image_search(request):
    if request.method == "POST":
        image = request.FILES.get("image")

        print("Uploaded image: ", image)

        image.seek(0)
        query_hist = generate_histogram(image)

        print("Query histogram length:", len(query_hist))

        results = []

        for card in KnowledgeCard.objects.all():
            try:
                score = compare_image_similarity(query_hist, card.histogram)
                print(f"{card.title}: {score}")
                results.append((card, score))
            except Exception as e:
                print("Error comparing:", e)

        results.sort(key=lambda x: x[1], reverse=True)

        cards = [card for card, score in results[:5]]

        return render(request, "home.html", {"cards": cards})

    return render(request, "image_search.html")
from django.shortcuts import render, redirect
import markdown2
from . import util
import random

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
    })


def entry(request, title):
    # Get content of entry
    content = util.get_entry(title)

    # If no entry, error page indicating that their requested page was not found
    if not content:
        return render(request, "encyclopedia/error.html", {
            "error_message": "Requested page was not found",
        })

    # Else return the entry where the markdown is converted to HTML
    return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": markdown2.markdown(content),
        })
    

def search(request):
    if request.method == "GET":
        # Get search promptand entries
        prompt = request.GET.get("q").strip().lower()
        entries = [e for e in util.list_entries()]

        # If prompt matches an entry, redirect to that entry
        if prompt in [e.lower() for e in entries]:
            return redirect(entry, prompt)
        
        # Return strings where prompt is a substring of the entry title
        substrings = [e for e in entries if prompt in e.lower()]
        if substrings:
            return render(request, "encyclopedia/results.html", {
                "pages": substrings,
            })

        # If not matching searches, return that searches weere not found
        return render(request, "encyclopedia/error.html", {
                "error_message": f"Search not found",
            })

def create(request):
    if request.method == "GET":
        return render(request, "encyclopedia/editor.html", {
            "redirect_to": "create",
            "entry_title": "",
            "entry_content": "",
        })
    else:
        title = request.POST.get("title").strip()
        content = request.POST.get("content")

        # Check that title dies not already exists
        if title.lower() in [e.lower() for e in util.list_entries()]:
            return render(request, "encyclopedia/error.html", {
                "error_message": f"{title} already exists",
            })
        
        # Save entry and redirect ti edited entry
        util.save_entry(title, content)
        return redirect(entry, title)


def edit(request):
    if request.method == "GET":
        # Render editor page with title and content
        title = request.GET.get("title")
        content = util.get_entry(title)
        return render(request, "encyclopedia/editor.html", {
            "redirect_to": "edit",
            "entry_title": title,
            "entry_content": content,
        })
    else:
        # Save the entry and redirect to the entry
        title = request.POST.get("title")
        content = request.POST.get("content")
        util.save_entry(title, content)
        return redirect(entry, title)


def random_entry(request):
    entries = util.list_entries()
    return redirect(entry, random.choice(entries))

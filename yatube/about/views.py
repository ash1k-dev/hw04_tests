from django.views.generic.base import TemplateView


class AboutAuthor(TemplateView):
    template_name = 'posts/about/author.html'


class AboutTech(TemplateView):
    template_name = 'posts/about/tech.html'

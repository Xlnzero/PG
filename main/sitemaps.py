from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return [
            "home",
            "about",
            "pam",
            "pam_got",
            "aks",
            "vid",
            "cat",
            "model",
            "about_mo",
            "contact",
        ]

    def location(self, item):
        return reverse(item)


class PamGotGallerySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6
    categories = ("zv", "od", "pol", "dv", "vip")

    def items(self):
        return self.categories

    def location(self, category):
        return reverse("pam_got_gallery", kwargs={"category": category})


class PamRenderGallerySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6
    categories = ("zv", "od", "pol", "dv", "vip")

    def items(self):
        return self.categories

    def location(self, category):
        return reverse("pam_render_gallery", kwargs={"category": category})


class OsnGallerySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    categories = ("aks", "obj", "vid")

    def items(self):
        return self.categories

    def location(self, category):
        return reverse("osn_gallery", kwargs={"category": category})


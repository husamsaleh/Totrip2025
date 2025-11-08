import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from wagtail.models import Page, Site
from blog.models import BlogIndexPage, BlogPage, BlogCategory, BlogAuthor
from tourguides.models import TourGuide, Language, Specialty, Location

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with initial data: admin user, blogs, and tour guides.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        admin_username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        admin_email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        admin_password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

        if not User.objects.filter(username=admin_username).exists():
            User.objects.create_superuser(admin_username, admin_email, admin_password)
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser: {admin_username}'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser "{admin_username}" already exists.'))

        try:
            site = Site.objects.get(is_default_site=True)
            root_page = site.root_page
        except Site.DoesNotExist:
            self.stdout.write(self.style.ERROR('Default site not found. Cannot create pages.'))
            root_page = None

        if root_page:
            try:
                blog_index_page = BlogIndexPage.objects.get(slug='blog')
                self.stdout.write(self.style.WARNING('Blog Index Page already exists.'))
            except BlogIndexPage.DoesNotExist:
                blog_index_page = BlogIndexPage(
                    title='Blog',
                    slug='blog',
                    intro='Welcome to our blog!',
                )
                root_page.add_child(instance=blog_index_page)
                blog_index_page.save_revision().publish()
                self.stdout.write(self.style.SUCCESS('Created Blog Index Page.'))

            category1, _ = BlogCategory.objects.get_or_create(
                slug='travel-tips',
                defaults={'name': 'Travel Tips'}
            )
            category2, _ = BlogCategory.objects.get_or_create(
                slug='destinations',
                defaults={'name': 'Destinations'}
            )
            category3, _ = BlogCategory.objects.get_or_create(
                slug='guides',
                defaults={'name': 'Guides'}
            )

            author, _ = BlogAuthor.objects.get_or_create(
                name='Admin',
                defaults={'bio': 'Administrator and content creator.'}
            )

            blog_posts_data = [
                {
                    'title': 'Top 10 Destinations in Saudi Arabia',
                    'slug': 'top-10-destinations-saudi-arabia',
                    'intro': 'Discover the most beautiful and historic places in Saudi Arabia.',
                    'body': '<p>Saudi Arabia is home to some of the most stunning destinations in the Middle East. From the ancient ruins of Al-Ula to the modern skyline of Riyadh, there is something for everyone.</p><p>Whether you are interested in history, culture, or adventure, Saudi Arabia has it all.</p>',
                    'categories': [category2, category3],
                    'date': timezone.now().date() - timedelta(days=5),
                },
                {
                    'title': 'Essential Travel Tips for First-Time Visitors',
                    'slug': 'essential-travel-tips-first-time-visitors',
                    'intro': 'Everything you need to know before visiting Saudi Arabia.',
                    'body': '<p>Planning your first trip to Saudi Arabia? Here are some essential tips to make your journey smooth and enjoyable.</p><p>From cultural etiquette to transportation, we cover all the basics.</p>',
                    'categories': [category1],
                    'date': timezone.now().date() - timedelta(days=3),
                },
                {
                    'title': 'Best Time to Visit Saudi Arabia',
                    'slug': 'best-time-visit-saudi-arabia',
                    'intro': 'Learn about the best seasons and weather conditions for your trip.',
                    'body': '<p>The climate in Saudi Arabia varies by region. Understanding the weather patterns can help you plan the perfect trip.</p><p>Winter months are generally the most comfortable for outdoor activities.</p>',
                    'categories': [category1, category2],
                    'date': timezone.now().date() - timedelta(days=1),
                },
            ]

            for post_data in blog_posts_data:
                try:
                    existing_post = BlogPage.objects.get(slug=post_data['slug'])
                    self.stdout.write(self.style.WARNING(f'Blog Post "{post_data["title"]}" already exists.'))
                except BlogPage.DoesNotExist:
                    blog_page = BlogPage(
                        title=post_data['title'],
                        slug=post_data['slug'],
                        intro=post_data['intro'],
                        body=post_data['body'],
                        date=post_data['date'],
                        author=author,
                        read_time=5,
                    )
                    blog_index_page.add_child(instance=blog_page)
                    blog_page.save_revision().publish()
                    blog_page.categories.set(post_data['categories'])
                    self.stdout.write(self.style.SUCCESS(f'Created Blog Post: {blog_page.title}'))

        arabic_lang, _ = Language.objects.get_or_create(name='Arabic', defaults={'code': 'ar'})
        english_lang, _ = Language.objects.get_or_create(name='English', defaults={'code': 'en'})

        specialty1, _ = Specialty.objects.get_or_create(name='Historical Tours')
        specialty2, _ = Specialty.objects.get_or_create(name='Adventure Tours')
        specialty3, _ = Specialty.objects.get_or_create(name='Cultural Tours')

        riyadh, _ = Location.objects.get_or_create(
            name='Riyadh',
            city='Riyadh',
            defaults={'country': 'Saudi Arabia', 'is_popular': True}
        )
        jeddah, _ = Location.objects.get_or_create(
            name='Jeddah',
            city='Jeddah',
            defaults={'country': 'Saudi Arabia', 'is_popular': True}
        )
        mecca, _ = Location.objects.get_or_create(
            name='Mecca',
            city='Mecca',
            defaults={'country': 'Saudi Arabia', 'is_popular': True}
        )

        tour_guides_data = [
            {
                'username': 'ahmed_guide',
                'email': 'ahmed@example.com',
                'first_name': 'Ahmed',
                'last_name': 'Al-Saud',
                'bio': 'Experienced tour guide specializing in historical and cultural tours of Saudi Arabia.',
                'years_of_experience': 8,
                'languages': [arabic_lang, english_lang],
                'specialties': [specialty1, specialty3],
            },
            {
                'username': 'fatima_guide',
                'email': 'fatima@example.com',
                'first_name': 'Fatima',
                'last_name': 'Al-Rashid',
                'bio': 'Adventure tour guide with expertise in desert expeditions and outdoor activities.',
                'years_of_experience': 5,
                'languages': [arabic_lang, english_lang],
                'specialties': [specialty2],
            },
            {
                'username': 'khalid_guide',
                'email': 'khalid@example.com',
                'first_name': 'Khalid',
                'last_name': 'Al-Mansouri',
                'bio': 'Professional guide offering comprehensive tours of major cities and landmarks.',
                'years_of_experience': 10,
                'languages': [arabic_lang, english_lang],
                'specialties': [specialty1, specialty2, specialty3],
            },
        ]

        for guide_data in tour_guides_data:
            user, created = User.objects.get_or_create(
                username=guide_data['username'],
                defaults={
                    'email': guide_data['email'],
                    'first_name': guide_data['first_name'],
                    'last_name': guide_data['last_name'],
                }
            )

            if created:
                user.set_password('guide123')
                user.save()

            tour_guide, tg_created = TourGuide.objects.get_or_create(
                user=user,
                defaults={
                    'bio': guide_data['bio'],
                    'years_of_experience': guide_data['years_of_experience'],
                    'is_verified': True,
                    'is_active': True,
                }
            )

            if tg_created:
                tour_guide.languages.set(guide_data['languages'])
                tour_guide.specialties.set(guide_data['specialties'])
                self.stdout.write(self.style.SUCCESS(f'Created Tour Guide: {user.get_full_name() or user.username}'))
            else:
                self.stdout.write(self.style.WARNING(f'Tour Guide "{user.get_full_name() or user.username}" already exists.'))

        self.stdout.write(self.style.SUCCESS('Database seeding complete!'))


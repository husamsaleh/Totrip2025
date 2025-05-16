# TourGuide Model Field Name Inconsistencies

## Model Fields

1. In the `TourGuide` model:
   - The main model name is `TourGuide` (one word)

2. In related models:
   - `WorkSchedule` model uses `tour_guide` (underscore) for the ForeignKey field
   - `Gallery` model uses `tour_guide` (underscore) for the ForeignKey field
   - `Video` model uses `tour_guide` (underscore) for the ForeignKey field
   - `Review` model uses both `tour_guide` (underscore) in the model definition and `guide` in some function calls

## View Function Inconsistencies

1. In `guide_dashboard` view:
   - Uses `tour_guide = TourGuide.objects.get(user=request.user)`
   - But then references:
     - `packages = TourPackage.objects.filter(guide=tour_guide)`
     - `schedules = WorkSchedule.objects.filter(guide=tour_guide)`
     - `reviews = Review.objects.filter(guide=tour_guide)`

2. In `add_tour_package` view:
   - Gets `tour_guide = get_object_or_404(TourGuide, user=request.user)`
   - But then assigns: `package.tour_guide = tour_guide`

3. In `guide_profile` view:
   - Uses `packages = TourPackage.objects.filter(tour_guide=tour_guide, is_active=True)`
   - But in the admin section the field may be different

## URL Naming Inconsistencies

1. URL pattern naming:
   - `path('dashboard/', views.guide_dashboard, name='tourguide_dashboard')` (using tourguide as one word)
   - `path('guides/<slug:slug>/', views.guide_profile, name='tourguide_profile')` (using tourguide as one word)

## Recommended Standardization

For consistency, the codebase should standardize on one of these patterns:
1. Use `tour_guide` (with underscore) throughout all models and views
2. OR use `guide` throughout all models and views
3. OR use `tourguide` (one word) throughout all models and views

The most common pattern currently appears to be `tour_guide` with underscore. 
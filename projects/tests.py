from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from .models import Project, Donation


class ProjectDateValidationTest(TestCase):
    def test_end_before_start_raises_error(self):
        start = timezone.now() + timezone.timedelta(days=2)
        end = timezone.now() + timezone.timedelta(days=1)
        project = Project(
            owner=User.objects.create_user(
                email="owner@test.com",
                first_name="Owner",
                last_name="User",
                phone_number="01012345678",
                password="pass",
                is_active=True,
            ),
            title="Test",
            details="Details",
            total_target=1000,
            start_time=start,
            end_time=end,
        )
        with self.assertRaises(Exception):
            project.clean()

    def test_past_start_time_raises_error_on_create(self):
        start = timezone.now() - timezone.timedelta(hours=1)
        end = timezone.now() + timezone.timedelta(days=1)
        owner = User.objects.create_user(
            email="owner@test.com",
            first_name="Owner",
            last_name="User",
            phone_number="01012345678",
            password="pass",
            is_active=True,
        )
        form_data = {
            "title": "Test",
            "details": "Details",
            "total_target": 1000,
            "start_time": start.strftime("%Y-%m-%dT%H:%M"),
            "end_time": end.strftime("%Y-%m-%dT%H:%M"),
        }
        self.client.force_login(owner)
        response = self.client.post(reverse("projects:create"), form_data)
        self.assertContains(response, "Start time cannot be in the past")

    def test_zero_target_raises_error(self):
        project = Project(
            owner=User.objects.create_user(
                email="owner@test.com",
                first_name="Owner",
                last_name="User",
                phone_number="01012345678",
                password="pass",
                is_active=True,
            ),
            title="Test",
            details="Details",
            total_target=0,
            start_time=timezone.now() + timezone.timedelta(days=1),
            end_time=timezone.now() + timezone.timedelta(days=2),
        )
        with self.assertRaises(Exception):
            project.clean()


class ProjectAuthorizationTest(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(
            email="a@test.com",
            first_name="User",
            last_name="A",
            phone_number="01012345678",
            password="pass",
            is_active=True,
        )
        self.user_b = User.objects.create_user(
            email="b@test.com",
            first_name="User",
            last_name="B",
            phone_number="01112345678",
            password="pass",
            is_active=True,
        )
        self.project = Project.objects.create(
            owner=self.user_a,
            title="Project A",
            details="Details",
            total_target=1000,
            start_time=timezone.now() + timezone.timedelta(days=1),
            end_time=timezone.now() + timezone.timedelta(days=10),
        )

    def test_user_cannot_edit_others_project(self):
        self.client.force_login(self.user_b)
        response = self.client.get(reverse("projects:update", kwargs={"pk": self.project.pk}))
        self.assertEqual(response.status_code, 403)

    def test_user_cannot_delete_others_project(self):
        self.client.force_login(self.user_b)
        response = self.client.get(reverse("projects:delete", kwargs={"pk": self.project.pk}))
        self.assertEqual(response.status_code, 403)

    def test_owner_can_edit(self):
        self.client.force_login(self.user_a)
        response = self.client.get(reverse("projects:update", kwargs={"pk": self.project.pk}))
        self.assertEqual(response.status_code, 200)

    def test_owner_can_delete(self):
        self.client.force_login(self.user_a)
        response = self.client.get(reverse("projects:delete", kwargs={"pk": self.project.pk}))
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_redirected_to_login(self):
        response = self.client.get(reverse("projects:create"))
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('projects:create')}"
        )


class DonationTest(TestCase):
    def setUp(self):
        self.donor = User.objects.create_user(
            email="donor@test.com",
            first_name="Donor",
            last_name="User",
            phone_number="01012345678",
            password="pass",
            is_active=True,
        )
        self.owner = User.objects.create_user(
            email="owner@test.com",
            first_name="Owner",
            last_name="User",
            phone_number="01112345678",
            password="pass",
            is_active=True,
        )
        self.project = Project.objects.create(
            owner=self.owner,
            title="Test Project",
            details="Details",
            total_target=1000,
            start_time=timezone.now() + timezone.timedelta(days=1),
            end_time=timezone.now() + timezone.timedelta(days=10),
        )

    def test_donation_updates_current_amount(self):
        donation = Donation.objects.create(
            project=self.project,
            donor=self.donor,
            amount=Decimal("50.00"),
        )
        self.project.current_amount += donation.amount
        self.project.save(update_fields=["current_amount"])
        self.project.refresh_from_db()
        self.assertEqual(self.project.current_amount, Decimal("50.00"))

    def test_donate_as_authenticated_user(self):
        self.client.force_login(self.donor)
        response = self.client.post(
            reverse("projects:detail", kwargs={"pk": self.project.pk}),
            {"amount": "25.00", "message": "Great project!"},
        )
        self.assertRedirects(response, reverse("projects:detail", kwargs={"pk": self.project.pk}))
        self.project.refresh_from_db()
        self.assertEqual(self.project.current_amount, Decimal("25.00"))

    def test_percent_raised(self):
        self.project.current_amount = Decimal("250.00")
        self.project.save(update_fields=["current_amount"])
        self.assertEqual(self.project.percent_raised(), 25)

    def test_percent_raised_caps_at_100(self):
        self.project.current_amount = Decimal("2000.00")
        self.project.save(update_fields=["current_amount"])
        self.assertEqual(self.project.percent_raised(), 100)


class PageRenderTest(TestCase):
    def test_home_page_renders(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    def test_about_page_renders(self):
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "about.html")

    def test_user_directory_empty(self):
        response = self.client.get(reverse("user_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/user_list.html")

    def test_user_directory_with_creator(self):
        owner = User.objects.create_user(
            email="c@test.com",
            first_name="Creator",
            last_name="User",
            phone_number="01012345678",
            password="pass",
            is_active=True,
        )
        Project.objects.create(
            owner=owner,
            title="P",
            details="D",
            total_target=100,
            start_time=timezone.now() + timezone.timedelta(days=1),
            end_time=timezone.now() + timezone.timedelta(days=10),
        )
        response = self.client.get(reverse("user_list"))
        self.assertContains(response, "Creator")

    def test_user_detail_page(self):
        owner = User.objects.create_user(
            email="c@test.com",
            first_name="Creator",
            last_name="User",
            phone_number="01012345678",
            password="pass",
            is_active=True,
        )
        project = Project.objects.create(
            owner=owner,
            title="My Project",
            details="Details",
            total_target=100,
            start_time=timezone.now() + timezone.timedelta(days=1),
            end_time=timezone.now() + timezone.timedelta(days=10),
        )
        response = self.client.get(reverse("user_detail", kwargs={"pk": owner.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Project")

"""Tests de performance (charge) pour M-Motors, avec Locust.

Installation :
    pip install -r requirements-perf.txt

Lancement avec interface web (recommande) :
    locust -f locustfile.py --host https://app-production-bbb1.up.railway.app
    puis ouvrir http://localhost:8089 et choisir le nombre d'utilisateurs.

Lancement sans interface (CI / terminal) :
    locust -f locustfile.py --host https://app-production-bbb1.up.railway.app \
           --users 50 --spawn-rate 5 --run-time 1m --headless

Note : le scenario de connexion necessite un host en HTTPS (le cookie CSRF
est marque "secure") et le compte admin seede par l'application.
"""
from locust import HttpUser, task, between


class VisiteurAnonyme(HttpUser):
    """Parcourt le catalogue public (le profil de charge le plus frequent)."""

    weight = 4
    wait_time = between(1, 3)

    @task(3)
    def accueil(self):
        self.client.get("/")

    @task(3)
    def liste_vehicules(self):
        self.client.get("/vehicles")

    @task(2)
    def filtrer_achat(self):
        self.client.get("/vehicles?type=achat")

    @task(2)
    def filtrer_location(self):
        self.client.get("/vehicles?type=location")

    @task(1)
    def detail_vehicule(self):
        # name= regroupe les URLs dynamiques dans une seule ligne de stats.
        with self.client.get(
            "/vehicles/1", name="/vehicles/[id]", catch_response=True
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()

    @task(1)
    def page_connexion(self):
        self.client.get("/auth/login")

    @task(1)
    def page_inscription(self):
        self.client.get("/auth/register")


class ClientConnecte(HttpUser):
    """Simule le flux de connexion complet (CSRF-aware) puis l'espace client."""

    weight = 1
    wait_time = between(2, 5)

    @task
    def connexion(self):
        # 1. GET de la page login -> le serveur depose le cookie csrf_token.
        self.client.get("/auth/login")
        token = self.client.cookies.get("csrf_token", "")

        # 2. POST avec le jeton CSRF recupere.
        with self.client.post(
            "/auth/login",
            data={
                "email": "admin@m-motors.fr",
                "password": "Admin123!",
                "csrf_token": token,
            },
            allow_redirects=False,
            catch_response=True,
            name="/auth/login [POST]",
        ) as resp:
            if resp.status_code in (302, 303):
                resp.success()
            else:
                resp.failure(f"Connexion inattendue : {resp.status_code}")

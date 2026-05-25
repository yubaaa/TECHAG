#!/usr/bin/env python3
"""
CPIRS Demo - Mode pas à pas
"""

import sys
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)

sys.path.insert(0, r"D:\M1\TECH AG\projet")

from cpirs import (
    CPIRS, MigrationMode,
    Container, Platform,
    UserProfile,
    seed_containers,
)

DIVIDER = "=" * 70

def pause(msg="Appuie sur ENTRÉE pour continuer..."):
    input(f"\n  ⏎  {msg}\n")

def print_results(docs, title):
    print(f"\n{'─'*70}")
    print(f"  {title}")
    print(f"{'─'*70}")
    if not docs:
        print("  (aucun résultat)")
        return
    for rank, doc in enumerate(docs, 1):
        print(f"  #{rank}  [{doc.category:10s}]  {doc.title}")
        print(f"         mots-clés : {', '.join(doc.keywords[:4])}")
        print(f"         score     : {doc.relevance_score:.4f}")
    print()

def print_migration_log(system):
    if not hasattr(system, "_last_agent"):
        return
    agent = system._last_agent
    summary = agent.migration_summary()
    print(f"\n{'─'*70}")
    print(f"  Journal de migration  (agent {summary['agent_id']})")
    print(f"{'─'*70}")
    for m in summary["migrations"]:
        arrow = "↔" if "inter_container" in m["type"] else "↕"
        print(f"  {arrow}  {m['from']}  →  {m['to']}  ({m['overhead_ms']} ms)")
    print()


# ══════════════════════════════════════════════════════════════════════
#  INTRODUCTION
# ══════════════════════════════════════════════════════════════════════
print(f"\n{DIVIDER}")
print("  CPIRS:")
print("  Centralised and Personalised Information Retrieval System")
print(f"{DIVIDER}")


pause("Commencer le CAS 1 — Migration Inter-Container")


# ══════════════════════════════════════════════════════════════════════
#  CAS 1 — INTER-CONTAINER
# ══════════════════════════════════════════════════════════════════════
print(f"\n{DIVIDER}")
print("  CAS 1 — MIGRATION INTER-CONTAINER")
print(f"{DIVIDER}")
print("""
  ┌─────────────────── PlatformA ───────────────────┐
  │                                                  │
  │  [ContainerA1] ──→ [ContainerA2] ──→ [ContainerA3] │
  │       ↑ Agent part d'ici et migre               │
  └──────────────────────────────────────────────────┘
""")

pause("Créer la plateforme et les containers...")

platform_A = Platform(platform_id="PlatformA")
c1 = Container(name="ContainerA1")
c2 = Container(name="ContainerA2")
c3 = Container(name="ContainerA3")
seed_containers(c1, c2, c3)
platform_A.register_container(c1)
platform_A.register_container(c2)
platform_A.register_container(c3)

system1 = CPIRS(name="CPIRS-InterContainer")
system1.add_platform(platform_A)

print("\nSystème créé :")
print(json.dumps(system1.status(), indent=6))

pause("Définir le profil utilisateur Dalila")

dalila = UserProfile(
    name="Dalila",
    preferred_categories=["AI", "IR"],
    keywords_of_interest=["machine learning", "neural network", "NLP", "BERT"],
)
print(f"""
     Profil utilisateur :
     Nom        : {dalila.name}
     Catégories : {dalila.preferred_categories}
     Intérêts   : {dalila.keywords_of_interest}
""")

pause("Lancer l'agent acheteur mobile (inter-container)...")

print("\nL'agent démarre et migre entre les containers...\n")
results1 = system1.search(
    query          = "machine learning neural network",
    user_profile   = dalila,
    max_results    = 4,
    migration_mode = MigrationMode.INTER_CONTAINER,
)

pause("Afficher le journal de migration...")
print_migration_log(system1)

pause("Afficher les résultats personnalisés pour Alice...")
print_results(results1, "Résultats pour Alice  (inter-container)")


# ══════════════════════════════════════════════════════════════════════
#  CAS 2 — INTER-PLATFORM
# ══════════════════════════════════════════════════════════════════════
pause("Passer au CAS 2 — Migration Inter-Platform")

print(f"\n{DIVIDER}")
print("  CAS 2 — MIGRATION INTER-PLATFORM")
print(f"{DIVIDER}")
print("""
  ┌──── PlatformX ────┐        ┌──── PlatformY ────┐
  │                   │        │                   │
  │ [X1] ──→ [X2]    │──────→ │ [Y1] ──→ [Y2]    │
  │  Agent migre      │        │  Agent continue   │
  └───────────────────┘        └───────────────────┘
""")

pause("Créer les deux plateformes et leurs containers...")

platform_X = Platform(platform_id="PlatformX")
platform_Y = Platform(platform_id="PlatformY")
cx1 = Container(name="ContainerX1")
cx2 = Container(name="ContainerX2")
cy1 = Container(name="ContainerY1")
cy2 = Container(name="ContainerY2")
seed_containers(cx1, cx2, cy1, cy2)
platform_X.register_container(cx1)
platform_X.register_container(cx2)
platform_Y.register_container(cy1)
platform_Y.register_container(cy2)

system2 = CPIRS(name="CPIRS-InterPlatform")
system2.add_platform(platform_X)
system2.add_platform(platform_Y)

print("\n Système créé :")
print(json.dumps(system2.status(), indent=6))

pause("Définir le profil utilisateur Bob...")

mourad = UserProfile(
    name="Mourad",
    preferred_categories=["databases", "cloud"],
    keywords_of_interest=["database", "NoSQL", "distributed", "cloud", "kubernetes"],
)
print(f"""
     Profil utilisateur :
     Nom        : {mourad.name}
     Catégories : {mourad.preferred_categories}
     Intérêts   : {mourad.keywords_of_interest}
""")

pause("Lancer l'agent acheteur mobile (inter-platform)...")

print("\n L'agent démarre et migre entre les plateformes...\n")
results2 = system2.search(
    query          = "distributed database NoSQL",
    user_profile   = mourad,
    max_results    = 4,
    migration_mode = MigrationMode.INTER_PLATFORM,
)

pause("Afficher le journal de migration...")
print_migration_log(system2)

pause("Afficher les résultats personnalisés pour Bob...")
print_results(results2, "Résultats pour Bob  (inter-platform)")


# ══════════════════════════════════════════════════════════════════════
#  FIN
# ══════════════════════════════════════════════════════════════════════
print(f"\n{DIVIDER}")
print(" Démonstration terminée.")
print(f"{DIVIDER}\n")
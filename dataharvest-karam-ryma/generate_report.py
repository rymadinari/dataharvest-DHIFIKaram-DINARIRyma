# -*- coding: utf-8 -*-
"""Genere le rapport technique DataHarvest en PDF (reportlab/platypus)."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, ListFlowable, ListItem
)
from reportlab.lib import colors

OUT_PATH = "output/rapport_technique.pdf"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="H1", fontSize=16, leading=20, spaceAfter=14, spaceBefore=6, fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name="H2", fontSize=13, leading=17, spaceAfter=10, spaceBefore=14, fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name="H3", fontSize=11.5, leading=15, spaceAfter=8, spaceBefore=10, fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name="BodyJustify", parent=styles["Normal"], fontSize=10.3, leading=14.5, alignment=TA_JUSTIFY, spaceAfter=8))
styles.add(ParagraphStyle(name="TODO", parent=styles["Normal"], fontSize=10.3, leading=14.5, alignment=TA_JUSTIFY,
                           spaceAfter=8, textColor=colors.HexColor("#B00000"), fontName="Helvetica-Oblique"))
styles.add(ParagraphStyle(name="CoverTitle", fontSize=26, leading=32, alignment=TA_CENTER, spaceAfter=10, fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name="CoverSub", fontSize=13, leading=18, alignment=TA_CENTER, spaceAfter=6))

def P(text, style="BodyJustify"):
    return Paragraph(text, styles[style])

def TODO(text):
    return Paragraph("[A COMPLETER PAR LE BINOME] " + text, styles["TODO"])

story = []

# ------------------------------------------------------------------ #
# Page de garde
# ------------------------------------------------------------------ #
story.append(Spacer(1, 6*cm))
story.append(P("DataHarvest", "CoverTitle"))
story.append(P("Rapport technique", "CoverSub"))
story.append(Spacer(1, 2*cm))
story.append(P("Prenom1 NOM1 &amp; Prenom2 NOM2", "CoverSub"))
story.append(P("Master Dev, Data &amp; IA -- 4e annee -- IPSSI", "CoverSub"))
story.append(P("Projet final Web Scraping -- [DATE]", "CoverSub"))
story.append(PageBreak())

# ------------------------------------------------------------------ #
# 1. Introduction et perimetre
# ------------------------------------------------------------------ #
story.append(P("1. Introduction et perimetre", "H1"))

story.append(P(
    "DataHarvest repond a un probleme recurrent du scraping artisanal : chaque nouveau site necessite, "
    "en general, un script dedie qui melange requete HTTP, parsing et sauvegarde dans un seul fichier. "
    "Ce couplage rend le code difficile a tester, a faire evoluer et a reutiliser d'un projet a l'autre. "
    "DataHarvest propose l'inverse : un coeur generique (fetch, parse, valide, stocke) pilote entierement "
    "par un fichier de configuration declaratif. Ajouter un nouveau site revient a ecrire un fichier YAML "
    "de selecteurs CSS, jamais une ligne de code Python.", "BodyJustify"
))

story.append(P("Perimetre volontairement exclu", "H3"))
story.append(P(
    "DataHarvest cible exclusivement les sites HTML statiques accessibles via une simple requete GET. "
    "Le rendu JavaScript cote client (sites en React/Vue sans SSR), l'authentification par formulaire, "
    "le defilement infini et l'execution asynchrone sont hors perimetre : ils demanderaient soit un moteur "
    "de rendu (Selenium/Playwright), soit une architecture evenementielle (asyncio/Twisted) qui aurait "
    "complexifie chaque composant pour un gain hors sujet dans le temps imparti (5 heures).", "BodyJustify"
))

story.append(P("Sites choisis pour les tests", "H3"))
story.append(P(
    "Cinq sites ont ete retenus pour couvrir trois niveaux de difficulte differents et des structures HTML "
    "variees : books.toscrape.com et quotes.toscrape.com (niveau 1, sites d'entrainement, structure "
    "previsible), pypi.org/search et fr.openfoodfacts.org (niveau 2, donnees publiques avec pagination "
    "par parametre de requete), et blogdumoderateur.com (niveau 3, media d'actualite avec pagination par "
    "chemin d'URL et selecteurs imbriques). Ce choix permet de verifier que le meme framework s'adapte "
    "a des schemas de pagination differents (chemin vs parametre de requete) sans modification du code.", "BodyJustify"
))
story.append(TODO(
    "Preciser ici, une fois le scraping reellement execute, les eventuelles difficultes rencontrees par "
    "site (ex : selecteur CSS a corriger apres inspection DevTools, structure differente de celle prevue)."
))

story.append(PageBreak())

# ------------------------------------------------------------------ #
# 2. Architecture et choix de conception
# ------------------------------------------------------------------ #
story.append(P("2. Architecture et choix de conception", "H1"))

story.append(P("2.1 Pourquoi une architecture en composants decouples ?", "H2"))
story.append(P(
    "Un script monolithique fonctionne pour un site, mais chaque site suivant oblige a copier-coller et "
    "adapter le meme code : la logique de retry, le parsing, la deduplication se retrouvent dupliques et "
    "divergent silencieusement au fil du temps. En decoupant DataHarvest en cinq composants "
    "independants (Config, Fetcher, Pipeline, Validator, Store), chaque brique a une responsabilite unique "
    "et un contrat d'interface stable :", "BodyJustify"
))
story.append(ListFlowable([
    ListItem(P("Testabilite : chaque composant se teste isolement avec des entrees/sorties simples "
               "(un dict, une liste, une chaine HTML), sans avoir a monter tout le pipeline ni a "
               "faire de vraies requetes reseau (voir tests/test_fetcher.py, entierement mocke).", "BodyJustify")),
    ListItem(P("Extensibilite : ajouter un backend de stockage (ex : PostgreSQL) ne touche que "
               "store.py ; ajouter un middleware ne touche que middleware.py. Aucun autre fichier "
               "n'a besoin d'etre modifie.", "BodyJustify")),
    ListItem(P("Lisibilite : un fichier de moins de 150 lignes avec une seule responsabilite se lit "
               "et se relit plus vite qu'un script de 800 lignes qui fait tout.", "BodyJustify")),
], bulletType="bullet", leftIndent=14))

story.append(P("2.2 Pourquoi BasePipeline est une ABC et non une classe a methodes vides ?", "H2"))
story.append(P(
    "Une classe normale avec des methodes qui ne font rien (`def process(self, html): pass`) laisse "
    "l'erreur se produire tres loin de sa cause : si une sous-classe oublie d'implementer next_page_url(), "
    "le bug n'apparait qu'a l'execution, quand l'Orchestrator appelle une methode qui retourne toujours "
    "None silencieusement -- sans jamais lever d'erreur explicite. En heritant d'abc.ABC et en marquant "
    "process() et next_page_url() avec @abstractmethod, Python refuse purement et simplement "
    "d'instancier une sous-classe incomplete : l'erreur remonte des la construction de l'objet, avec un "
    "message explicite (\"Can't instantiate abstract class ... without an implementation for abstract "
    "method\"). C'est exactement ce qui s'est produit pendant le developpement de GenericPipeline, qui "
    "a du recevoir une implementation par defaut de next_page_url() (retournant toujours None) pour "
    "rester instanciable, PaginationPipeline la surchargeant ensuite avec la vraie logique. La garantie "
    "apportee a l'utilisateur du framework est donc contractuelle plutot que documentaire : le contrat "
    "d'interface est verifie par l'interpreteur, pas seulement suggere par un commentaire.", "BodyJustify"
))

story.append(P("2.3 Pourquoi le pattern middleware pour le Fetcher ?", "H2"))
story.append(P(
    "Le meme mecanisme est utilise par Django et Flask pour intercepter requetes/reponses sans modifier "
    "le coeur du framework. Applique au Fetcher, il permet d'ajouter logging, retry ou rate-limiting "
    "comme des briques independantes, activables ou non selon la config, sans jamais toucher a "
    "fetch(). Sans ce pattern, gerer le retry aurait oblige a coder le backoff exponentiel directement "
    "dans fetch(), en melangeant logique de telechargement et politique de resilience dans la meme "
    "methode -- rendant impossible de tester la logique de retry independamment d'une vraie requete "
    "HTTP. Avec RetryMiddleware isole, les tests (tests/test_middleware.py) verifient le calcul du "
    "delai exponentiel et la decision de retry en pur Python, sans mock reseau.", "BodyJustify"
))

story.append(P("2.4 Pourquoi la configuration via YAML plutot que des arguments CLI ?", "H2"))
story.append(P(
    "Un fichier de configuration YAML capture un etat complet et versionnable : les selecteurs CSS, les "
    "regles de pagination, les parametres de fetch, tout se relit et se modifie sans relancer une longue "
    "commande. C'est aussi la seule option raisonnable des qu'un site necessite plus de trois ou quatre "
    "champs de selecteurs -- une commande CLI avec vingt options `--selector-titre`, `--selector-prix`, "
    "etc. deviendrait illisible. A l'inverse, les arguments CLI restent preferables pour des parametres "
    "ponctuels qui ne meritent pas d'etre persistes (ex : --dry-run, le chemin d'export). DataHarvest "
    "applique cette distinction : la configuration structurelle du scraping vit en YAML, les options "
    "d'execution ponctuelles vivent en CLI.", "BodyJustify"
))

story.append(P("2.5 Pourquoi l'injection de dependances plutot que des imports directs ?", "H2"))
story.append(P(
    "Si Fetcher importait directement `from .middleware import RetryMiddleware` et l'instanciait "
    "lui-meme en interne, il serait impossible de tester fetch() sans declencher le vrai comportement "
    "de retry (attentes reelles, vraies exceptions requests). En recevant sa liste de middlewares au "
    "constructeur (`Fetcher(config, middlewares=[...])`), le Fetcher ne connait que l'interface "
    "BaseMiddleware, jamais une implementation concrete. Concretement, tests/test_fetcher.py "
    "instancie un Fetcher avec une session mockee et un RetryMiddleware a base_delay=0.0 pour que "
    "le test s'execute en quelques millisecondes au lieu d'attendre reellement le backoff exponentiel "
    "-- ce qui serait impossible si Fetcher construisait lui-meme son RetryMiddleware avec des valeurs "
    "figees.", "BodyJustify"
))
story.append(P(
    "Le meme raisonnement s'applique a l'Orchestrator lui-meme : il recoit un objet Config deja charge "
    "et valide, plutot que de charger un chemin de fichier en interne. Un test unitaire peut ainsi "
    "construire une Config a partir d'un fichier temporaire (voir tests/test_integration.py, fixture "
    "_make_config) et l'injecter dans un Orchestrator dont on mocke ensuite uniquement la methode "
    "fetch() du Fetcher -- isolant completement le test de toute dependance reseau tout en exercant "
    "l'integralite de la logique metier (pagination, validation, deduplication, comptage du rapport de "
    "session).", "BodyJustify"
))

story.append(P("2.6 Flux de donnees et gestion des erreurs", "H2"))
story.append(P(
    "L'Orchestrator centralise deliberement toute la gestion des erreurs de haut niveau : si le "
    "Fetcher leve une FetchError (retries epuises), la boucle de pagination s'arrete proprement et "
    "retourne un rapport partiel plutot que de laisser l'exception remonter et interrompre brutalement "
    "le processus -- une session qui a scrape 3 pages sur 5 avant qu'un site ne devienne inaccessible "
    "doit conserver les items deja stockes plutot que tout perdre. A l'inverse, les erreurs de plus bas "
    "niveau (un selecteur CSS qui ne matche rien, un champ manquant) ne remontent jamais d'exception : "
    "GenericPipeline retourne une chaine vide pour un champ absent, et Validator se contente de rejeter "
    "l'item concerne en le loggant. Cette distinction -- erreurs bloquantes au niveau reseau, erreurs "
    "tolerees au niveau extraction -- reflete le fait qu'un HTML imparfait est la norme du web reel, "
    "alors qu'un site inaccessible est une condition d'arret legitime.", "BodyJustify"
))

story.append(P("2.7 Convention de nommage des champs dans la Pipeline", "H2"))
story.append(P(
    "GenericPipeline applique une convention plutot qu'une configuration explicite pour determiner "
    "quelle partie d'un tag HTML extraire : le champ nomme 'url' recupere l'attribut href d'un lien, "
    "un tag possedant un attribut datetime le retourne tel quel (utile pour les balises &lt;time&gt;), "
    "et tout le reste recupere le texte visible. Cette approche minimise la verbosite des fichiers de "
    "configuration (un simple selecteur CSS par champ, comme impose par le sujet), au prix d'une regle "
    "implicite qu'il faut documenter clairement pour l'utilisateur du framework -- c'est l'objet de la "
    "section 5.2 de ce rapport, qui revient sur les limites de ce choix.", "BodyJustify"
))

story.append(P("2.8 Compromis architecturaux assumes", "H2"))
story.append(P(
    "Toute architecture est un choix de compromis, pas une solution neutre. Trois decisions meritent "
    "d'etre assumees explicitement plutot que presentees comme allant de soi.", "BodyJustify"
))
story.append(ListFlowable([
    ListItem(P("Couplage volontaire dans l'Orchestrator : contrairement aux quatre autres composants, "
               "l'Orchestrator connait et instancie directement Fetcher, Pipeline, Validator et Store. "
               "Ce couplage centralise est assume : quelqu'un doit assembler le systeme, et le "
               "concentrer dans un seul point d'entree evite de disperser la logique d'assemblage "
               "(quel middleware avec quel Fetcher, quelle Pipeline avec quelle config) a travers "
               "plusieurs fichiers.", "BodyJustify")),
    ListItem(P("Pas de cache de requetes : chaque execution de crawl() retelecharge integralement "
               "les pages, y compris celles deja visitees lors d'une session precedente. Un cache "
               "(par exemple base sur le hash de l'URL et un TTL configurable) reduirait la charge sur "
               "le site cible mais complexifierait Fetcher avec une nouvelle responsabilite -- "
               "juge hors scope pour la duree du projet.", "BodyJustify")),
    ListItem(P("Validation binaire plutot que graduee : Validator classe chaque item en valide ou "
               "rejete, sans notion de score de confiance intermediaire. Un item avec un titre "
               "legerement trop court est rejete au meme titre qu'un item completement vide, ce qui "
               "simplifie l'implementation mais perd une information potentiellement utile pour "
               "affiner les selecteurs CSS a posteriori.", "BodyJustify")),
], bulletType="bullet", leftIndent=14))

story.append(PageBreak())

# ------------------------------------------------------------------ #
# 3. Comparaison avec Scrapy
# ------------------------------------------------------------------ #
story.append(P("3. Comparaison avec Scrapy", "H1"))

story.append(P("3.1 Fonctionnalites de Scrapy absentes de DataHarvest", "H2"))

scrapy_table_data = [
    ["Fonctionnalite Scrapy", "Raison de l'absence dans DataHarvest"],
    ["Moteur asynchrone (Twisted/asyncio)",
     "Hors scope pour 5h de developpement : reecrire Fetcher et Orchestrator en "
     "asynchrone aurait multiplie la complexite (gestion des coroutines, "
     "synchronisation du Store) pour un gain de performance non prioritaire "
     "sur un projet pedagogique."],
    ["Middleware de gestion des cookies/sessions avancee",
     "requests.Session() couvre les besoins de base (persistance des cookies) ; "
     "la gestion fine (rotation de sessions, cookies par domaine) est hors scope."],
    ["Item pipelines chainables avec priorites",
     "DataHarvest a une seule Pipeline par config ; le chainage de plusieurs "
     "etapes de traitement (nettoyage, enrichissement, export multiple) "
     "n'a pas ete implemente faute de temps, bien que l'architecture le "
     "permettrait facilement (liste de pipelines au lieu d'une seule)."],
    ["Middleware de rotation de proxies/User-Agent",
     "Complexite d'implementation (pool de proxies, detection de bannissement) "
     "hors scope pour la duree du projet."],
    ["Scrapy Shell (console interactive de test des selecteurs)",
     "Outil de productivite important mais independant du coeur fonctionnel : "
     "priorite donnee aux composants metier plutot qu'a l'outillage annexe."],
]
t = Table(scrapy_table_data, colWidths=[6*cm, 10.5*cm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2b2b2b")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8.7),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
]))
story.append(t)
story.append(Spacer(1, 12))

story.append(P("3.2 Quand preferer DataHarvest a Scrapy ?", "H2"))
story.append(P(
    "Scenario 1 -- prototypage rapide sur un site unique : un data analyst qui doit extraire "
    "ponctuellement les prix d'un catalogue pour une etude, sans investir dans l'apprentissage du "
    "framework Scrapy (spiders, settings.py, items.py, pipelines.py), prefere ecrire un fichier YAML "
    "de vingt lignes et lancer une commande. Scenario 2 -- integration dans un pipeline data existant "
    "deja synchrone : une equipe qui alimente deja un ETL en Python synchrone (pandas, SQLAlchemy) "
    "integre plus simplement DataHarvest, dont l'API `Orchestrator.run() -> dict` s'appelle comme une "
    "fonction Python ordinaire, sans avoir a faire cohabiter une boucle d'evenements Twisted avec le "
    "reste du pipeline.", "BodyJustify"
))

story.append(P("3.3 Impact du synchrone vs asynchrone : calcul theorique", "H2"))
story.append(P(
    "Avec DOWNLOAD_DELAY=1s, scraper 100 pages en synchrone (DataHarvest, une requete a la fois) prend "
    "au minimum 100 x 1s = 100 secondes, plus le temps de reponse reseau de chaque page (a titre "
    "d'exemple 0,3s en moyenne), soit environ 130 secondes. Scrapy, avec CONCURRENT_REQUESTS=16 "
    "(valeur par defaut) et le meme delai applique par domaine plutot que par requete individuelle, "
    "peut traiter jusqu'a 16 pages en parallele : le temps total se rapproche de "
    "100 / 16 x (1s + 0,3s) &asymp; 8,1 secondes, soit un gain d'environ 16x sur ce scenario. "
    "L'ecart se creuse encore si le site cible autorise un DOWNLOAD_DELAY plus faible ou si le nombre "
    "de pages augmente : le temps de DataHarvest croit lineairement avec le nombre de pages, celui de "
    "Scrapy croit lineairement avec (nombre de pages / concurrence).", "BodyJustify"
))
story.append(P(
    "Ce calcul reste theorique : en pratique, la concurrence de Scrapy est plafonnee par "
    "CONCURRENT_REQUESTS_PER_DOMAIN (8 par defaut), ce qui evite de saturer un seul serveur cible meme "
    "avec CONCURRENT_REQUESTS=16 global reparti sur plusieurs domaines. Sur un scraping mono-domaine "
    "comme les cas d'usage de ce projet, le gain reel se rapproche donc davantage d'un facteur 8 que 16. "
    "Il faut aussi noter que le gain de Scrapy ne se paie pas seulement en complexite de code : il "
    "augmente aussi la charge instantanee imposee au serveur cible, ce qui rejoint la question du cadre "
    "ethique traitee en section 4 -- une politique de delai respectueuse (DOWNLOAD_DELAY, "
    "AUTOTHROTTLE) reste necessaire independamment du framework utilise.", "BodyJustify"
))

story.append(P("3.4 Courbe d'apprentissage et cout d'entree", "H2"))
story.append(P(
    "Au-dela de la performance brute, le cout d'entree different des deux outils merite d'etre "
    "compare. Scrapy impose ses propres conventions (structure de projet generee par scrapy startproject, "
    "classes Spider avec des methodes de callback, settings.py centralisant des dizaines d'options) : "
    "un developpeur doit assimiler ce vocabulaire avant de pouvoir ecrire son premier spider fonctionnel. "
    "DataHarvest, plus modeste, repose sur des concepts deja familiers a tout developpeur Python "
    "(classes, ABC, dictionnaires) et un fichier de configuration dont la structure se comprend en "
    "quelques minutes de lecture. Ce moindre cout d'entree se paie en retour par l'absence des "
    "fonctionnalites avancees listees en 3.1 : DataHarvest est delibere pour couvrir 80% des besoins "
    "de scraping simple avec 20% de la complexite d'apprentissage de Scrapy, plutot que de viser "
    "l'exhaustivite fonctionnelle.", "BodyJustify"
))

story.append(PageBreak())

# ------------------------------------------------------------------ #
# 4. Cadre legal et ethique
# ------------------------------------------------------------------ #
story.append(P("4. Cadre legal et ethique", "H1"))

story.append(P("4.1 Analyse du robots.txt", "H2"))
story.append(TODO(
    "Consulter reellement https://www.blogdumoderateur.com/robots.txt (et le robots.txt de chaque "
    "site retenu) avant la restitution, lister les chemins Disallow rencontres, et confirmer explicitement "
    "que les URLs scrapees par vos configs ne figurent pas dans ces chemins interdits. Documenter ici "
    "le resultat (capture d'ecran ou extrait du fichier accepte)."
))

story.append(P("4.2 Base legale RGPD (article 6)", "H2"))
story.append(P(
    "L'article 6 du RGPD exige une base legale pour tout traitement de donnees a caractere personnel. "
    "Dans le cas des sites retenus pour ce projet (catalogues de livres, citations, paquets logiciels, "
    "produits alimentaires, articles de blog), les donnees collectees sont majoritairement des donnees "
    "publiques a caractere non personnel (prix, titres, descriptions techniques). Lorsque des donnees "
    "pourraient toucher des personnes physiques identifiables (ex : nom d'auteur sur quotes.toscrape.com, "
    "nom de mainteneur de paquet sur pypi.org), la base legale mobilisable est l'interet legitime "
    "(article 6.1.f) : la collecte poursuit un objectif pedagogique et de recherche documentee, "
    "proportionne, sans profilage ni reutilisation commerciale, et les donnees en question sont deja "
    "rendues publiques par la personne elle-meme ou par l'organisation qui les publie.", "BodyJustify"
))

story.append(P("4.3 Les donnees collectees sont-elles des donnees personnelles ?", "H2"))
story.append(P(
    "Au sens de l'article 4.1 du RGPD, une donnee personnelle est toute information se rapportant a une "
    "personne physique identifiee ou identifiable. Les prix de livres, notes, categories ou tags collectes "
    "sur books.toscrape.com et quotes.toscrape.com ne se rapportent a aucune personne. Le nom d'auteur "
    "affiche sur une citation (quotes.toscrape.com) ou le nom d'un mainteneur de paquet Python "
    "(pypi.org) peuvent en revanche constituer une donnee a caractere personnel si la personne est "
    "identifiable a partir de ce seul nom -- meme lorsqu'il s'agit d'un pseudonyme professionnel deja "
    "public. DataHarvest ne collecte cependant aucune donnee de contact, de profil ou de comportement "
    "associee a ces noms, ce qui limite fortement le risque pour les personnes concernees.", "BodyJustify"
))

story.append(P("4.4 Mecanismes techniques de 'bon citoyen du web'", "H2"))
story.append(ListFlowable([
    ListItem(P("Throttling configurable : config.fetcher.delay applique entre chaque requete "
               "(fetch_all()), et RateLimitMiddleware garantit un delai minimum par domaine meme "
               "en cas d'appels concurrents.", "BodyJustify")),
    ListItem(P("User-Agent identifiable et contactable : chaque config utilise "
               "\"DataHarvest/1.0 (+contact@ipssi.fr)\", jamais le User-Agent par defaut de la "
               "librairie requests, permettant a l'administrateur du site cible d'identifier et de "
               "contacter l'origine du trafic.", "BodyJustify")),
    ListItem(P("Contrainte UNIQUE(url) en base : le backend sqlite refuse les doublons par URL "
               "(INSERT OR IGNORE), evitant de re-solliciter inutilement le site pour des donnees "
               "deja collectees lors d'executions successives.", "BodyJustify")),
    ListItem(P("Retries bornes avec backoff exponentiel : RetryMiddleware limite le nombre "
               "de tentatives (max_retries configurable) et espace les nouvelles requetes "
               "exponentiellement plutot que de marteler un serveur qui repond deja en erreur "
               "(429/5xx).", "BodyJustify")),
], bulletType="bullet", leftIndent=14))

story.append(PageBreak())

# ------------------------------------------------------------------ #
# 5. Difficultes et retrospective
# ------------------------------------------------------------------ #
story.append(P("5. Difficultes et retrospective", "H1"))

story.append(P("5.1 Difficulte technique principale", "H2"))
story.append(P(
    "La difficulte la plus structurante a ete la conception de GenericPipeline._extract_value : "
    "extraire une valeur depuis un tag BeautifulSoup selon une convention generique valable pour tous "
    "les sites (texte visible par defaut, attribut href pour le champ 'url', attribut datetime quand il "
    "est present) sans coder de cas particulier par site. Une premiere version extrayait le href des que "
    "le tag matche etait un &lt;a&gt;, quel que soit le champ vise -- ce qui cassait des qu'un meme "
    "selecteur CSS (ex : 'h2.title a') etait reutilise a la fois pour le champ 'titre' (on veut le texte) "
    "et le champ 'url' (on veut le href). La correction a consiste a faire dependre l'extraction du nom "
    "du champ plutot que du seul type de tag rencontre.", "BodyJustify"
))
story.append(TODO(
    "Completer avec vos propres difficultes rencontrees pendant le developpement (ex : ajustement des "
    "selecteurs CSS sur les vrais sites, configuration Git, gestion des conflits de merge)."
))

story.append(P("5.2 Ce qui serait fait differemment", "H2"))
story.append(P(
    "L'extraction de valeur par convention de nommage de champ (section 5.1) reste fragile : elle "
    "suppose implicitement qu'un champ nomme 'url' pointe toujours vers un &lt;a href&gt;. Une version "
    "future gagnerait a expliciter le type d'extraction dans la config elle-meme (ex : "
    "`url: {selector: 'h2.title a', attr: 'href'}` plutot qu'une simple chaine), rendant le comportement "
    "visible dans le YAML plutot qu'implicite dans le code Python.", "BodyJustify"
))

story.append(P("5.3 Fonctionnalite non implementee faute de temps", "H2"))
story.append(P(
    "Le RateLimitMiddleware (extension bonus) est implemente et teste au niveau unitaire, mais "
    "l'Orchestrator ne l'active pas par defaut dans sa chaine de middlewares -- seuls "
    "LoggingMiddleware et RetryMiddleware y sont instancies en dur. Une implementation complete "
    "rendrait la liste de middlewares elle-meme configurable depuis le YAML (ex : une cle "
    "`fetcher.middlewares: [logging, retry, rate_limit]`), permettant d'activer ou desactiver chaque "
    "brique sans modifier orchestrator.py.", "BodyJustify"
))

story.append(P("5.4 Repartition des taches", "H2"))
story.append(TODO(
    "Documenter ici la repartition reelle du binome (qui a code quoi) et confirmer qu'elle est visible "
    "dans l'historique Git (git log --oneline --author=\"...\"). Le planning suggere par le sujet "
    "(section 9) propose une repartition Etudiant A / Etudiant B par sprint (Config vs Middleware, "
    "Pipeline vs Validator, Orchestrator vs CLI) : indiquer si elle a ete suivie telle quelle ou adaptee."
))

story.append(PageBreak())

# ------------------------------------------------------------------ #
# 6. Perspectives
# ------------------------------------------------------------------ #
story.append(P("6. Perspectives", "H1"))

story.append(P("6.1 Une sixieme brique : Notifier", "H2"))
story.append(P(
    "Un composant Notifier completerait naturellement le flux de l'Orchestrator en envoyant une alerte "
    "(email, webhook Slack/Discord) a la fin de chaque session de scraping, notamment en cas d'echec ou "
    "de chute anormale du nombre d'items collectes par rapport aux executions precedentes -- un signal "
    "frequent de changement de structure HTML sur le site cible.", "BodyJustify"
))
story.append(Paragraph(
    "class BaseNotifier(ABC):<br/>"
    "&nbsp;&nbsp;&nbsp;&nbsp;@abstractmethod<br/>"
    "&nbsp;&nbsp;&nbsp;&nbsp;def notify(self, report: dict) -&gt; None:<br/>"
    "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\"\"\"Envoie le rapport de session (report) vers un canal externe.\"\"\"<br/><br/>"
    "class EmailNotifier(BaseNotifier):<br/>"
    "&nbsp;&nbsp;&nbsp;&nbsp;def __init__(self, smtp_config: dict, recipients: list[str]):<br/>"
    "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;...<br/>"
    "&nbsp;&nbsp;&nbsp;&nbsp;def notify(self, report: dict) -&gt; None:<br/>"
    "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if report['items_stockes'] &lt; report.get('seuil_alerte', 0):<br/>"
    "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self._send_email(...)",
    ParagraphStyle(name="Code", parent=styles["Normal"], fontName="Courier", fontSize=8.5,
                   leading=12, backColor=colors.HexColor("#f2f2f2"), borderPadding=8, spaceAfter=10)
))
story.append(P(
    "Comme les autres composants, Notifier s'injecterait dans l'Orchestrator au constructeur "
    "(`Orchestrator(config, notifiers=[EmailNotifier(...)])`), sans creer de dependance directe entre "
    "orchestrator.py et une implementation concrete de notification.", "BodyJustify"
))

story.append(P("6.2 Compatibilite avec les sites JavaScript sans Selenium", "H2"))
story.append(P(
    "Selenium pilote un navigateur complet, ce qui le rend lourd (process navigateur dedie, lenteur, "
    "consommation memoire). Deux alternatives plus legeres existent : Playwright, qui offre une API "
    "similaire a Selenium mais avec un mode headless plus performant et un support natif de "
    "l'attente d'elements ; et le pre-rendu via un service comme Splash (rendu HTML apres execution "
    "JS, expose comme une simple API HTTP interrogeable par le Fetcher existant sans le modifier). "
    "Concretement, DataHarvest pourrait ajouter un `PlaywrightFetcher` implementant la meme interface "
    "que `Fetcher` (une methode fetch(url) -&gt; str), permettant a l'Orchestrator de choisir dynamiquement "
    "le fetcher a utiliser selon un champ `fetcher.engine: requests|playwright` dans la config -- sans "
    "modifier Pipeline, Validator ni Store.", "BodyJustify"
))

story.append(P("6.3 Distribution sur PyPI", "H2"))
story.append(P(
    "Publier DataHarvest sur PyPI necessiterait : un fichier pyproject.toml declarant les metadonnees "
    "du paquet (nom, version, dependances, point d'entree CLI via `[project.scripts]`) ; le retrait de "
    "tout chemin absolu ou relatif code en dur (le CLI doit fonctionner depuis n'importe quel repertoire "
    "de travail) ; une couverture de tests etendue aux cas limites non couverts par le present rapport "
    "(encodages non-UTF-8, HTML malforme) ; une politique de versionnement semantique explicite ; et "
    "un packaging verifie via `python -m build` puis `twine upload` vers PyPI, apres tests sur TestPyPI.", "BodyJustify"
))

story.append(PageBreak())

# ------------------------------------------------------------------ #
# Bibliographie
# ------------------------------------------------------------------ #
story.append(P("Bibliographie / Sources", "H1"))
story.append(ListFlowable([
    ListItem(P("Documentation officielle Scrapy -- https://docs.scrapy.org/", "BodyJustify")),
    ListItem(P("Documentation officielle Requests -- https://requests.readthedocs.io/", "BodyJustify")),
    ListItem(P("Documentation officielle Beautiful Soup 4 -- https://www.crummy.com/software/BeautifulSoup/bs4/doc/", "BodyJustify")),
    ListItem(P("Reglement General sur la Protection des Donnees (RGPD), articles 4 et 6 -- https://eur-lex.europa.eu/eli/reg/2016/679/oj", "BodyJustify")),
    ListItem(P("Documentation Playwright pour Python -- https://playwright.dev/python/", "BodyJustify")),
    ListItem(P("PEP 517 / packaging.python.org -- guide de publication d'un paquet sur PyPI", "BodyJustify")),
]))
story.append(TODO(
    "Ajouter toute autre source effectivement consultee (articles, RFC, pages robots.txt des sites "
    "cibles) au moment de la redaction finale."
))

doc = SimpleDocTemplate(
    OUT_PATH, pagesize=A4,
    leftMargin=2.2*cm, rightMargin=2.2*cm, topMargin=2*cm, bottomMargin=2*cm,
    title="DataHarvest -- Rapport technique",
)
doc.build(story)
print("OK ->", OUT_PATH)

from datetime import time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import FooterLink, SiteSettings
from pages.models import BoardMember, HistoryEntry, HomeFeature, HomeMetric, HomePage, Page, PageType
from programs.models import Instructor, PricingBlock, Program, ProgramCategory, ProgramSchedule, ProgramSession
from stories.models import Story, StoryAttachment, StoryType


LEGACY_PROGRAM_CATEGORY_SLUGS = {"music", "dance", "arts", "clubs"}


class Command(BaseCommand):
    help = "Зарежда неутрално начално съдържание за публичния сайт."

    def handle(self, *args, **options):
        self.seed_site_settings()
        self.seed_home_page()
        categories = self.seed_categories()
        instructors = self.seed_instructors()
        self.seed_programs(categories, instructors)
        self.seed_projects()
        self.seed_pages()
        self.seed_history_entries()
        self.seed_board_members()
        self.seed_footer_links()
        self.seed_sessions()
        self.stdout.write(self.style.SUCCESS("Примерното съдържание е готово."))

    def seed_site_settings(self):
        if SiteSettings.objects.exists():
            return
        SiteSettings.objects.create(
            site_name='Народно читалище „Св. св. Кирил и Методий – 1926“',
            site_tagline="Културни програми, общностни инициативи и ясно подредена публична информация.",
            footer_summary=(
                "Сайтът обединява програми, публикации, контакти и правна информация "
                "в структура, която може да се поддържа изцяло от администрацията."
            ),
            address_line="кв. Враждебна, ул. „8-ма“ 47",
            city="София",
            postal_code="1839",
            phone_primary="087 782 0388",
            phone_secondary="",
            email="chitalishtevrajdebna@gmail.com",
            contact_page_title="Контакти",
            contact_page_intro="",
            contact_page_hours_label="Работно време",
            contact_page_map_label="Карта за разположение:",
            contact_page_form_heading="За да изпратите съобщение, моля попълнете формата:",
            contact_page_submit_label="Изпрати запитване",
            contact_page_privacy_note="Ще използваме данните ви само за обработка на това запитване.",
            contact_page_success_message=(
                "Благодарим. Съобщението ви беше изпратено успешно и ще се свържем с вас при възможност."
            ),
            location_name="Основна база",
            location_short_description="Главна читалищна сграда за административно обслужване, уроци и малки събития.",
            working_hours_summary="Понеделник - петък, 09:00 - 18:00",
            map_embed_url=(
                "https://www.openstreetmap.org/export/embed.html?bbox=23.311%2C42.688%2C23.335%2C42.703&layer=mapnik"
            ),
            location_access_notes="Достъп от улица и асансьор до втория етаж.",
        )

    def seed_home_page(self):
        home_page, _ = HomePage.objects.get_or_create(
            pk=1,
            defaults={
                "hero_badge": "КУЛТУРА И ОБЩНОСТ",
                "hero_title": "Програми, новини и обществена дейност в една подредена читалищна платформа.",
                "hero_body": (
                    "Публичната част показва как могат да бъдат организирани програми, "
                    "новини, контакти и записвания, когато редакторската работа минава през администрацията."
                ),
                "primary_cta_label": "Вижте програмите",
                "primary_cta_url": "/programs/",
                "secondary_cta_label": "Отворете контактите",
                "secondary_cta_url": "/contact/",
                "mission_title": "Култура, образование и достъпност",
                "mission_body": (
                    "Платформата комбинира школа по изкуства, пространство за местни инициативи "
                    "и ясна информационна архитектура за родители, участници и партньори."
                ),
                "programs_heading": "Школи и клубове",
                "programs_intro": "Категории, преподаватели, графици, цени и форма за записване.",
                "stories_heading": "Новини",
                "stories_intro": "Всички публикации са събрани в един общ архив.",
                "contacts_heading": "Контакти, работно време и запитвания",
                "contacts_intro": "Контактната зона обединява адрес, работно време и форма за директно запитване.",
            },
        )
        if not home_page.stats.exists():
            HomeMetric.objects.bulk_create(
                [
                    HomeMetric(home_page=home_page, value="8", label="Активни програми", description="Музика, танц, визуални изкуства и клубове.", sort_order=1),
                    HomeMetric(home_page=home_page, value="1", label="Основна локация", description="Адресът и картата се поддържат от глобалните настройки.", sort_order=2),
                    HomeMetric(home_page=home_page, value="1", label="Обща администрация", description="Публичното съдържание се поддържа от единна редакторска среда.", sort_order=3),
                ]
            )
        if not home_page.features.exists():
            HomeFeature.objects.bulk_create(
                [
                    HomeFeature(home_page=home_page, eyebrow="Структура", title="Програми с детайли", description="Всяка програма има категория, инструктори, график, цени, галерия и записване.", sort_order=1),
                    HomeFeature(home_page=home_page, eyebrow="Публикации", title="Новини", description="Публикациите могат да съдържат прикачени файлове и да работят като архив.", sort_order=2),
                    HomeFeature(home_page=home_page, eyebrow="Обслужване", title="Контакти и правни страници", description="Контактната зона събира адрес, работно време и политики за поверителност.", sort_order=3),
                ]
            )

    def seed_categories(self):
        category_specs = [
            ("kids", "Деца", "Школи, ателиета и клубове за деца и ученици.", 1),
            ("adults", "Възрастни", "Курсове, клубове и занимания за възрастни участници.", 2),
        ]
        categories = {}
        for slug, name, description, order in category_specs:
            category, created = ProgramCategory.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "description": description, "sort_order": order},
            )
            if not created:
                changed_fields = []
                field_values = {
                    "name": name,
                    "description": description,
                    "sort_order": order,
                    "is_published": True,
                }
                for field, value in field_values.items():
                    if getattr(category, field) != value:
                        setattr(category, field, value)
                        changed_fields.append(field)
                if changed_fields:
                    category.save(update_fields=changed_fields)
            categories[slug] = category
        return categories

    def seed_instructors(self):
        instructor_specs = [
            {
                "slug": "mira-petrova",
                "full_name": "Мира Петрова",
                "role_title": "Преподавател по пиано и солфеж",
                "biography": "Работи с начинаещи и напреднали курсисти, като комбинира техника, слухови упражнения и сценична увереност.",
                "credentials": "Магистър по музикална педагогика.",
                "email": "mira@example.bg",
                "phone": "+359 88 111 1111",
                "sort_order": 1,
            },
            {
                "slug": "ivo-stoyanov",
                "full_name": "Иво Стоянов",
                "role_title": "Хореограф и водещ на групи",
                "biography": "Организира занимания за деца и възрастни с фокус върху координация, ритъм и сценично присъствие.",
                "credentials": "Опит в клубна и сценична подготовка.",
                "email": "ivo@example.bg",
                "phone": "+359 88 222 2222",
                "sort_order": 2,
            },
            {
                "slug": "lora-georgieva",
                "full_name": "Лора Георгиева",
                "role_title": "Художник и ръководител на ателие",
                "biography": "Работи върху наблюдателност, композиция и материали чрез практични творчески задачи.",
                "credentials": "Практикуващ художник и водещ на детски работилници.",
                "email": "lora@example.bg",
                "phone": "+359 88 333 3333",
                "sort_order": 3,
            },
        ]
        instructors = {}
        for spec in instructor_specs:
            instructor, _ = Instructor.objects.get_or_create(slug=spec["slug"], defaults=spec)
            instructors[spec["slug"]] = instructor
        return instructors

    def seed_programs(self, categories, instructors):
        program_specs = [
            {
                "slug": "piano-studio",
                "category": categories["kids"],
                "title": "Пиано студио",
                "summary": "Индивидуални уроци по пиано с адаптивен график за деца и възрастни.",
                "description": "Програмата съчетава инструментална техника, четене на ноти и подготовка за малки вътрешни концерти.",
                "audience": "Начинаещи и средно напреднали",
                "duration": "60 минути",
                "age_group": "7+ години",
                "level": "Начално до средно ниво",
                "location_name": "Основна зала",
                "inquiry_phone": "+359 88 101 0101",
                "inquiry_email": "programs@example.bg",
                "sort_order": 1,
                "instructors": [instructors["mira-petrova"]],
                "schedules": [
                    ("Следобедна група", "Понеделник", time(17, 0), time(18, 0), "Студио 2", ""),
                    ("Индивидуални часове", "Сряда", time(18, 30), time(20, 30), "Студио 2", "Часовете се уточняват с преподавател."),
                ],
                "pricing": [
                    ("Пробен урок", "25 лв.", "еднократно", "Подходящо за първо посещение.", False),
                    ("Месечен пакет", "120 лв.", "4 посещения", "Фиксирани часове с приоритет при записване.", True),
                ],
            },
            {
                "slug": "folk-rhythm-lab",
                "category": categories["adults"],
                "title": "Лаборатория за сценичен фолклор",
                "summary": "Групови занимания по ритъм, стъпки и ансамблово движение.",
                "description": "Примерна програма за движение и сценична култура, предназначена за участници с интерес към фолклорни форми и групова работа.",
                "audience": "Деца, младежи и възрастни",
                "duration": "90 минути",
                "age_group": "10+ години",
                "level": "Смесени групи",
                "location_name": "Голяма зала",
                "inquiry_phone": "+359 88 202 0202",
                "inquiry_email": "dance@example.bg",
                "sort_order": 2,
                "instructors": [instructors["ivo-stoyanov"]],
                "schedules": [
                    ("Основна група", "Вторник", time(18, 30), time(20, 0), "Голяма зала", ""),
                    ("Уикенд практика", "Събота", time(11, 0), time(12, 30), "Голяма зала", "Подходящо за нови участници."),
                ],
                "pricing": [
                    ("Единично посещение", "18 лв.", "на посещение", "Гъвкава опция за присъствие.", False),
                    ("Месечен абонамент", "95 лв.", "8 посещения", "Включва участие в открити репетиции.", True),
                ],
            },
            {
                "slug": "drawing-workshop",
                "category": categories["kids"],
                "title": "Ателие по рисуване",
                "summary": "Практически курс по рисунка, композиция и работа с различни материали.",
                "description": "Заниманията са ориентирани към наблюдение, личен стил и развиване на увереност в работата с цвят, линия и форма.",
                "audience": "Деца и младежи",
                "duration": "75 минути",
                "age_group": "8-16 години",
                "level": "Начално ниво",
                "location_name": "Ателие Север",
                "inquiry_phone": "+359 88 303 0303",
                "inquiry_email": "art@example.bg",
                "sort_order": 3,
                "instructors": [instructors["lora-georgieva"]],
                "schedules": [
                    ("Детска група", "Четвъртък", time(17, 30), time(18, 45), "Ателие Север", ""),
                    ("Съботна работилница", "Събота", time(13, 0), time(14, 15), "Ателие Север", "Всички материали са осигурени."),
                ],
                "pricing": [
                    ("Месечен пакет", "88 лв.", "4 посещения", "Материалите са включени.", True),
                    ("Двумесечен пакет", "160 лв.", "8 посещения", "Подходящ за последователна работа.", False),
                ],
            },
            {
                "slug": "kids-music-circle",
                "category": categories["kids"],
                "title": "Музикален кръжок за деца",
                "summary": "Въвеждащи занимания по ритъм, песен и работа в малка група.",
                "description": "Форматът е подходящ за ранно запознаване с музикалния свят чрез игра, движение и слухови упражнения.",
                "audience": "Деца в предучилищна и ранна училищна възраст",
                "duration": "50 минути",
                "age_group": "5-8 години",
                "level": "Начално ниво",
                "location_name": "Малка зала",
                "inquiry_phone": "+359 88 404 0404",
                "inquiry_email": "kids@example.bg",
                "sort_order": 4,
                "instructors": [instructors["mira-petrova"]],
                "schedules": [
                    ("Седмична група", "Петък", time(17, 0), time(17, 50), "Малка зала", ""),
                ],
                "pricing": [
                    ("Месечен пакет", "72 лв.", "4 посещения", "Включва материали за игри и ритъм.", True),
                ],
            },
        ]

        for spec in program_specs:
            schedules = spec.pop("schedules")
            pricing = spec.pop("pricing")
            instructors_list = spec.pop("instructors")
            program, created = Program.objects.get_or_create(slug=spec["slug"], defaults=spec)
            if (
                not created
                and program.category_id != spec["category"].id
                and program.category.slug in LEGACY_PROGRAM_CATEGORY_SLUGS
            ):
                program.category = spec["category"]
                program.save(update_fields=["category", "updated_at"])
            if created and not program.instructors.exists():
                program.instructors.set(instructors_list)
            elif not program.instructors.exists():
                program.instructors.set(instructors_list)
            if not program.schedule_entries.exists():
                for order, entry in enumerate(schedules, start=1):
                    title, day_label, start_time, end_time, room, notes = entry
                    ProgramSchedule.objects.create(
                        program=program,
                        title=title,
                        day_label=day_label,
                        start_time=start_time,
                        end_time=end_time,
                        room=room,
                        notes=notes,
                        sort_order=order,
                    )
            if not program.pricing_options.exists():
                for order, entry in enumerate(pricing, start=1):
                    title, price_label, billing_period, description, is_featured = entry
                    PricingBlock.objects.create(
                        program=program,
                        title=title,
                        price_label=price_label,
                        billing_period=billing_period,
                        description=description,
                        is_featured=is_featured,
                        sort_order=order,
                    )

        ProgramCategory.objects.filter(
            slug__in=LEGACY_PROGRAM_CATEGORY_SLUGS,
            programs__isnull=True,
        ).update(is_published=False)

    def seed_projects(self):
        today = timezone.localdate()
        project_specs = [
            {
                "slug": "open-stage-week",
                "story_type": StoryType.PROJECT,
                "title": "Седмица на отворената сцена",
                "excerpt": "Примерен проект за публични репетиции, ателиета и малки представяния.",
                "body": (
                    "Публикацията обобщава програмата, партньорствата и резултатите от "
                    "седмица с отворени занимания, репетиции и малки представяния."
                ),
                "published_at": today - timedelta(days=20),
            },
            {
                "slug": "library-update-spring",
                "story_type": StoryType.NEWS,
                "title": "Пролетно обновяване на библиотечната зона",
                "excerpt": "Кратка новина за работно време, обновени кътове и нови постъпления.",
                "body": (
                    "Кратък формат за актуализации, важни срокове и служебна информация "
                    "за посетители, участници и партньори."
                ),
                "published_at": today - timedelta(days=8),
            },
            {
                "slug": "community-labs-2026",
                "story_type": StoryType.STORY,
                "title": "Общностни лаборатории 2026",
                "excerpt": "Серия от тематични работилници за родители, младежи и местни артисти.",
                "body": (
                    "Архив на сезонна инициатива с пространство за публикуване на цели, "
                    "график, резултати и външни ресурси."
                ),
                "published_at": today - timedelta(days=2),
            },
        ]
        for spec in project_specs:
            story, _ = Story.objects.get_or_create(slug=spec["slug"], defaults=spec)
            if not story.attachments.exists():
                StoryAttachment.objects.create(
                    story=story,
                    title="Повече информация",
                    external_url="https://example.bg/resources/community-update",
                    description="Примерна външна връзка, която може да бъде заменена с реален ресурс.",
                    sort_order=1,
                )

    def seed_pages(self):
        page_specs = [
            {
                "slug": "history",
                "page_type": PageType.HISTORY,
                "title": "История",
                "intro": "Исторически разказ за развитието на институцията и общността.",
                "body": "Тук може да опишете създаването на организацията, важни етапи и промени в ролята й през годините.",
                "callout_title": "Как да използвате страницата",
                "callout_body": "Публикувайте реални дати, имена и архивни факти след редакционна проверка.",
                "show_in_footer": True,
                "sort_order": 1,
            },
            {
                "slug": "library",
                "page_type": PageType.STANDARD,
                "title": "Библиотека",
                "navigation_title": "Библиотека",
                "intro": "Публична секция за фонда, читателските инициативи и полезна информация за заемане.",
                "body": (
                    "<p>Библиотеката съхранява и развива фонд с художествена, детска, "
                    "научнопопулярна и справочна литература за читатели от всички възрасти.</p>"
                    "<p>Добавете информация за условията за заемане, читателските инициативи, "
                    "новите заглавия и възможностите за дарение на книги.</p>"
                ),
                "callout_title": "Работно време",
                "callout_body": "Понеделник - петък: 09:00 - 18:00\nСъбота и неделя: почивни дни",
                "show_in_header": True,
                "sort_order": 2,
            },
            {
                "slug": "charter",
                "page_type": PageType.CHARTER,
                "title": "Устав",
                "intro": "Секция за правила, устройства и публични нормативни документи.",
                "body": "Използвайте страницата за публикуване на одобрени правни текстове, вътрешни правила и официални документи.",
                "callout_title": "Внимание",
                "callout_body": "Ако имате прикачени файлове, можете да ги публикувате и в секцията за проекти или новини.",
                "show_in_footer": True,
                "sort_order": 2,
            },
            {
                "slug": "board",
                "page_type": PageType.GOVERNANCE,
                "title": "Настоятелство и екип",
                "intro": "Кратко представяне на екипа и членовете на управлението.",
                "body": "Подходящо място за мисия на екипа, мандати и редакторски бележки.",
                "callout_title": "",
                "callout_body": "",
                "show_in_header": True,
                "sort_order": 3,
            },
            {
                "slug": "privacy",
                "page_type": PageType.PRIVACY,
                "title": "Политика за поверителност",
                "intro": "Примерен шаблон за данни, изпратени през формите на сайта.",
                "body": "Опишете как се съхраняват и обработват данните от формите за контакт и записване, кой ги преглежда в администрацията и кой отговаря за тази обработка.",
                "callout_title": "Преди публикуване",
                "callout_body": "Съгласувайте текста с реалните процеси и законови изисквания.",
                "show_in_footer": True,
                "sort_order": 4,
            },
            {
                "slug": "cookies",
                "page_type": PageType.COOKIES,
                "title": "Политика за бисквитки",
                "intro": "Примерен текст за основни и аналитични бисквитки.",
                "body": "Интерфейсът записва избора на посетителя в отделна бисквитка и не активира допълнителни аналитични скриптове по подразбиране.",
                "callout_title": "Текущо поведение",
                "callout_body": "Ако включите външни услуги, опишете ги тук подробно.",
                "show_in_footer": True,
                "sort_order": 5,
            },
        ]
        for spec in page_specs:
            Page.objects.get_or_create(slug=spec["slug"], defaults=spec)

    def seed_history_entries(self):
        if HistoryEntry.objects.exists():
            return
        history_page = Page.objects.filter(slug="history").first()
        if not history_page:
            return
        HistoryEntry.objects.bulk_create(
            [
                HistoryEntry(
                    page=history_page,
                    title="Създаване на читалищната база",
                    slug="founding",
                    period_label="1950-те",
                    summary="Начало на местната културна дейност и първите общностни събирания.",
                    body="Записът може да съчетава кратко резюме с по-подробен текст за събития, участници и архивни материали.",
                    sort_order=1,
                ),
                HistoryEntry(
                    page=history_page,
                    title="Разширяване на програмите за деца",
                    slug="childrens-programs",
                    period_label="1990-те",
                    summary="Добавяне на устойчиви творчески школи и читателски инициативи.",
                    body="Подходящо място за дати, имена на ръководители и снимков архив, когато реалното съдържание бъде подготвено.",
                    sort_order=2,
                ),
                HistoryEntry(
                    page=history_page,
                    title="Съвременна програма и партньорства",
                    slug="modern-programs",
                    period_label="2020+",
                    summary="Нова фаза с проектни формати, работилници и по-структурирана комуникация.",
                    body="Тук могат да се опишат нови услуги, обновяване на пространства и включване на партньорски организации.",
                    sort_order=3,
                ),
            ]
        )

    def seed_board_members(self):
        if BoardMember.objects.exists():
            return
        BoardMember.objects.bulk_create(
            [
                BoardMember(
                    slug="elena-marinova",
                    full_name="Елена Маринова",
                    role="Председател",
                    short_bio="Координира общата програма, партньорствата и развитието на публичните услуги.",
                    biography="Подходящо място за по-дълго представяне на управленски опит, визия и обществени инициативи.",
                    phone="+359 88 444 1101",
                    sort_order=1,
                ),
                BoardMember(
                    slug="nikola-todorov",
                    full_name="Никола Тодоров",
                    role="Секретар",
                    short_bio="Отговаря за административните процеси, графиците и координацията с преподавателите.",
                    biography="Примерно описание на административна роля, организационен опит и контакт с преподавателския екип.",
                    phone="+359 88 444 1102",
                    sort_order=2,
                ),
                BoardMember(
                    slug="yana-hristova",
                    full_name="Яна Христова",
                    role="Координатор програми",
                    short_bio="Поддържа комуникацията с участници, родители и гост-артисти.",
                    biography="Полезно поле за конкретни ресори, текущи инициативи и редакторски бележки за публичния профил.",
                    phone="+359 88 444 1103",
                    sort_order=3,
                ),
            ]
        )

    def seed_footer_links(self):
        if FooterLink.objects.exists():
            return
        FooterLink.objects.bulk_create(
            [
                FooterLink(title="Програми", url="/programs/", sort_order=1),
                FooterLink(title="Новини", url="/novini/", sort_order=2),
                FooterLink(title="История", url="/about/history/", sort_order=3),
                FooterLink(title="Контакти", url="/contact/", sort_order=4),
                FooterLink(title="Поверителност", url="/privacy/", sort_order=5),
                FooterLink(title="Бисквитки", url="/cookies/", sort_order=6),
                FooterLink(
                    title="Facebook",
                    url="https://www.facebook.com/profile.php?id=61550898774893",
                    open_in_new_tab=True,
                    sort_order=7,
                ),
            ]
        )

    def seed_sessions(self):
        if ProgramSession.objects.exists():
            return
        today = timezone.localdate()
        piano_program = Program.objects.filter(slug="piano-studio").first()
        dance_program = Program.objects.filter(slug="folk-rhythm-lab").first()
        drawing_program = Program.objects.filter(slug="drawing-workshop").first()
        ProgramSession.objects.bulk_create(
            [
                ProgramSession(
                    program=piano_program,
                    title="Открита репетиция",
                    date=today + timedelta(days=6),
                    time=time(18, 30),
                    description="Кратка среща за родители и нови участници.",
                    category="Програми",
                    attendees=24,
                    location_name=getattr(piano_program, "location_name", ""),
                ),
                ProgramSession(
                    program=dance_program,
                    title="Среща на читателския клуб",
                    date=today + timedelta(days=10),
                    time=time(19, 0),
                    description="Обсъждане на съвременна българска проза.",
                    category="Клубове",
                    attendees=16,
                    location_name=getattr(dance_program, "location_name", ""),
                ),
                ProgramSession(
                    program=drawing_program,
                    title="Уикенд ателие",
                    date=today + timedelta(days=14),
                    time=time(11, 0),
                    description="Свободна творческа сесия с материали на място.",
                    category="Работилници",
                    attendees=12,
                    location_name=getattr(drawing_program, "location_name", ""),
                ),
            ]
        )

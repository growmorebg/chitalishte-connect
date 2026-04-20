from core.models import (
    FooterLink,
    PublishedQuerySet,
    SeoFieldsMixin,
    SiteSettings,
    SingletonModel,
    TimeStampedModel,
)
from inquiries.models import InquiryStatus, InquirySubmission, InquiryType
from pages.models import (
    BoardMember,
    GalleryImage,
    HistoryEntry,
    HomeFeature,
    HomeMetric,
    HomePage,
    LibraryImage,
    Page,
    PageType,
)
from programs.models import (
    Instructor,
    PricingBlock,
    Program,
    ProgramCategory,
    ProgramGalleryImage,
    ProgramSchedule,
    ProgramSession,
)
from stories.models import Story, StoryAttachment, StoryType

SingletonMixin = SingletonModel
HomeStat = HomeMetric
StaticPage = Page
StaticPageType = PageType
LeadershipMember = BoardMember
ProgramPricing = PricingBlock
Event = ProgramSession
Project = Story
ProjectAttachment = StoryAttachment
ProjectType = StoryType

__all__ = [
    "BoardMember",
    "Event",
    "FooterLink",
    "GalleryImage",
    "HistoryEntry",
    "HomeFeature",
    "HomeMetric",
    "HomePage",
    "HomeStat",
    "InquiryStatus",
    "InquirySubmission",
    "InquiryType",
    "Instructor",
    "LeadershipMember",
    "LibraryImage",
    "Page",
    "PageType",
    "PricingBlock",
    "Program",
    "ProgramCategory",
    "ProgramGalleryImage",
    "ProgramPricing",
    "ProgramSchedule",
    "ProgramSession",
    "Project",
    "ProjectAttachment",
    "ProjectType",
    "PublishedQuerySet",
    "SeoFieldsMixin",
    "SingletonMixin",
    "SingletonModel",
    "SiteSettings",
    "StaticPage",
    "StaticPageType",
    "Story",
    "StoryAttachment",
    "StoryType",
    "TimeStampedModel",
]

"""
Setup script for the Open edX package.
"""

from setuptools import setup

setup(
    name="Open edX",
    version="0.9",
    install_requires=["setuptools"],
    requires=[],
    # NOTE: These are not the names we should be installing.  This tree should
    # be reorganized to be a more conventional Python tree.
    packages=[
        "cms",
        "lms",
        "openedx",
    ],
    entry_points={
        "openedx.course_tab": [
            "ccx = lms.djangoapps.ccx.plugins:CcxCourseTab",
            "courseware = lms.djangoapps.courseware.tabs:CoursewareTab",
            "course_info = lms.djangoapps.courseware.tabs:CourseInfoTab",
            "discussion = lms.djangoapps.discussion.plugins:DiscussionTab",
            "edxnotes = lms.djangoapps.edxnotes.plugins:EdxNotesTab",
            "external_discussion = lms.djangoapps.courseware.tabs:ExternalDiscussionCourseTab",
            "external_link = lms.djangoapps.courseware.tabs:ExternalLinkCourseTab",
            "html_textbooks = lms.djangoapps.courseware.tabs:HtmlTextbookTabs",
            "instructor = lms.djangoapps.instructor.views.instructor_dashboard:InstructorDashboardTab",
            "notes = lms.djangoapps.notes.views:NotesTab",
            "pdf_textbooks = lms.djangoapps.courseware.tabs:PDFTextbookTabs",
            "progress = lms.djangoapps.courseware.tabs:ProgressTab",
            "static_tab = xmodule.tabs:StaticTab",
            "syllabus = lms.djangoapps.courseware.tabs:SyllabusTab",
            "teams = lms.djangoapps.teams.plugins:TeamsTab",
            "textbooks = lms.djangoapps.courseware.tabs:TextbookTabs",
            "wiki = lms.djangoapps.course_wiki.tab:WikiTab",
        ],
        "openedx.course_tool": [
            "course_bookmarks = openedx.features.course_bookmarks.plugins:CourseBookmarksTool",
            "course_updates = openedx.features.course_experience.plugins:CourseUpdatesTool",
            "course_reviews = openedx.features.course_experience.plugins:CourseReviewsTool",
            "verified_upgrade = courseware.course_tools:VerifiedUpgradeTool",
        ],
        "openedx.user_partition_scheme": [
            "random = openedx.core.djangoapps.user_api.partition_schemes:RandomUserPartitionScheme",
            "cohort = openedx.core.djangoapps.course_groups.partition_scheme:CohortPartitionScheme",
            "verification = openedx.core.djangoapps.user_api.partition_schemes:ReturnGroup1PartitionScheme",
            "enrollment_track = openedx.core.djangoapps.verified_track_content.partition_scheme:EnrollmentTrackPartitionScheme",
        ],
        "openedx.block_structure_transformer": [
            "library_content = lms.djangoapps.course_blocks.transformers.library_content:ContentLibraryTransformer",
            "split_test = lms.djangoapps.course_blocks.transformers.split_test:SplitTestTransformer",
            "start_date = lms.djangoapps.course_blocks.transformers.start_date:StartDateTransformer",
            "user_partitions = lms.djangoapps.course_blocks.transformers.user_partitions:UserPartitionTransformer",
            "visibility = lms.djangoapps.course_blocks.transformers.visibility:VisibilityTransformer",
            "hidden_content = lms.djangoapps.course_blocks.transformers.hidden_content:HiddenContentTransformer",
            "course_blocks_api = lms.djangoapps.course_api.blocks.transformers.blocks_api:BlocksAPITransformer",
            "milestones = lms.djangoapps.course_api.blocks.transformers.milestones:MilestonesAndSpecialExamsTransformer",
            "grades = lms.djangoapps.grades.transformer:GradesTransformer",
            "completion = lms.djangoapps.course_api.blocks.transformers.block_completion:BlockCompletionTransformer",
            "load_override_data = lms.djangoapps.course_blocks.transformers.load_override_data:OverrideDataTransformer"
        ],
        "openedx.ace.policy": [
            "bulk_email_optout = lms.djangoapps.bulk_email.policies:CourseEmailOptout"
        ],
        "lms.djangoapp": [
            "ace_common = openedx.core.djangoapps.ace_common.apps:AceCommonConfig",
            "discussion = lms.djangoapps.discussion.apps:DiscussionConfig",
            "grades = lms.djangoapps.grades.apps:GradesConfig",
            "plugins = openedx.core.djangoapps.plugins.apps:PluginsConfig",
            "schedules = openedx.core.djangoapps.schedules.apps:SchedulesConfig",
            "theming = openedx.core.djangoapps.theming.apps:ThemingConfig",
            "bookmarks = openedx.core.djangoapps.bookmarks.apps:BookmarksConfig",
            "zendesk_proxy = openedx.core.djangoapps.zendesk_proxy.apps:ZendeskProxyConfig",
            "instructor = lms.djangoapps.instructor.apps:InstructorConfig",
            # 'navoica_api = navoica-api.navoica_api.apps:NavoicaApiConfig',  # prepared plugin config
        ],
        "cms.djangoapp": [
            "ace_common = openedx.core.djangoapps.ace_common.apps:AceCommonConfig",
            "plugins = openedx.core.djangoapps.plugins.apps:PluginsConfig",
            "schedules = openedx.core.djangoapps.schedules.apps:SchedulesConfig",
            "theming = openedx.core.djangoapps.theming.apps:ThemingConfig",
            "bookmarks = openedx.core.djangoapps.bookmarks.apps:BookmarksConfig",
            "zendesk_proxy = openedx.core.djangoapps.zendesk_proxy.apps:ZendeskProxyConfig",
        ],
    }
)

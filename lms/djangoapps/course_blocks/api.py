"""
API entry point to the course_blocks app with top-level
get_course_blocks function.
"""
from django.conf import settings

from openedx.core.djangoapps.content.block_structure.api import get_block_structure_manager
from openedx.core.djangoapps.content.block_structure.transformers import BlockStructureTransformers

from .transformers import library_content, start_date, user_partitions, visibility, load_override_data
from .usage_info import CourseUsageInfo

INDIVIDUAL_STUDENT_OVERRIDE_PROVIDER = 'courseware.student_field_overrides.IndividualStudentOverrideProvider'


def has_individual_student_override_provider():
    """
    check if FIELD_OVERRIDE_PROVIDERS has class
    `courseware.student_field_overrides.IndividualStudentOverrideProvider`
    """
    return INDIVIDUAL_STUDENT_OVERRIDE_PROVIDER in getattr(settings, 'FIELD_OVERRIDE_PROVIDERS', ())


def get_course_block_access_transformers(grading=False):
    """
    Default list of transformers for manipulating course block structures
    based on the user's access to the course blocks.
    """
    if grading:
        course_block_access_transformers = [
            library_content.ContentLibraryTransformer(),
            user_partitions.UserPartitionTransformer(),
            visibility.VisibilityTransformer(),
        ]
    else:
        course_block_access_transformers = [
            library_content.ContentLibraryTransformer(),
            start_date.StartDateTransformer(),
            user_partitions.UserPartitionTransformer(),
            visibility.VisibilityTransformer(),
        ]
    if has_individual_student_override_provider():
        course_block_access_transformers += [load_override_data.OverrideDataTransformer()]

    return course_block_access_transformers


def get_course_blocks(
        user,
        starting_block_usage_key,
        transformers=None,
        collected_block_structure=None,
        grading=False,
):
    """
    A higher order function implemented on top of the
    block_structure.get_blocks function returning a transformed block
    structure for the given user starting at starting_block_usage_key.

    Arguments:
        user (django.contrib.auth.models.User) - User object for
            which the block structure is to be transformed.

        starting_block_usage_key (UsageKey) - Specifies the starting block
            of the block structure that is to be transformed.

        transformers (BlockStructureTransformers) - A collection of
            transformers whose transform methods are to be called.
            If None, get_course_block_access_transformers() is used.

        collected_block_structure (BlockStructureBlockData) - A
            block structure retrieved from a prior call to
            BlockStructureManager.get_collected.  Can be optionally
            provided if already available, for optimization.

    Returns:
        BlockStructureBlockData - A transformed block structure,
            starting at starting_block_usage_key, that has undergone the
            transform methods for the given user and the course
            associated with the block structure.  If using the default
            transformers, the transformed block structure will be
            exactly equivalent to the blocks that the given user has
            access.
    """
    if not transformers:
        transformers = BlockStructureTransformers(get_course_block_access_transformers(grading))
    transformers.usage_info = CourseUsageInfo(starting_block_usage_key.course_key, user)

    return get_block_structure_manager(starting_block_usage_key.course_key).get_transformed(
        transformers,
        starting_block_usage_key,
        collected_block_structure,
    )

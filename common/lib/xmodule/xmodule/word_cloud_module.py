"""Word cloud is ungraded xblock used by students to
generate and view word cloud.

On the client side we show:
If student does not yet answered - `num_inputs` numbers of text inputs.
If student have answered - words he entered and cloud.
"""

import json
import logging

from pkg_resources import resource_string
from web_fragments.fragment import Fragment
from xblock.fields import Boolean, Dict, Integer, List, Scope, String

from xmodule.editing_module import MetadataOnlyEditingDescriptor
from xmodule.raw_module import EmptyDataRawDescriptor
from xmodule.x_module import XModule

log = logging.getLogger(__name__)

# Make '_' a no-op so we can scrape strings. Using lambda instead of
#  `django.utils.translation.ugettext_noop` because Django cannot be imported in this file
_ = lambda text: text


def pretty_bool(value):
    """Check value for possible `True` value.

    Using this function we can manage different type of Boolean value
    in xml files.
    """
    bool_dict = [True, "True", "true", "T", "t", "1"]
    return value in bool_dict


class WordCloudFields(object):
    """XFields for word cloud."""
    display_name = String(
        display_name=_("Display Name"),
        help=_("The display name for this component."),
        scope=Scope.settings,
        default="Word cloud"
    )
    instructions = String(
        display_name=_("Instructions"),
        help=_("Add instructions to help learners understand how to use the word cloud. Clear instructions are important, especially for learners who have accessibility requirements."),  # nopep8 pylint: disable=C0301
        scope=Scope.settings,
    )
    num_inputs = Integer(
        display_name=_("Inputs"),
        help=_("The number of text boxes available for learners to add words and sentences."),
        scope=Scope.settings,
        default=5,
        values={"min": 1}
    )
    num_top_words = Integer(
        display_name=_("Maximum Words"),
        help=_("The maximum number of words displayed in the generated word cloud."),
        scope=Scope.settings,
        default=250,
        values={"min": 1}
    )
    display_student_percents = Boolean(
        display_name=_("Show Percents"),
        help=_("Statistics are shown for entered words near that word."),
        scope=Scope.settings,
        default=True
    )

    # Fields for descriptor.
    submitted = Boolean(
        help=_("Whether this learner has posted words to the cloud."),
        scope=Scope.user_state,
        default=False
    )
    student_words = List(
        help=_("Student answer."),
        scope=Scope.user_state,
        default=[]
    )
    all_words = Dict(
        help=_("All possible words from all learners."),
        scope=Scope.user_state_summary
    )
    top_words = Dict(
        help=_("Top num_top_words words for word cloud."),
        scope=Scope.user_state_summary
    )


class WordCloudModule(WordCloudFields, XModule):
    """WordCloud Xmodule"""
    js = {
        'js': [
            resource_string(__name__, 'js/src/javascript_loader.js'),
        ],
    }
    css = {'scss': [resource_string(__name__, 'css/word_cloud/display.scss')]}
    js_module_name = "WordCloud"

    def get_state(self):
        """Return success json answer for client."""
        if self.submitted:
            total_count = sum(self.all_words.itervalues())
            return json.dumps({
                'status': 'success',
                'submitted': True,
                'display_student_percents': pretty_bool(
                    self.display_student_percents
                ),
                'student_words': {
                    word: self.all_words[word] for word in self.student_words
                },
                'total_count': total_count,
                'top_words': self.prepare_words(self.top_words, total_count)
            })
        else:
            return json.dumps({
                'status': 'success',
                'submitted': False,
                'display_student_percents': False,
                'student_words': {},
                'total_count': 0,
                'top_words': {}
            })

    def good_word(self, word):
        """Convert raw word to suitable word."""
        return word.strip().lower()

    def prepare_words(self, top_words, total_count):
        """Convert words dictionary for client API.

        :param top_words: Top words dictionary
        :type top_words: dict
        :param total_count: Total number of words
        :type total_count: int

        :rtype: list of dicts. Every dict is 3 keys: text - actual word,
        size - counter of word, percent - percent in top_words dataset.

        Calculates corrected percents for every top word:

        For every word except last, it calculates rounded percent.
        For the last is 100 - sum of all other percents.

        """
        list_to_return = []
        percents = 0
        for num, word_tuple in enumerate(top_words.iteritems()):
            if num == len(top_words) - 1:
                percent = 100 - percents
            else:
                percent = round(100.0 * word_tuple[1] / total_count)
                percents += percent
            list_to_return.append(
                {
                    'text': word_tuple[0],
                    'size': word_tuple[1],
                    'percent': percent
                }
            )
        return list_to_return

    def top_dict(self, dict_obj, amount):
        """Return top words from all words, filtered by number of
        occurences

        :param dict_obj: all words
        :type dict_obj: dict
        :param amount: number of words to be in top dict
        :type amount: int
        :rtype: dict
        """
        return dict(
            sorted(
                dict_obj.items(),
                key=lambda x: x[1],
                reverse=True
            )[:amount]
        )

    def handle_ajax(self, dispatch, data):
        """Ajax handler.

        Args:
            dispatch: string request slug
            data: dict request get parameters

        Returns:
            json string
        """
        if dispatch == 'submit':
            if self.submitted:
                return json.dumps({
                    'status': 'fail',
                    'error': 'You have already posted your data.'
                })

            # Student words from client.
            # FIXME: we must use raw JSON, not a post data (multipart/form-data)
            raw_student_words = data.getall('student_words[]')
            student_words = filter(None, map(self.good_word, raw_student_words))

            self.student_words = student_words

            # FIXME: fix this, when xblock will support mutable types.
            # Now we use this hack.
            # speed issues
            temp_all_words = self.all_words

            self.submitted = True

            # Save in all_words.
            for word in self.student_words:
                temp_all_words[word] = temp_all_words.get(word, 0) + 1

            # Update top_words.
            self.top_words = self.top_dict(
                temp_all_words,
                self.num_top_words
            )

            # Save all_words in database.
            self.all_words = temp_all_words

            return self.get_state()
        elif dispatch == 'get_state':
            return self.get_state()
        else:
            return json.dumps({
                'status': 'fail',
                'error': 'Unknown Command!'
            })

    def student_view(self, context):
        """
        Renders the output that a student will see.
        """
        fragment = Fragment()

        fragment.add_content(self.system.render_template('word_cloud.html', {
            'ajax_url': self.system.ajax_url,
            'display_name': self.display_name,
            'instructions': self.instructions,
            'element_class': self.location.block_type,
            'element_id': self.location.html_id(),
            'num_inputs': self.num_inputs,
            'submitted': self.submitted,
        }))

        fragment.add_javascript_url(self.runtime.local_resource_url(self, 'public/js/d3.min.js'))
        fragment.add_javascript_url(self.runtime.local_resource_url(self, 'public/js/d3.layout.cloud.js'))
        fragment.add_javascript_url(self.runtime.local_resource_url(self, 'public/js/word_cloud.js'))
        fragment.add_javascript_url(self.runtime.local_resource_url(self, 'public/js/word_cloud_main.js'))

        return fragment

    def author_view(self, context):
        """
        Renders the output that an author will see.
        """
        return self.student_view(context)


class WordCloudDescriptor(WordCloudFields, MetadataOnlyEditingDescriptor, EmptyDataRawDescriptor):
    """Descriptor for WordCloud Xmodule."""
    module_class = WordCloudModule
    resources_dir = 'assets/word_cloud'
    template_dir_name = 'word_cloud'

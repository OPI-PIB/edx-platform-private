(function(define) {
    define(['jquery', 'backbone', 'gettext'], function($, Backbone, gettext) {
        'use strict';

        return Backbone.View.extend({

            el: '#discovery-form',
            events: {
                'submit form': 'submitForm'
            },

            initialize: function() {
                this.$searchField = this.$el.find('input');
                this.$searchButton = this.$el.find('button');
                this.$message = this.$el.find('.js-discovery-message');
                this.$loadingIndicator = this.$el.find('#loading-indicator');
            },

            submitForm: function(event) {
                event.preventDefault();
                this.doSearch();
            },

            doSearch: function(term) {
                this.$message.removeClass('not-found');
                if (term !== undefined) {
                    this.$searchField.val(term);
                } else {
                    term = this.$searchField.val();
                }
                this.trigger('search', $.trim(term));
            },

            clearSearch: function() {
                this.$searchField.val('');
            },

            showLoadingIndicator: function() {
                this.$loadingIndicator.removeClass('hidden');
            },

            hideLoadingIndicator: function() {
                this.$loadingIndicator.addClass('hidden');
            },

            showFoundMessage: function(count) {
                var msg = ngettext(
                'Viewing %s course',
                'Viewing %s courses',
                count
            );
                this.$message.html(interpolate(msg, [count]));
                this.$message.removeClass('text-danger');
            },

            showNotFoundMessage: function(term) {
                var msg = interpolate(
                gettext('We couldn\'t find any results for "%s".'),
                [_.escape(term)]
            );
                this.$message.html(msg).addClass('text-danger');
                this.clearSearch();
            },

            showErrorMessage: function() {
                this.$message.html(gettext('There was an error, try searching again.')).addClass('text-danger');
            }

        });
    });
}(define || RequireJS.define));

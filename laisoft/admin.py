from django.contrib import admin
from django.contrib.admin.options import BaseModelAdmin
from django.db.models.constants import LOOKUP_SEP


class AdminBaseWithSelectRelated(BaseModelAdmin):
    """
    Admin Base using list_select_related for get_queryset related fields
    """
    list_select_related = []

    def get_queryset(self, request):
        return super(AdminBaseWithSelectRelated, self).get_queryset(request).select_related(*self.list_select_related)

    def form_apply_select_related(self, form):
        for related_field in self.list_select_related:
            splitted = related_field.split(LOOKUP_SEP)

            if len(splitted) > 1:
                field = splitted[0]
                related = LOOKUP_SEP.join(splitted[1:])
                form.base_fields[field].queryset = form.base_fields[field].queryset.select_related(related)


class AdminInlineWithSelectRelated(admin.TabularInline, AdminBaseWithSelectRelated):
    """
    Admin Inline using list_select_related for get_queryset and get_formset related fields
    """

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(AdminInlineWithSelectRelated, self).get_formset(request, obj, **kwargs)

        self.form_apply_select_related(formset.form)

        return formset


class AdminWithSelectRelated(admin.ModelAdmin, AdminBaseWithSelectRelated):
    """
    Admin using list_select_related for get_queryset and get_form related fields
    """

    def get_form(self, request, obj=None, **kwargs):
        form = super(AdminWithSelectRelated, self).get_form(request, obj, **kwargs)

        self.form_apply_select_related(form)

        return form


class FilterWithSelectRelated(admin.RelatedFieldListFilter):
    list_select_related = []

    def field_choices(self, field, request, model_admin):
        return [
            (getattr(x, field.remote_field.get_related_field().attname), str(x))
            for x in self.get_queryset(field)
        ]

    def get_queryset(self, field):
        return field.remote_field.model._default_manager.select_related(*self.list_select_related)
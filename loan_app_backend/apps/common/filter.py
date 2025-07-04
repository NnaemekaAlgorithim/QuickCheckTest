from django_filters import rest_framework as filters


class GenericFilterSet(filters.FilterSet):
    """
    A reusable filter set that dynamically generates filters for any Django model.
    
    Args:
        model: The Django model to filter.
        fields: List of field names to include in the filter set.
        text_search_fields: List of CharField/EmailField names for text search (icontains).
        date_fields: List of DateTimeField names for exact and range filters.
        boolean_fields: List of BooleanField names for exact filters.
    """
    
    def __init__(self, *args, model=None, fields=None, text_search_fields=None, 
                 date_fields=None, boolean_fields=None, **kwargs):
        self.model = model or self.Meta.model
        self.fields = fields or []
        self.text_search_fields = text_search_fields or []
        self.date_fields = date_fields or []
        self.boolean_fields = boolean_fields or []

        # Initialize parent with empty data to set up meta
        super().__init__(*args, **kwargs)

        # Dynamically add filters based on provided fields
        self._add_dynamic_filters()

    def _add_dynamic_filters(self):
        """Add filters based on field types and provided configurations."""
        # Text search filters (icontains)
        for field_name in self.text_search_fields:
            if field_name in [f.name for f in self.model._meta.get_fields()]:
                self.filters[field_name] = filters.CharFilter(
                    field_name=field_name, lookup_expr='icontains'
                )

        # Date filters (exact and range)
        for field_name in self.date_fields:
            if field_name in [f.name for f in self.model._meta.get_fields()]:
                # Exact date filter
                self.filters[field_name] = filters.DateFilter(
                    field_name=field_name, lookup_expr='exact'
                )
                # Date range filter
                self.filters[f'{field_name}__range'] = filters.DateFromToRangeFilter(
                    field_name=field_name
                )

        # Boolean filters
        for field_name in self.boolean_fields:
            if field_name in [f.name for f in self.model._meta.get_fields()]:
                self.filters[field_name] = filters.BooleanFilter(
                    field_name=field_name
                )

    class Meta:
        model = None  # Placeholder, will be set dynamically
        fields = []   # Placeholder, will be populated dynamically

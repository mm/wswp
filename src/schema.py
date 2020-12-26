"""
Defines input/output schema for data being passed
to and from the API.
"""

from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError, validates, validates_schema, EXCLUDE
from src.model import Activity, Submission

# This will be bound to an application object
# within the app factory
ma = Marshmallow()


class ActivitySchema(ma.SQLAlchemyAutoSchema):
    """Marshmallow schema based off the ORM definition
    of an Activity.
    """
    class Meta:
        model = Activity
        include_fk = True
        # This controls which fields will be exposed:
        fields = (
            "id", "name", "url", "description", "paid",
            "price_desc", "min_players", "max_players",
            "created_date", "submitted_by"
        )
        unknown=EXCLUDE

    # Override URL, because we want to use the built-in
    # Marshmallow URL validator:
    url = fields.URL(required=True)

    # A custom validator for min_players:
    @validates("min_players")
    def validate_players(self, value):
        if value <= 0:
            raise ValidationError("Minimum players has to be at least 1")


class SubmissionSchema(ma.SQLAlchemyAutoSchema):
    """Marshmallow schema based off the ORM definition of
    a Submission.
    """

    class Meta:
        model = Submission
        fields = (
            "id", "name", "url", "description", "paid",
            "price_desc", "min_players", "max_players",
            "created_date", "approved", "archived",
            "submitted_by"
        )
        unknown=EXCLUDE
    # Override URL, because we want to use the built-in
    # Marshmallow URL validator:
    url = fields.URL(required=True)
    approved = fields.Boolean(dump_only=True)
    name = fields.String(required=True)
    description = fields.String(required=True)
    paid = fields.Bool(default=False, missing=False)
    min_players = fields.Integer(required=True)

    # A custom validator for min_players:
    @validates("min_players")
    def validate_players(self, value):
        if value <= 0:
            raise ValidationError("Minimum players has to be at least 1")

    # Custom validator to check and make sure our max players is greater (or equal to) min players
    @validates_schema
    def validate_max_players(self, data, **kwargs):
        if data['max_players'] and data['max_players'] < data['min_players']:
            raise ValidationError({'max_players': ["Maximum players must be blank or greater than the minimum players"]})
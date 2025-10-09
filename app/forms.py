"""Flask-WTF forms."""

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import IntegerField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional


class LoginForm(FlaskForm):
    """Login form."""

    email = StringField(
        "Email",
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "you@example.com", "autocomplete": "email"},
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
        render_kw={"placeholder": "Password", "autocomplete": "current-password"},
    )
    submit = SubmitField("Log In")


class ManualUploadForm(FlaskForm):
    """Manual upload form."""

    file = FileField(
        "PDF File",
        validators=[FileRequired(), FileAllowed(["pdf"], "Only PDF files are allowed")],
    )
    title = StringField(
        "Title",
        validators=[DataRequired(), Length(min=1, max=200)],
        render_kw={"placeholder": "e.g., Refrigerator User Manual"},
    )
    brand = StringField(
        "Brand",
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "e.g., Samsung"},
    )
    model = StringField(
        "Model Number",
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "e.g., RF28R7351SG"},
    )
    device_type = StringField(
        "Device Type",
        validators=[Optional(), Length(max=50)],
        render_kw={"placeholder": "e.g., Appliance, Electronics"},
    )
    room = StringField(
        "Room/Location",
        validators=[Optional(), Length(max=50)],
        render_kw={"placeholder": "e.g., Kitchen"},
    )
    year = IntegerField(
        "Year",
        validators=[Optional()],
        render_kw={"placeholder": "e.g., 2023"},
    )
    tags = StringField(
        "Tags",
        validators=[Optional(), Length(max=200)],
        render_kw={"placeholder": "Comma-separated, e.g., warranty, installation"},
    )
    submit = SubmitField("Upload Manual")


class ManualEditForm(FlaskForm):
    """Manual edit form."""

    title = StringField(
        "Title",
        validators=[DataRequired(), Length(min=1, max=200)],
        render_kw={"placeholder": "e.g., Refrigerator User Manual"},
    )
    brand = StringField(
        "Brand",
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "e.g., Samsung"},
    )
    model = StringField(
        "Model Number",
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "e.g., RF28R7351SG"},
    )
    device_type = StringField(
        "Device Type",
        validators=[Optional(), Length(max=50)],
        render_kw={"placeholder": "e.g., Appliance, Electronics"},
    )
    room = StringField(
        "Room/Location",
        validators=[Optional(), Length(max=50)],
        render_kw={"placeholder": "e.g., Kitchen"},
    )
    year = IntegerField(
        "Year",
        validators=[Optional()],
        render_kw={"placeholder": "e.g., 2023"},
    )
    tags = StringField(
        "Tags",
        validators=[Optional(), Length(max=200)],
        render_kw={"placeholder": "Comma-separated, e.g., warranty, installation"},
    )
    submit = SubmitField("Update Manual")


class SearchForm(FlaskForm):
    """Search form."""

    query = StringField(
        "Search",
        validators=[DataRequired(), Length(min=1, max=200)],
        render_kw={"placeholder": "Search manuals...", "autocomplete": "off"},
    )
    brand = StringField("Brand", validators=[Optional()])
    room = StringField("Room", validators=[Optional()])
    device_type = StringField("Device Type", validators=[Optional()])
    submit = SubmitField("Search")

from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, StringField, SelectField
from wtforms.fields.choices import RadioField


class CreateEntry(FlaskForm):
    age = IntegerField('Age')
    sex = StringField('Sex')
    chestPain = SelectField('Chest Pain Type', choices=[
        'ASY', 'ATA', 'NAP', 'TA'])
    restingBP = IntegerField('Resting BP')
    cholesterol = IntegerField('Cholesterol')
    maxHeartRate = IntegerField('Max Heart Rate')
    restingECG = SelectField('Resting ECG?', choices=['Normal', 'LVH', 'ST'])
    exerciseAngina = SelectField('Exercise Angina', choices=['N', 'Y'])
    heartDisease = RadioField('Heart Disease? (0 / 1)', choices=['0', '1'])
    create = SubmitField('Create')


class DeleteEntry(FlaskForm):
    key = StringField('ID')
    delete = SubmitField('Delete')


class UpdateEntry(FlaskForm):
    key = StringField('ID')
    age = IntegerField('Age')
    sex = StringField('Sex')
    chestPain = SelectField('Chest Pain Type', choices=['',
                                                        'ASY', 'ATA', 'NAP', 'TA'])
    restingBP = IntegerField('Resting BP')
    cholesterol = IntegerField('Cholesterol')
    maxHeartRate = IntegerField('Max Heart Rate')
    restingECG = SelectField('Resting ECG?', choices=[
                             '', 'Normal', 'LVH', 'ST'])
    exerciseAngina = SelectField('Exercise Angina', choices=['', 'N', 'Y'])
    heartDisease = RadioField('Heart Disease? (0 / 1)', choices=['0', '1'])
    update = SubmitField('Update')

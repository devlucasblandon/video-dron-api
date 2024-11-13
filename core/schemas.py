from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    email = fields.Str()

class VideoSchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True)
    size = fields.Str(required=True)
    created_at = fields.DateTime(required=True)
    video_url=fields.Str(required=True)

class TaskSchema(Schema):
    id = fields.Int()
    timestamp = fields.DateTime()
    status = fields.Str()
    filename = fields.Str()
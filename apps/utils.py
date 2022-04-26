def search_(value=None, field=None):
    query = {}
    if value is not None and len(value) != 0:
        query.update({field: {"$in": value}})
    query = query if len(query) != 0 else {"_id": {"$exists": "true"}}
    return {"$match": query}


def search_text(text):
    if text != '':
        query = {'$text':{'$search':text}}
    else:
        query = {"_id":{"$exists": "true"}}
    return {"$match": query}


def search_field(field=None, frame=None):
    query={}
    if field is not None and len(field) != 0:
        query.update({"field": {"$in": field}})
    if frame is not None and len(frame) != 0:
        query.update({"frames.frame": {"$in":frame}})
    query = query if len(query) != 0 else {"_id": {"$exists": "true"}}
    return {"$match": query}


def fulltext_search(db, text, verb, language, field,
                    frames, context):
    results = db.verbs.aggregate([search_text(text),
                    search_(value=verb, field="verb"),
                    {
                        "$unwind":"$examples"
                    },
                    {
                        "$lookup": {
                            "from": "languages",
                            "localField": "lang",
                            "foreignField": "_id",
                            'pipeline': [search_(value=language,
                                                field="lang")],
                            "as": "languages"
                        }},
                    {
                        "$unwind":"$languages"
                    },
                    {
                        "$lookup": {
                            "from": "contexts",
                            "localField": "examples.context",
                            "foreignField": "_id",
                            'pipeline': [search_(value=context,
                                                field="context")],
                            "as": "contexts"
                        }
                    },
                    {
                        "$unwind":"$contexts"
                    },
                    {
                        "$lookup": {
                            "from": "fields",
                            "localField": "field_id",
                            "foreignField": "_id",
                             "pipeline": [search_field(field, frames)],
                            "as": "fields"
                        }
                    },
                    {
                        "$unwind": "$fields"
                    },
                    {
                        "$project": {
                            "examples": {
                                "example": "$examples.example",
                                "translation": "$examples.translation"},
                            "languages": {
                                "language": "$languages.lang",
                                "verb": "$verb",
                            },
                            "frames":{
                                "field":"$fields.field",
                                "frame":"$fields.frames.frame",
                                "context":"$contexts.context"
                            }
                        }
                    },
                ])
    return results


def find_languages(name):
    res = db.fields.aggregate([
                        {'$match': {'field': name}},
                        {'$lookup': {
                            'from': 'verbs',
                            'localField': '_id',
                            'foreignField': 'field_id',
                            'as': 'verbs'
                        }},
                        {'$lookup': {
                            'from': 'languages',
                            'localField': 'verbs.lang',
                            'foreignField': '_id',
                            'as': 'languages'
                        }},
                        {'$unwind': '$languages'},
                        {'$project': {
                            'lang': '$languages.lang',
                        }}
                    ])
    return res

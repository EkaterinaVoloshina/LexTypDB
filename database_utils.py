import pandas as pd
import pymongo
from bson import ObjectId




def init_connection():
    client = pymongo.MongoClient("mongodb+srv://admin:pPfUr2o28YlFw9XL@cluster0.jrhpdpf.mongodb.net/?retryWrites=true&w=majority")
    db = client.lextyp_database
    return db


def check_lang(db, language):
    df_lang = language.unique()
    languages = db.languages.find().distinct('lang')
    for language in df_lang:
        if language not in languages:
            object_id = ObjectId()
            db.languages.insert_one({'_id':object_id,
                                   'lang':language})
            st.text('Добавлен новый язык')


def check_context(db, field, frame, context):
    contexts = db.contexts
    fields = db.fields
    frames = db.frames
    context_id = contexts.find_one({"context":context})
    if not context_id:
        field_id = fields.find_one({"field":field})
        frame_id = frames.find_one({"frame":frame})
        context_id = ObjectId()
        if not field_id:
            field_id = ObjectId()
            fields.insert_one({
                "_id": field_id,
                "field": field,
            })
            st.text("Добавлено новое поле")
        else:
            field_id = field_id["_id"]

        if not frame_id:
            frame_id = ObjectId()
            frames.insert_one({"_id": frame_id,
                          "frame": frame,
                          "field": field_id})
            contexts.insert_one({
            '_id': context_id,
            'context':context,
            'frame': frame_id
            })
            st.text("Добавлен новый фрейм")
        else:
            frame_id = frame_id["_id"]
            st.text("Добавлен новый контекст")
            contexts.insert_one({
                '_id': context_id,
                'context':context,
                'frame': frame_id
                })
    else:
        context_id = context_id['_id']
    return context_id


def check_verbs(db, context_id, verb, example, field,
               translation, speakers, lang):
    lang_id = db.languages.find_one({"lang":lang})["_id"]
    verb_id = db.verbs.find_one({"verb":verb, "lang":lang_id})
    field_id = db.fields.find_one({"field": field})["_id"]
    if not verb_id:
        db.verbs.insert_one({"_id":ObjectId(),
                     "verb":verb,
                     "lang":lang_id,
                     "field_id": field_id,
                     "examples":[{"example":example,
                                "translation":translation,
                                "speakers":speakers,
                                "context":context_id}]})
    else:
        db.verbs.update_one({"_id":verb_id["_id"]},
                            {"$set":{"examples":[{"example":example,
                                     "translation":translation,
                                     "speakers":speakers,
                                     "context":context_id}]}
                         })


def add_data(db, df):
    check_lang(db, df['Language'])
    for num, row in df.iterrows():
        context_id = check_context(db, row["Field"],
                                   row["Frame"], row["Context"])
        check_verbs(db, context_id, row["Verb"], row["Example"], row["Field"],
                   row["Translation"], row["Speakers"], row["Language"])


def find_languages(db, name):
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
        {'$lookup': {
            'from': 'contexts',
            'localField': 'verbs.examples.context',
            'foreignField': '_id',
            'as': 'contexts'
        }},
        {'$lookup': {
            'from': 'frames',
            'localField': 'contexts.frame',
            'foreignField': '_id',
            'as': 'frames'
        }},
        {'$project': {
            'lang': '$languages.lang',
            'frames': '$frames.frame'
        }}
    ])
    return res


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


def find_sem_maps(db, language, field):
    results = db.verbs.aggregate([{"$lookup": {
            "from": "languages",
            "localField": "lang",
            "foreignField": "_id",
            'pipeline': [search_(value=language,
                                 field="lang")],
            "as": "languages"}
            },
            {
                "$lookup": {
                    "from": "contexts",
                    "localField": "examples.context",
                    "foreignField": "_id",
                    "as": "contexts"}
            },
            {
                "$lookup": {
                    "from": "frames",
                    "localField": "contexts.frame",
                    "foreignField": "_id",
                    "as": "frames"}
            },
            {
                "$lookup": {
                    "from": "fields",
                    "localField": "field_id",
                    "foreignField": "_id",
                    "pipeline": [search_(field, "field")],
                    "as": "fields"
                    }
            },
            {"$project": {
                "contexts": "$contexts.context",
                "field": "$fields.field",
                "frames": "$frames.frame",
                "language": "$languages.lang"}
            }, ])
    return results

def fulltext_search(db, text, verb, language, field,
                    frame, context, source):
    results = db.verbs.aggregate([search_text(text),
                    search_(value=verb, field="verb"),
                    search_(value=source, field="examples.source"),
                    {
                        "$unwind":"$examples"
                    },
                    {
                        "$lookup": {
                            "from": "languages",
                            "localField": "lang_id",
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
                            "from": "frames",
                            "localField": "contexts.frame",
                            "foreignField": "_id",
                            'pipeline': [search_(value=frame,
                                                field="frame")],
                            "as": "frames"
                        }
                    },
                    {
                        "$unwind":"$frames"
                    },
                    {
                        "$lookup": {
                            "from": "fields",
                            "localField": "frames.field",
                            "foreignField": "_id",
                             "pipeline": [search_(field, "field")],
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
                                "translation": "$examples.translation",
                                "source": "$examples.source"},
                            "languages": {
                                "language": "$languages.lang",
                                "verb": "$verb",
                            },
                            "frames":{
                                "field":"$fields.field",
                                "frame":"$frames.frame",
                                "context":"$contexts.context"
                            }
                        }
                    },
                ])
    return results


def get_fields(db):
    fields = sorted(list(map(str, db.fields.find().distinct("field"))))
    languages = sorted(list(map(str, db.languages.find().distinct("lang"))))
    verbs = sorted(list(map(str, db.verbs.find().distinct("verb"))))
    frames = sorted(list(map(str, db.frames.find().distinct("frame"))))
    contexts = sorted(list(map(str, db.contexts.find().distinct("context"))))
    sources = sorted(list(map(str, db.verbs.find().distinct("examples.source"))))
    return fields, languages, verbs, frames, contexts, sources
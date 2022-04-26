import pandas as pd
import pymongo

def check_context(db, field, frame, context):
    contexts = db.contexts
    context_id = contexts.find_one({'context':context})
    if not context_id:
        context_id = ObjectId()
        contexts.insert_one({
            '_id': context_id,
            'field':field,
            'frame':frame,
            'context':context
        })
    else:
        context_id = context_id['_id']
    return context_id


def add_data(db, file):
    df = pd.read_csv(file)
    for num, row in df.iterrows():
        context_id = check_context(db, row['Field'],
                                   row['Frame'], row['Context'])
        db.examples.insert_one({
            '_id': ObjectId(),
            'verb': row['Verb'],
            'example': row['Example'],
            'translation': row['Translation'],
            'speakers': row['Speakers'],
            'language': row['Language'],
            'context': context_id
        })
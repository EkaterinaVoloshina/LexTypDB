from flask import Flask
from flask import url_for, render_template, request, redirect

from database_utils import *

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = "tables"

def check_empty(arg_list):
    if arg_list == [""]:
        return list()
    else:
        return arg_list

@app.route('/')
def index():
    db = init_connection()
    fields, languages, verbs, frames, contexts, sources = get_fields(db)
    return render_template('index.html', fields=fields,
                           frames=frames, languages=languages,
                           contexts=contexts, verbs=verbs,
                           sources=sources)



@app.route('/semantic_fields')
def semantic_fields():
    db = init_connection()
    fields = sorted(list(map(str, db.fields.find().distinct("field"))))
    return render_template('semantic_fields.html', fields=fields)

@app.route('/get_field', methods=["get"])
def get_field():
    db = init_connection()
    if not request.args:
        return redirect(url_for('semantic_fields'))

    fields = sorted(list(map(str, db.fields.find().distinct("field"))))
    field = check_empty(request.args.getlist('field'))[0]
    result = find_languages(db, field)
    return render_template('semfields_results.html',
                           result=next(iter(result)), field=field,
                           fields=fields)

@app.route('/about_project')
def about_project():
    return render_template('about_project.html')

@app.route('/visualisation')
def visualisation():
    return render_template('visualisation.html')

@app.route('/get_table', methods=["POST"])
def get_table():
    print(request.form)
    if "file" in request.form:
        file = request.form['file']
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file))
    return render_template('thanks.html')

@app.route('/proceed_survey', methods=["POST"])
def proceed_survey():
    return render_template('additional_survey.html')

@app.route('/survey')
def survey():
    db = init_connection()
    return render_template('survey.html')


@app.route('/forms')
def forms():
    db = init_connection()
    fields = sorted(list(map(str, db.fields.find().distinct("field"))))
    languages = sorted(list(map(str, db.languages.find().distinct("lang"))))
    return render_template('forms.html',
                           fields=fields,
                           languages=languages)

@app.route('/log_in')
def log_in():
    return render_template('log_in.html')

@app.route('/generate_form', methods=['get'])
def generate_form():
    if not request.args:
        return redirect(url_for('forms'))
    print(request.args)
    button = check_empty(request.args.getlist('button'))[0]
    field = check_empty(request.args.getlist('field'))
    language = check_empty(request.args.getlist('language'))
    if button == "table":
        return render_template('table.html')
    elif button == "survey":
        db = init_connection()
        results = list(fulltext_search(db, text="",
                                       verb=None, language=language,
                                       field=field, frame=None,
                                       context=None,
                                       source=None))
        contexts = [res["frames"]["context"] for res in results]
        return render_template('survey.html',
                               contexts=contexts)

@app.route('/process_data', methods=['get'])
def process_data():
    db = init_connection()
    if not request.args:
        return redirect(url_for('index'))
    field = check_empty(request.args.getlist('field'))
    frame = check_empty(request.args.getlist('frame'))
    verb = check_empty(request.args.getlist('verb'))
    context = check_empty(request.args.getlist('context'))
    language = check_empty(request.args.getlist('language'))
    source = check_empty(request.args.getlist('source'))
    text = ""
    results = list(fulltext_search(db, text, verb, language, field, frame, context, source))
    fields, languages, verbs, frames, contexts, sources = get_fields(db)
    if results:
        return render_template('search_results.html',
                               results=results, fields=fields,
                               frames=frames, languages=languages,
                               contexts=contexts, verbs=verbs,
                               num_results=len(results))
    else:
        return render_template('index.html',
                               fields=fields,
                               frames=frames, languages=languages,
                               contexts=contexts, verbs=verbs,
                               )


if __name__ == '__main__':
    app.run()
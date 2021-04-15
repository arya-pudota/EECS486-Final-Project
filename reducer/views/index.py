import flask
import reducer
from reducer import summarize

@reducer.app.route('/', methods=['GET', 'POST'])
def show_index():
	if flask.request.method == 'GET':
		return flask.render_template('index.html')
	
	context = summarize.return_summary(flask.request.form["article_url"])
	return flask.render_template('summary.html', **context)

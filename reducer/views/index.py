import flask
import reducer


@reducer.app.route('/', methods=['GET', 'POST'])
def show_index():
	if flask.request.method == 'GET':
		return flask.render_template('index.html')
	print(f'Article url: {flask.request.form["article_url"]}')
	context = reducer.return_summary(flask.reqest.form["article_url"])
	return flask.render_template('summary.html', **context)

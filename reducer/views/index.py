import flask
import reducer


@reducer.app.route('/', methods=['GET', 'POST'])
def show_index():
	if flask.request.method == 'GET':
		return flask.render_template('index.html')
	
	print(f'Article url: {flask.request.form["article_url"]}')
	context = {
		'article_title': flask.request.form['article_url'],
		'article_summary': 'test summary',
		'home_url': flask.url_for('show_index'),
		'image_url': 'https://i0.wp.com/www.michigandaily.com/wp-content/uploads/2021/04/iam.STK_.City-Hall.2.16.21.0015.jpg?fit=1200%2C800&ssl=1'
		}
	return flask.render_template('summary.html', **context)

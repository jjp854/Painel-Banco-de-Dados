from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
from psycopg2.extras import DictCursor

app = Flask(__name__)
app.secret_key = '123'  # Necessário para usar sessões


def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="base",
        user="postgres",
        password="123"
    )
    return conn


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and 'username' in user:  # Verifica se 'username' está presente em user
            session['username'] = user['username']  # Armazena o username na sessão
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove o username da sessão
    return redirect(url_for('login'))


@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/consulta', methods=['GET', 'POST'])
def consulta():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        search_by = request.form['searchBy']
        search_value = request.form['searchValue']
        conn = get_db_connection()
        cur = conn.cursor()

        query = ""
        if search_by == 'cpf':
            query = "SELECT nome, numero, endereco, conta, cpf FROM m1z WHERE cpf = %s"
        elif search_by == 'nome':
            query = "SELECT nome, numero, endereco, conta, cpf FROM m1z WHERE nome = %s"
        elif search_by == 'numero':
            query = "SELECT nome, numero, endereco, conta, cpf FROM m1z WHERE numero = %s"

        cur.execute(query, (search_value,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result:
            result = {
                'nome': result[0],
                'numero': result[1],
                'endereco': result[2],
                'conta': result[3],
                'cpf': result[4]
            }
        return render_template('consulta.html', result=result)

    return render_template('consulta.html')


if __name__ == '__main__':
    app.run(debug=True)
